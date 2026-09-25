"""Interest: each day's accrual on a positive closing, adjusted when a closing changes, and its capitalization
(AMB-005, AMB-006, AMB-007, AMB-023)."""

from collections.abc import Iterator
from typing import assert_never

from account_ledger.domain.balances import compute_closing
from account_ledger.domain.model.config import Account, AnyAccount, is_aed
from account_ledger.domain.model.event_log import Accepted, Log, append_entry, list_counted_events
from account_ledger.domain.model.events import Capitalization, InterestAccrual, InterestAdjustment
from account_ledger.domain.model.ids import AccountId, CapitalizationId, Day, InterestId
from account_ledger.domain.model.money import (
    Aed,
    Bhd,
    Direction,
    Money,
    NotPositive,
    compute_daily_interest,
    make_amount_of,
    narrow_currency,
)
from account_ledger.domain.reversals import list_reversed_targets


def accrue_interest(log: Log, account: AnyAccount, today: Day, first_day: Day) -> Log:
    """For each day so far whose interest differs from what was fired for it, the difference: today's accrual, or an
    adjustment of an earlier day, value-dated today (AMB-005)."""
    for day, change in _list_interest_changes(log, account, today, first_day):
        log = append_entry(log, Accepted(_make_interest_event(account.id, day, today, change), today))
    return log


def _list_interest_changes(log: Log, account: AnyAccount, today: Day, first_day: Day) -> list[tuple[Day, Money]]:
    """Each day from ``first_day`` to ``today`` whose interest differs from what has fired, with the difference."""
    # Both branches read alike; each narrows the account to one currency for the generic call.
    if is_aed(account):
        return list(_find_interest_changes(log, account, today, first_day))
    return list(_find_interest_changes(log, account, today, first_day))


def _find_interest_changes[M: (Aed, Bhd)](
    log: Log, account: Account[M], today: Day, first_day: Day
) -> Iterator[tuple[Day, M]]:
    """Each day from ``first_day`` to ``today`` whose interest differs from what has fired, in its currency."""
    for day in first_day.span_to(today):
        change = compute_daily_interest(compute_interest_base(log, account, day)) - sum_interest_fired(
            log, account, day
        )
        if change.value != 0:
            yield day, change


def _make_interest_event(
    account: AccountId, day: Day, today: Day, change: Money
) -> InterestAccrual | InterestAdjustment:
    """The event that fires a day's interest change: an accrual for today, an adjustment for an earlier day."""
    if change.value > 0:
        direction, amount = Direction.UP, make_amount_of(change)
    else:
        direction, amount = Direction.DOWN, make_amount_of(-change)
    assert not isinstance(amount, NotPositive)  # a change is never zero
    marker = InterestId(account, day, today)
    if day == today:  # nothing is fired for today before its close, so today's change is its first, positive accrual
        return InterestAccrual(marker, account, today, amount)
    return InterestAdjustment(marker, account, today, direction, amount)


def capitalize_interest(log: Log, account: AnyAccount, today: Day) -> Log:
    """The account's accrued interest, credited value-dated today when it is above zero (AMB-007, AMB-023)."""
    amount = make_amount_of(_compute_accrued_of(log, account))
    if isinstance(amount, NotPositive):
        return log
    capitalization = Capitalization(CapitalizationId(account.id, today), account.id, today, amount)
    return append_entry(log, Accepted(capitalization, today))


def _compute_accrued_of(log: Log, account: AnyAccount) -> Money:
    """The interest the account has accrued and not yet capitalized."""
    # Both branches read alike; each narrows the account to one currency for the generic call.
    if is_aed(account):
        return compute_accrued(log, account)
    return compute_accrued(log, account)


def compute_accrued[M: (Aed, Bhd)](log: Log, account: Account[M]) -> M:
    """The account's interest events, net of their directions, less its capitalizations, each less its reversals
    (AMB-007, AMB-035)."""
    total, undone_ids = type(account.opening).make_zero(), list_reversed_targets(log, account.id)
    for event in list_counted_events(log, account.id):
        match event:
            case InterestAccrual() | InterestAdjustment() if event.id not in undone_ids:
                total = total + narrow_currency(total, _sign_interest(event))
            case Capitalization(id=capitalization_id, amount=amount) if capitalization_id not in undone_ids:
                total = total - narrow_currency(total, amount.money)
            case _:
                pass
    return total


def list_accrued_days[M: (Aed, Bhd)](
    log: Log, account: Account[M], capitalization: CapitalizationId
) -> tuple[Day, ...]:
    """The days whose interest a capitalization pays: each day whose interest events, fired since the account's
    previous capitalization, do not net to zero (tech-docs 003)."""
    zero, undone_ids = type(account.opening).make_zero(), list_reversed_targets(log, account.id)
    net_interest: dict[Day, M] = {}
    for event in list_counted_events(log, account.id):
        match event:
            case Capitalization(id=capitalization_id) if capitalization_id == capitalization:
                break
            case Capitalization(id=capitalization_id) if capitalization_id not in undone_ids:
                net_interest = {}
            case InterestAccrual() | InterestAdjustment() if event.id not in undone_ids:
                day = event.id.covered_day
                net_interest[day] = net_interest.get(day, zero) + narrow_currency(zero, _sign_interest(event))
            case _:
                pass
    return tuple(sorted(day for day, money in net_interest.items() if money != zero))


def list_accrued_days_of(log: Log, account: AnyAccount, capitalization: CapitalizationId) -> tuple[Day, ...]:
    """``list_accrued_days`` for an account whose currency is known only at run time."""
    if is_aed(account):
        return list_accrued_days(log, account, capitalization)
    return list_accrued_days(log, account, capitalization)


def compute_interest_base[M: (Aed, Bhd)](log: Log, account: Account[M], day: Day) -> M:
    """The closing less any capitalization value-dated that day, which posts after the day's interest (AMB-023); one
    whose reversal that closing already counts is out of it already (AMB-035)."""
    total = compute_closing(log, account, day)
    undone_ids = list_reversed_targets(log, account.id, cutoff_day=day)
    for event in list_counted_events(log, account.id):
        match event:
            case Capitalization(id=capitalization_id, value_day=value_day, amount=amount) if (
                value_day == day and capitalization_id not in undone_ids
            ):
                total = total - narrow_currency(total, amount.money)
            case _:
                pass
    return total


def sum_interest_fired[M: (Aed, Bhd)](log: Log, account: Account[M], day: Day) -> M:
    """The account's interest events for a day, net of their directions and reversals (tech-docs 002, step 2)."""
    total, undone_ids = type(account.opening).make_zero(), list_reversed_targets(log, account.id)
    for event in list_counted_events(log, account.id):
        match event:
            case InterestAccrual() | InterestAdjustment() if event.id.covered_day == day and event.id not in undone_ids:
                total = total + narrow_currency(total, _sign_interest(event))
            case _:
                pass
    return total


def _sign_interest(event: InterestAccrual | InterestAdjustment) -> Money:
    """An interest event's amount, negative for an adjustment down."""
    match event:
        case InterestAdjustment(direction=Direction.DOWN, amount=amount):
            return -amount.money
        case InterestAccrual(amount=amount) | InterestAdjustment(amount=amount):
            return amount.money
        case _:
            assert_never(event)
