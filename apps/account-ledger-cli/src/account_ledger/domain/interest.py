"""Interest: each day's accrual on a positive closing, adjusted when a closing changes, and its capitalization
(AMB-005, AMB-006, AMB-007, AMB-023)."""

from typing import assert_never

from account_ledger.common.result import Err, Ok, Result
from account_ledger.domain.balances import compute_closing
from account_ledger.domain.model.config import Account, AnyAccount, is_aed
from account_ledger.domain.model.event_log import Accepted, Log, append_entry, list_counted_events
from account_ledger.domain.model.events import Capitalization, InterestAccrual, InterestAdjustment
from account_ledger.domain.model.ids import AccountId, CapitalizationId, Day, InterestId
from account_ledger.domain.model.money import (
    Aed,
    Bhd,
    CurrencyMismatch,
    Direction,
    Money,
    compute_daily_interest,
    make_amount_of,
    sum_money,
)
from account_ledger.domain.reversals import list_reversed_targets


def accrue_interest(log: Log, account: AnyAccount, today: Day, first_day: Day) -> Result[Log, CurrencyMismatch]:
    """For each day so far whose interest differs from what was fired for it, the difference: today's accrual, or an
    adjustment of an earlier day, value-dated today (AMB-005)."""
    if isinstance(changes := _list_interest_changes(log, account, today, first_day), Err):
        return changes
    for day, change in changes.value:
        log = append_entry(log, Accepted(_make_interest_event(account.id, day, today, change), today))
    return Ok(log)


def _list_interest_changes(
    log: Log, account: AnyAccount, today: Day, first_day: Day
) -> Result[tuple[tuple[Day, Money], ...], CurrencyMismatch]:
    """Each day from ``first_day`` to ``today`` whose interest differs from what has fired, with the difference."""
    # Both branches read alike; each narrows the account to one currency for the generic call.
    if is_aed(account):
        return _find_interest_changes(log, account, today, first_day)
    return _find_interest_changes(log, account, today, first_day)


def _find_interest_changes[M: (Aed, Bhd)](
    log: Log, account: Account[M], today: Day, first_day: Day
) -> Result[tuple[tuple[Day, M], ...], CurrencyMismatch]:
    """Each day from ``first_day`` to ``today`` whose interest differs from what has fired, in its currency."""
    changes: list[tuple[Day, M]] = []
    for day in first_day.span_to(today):
        if isinstance(change := _compute_interest_change(log, account, day), Err):
            return change
        if change.value.value != 0:
            changes.append((day, change.value))
    return Ok(tuple(changes))


def _compute_interest_change[M: (Aed, Bhd)](log: Log, account: Account[M], day: Day) -> Result[M, CurrencyMismatch]:
    """The day's interest on its base, less what has fired for it."""
    if isinstance(base := compute_interest_base(log, account, day), Err):
        return base
    return sum_interest_fired(log, account, day).map(lambda fired: compute_daily_interest(base.value) - fired)


def _make_interest_event(
    account: AccountId, day: Day, today: Day, change: Money
) -> InterestAccrual | InterestAdjustment:
    """The event that fires a day's interest change: an accrual for today, an adjustment for an earlier day."""
    direction = Direction.UP if change.value > 0 else Direction.DOWN
    made_amount = make_amount_of(change if direction is Direction.UP else -change)
    assert isinstance(made_amount, Ok)  # a change is never zero
    amount = made_amount.value
    marker = InterestId(account, day, today)
    if day == today:  # nothing is fired for today before its close, so today's change is its first, positive accrual
        return InterestAccrual(marker, account, today, amount)
    return InterestAdjustment(marker, account, today, direction, amount)


def capitalize_interest(log: Log, account: AnyAccount, today: Day) -> Result[Log, CurrencyMismatch]:
    """The account's accrued interest, credited value-dated today when it is above zero (AMB-007, AMB-023)."""
    if isinstance(accrued := _compute_accrued_of(log, account), Err):
        return accrued
    match make_amount_of(accrued.value):
        case Ok(amount):
            capitalization = Capitalization(CapitalizationId(account.id, today), account.id, today, amount)
            return Ok(append_entry(log, Accepted(capitalization, today)))
        case Err():
            return Ok(log)


def _compute_accrued_of(log: Log, account: AnyAccount) -> Result[Money, CurrencyMismatch]:
    """The interest the account has accrued and not yet capitalized."""
    # Both branches read alike; each narrows the account to one currency for the generic call.
    if is_aed(account):
        return compute_accrued(log, account)
    return compute_accrued(log, account)


def compute_accrued[M: (Aed, Bhd)](log: Log, account: Account[M]) -> Result[M, CurrencyMismatch]:
    """The account's interest events, net of their directions, less its capitalizations, each less its reversals
    (AMB-007, AMB-035)."""
    undone_ids = list_reversed_targets(log, account.id)
    changes: list[Money] = []
    for event in list_counted_events(log, account.id):
        match event:
            case InterestAccrual() | InterestAdjustment() if event.id not in undone_ids:
                changes.append(_sign_interest(event))
            case Capitalization(id=capitalization_id, amount=amount) if capitalization_id not in undone_ids:
                changes.append(-amount.money)
            case _:
                pass
    return sum_money(type(account.opening).make_zero(), changes)


def list_accrued_days[M: (Aed, Bhd)](
    log: Log, account: Account[M], capitalization: CapitalizationId
) -> Result[tuple[Day, ...], CurrencyMismatch]:
    """The days whose interest a capitalization pays: each day whose interest events, fired since the account's
    previous capitalization, do not net to zero (tech-docs 003)."""
    zero = type(account.opening).make_zero()
    accrued_days: list[Day] = []
    for day, changes in sorted(_map_interest_since_capitalization(log, account.id, capitalization).items()):
        if isinstance(net_interest := sum_money(zero, changes), Err):
            return net_interest
        if net_interest.value != zero:
            accrued_days.append(day)
    return Ok(tuple(accrued_days))


def _map_interest_since_capitalization(
    log: Log, account_id: AccountId, capitalization: CapitalizationId
) -> dict[Day, list[Money]]:
    """Each day's signed interest events fired since the capitalization before this one, up to this one."""
    undone_ids = list_reversed_targets(log, account_id)
    interest_by_day: dict[Day, list[Money]] = {}
    for event in list_counted_events(log, account_id):
        match event:
            case Capitalization(id=capitalization_id) if capitalization_id == capitalization:
                break
            case Capitalization(id=capitalization_id) if capitalization_id not in undone_ids:
                interest_by_day = {}
            case InterestAccrual() | InterestAdjustment() if event.id not in undone_ids:
                interest_by_day.setdefault(event.id.covered_day, []).append(_sign_interest(event))
            case _:
                pass
    return interest_by_day


def list_accrued_days_of(
    log: Log, account: AnyAccount, capitalization: CapitalizationId
) -> Result[tuple[Day, ...], CurrencyMismatch]:
    """``list_accrued_days`` for an account whose currency is known only at run time."""
    if is_aed(account):
        return list_accrued_days(log, account, capitalization)
    return list_accrued_days(log, account, capitalization)


def compute_interest_base[M: (Aed, Bhd)](log: Log, account: Account[M], day: Day) -> Result[M, CurrencyMismatch]:
    """The closing less any capitalization value-dated that day, which posts after the day's interest (AMB-023); one
    whose reversal that closing already counts is out of it already (AMB-035)."""
    undone_ids = list_reversed_targets(log, account.id, cutoff_day=day)
    capitalized_moneys: list[Money] = []
    for event in list_counted_events(log, account.id):
        match event:
            case Capitalization(id=capitalization_id, value_day=value_day, amount=amount) if (
                value_day == day and capitalization_id not in undone_ids
            ):
                capitalized_moneys.append(-amount.money)
            case _:
                pass
    return compute_closing(log, account, day).flat_map(lambda closing: sum_money(closing, capitalized_moneys))


def sum_interest_fired[M: (Aed, Bhd)](log: Log, account: Account[M], day: Day) -> Result[M, CurrencyMismatch]:
    """The account's interest events for a day, net of their directions and reversals (tech-docs 002, step 2)."""
    undone_ids = list_reversed_targets(log, account.id)
    fired_moneys = [
        _sign_interest(event)
        for event in list_counted_events(log, account.id)
        if isinstance(event, InterestAccrual | InterestAdjustment)
        and event.id.covered_day == day
        and event.id not in undone_ids
    ]
    return sum_money(type(account.opening).make_zero(), fired_moneys)


def _sign_interest(event: InterestAccrual | InterestAdjustment) -> Money:
    """An interest event's amount, negative for an adjustment down."""
    match event:
        case InterestAdjustment(direction=Direction.DOWN, amount=amount):
            return -amount.money
        case InterestAccrual(amount=amount) | InterestAdjustment(amount=amount):
            return amount.money
        case _:
            assert_never(event)
