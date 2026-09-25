"""Balances: pure functions over a log, each scanning it whole (D7) and returning the account's own currency."""

from typing import assert_never

from account_ledger.domain.authorizations import sum_holds
from account_ledger.domain.model.config import Account, AnyAccount, is_aed
from account_ledger.domain.model.event_log import (
    Log,
    LoggedEvent,
    find_first_entry,
    list_counted_events,
    list_instalments,
)
from account_ledger.domain.model.events import (
    Authorization,
    Capitalization,
    Credit,
    Debit,
    Fee,
    FeeRefund,
    Instalment,
    Instalments,
    InterestAccrual,
    InterestAdjustment,
    Reversal,
    Settlement,
    Whole,
)
from account_ledger.domain.model.ids import AccountId, Day
from account_ledger.domain.model.money import Aed, Bhd, Money, narrow_currency


def _list_effects(log: Log, account_id: AccountId) -> list[tuple[Day, Money]]:
    """Each counted entry's value day and signed effect on the account's ledger balance."""
    effects: list[tuple[Day, Money]] = []
    for event in list_counted_events(log, account_id):
        effects.extend((event.value_day, amount) for amount in _list_moved_amounts(log, event))
    return effects


def _list_moved_amounts(log: Log, event: LoggedEvent) -> tuple[Money, ...]:
    """The signed amounts an event moves on the ledger balance; none for an event that moves nothing."""
    match event:
        case Credit():
            match event.posting:
                case Whole():
                    return (event.amount.money,)
                case Instalments():
                    return ()  # a credit in instalments posts nothing itself; its instalments post the parts
                case _:
                    assert_never(event.posting)
        case Instalment() | FeeRefund() | Capitalization():
            return (event.amount.money,)
        case Debit() | Settlement() | Fee():
            return (-event.amount.money,)
        case Authorization():
            return ()  # a hold moves the available balance only, never the ledger balance
        case InterestAccrual() | InterestAdjustment():
            return ()  # interest moves accrued interest, never the ledger balance, until capitalized (AMB-007)
        case Reversal(target=reverses):
            target = find_first_entry(log, reverses)
            undone_amounts = () if target is None else _list_undone_amounts(log, target.event)
            return tuple(-amount for amount in undone_amounts)  # counted from the reversal's own value day
        case _:
            assert_never(event)


def _list_undone_amounts(log: Log, target: LoggedEvent) -> tuple[Money, ...]:
    """What reversing the target takes out: what it moved, and for a credit in instalments, every instalment."""
    match target:
        case Credit(posting=Instalments()):
            amounts: list[Money] = []
            for part in list_instalments(log, target.id):
                amounts.extend(_list_moved_amounts(log, part))
            return tuple(amounts)
        case _:
            return _list_moved_amounts(log, target)


def compute_closing[M: (Aed, Bhd)](log: Log, account: Account[M], day: Day) -> M:
    """The opening plus the effect of every counted entry for the account with value day <= day."""
    total = account.opening
    for value_day, effect in _list_effects(log, account.id):
        if value_day <= day:
            total = total + narrow_currency(total, effect)
    return total


def compute_available[M: (Aed, Bhd)](log: Log, account: Account[M], day: Day) -> M:
    """The closing less the holds."""
    return compute_closing(log, account, day) - sum_holds(log, account, day)


def compute_available_of(log: Log, account: AnyAccount, day: Day) -> Money:
    """``compute_available`` for an account whose currency is known only at run time."""
    if is_aed(account):
        return compute_available(log, account, day)
    return compute_available(log, account, day)


def compute_closing_of(log: Log, account: AnyAccount, day: Day) -> Money:
    """``compute_closing`` for an account whose currency is known only at run time."""
    # The branches read alike, but pyright binds M to Aed in the first and to Bhd in the second.
    if is_aed(account):
        return compute_closing(log, account, day)
    return compute_closing(log, account, day)
