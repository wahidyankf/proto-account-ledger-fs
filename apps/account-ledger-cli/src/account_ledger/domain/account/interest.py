"""Interest: each day's accrual on a positive closing, adjusted when a closing changes, and its capitalization
(AMB-005, AMB-006, AMB-007, AMB-023)."""

from typing import assert_never

from account_ledger.common.result import Err, Ok, Result
from account_ledger.domain.account.balances import (
    compute_closing,
)
from account_ledger.domain.account.domain_events import (
    InterestAccrued,
    InterestAdjusted,
    InterestCapitalized,
    LogEntry,
)
from account_ledger.domain.account.history import (
    AccountHistoryIn,
)
from account_ledger.domain.account.reversals import (
    list_reversed_targets,
)
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


def accrue_interest[M: (Aed, Bhd)](
    history: AccountHistoryIn[M], today: Day, first_day: Day
) -> Result[tuple[LogEntry, ...], CurrencyMismatch]:
    """For each day so far whose interest differs from what was generated for it, the difference: today's accrual, or an
    adjustment of an earlier day, value-dated today (AMB-005)."""
    if isinstance(changes := _find_interest_changes(history, today, first_day), Err):
        return changes
    return Ok(tuple(_record_interest_change(history.account.id, day, today, change) for day, change in changes.value))


def _find_interest_changes[M: (Aed, Bhd)](
    history: AccountHistoryIn[M], today: Day, first_day: Day
) -> Result[tuple[tuple[Day, M], ...], CurrencyMismatch]:
    """Each day from ``first_day`` to ``today`` whose interest differs from what was generated, in its currency."""
    changes: list[tuple[Day, M]] = []
    for day in first_day.span_to(today):
        if isinstance(change := _compute_interest_change(history, day), Err):
            return change
        if change.value.value != 0:
            changes.append((day, change.value))
    return Ok(tuple(changes))


def _compute_interest_change[M: (Aed, Bhd)](history: AccountHistoryIn[M], day: Day) -> Result[M, CurrencyMismatch]:
    """The day's interest on its base, less what was generated for it."""
    if isinstance(base := _compute_interest_base(history, day), Err):
        return base
    return _sum_interest_generated(history, day).map(lambda generated: compute_daily_interest(base.value) - generated)


def _record_interest_change(
    account: AccountId, day: Day, today: Day, change: Money
) -> InterestAccrued | InterestAdjusted:
    """A day's interest change as it is recorded today: an accrual for today, an adjustment for an earlier day."""
    direction = Direction.UP if change.value > 0 else Direction.DOWN
    made_amount = make_amount_of(change if direction is Direction.UP else -change)
    assert isinstance(made_amount, Ok)  # a change is never zero
    amount = made_amount.value
    interest_id = InterestId(account, day, today)
    if (
        day == today
    ):  # nothing is generated for today before its close, so today's change is its first, positive accrual
        return InterestAccrued(InterestAccrual(interest_id, account, today, amount), today)
    return InterestAdjusted(InterestAdjustment(interest_id, account, today, direction, amount), today)


def capitalize_interest[M: (Aed, Bhd)](
    history: AccountHistoryIn[M], today: Day
) -> Result[tuple[LogEntry, ...], CurrencyMismatch]:
    """The account's accrued interest, credited value-dated today when it is above zero (AMB-007, AMB-023)."""
    if isinstance(accrued := _compute_accrued(history), Err):
        return accrued
    account_id = history.account.id
    match make_amount_of(accrued.value):
        case Ok(amount):
            capitalization = Capitalization(CapitalizationId(account_id, today), account_id, today, amount)
            return Ok((InterestCapitalized(capitalization, today),))
        case Err():
            return Ok(())


def _compute_accrued[M: (Aed, Bhd)](history: AccountHistoryIn[M]) -> Result[M, CurrencyMismatch]:
    """The account's interest events, net of their directions, less its capitalizations, each less its reversals
    (AMB-007, AMB-035)."""
    undone_ids = list_reversed_targets(history)
    changes: list[Money] = []
    for event in history.list_counted_events():
        match event:
            case InterestAccrual() | InterestAdjustment() if event.id not in undone_ids:
                changes.append(_sign_interest(event))
            case Capitalization(id=capitalization_id, amount=amount) if capitalization_id not in undone_ids:
                changes.append(-amount.money)
            case _:
                pass
    return sum_money(type(history.account.opening).make_zero(), changes)


def list_accrued_days[M: (Aed, Bhd)](
    history: AccountHistoryIn[M], capitalization: CapitalizationId
) -> Result[tuple[Day, ...], CurrencyMismatch]:
    """The days whose interest a capitalization pays: each day whose interest events, generated since the account's
    previous capitalization, do not net to zero (tech-docs 003)."""
    zero = type(history.account.opening).make_zero()
    accrued_days: list[Day] = []
    for day, changes in sorted(_map_interest_since_capitalization(history, capitalization).items()):
        if isinstance(net_interest := sum_money(zero, changes), Err):
            return net_interest
        if net_interest.value != zero:
            accrued_days.append(day)
    return Ok(tuple(accrued_days))


def _map_interest_since_capitalization[M: (Aed, Bhd)](
    history: AccountHistoryIn[M], capitalization: CapitalizationId
) -> dict[Day, list[Money]]:
    """Each day's signed interest events generated since the capitalization before this one, up to this one."""
    undone_ids = list_reversed_targets(history)
    interest_by_day: dict[Day, list[Money]] = {}
    for event in history.list_counted_events():
        match event:
            case Capitalization(id=capitalization_id) if capitalization_id == capitalization:
                break
            case Capitalization(id=capitalization_id) if capitalization_id not in undone_ids:
                interest_by_day = {}
            case InterestAccrual() | InterestAdjustment() if event.id not in undone_ids:
                interest_by_day.setdefault(event.id.for_day, []).append(_sign_interest(event))
            case _:
                pass
    return interest_by_day


def _compute_interest_base[M: (Aed, Bhd)](history: AccountHistoryIn[M], day: Day) -> Result[M, CurrencyMismatch]:
    """The closing less any capitalization value-dated that day, which posts after the day's interest (AMB-023); one
    whose reversal that closing already counts is out of it already (AMB-035)."""
    undone_ids = list_reversed_targets(history, cutoff_day=day)
    capitalized_values: list[Money] = []
    for event in history.list_counted_events():
        match event:
            case Capitalization(id=capitalization_id, value_date=value_date, amount=amount) if (
                value_date == day and capitalization_id not in undone_ids
            ):
                capitalized_values.append(-amount.money)
            case _:
                pass
    return compute_closing(history, day).flat_map(lambda closing: sum_money(closing, capitalized_values))


def _sum_interest_generated[M: (Aed, Bhd)](history: AccountHistoryIn[M], day: Day) -> Result[M, CurrencyMismatch]:
    """The account's interest events for a day, net of their directions and reversals (tech-docs 002, step 2)."""
    undone_ids = list_reversed_targets(history)
    generated_values = [
        _sign_interest(event)
        for event in history.list_counted_events()
        if isinstance(event, InterestAccrual | InterestAdjustment)
        and event.id.for_day == day
        and event.id not in undone_ids
    ]
    return sum_money(type(history.account.opening).make_zero(), generated_values)


def _sign_interest(event: InterestAccrual | InterestAdjustment) -> Money:
    """An interest event's amount, negative for an adjustment down."""
    match event:
        case InterestAdjustment(direction=Direction.DOWN, amount=amount):
            return -amount.money
        case InterestAccrual(amount=amount) | InterestAdjustment(amount=amount):
            return amount.money
        case _:
            assert_never(event)
