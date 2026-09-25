"""Interest: each day's accrual on a positive closing, adjusted when a closing changes, and its capitalization
(AMB-005, AMB-006, AMB-007, AMB-023)."""

from collections.abc import Iterator
from typing import assert_never

from account_ledger.domain.balances import closing
from account_ledger.domain.model.config import Account, AnyAccount, is_aed
from account_ledger.domain.model.event_log import Accepted, Log, append, counted
from account_ledger.domain.model.events import Capitalization, InterestAccrual, InterestAdjustment
from account_ledger.domain.model.ids import AccountId, CapitalizationId, Day, InterestId
from account_ledger.domain.model.money import Aed, Bhd, Direction, Money, NotPositive, amount_of, daily_interest, same
from account_ledger.domain.reversals import reversed_targets


def accrue_interest(log: Log, account: AnyAccount, today: Day, first: Day) -> Log:
    """For each day so far whose interest differs from what was fired for it, the difference: today's accrual, or an
    adjustment of an earlier day, value-dated today (AMB-005)."""
    for day, change in _changes(log, account, today, first):
        log = append(log, Accepted(_interest_event(account.id, day, today, change), today))
    return log


def _changes(log: Log, account: AnyAccount, today: Day, first: Day) -> list[tuple[Day, Money]]:
    # Both branches read alike; each narrows the account to one currency for the generic call.
    if is_aed(account):
        return list(_changed(log, account, today, first))
    return list(_changed(log, account, today, first))


def _changed[M: (Aed, Bhd)](log: Log, account: Account[M], today: Day, first: Day) -> Iterator[tuple[Day, M]]:
    for day in first.through(today):
        change = daily_interest(interest_base(log, account, day)) - interest_fired(log, account, day)
        if change.value != 0:
            yield day, change


def _interest_event(account: AccountId, day: Day, today: Day, change: Money) -> InterestAccrual | InterestAdjustment:
    if change.value > 0:
        direction, amount = Direction.UP, amount_of(change)
    else:
        direction, amount = Direction.DOWN, amount_of(-change)
    assert not isinstance(amount, NotPositive)  # a change is never zero
    marker = InterestId(account, day, today)
    if day == today:  # nothing is fired for today before its close, so today's change is its first, positive accrual
        return InterestAccrual(marker, account, today, amount)
    return InterestAdjustment(marker, account, today, direction, amount)


def capitalize_interest(log: Log, account: AnyAccount, today: Day) -> Log:
    """The account's accrued interest, credited value-dated today when it is above zero (AMB-007, AMB-023)."""
    amount = amount_of(_accrued(log, account))
    if isinstance(amount, NotPositive):
        return log
    capitalization = Capitalization(CapitalizationId(account.id, today), account.id, today, amount)
    return append(log, Accepted(capitalization, today))


def _accrued(log: Log, account: AnyAccount) -> Money:
    # Both branches read alike; each narrows the account to one currency for the generic call.
    if is_aed(account):
        return accrued(log, account)
    return accrued(log, account)


def accrued[M: (Aed, Bhd)](log: Log, account: Account[M]) -> M:
    """The account's interest events, net of their directions, less its capitalizations, each less its reversals
    (AMB-007, AMB-035)."""
    total, undone = type(account.opening).zero(), reversed_targets(log, account.id)
    for event in counted(log, account.id):
        match event:
            case InterestAccrual() | InterestAdjustment() if event.id not in undone:
                total = total + same(total, _signed_interest(event))
            case Capitalization(id=paid, amount=amount) if paid not in undone:
                total = total - same(total, amount.money)
            case _:
                pass
    return total


def accrued_days[M: (Aed, Bhd)](log: Log, account: Account[M], capitalization: CapitalizationId) -> tuple[Day, ...]:
    """The days whose interest a capitalization pays: each day whose interest events, fired since the account's
    previous capitalization, do not net to zero (tech-docs 003)."""
    zero, undone = type(account.opening).zero(), reversed_targets(log, account.id)
    net: dict[Day, M] = {}
    for event in counted(log, account.id):
        match event:
            case Capitalization(id=paid) if paid == capitalization:
                break
            case Capitalization(id=paid) if paid not in undone:
                net = {}
            case InterestAccrual() | InterestAdjustment() if event.id not in undone:
                day = event.id.for_day
                net[day] = net.get(day, zero) + same(zero, _signed_interest(event))
            case _:
                pass
    return tuple(sorted(day for day, money in net.items() if money != zero))


def accrued_days_of(log: Log, account: AnyAccount, capitalization: CapitalizationId) -> tuple[Day, ...]:
    """``accrued_days`` for an account whose currency is known only at run time."""
    if is_aed(account):
        return accrued_days(log, account, capitalization)
    return accrued_days(log, account, capitalization)


def interest_base[M: (Aed, Bhd)](log: Log, account: Account[M], day: Day) -> M:
    """The closing less any capitalization value-dated that day, which posts after the day's interest (AMB-023); one
    whose reversal that closing already counts is out of it already (AMB-035)."""
    total = closing(log, account, day)
    undone = reversed_targets(log, account.id, by=day)
    for event in counted(log, account.id):
        match event:
            case Capitalization(id=paid, value_day=value_day, amount=amount) if value_day == day and paid not in undone:
                total = total - same(total, amount.money)
            case _:
                pass
    return total


def interest_fired[M: (Aed, Bhd)](log: Log, account: Account[M], day: Day) -> M:
    """The account's interest events for a day, net of their directions and reversals (tech-docs 002, step 2)."""
    total, undone = type(account.opening).zero(), reversed_targets(log, account.id)
    for event in counted(log, account.id):
        match event:
            case InterestAccrual() | InterestAdjustment() if event.id.for_day == day and event.id not in undone:
                total = total + same(total, _signed_interest(event))
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
        case _:
            assert_never(event)
