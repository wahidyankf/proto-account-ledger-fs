"""Balances: pure functions over one account's history, each scanning it whole (D7), in the account's own currency."""

from typing import assert_never

from account_ledger.common.result import Err, Result
from account_ledger.domain.authorizations import sum_holds
from account_ledger.domain.model.event_log import (
    AccountHistory,
    AnyHistory,
    LoggedEvent,
    find_first_entry,
    is_aed_history,
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
from account_ledger.domain.model.ids import Day
from account_ledger.domain.model.money import Aed, Bhd, CurrencyMismatch, Money, sum_money


def _list_effects[M: (Aed, Bhd)](history: AccountHistory[M]) -> list[tuple[Day, Money]]:
    """Each counted entry's value date and signed effect on the account's ledger balance."""
    effects: list[tuple[Day, Money]] = []
    for event in list_counted_events(history):
        effects.extend((event.value_date, amount) for amount in _list_moved_amounts(history, event))
    return effects


def _list_moved_amounts[M: (Aed, Bhd)](history: AccountHistory[M], event: LoggedEvent) -> tuple[Money, ...]:
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
            target = find_first_entry(history.entries, reverses)
            undone_amounts = () if target is None else _list_undone_amounts(history, target.event)
            return tuple(-amount for amount in undone_amounts)  # counted from the reversal's own value date
        case _:
            assert_never(event)


def _list_undone_amounts[M: (Aed, Bhd)](history: AccountHistory[M], target: LoggedEvent) -> tuple[Money, ...]:
    """What reversing the target takes out: what it moved, and for a credit in instalments, every instalment."""
    match target:
        case Credit(posting=Instalments()):
            amounts: list[Money] = []
            for part in list_instalments(history, target.id):
                amounts.extend(_list_moved_amounts(history, part))
            return tuple(amounts)
        case _:
            return _list_moved_amounts(history, target)


def compute_closing[M: (Aed, Bhd)](history: AccountHistory[M], day: Day) -> Result[M, CurrencyMismatch]:
    """The opening plus the effect of every counted entry with value date <= day."""
    effects = [effect for value_date, effect in _list_effects(history) if value_date <= day]
    return sum_money(history.account.opening, effects)


def compute_available[M: (Aed, Bhd)](history: AccountHistory[M], day: Day) -> Result[M, CurrencyMismatch]:
    """The closing less the holds."""
    if isinstance(closing := compute_closing(history, day), Err):
        return closing
    return sum_holds(history, day).map(lambda holds: closing.value - holds)


def compute_available_of(history: AnyHistory, day: Day) -> Result[Money, CurrencyMismatch]:
    """``compute_available`` for an account whose currency is known only at run time."""
    if is_aed_history(history):
        return compute_available(history, day)
    return compute_available(history, day)


def compute_closing_of(history: AnyHistory, day: Day) -> Result[Money, CurrencyMismatch]:
    """``compute_closing`` for an account whose currency is known only at run time."""
    # The branches read alike, but pyright binds M to Aed in the first and to Bhd in the second.
    if is_aed_history(history):
        return compute_closing(history, day)
    return compute_closing(history, day)
