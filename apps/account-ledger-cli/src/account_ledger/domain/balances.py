"""Balances: pure functions over a log, each scanning it whole (D7) and returning the account's own currency."""

from typing import assert_never

from account_ledger.domain.authorizations import holds
from account_ledger.domain.model.config import Account, AnyAccount, is_aed
from account_ledger.domain.model.event_log import Log, LoggedEvent, counted, first, instalments_of
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
from account_ledger.domain.model.money import Aed, Bhd, Money, same


def _effects(log: Log, account_id: AccountId) -> list[tuple[Day, Money]]:
    """Each counted entry's value day and signed effect on the account's ledger balance."""
    return [(event.value_day, moved) for event in counted(log, account_id) for moved in _moved(log, event)]


def _moved(log: Log, event: LoggedEvent) -> tuple[Money, ...]:
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
        case Reversal(reverses=reverses):
            target = first(log, reverses)
            undone = () if target is None else _undone(log, target.event)
            return tuple(-moved for moved in undone)  # counted from the reversal's own value day
        case _:
            assert_never(event)


def _undone(log: Log, target: LoggedEvent) -> tuple[Money, ...]:
    """What reversing the target takes out: what it moved, and for a credit in instalments, every instalment."""
    match target:
        case Credit(posting=Instalments()):
            return tuple(moved for part in instalments_of(log, target.id) for moved in _moved(log, part))
        case _:
            return _moved(log, target)


def closing[M: (Aed, Bhd)](log: Log, account: Account[M], day: Day) -> M:
    """The opening plus the effect of every counted entry for the account with value day <= day."""
    total = account.opening
    for value_day, effect in _effects(log, account.id):
        if value_day <= day:
            total = total + same(total, effect)
    return total


def available[M: (Aed, Bhd)](log: Log, account: Account[M], day: Day) -> M:
    """The closing less the holds."""
    return closing(log, account, day) - holds(log, account, day)


def available_of(log: Log, account: AnyAccount, day: Day) -> Money:
    """``available`` for an account whose currency is known only at run time."""
    if is_aed(account):
        return available(log, account, day)
    return available(log, account, day)


def closing_of(log: Log, account: AnyAccount, day: Day) -> Money:
    """``closing`` for an account whose currency is known only at run time."""
    # The branches read alike, but pyright binds M to Aed in the first and to Bhd in the second.
    if is_aed(account):
        return closing(log, account, day)
    return closing(log, account, day)
