"""Balances: pure functions over a log, each scanning it whole (D7) and returning the account's own currency."""

from collections.abc import Iterator
from typing import assert_never

from account_ledger.authorizations import Approved, Declined, Settled, records
from account_ledger.config import Account, AnyAccount, is_aed
from account_ledger.events import (
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
from account_ledger.ids import AccountId, Day
from account_ledger.log import Accepted, Log, LoggedEvent, SettlementAccepted, first, instalments_of
from account_ledger.money import Aed, Bhd, CurrencyMismatch, Direction, Money, same_as


def _effects(log: Log, account_id: AccountId) -> list[tuple[Day, Money]]:
    """Each counted entry's value day and signed effect on the account's ledger balance."""
    return [(event.value_day, moved) for event in _counted(log, account_id) for moved in _moved(log, event)]


def _counted(log: Log, account_id: AccountId) -> Iterator[LoggedEvent]:
    """The events of the account's accepted entries; a hold is read by ``holds``, and a refusal moves nothing."""
    for entry in log:
        match entry:
            case Accepted(event=event) | SettlementAccepted(event=event) if event.account == account_id:
                yield event
            case _:
                pass


def _moved(log: Log, event: LoggedEvent) -> tuple[Money, ...]:
    """The signed amounts an event moves on the ledger balance; none for an event that moves nothing."""
    match event:
        case Credit():
            match event.posting:
                case Whole():
                    return (event.amount.money,)
                case Instalments():
                    return ()  # a credit in instalments posts nothing itself; its instalments post the parts
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
            total = total + _same(total, effect)
    return total


def holds[M: (Aed, Bhd)](log: Log, account: Account[M], day: Day) -> M:
    """The hold of every approved authorization on the account whose value day is <= day (AMB-010)."""
    total = type(account.opening).zero()
    for record in records(log):
        opened, state = record.authorization, record.state
        if opened.account != account.id or opened.value_day > day:
            continue
        match state:
            case Approved(hold=hold):
                total = total + _same(total, hold.money)
            case Declined() | Settled():
                pass  # a declined authorization holds nothing, and a final settlement released the hold
            case _:
                assert_never(state)
    return total


def available[M: (Aed, Bhd)](log: Log, account: Account[M], day: Day) -> M:
    """The closing less the holds."""
    return closing(log, account, day) - holds(log, account, day)


def available_of(log: Log, account: AnyAccount, day: Day) -> Money:
    """``available`` for an account whose currency is known only at run time."""
    if is_aed(account):
        return available(log, account, day)
    return available(log, account, day)


def interest_base[M: (Aed, Bhd)](log: Log, account: Account[M], day: Day) -> M:
    """The closing less any capitalization value-dated that day, which posts after the day's interest (AMB-023)."""
    total = closing(log, account, day)
    for event in _counted(log, account.id):
        match event:
            case Capitalization(value_day=value_day, amount=amount) if value_day == day:
                total = total - _same(total, amount.money)
            case _:
                pass
    return total


def accrued[M: (Aed, Bhd)](log: Log, account: Account[M]) -> M:
    """The account's interest events, net of their directions, less its capitalizations (AMB-007)."""
    total = type(account.opening).zero()
    for event in _counted(log, account.id):
        match event:
            case InterestAccrual() | InterestAdjustment():
                total = total + _same(total, _signed_interest(event))
            case Capitalization(amount=amount):
                total = total - _same(total, amount.money)
            case _:
                pass
    return total


def interest_fired[M: (Aed, Bhd)](log: Log, account: Account[M], day: Day) -> M:
    """The account's interest events for a day, net of their directions (tech-docs 002, step 2)."""
    total = type(account.opening).zero()
    for event in _counted(log, account.id):
        match event:
            case InterestAccrual() | InterestAdjustment() if event.id.for_day == day:
                total = total + _same(total, _signed_interest(event))
            case _:
                pass
    return total


def _signed_interest(event: InterestAccrual | InterestAdjustment) -> Money:
    """An interest event's amount, negative for an adjustment down."""
    match event:
        case InterestAdjustment(direction=Direction.DOWN, amount=amount):
            return -amount.money
        case InterestAccrual(amount=amount) | InterestAdjustment(amount=amount):
            return amount.money


def _same[M: (Aed, Bhd)](like: M, money: Money) -> M:
    same = same_as(like, money)
    if isinstance(same, CurrencyMismatch):
        raise ValueError(f"an {same.found} effect on an {same.expected} account")  # the reader makes this unreachable
    return same


def closing_of(log: Log, account: AnyAccount, day: Day) -> Money:
    """``closing`` for an account whose currency is known only at run time."""
    # The branches read alike, but pyright binds M to Aed in the first and to Bhd in the second.
    if is_aed(account):
        return closing(log, account, day)
    return closing(log, account, day)
