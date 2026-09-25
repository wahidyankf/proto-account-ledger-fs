"""The day report: what one day's close shows, as data."""

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum, auto
from types import MappingProxyType

from account_ledger.common.result import Err, Ok, Result
from account_ledger.domain.authorizations import AuthorizationRecord, list_records
from account_ledger.domain.balances import compute_available_of, compute_closing_of
from account_ledger.domain.interest import list_accrued_days_of
from account_ledger.domain.model.config import AnyAccount, LedgerConfig
from account_ledger.domain.model.event_log import (
    Accepted,
    Log,
    LogEntry,
    LoggedEvent,
    Rejected,
    list_instalments,
)
from account_ledger.domain.model.events import (
    Authorization,
    Capitalization,
    Credit,
    Debit,
    Fee,
    FeeRefund,
    IncomingEvent,
    Instalment,
    InterestAccrual,
    InterestAdjustment,
    Reversal,
    Settlement,
)
from account_ledger.domain.model.ids import AccountId, Day
from account_ledger.domain.model.money import CurrencyMismatch, Money


@dataclass(frozen=True, slots=True)
class Restatement:
    """An earlier day's closing that differs from the one last reported for it; None where an account's did not."""

    day: Day
    closing_balances: Mapping[AccountId, Money | None]


type ReportedClosings = Mapping[Day, Mapping[AccountId, Money]]


class Step(Enum):
    """The three end-of-day steps, in the order a close runs them (AMB-023)."""

    FEES = 1
    INTEREST = 2
    CAPITALIZATION = 3


class Note(Enum):
    """Why a step's row shows nothing generated of its kind (tech-docs 002); the renderer prints its text."""

    NO_FEE = auto()
    NO_NEW_FEE = auto()
    NO_INTEREST = auto()
    NO_CAPITALIZATION = auto()


type EndOfDayEvent = Fee | FeeRefund | InterestAccrual | InterestAdjustment


@dataclass(frozen=True, slots=True)
class Generated:
    """An event a step generated at the day's close."""

    step: Step
    event: EndOfDayEvent


@dataclass(frozen=True, slots=True)
class Capitalized:
    """Step 3's capitalization, with the days whose interest it pays."""

    event: Capitalization
    days: tuple[Day, ...]


@dataclass(frozen=True, slots=True)
class NothingGenerated:
    """A step that generated nothing of its kind for these accounts."""

    step: Step
    accounts: tuple[AccountId, ...]
    note: Note


@dataclass(frozen=True, slots=True)
class Processed:
    """An incoming event processed that day, the entry it made whatever its outcome, and the instalments it made."""

    event: IncomingEvent
    entry: LogEntry
    instalments: tuple[Instalment, ...]


@dataclass(frozen=True, slots=True)
class DayReport:
    """One day's close; each per-account field maps an account ID to its money."""

    day: Day
    processed_events: tuple[Processed, ...]
    closing_balances: Mapping[AccountId, Money]
    available_balances: Mapping[AccountId, Money]
    restatements: tuple[Restatement, ...]
    authorizations: tuple[AuthorizationRecord, ...]
    errors: Mapping[AccountId, tuple[Rejected, ...]]
    end_of_day: tuple[Generated | Capitalized | NothingGenerated, ...]


def build_report(
    log: Log, day: Day, config: LedgerConfig, reported_closings: ReportedClosings
) -> Result[DayReport, CurrencyMismatch]:
    """The report for ``day`` from the log as it stands at that day's close, restating each earlier closing that
    differs from the one last reported for it (AMB-022)."""
    if isinstance(closing_balances := _map_balances(log, day, config.accounts, compute_closing_of), Err):
        return closing_balances
    if isinstance(available_balances := _map_balances(log, day, config.accounts, compute_available_of), Err):
        return available_balances
    if isinstance(restatements := _list_restatements(log, day, config, reported_closings), Err):
        return restatements
    # Day 0 is the opening, never closed
    end_of_day_rows = _build_end_of_day_rows(log, day, config) if day >= config.first_day else Ok(())
    if isinstance(end_of_day_rows, Err):
        return end_of_day_rows
    return Ok(
        DayReport(
            day,
            _list_processed_events(log, day),
            closing_balances.value,
            available_balances.value,
            restatements.value,
            list_records(log),  # every authorization known by the day's end, with its state then (AMB-019, AMB-025)
            MappingProxyType({account.id: _list_errors(log, day, account.id) for account in config.accounts}),
            end_of_day_rows.value,
        )
    )


def _map_balances(
    log: Log,
    day: Day,
    accounts: tuple[AnyAccount, ...],
    compute_balance: Callable[[Log, AnyAccount, Day], Result[Money, CurrencyMismatch]],
) -> Result[Mapping[AccountId, Money], CurrencyMismatch]:
    """Each account's balance on the day, by its ID, in the configured order."""
    balances: dict[AccountId, Money] = {}
    for account in accounts:
        if isinstance(balance := compute_balance(log, account, day), Err):
            return balance
        balances[account.id] = balance.value
    return Ok(MappingProxyType(balances))


def _list_processed_events(log: Log, day: Day) -> tuple[Processed, ...]:
    """Every incoming event processed that day, in log order, with the instalments it generated (tech-docs 002)."""
    processed_events: list[Processed] = []
    for entry in log:
        event = _select_incoming_event(entry)
        if event is not None and entry.processed_day == day:
            instalments = list_instalments(log, event.id) if isinstance(entry, Accepted) else ()
            processed_events.append(Processed(event, entry, instalments))
    return tuple(processed_events)


def _select_incoming_event(entry: LogEntry) -> IncomingEvent | None:
    """The entry's event if it came from the stream, or ``None`` if the ledger generated it."""
    match entry.event:
        case Credit() | Debit() | Authorization() | Settlement() | Reversal() as event:
            return event
        case _:
            return None


def _build_end_of_day_rows(
    log: Log, day: Day, config: LedgerConfig
) -> Result[tuple[Generated | Capitalized | NothingGenerated, ...], CurrencyMismatch]:
    """Each step's events in the order generated, with a row for a step that generated nothing of its kind
    (tech-docs 002)."""
    generated_events = [entry.event for entry in log if isinstance(entry, Accepted) and entry.processed_day == day]
    everyone = tuple(account.id for account in config.accounts)
    rows = _build_fee_rows(generated_events, everyone) + _build_interest_rows(generated_events, everyone)
    if day not in config.capitalization_days:  # step 3 has no row on any other day
        return Ok(tuple(rows))
    if isinstance(capitalization_rows := _build_capitalization_rows(log, generated_events, config.accounts), Err):
        return capitalization_rows
    return Ok(tuple(rows + capitalization_rows.value))


def _build_fee_rows(
    generated_events: Sequence[LoggedEvent], everyone: tuple[AccountId, ...]
) -> list[Generated | Capitalized | NothingGenerated]:
    """Step 1: each fee or refund generated, then a note when no fee was."""
    fees = [event for event in generated_events if isinstance(event, Fee | FeeRefund)]
    rows: list[Generated | Capitalized | NothingGenerated] = [Generated(Step.FEES, event) for event in fees]
    if not any(isinstance(event, Fee) for event in fees):
        rows.append(NothingGenerated(Step.FEES, everyone, Note.NO_NEW_FEE if fees else Note.NO_FEE))
    return rows


def _build_interest_rows(
    generated_events: Sequence[LoggedEvent], everyone: tuple[AccountId, ...]
) -> list[Generated | Capitalized | NothingGenerated]:
    """Step 2: each account's interest events generated, then a note for each account that accrued none."""
    rows: list[Generated | Capitalized | NothingGenerated] = []
    for account in everyone:
        interest = [
            event
            for event in generated_events
            if isinstance(event, InterestAccrual | InterestAdjustment) and event.account == account
        ]
        rows.extend(Generated(Step.INTEREST, event) for event in interest)
        if not any(isinstance(event, InterestAccrual) for event in interest):
            rows.append(NothingGenerated(Step.INTEREST, (account,), Note.NO_INTEREST))
    return rows


def _build_capitalization_rows(
    log: Log, generated_events: Sequence[LoggedEvent], accounts: tuple[AnyAccount, ...]
) -> Result[list[Generated | Capitalized | NothingGenerated], CurrencyMismatch]:
    """Step 3: each account's capitalization with the days it gathers, or a note when none was paid."""
    rows: list[Generated | Capitalized | NothingGenerated] = []
    for account in accounts:
        capitalizations = [
            event for event in generated_events if isinstance(event, Capitalization) and event.account == account.id
        ]
        for event in capitalizations:
            if isinstance(accrued_days := list_accrued_days_of(log, account, event.id), Err):
                return accrued_days
            rows.append(Capitalized(event, accrued_days.value))
        if not capitalizations:
            rows.append(NothingGenerated(Step.CAPITALIZATION, (account.id,), Note.NO_CAPITALIZATION))
    return Ok(rows)


def _list_errors(log: Log, day: Day, account_id: AccountId) -> tuple[Rejected, ...]:
    """Each event refused that day on the account, in log order (AMB-014); a duplicate is not an error."""
    return tuple(
        entry
        for entry in log
        if isinstance(entry, Rejected) and entry.processed_day == day and entry.event.account == account_id
    )


def _list_restatements(
    log: Log, day: Day, config: LedgerConfig, reported_closings: ReportedClosings
) -> Result[tuple[Restatement, ...], CurrencyMismatch]:
    """Each earlier closing that now differs from the one last reported, oldest first (AMB-022)."""
    restatements: list[Restatement] = []
    for earlier_day in sorted(reported_day for reported_day in reported_closings if reported_day < day):
        if isinstance(current_closings := _map_balances(log, earlier_day, config.accounts, compute_closing_of), Err):
            return current_closings
        reported_day_closings = reported_closings[earlier_day]
        changes: dict[AccountId, Money | None] = {
            account_id: None if closing == reported_day_closings[account_id] else closing
            for account_id, closing in current_closings.value.items()
        }
        if any(money is not None for money in changes.values()):
            restatements.append(Restatement(earlier_day, MappingProxyType(changes)))
    return Ok(tuple(restatements))


def update_reported(reported_closings: ReportedClosings, day_report: DayReport) -> ReportedClosings:
    """The closings last reported for each day, once this report is printed: its own, and each it restated."""
    updated_closings = {
        reported_day: dict(closing_balances) for reported_day, closing_balances in reported_closings.items()
    }
    updated_closings[day_report.day] = dict(day_report.closing_balances)
    for restatement in day_report.restatements:
        for account_id, money in restatement.closing_balances.items():
            if money is not None:
                updated_closings[restatement.day][account_id] = money
    return MappingProxyType(
        {
            reported_day: MappingProxyType(closing_balances)
            for reported_day, closing_balances in updated_closings.items()
        }
    )
