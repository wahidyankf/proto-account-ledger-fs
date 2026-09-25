"""The day report: what one day's close shows, as data."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum, auto
from types import MappingProxyType

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
from account_ledger.domain.model.money import Money


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
    """Why a step's row shows nothing fired of its kind (tech-docs 002); the renderer prints its text."""

    NO_FEE = auto()
    NO_NEW_FEE = auto()
    NO_INTEREST = auto()
    NO_CAPITALIZATION = auto()


type EndOfDayEvent = Fee | FeeRefund | InterestAccrual | InterestAdjustment


@dataclass(frozen=True, slots=True)
class Fired:
    """An event a step fired at the day's close."""

    step: Step
    event: EndOfDayEvent


@dataclass(frozen=True, slots=True)
class Capitalized:
    """Step 3's capitalization, with the days whose interest it pays."""

    event: Capitalization
    days: tuple[Day, ...]


@dataclass(frozen=True, slots=True)
class NothingFired:
    """A step that fired nothing of its kind for these accounts."""

    step: Step
    accounts: tuple[AccountId, ...]
    note: Note


@dataclass(frozen=True, slots=True)
class Processed:
    """An incoming event processed that day, the entry it made whatever its outcome, and the instalments it fired."""

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
    end_of_day: tuple[Fired | Capitalized | NothingFired, ...]


def build_report(log: Log, day: Day, config: LedgerConfig, reported_closings: ReportedClosings) -> DayReport:
    """The report for ``day`` from the log as it stands at that day's close, restating each earlier closing that
    differs from the one last reported for it (AMB-022)."""
    closing_balances: dict[AccountId, Money] = {
        account.id: compute_closing_of(log, account, day) for account in config.accounts
    }
    available_balances: dict[AccountId, Money] = {
        account.id: compute_available_of(log, account, day) for account in config.accounts
    }
    end_of_day_rows = (
        _build_end_of_day_rows(log, day, config) if day >= config.first_day else ()
    )  # Day 0 is the opening, never closed
    return DayReport(
        day,
        _list_processed_events(log, day),
        MappingProxyType(closing_balances),
        MappingProxyType(available_balances),
        _list_restatements(log, day, config, reported_closings),
        list_records(log),  # every authorization known by the day's end, with its state then (AMB-019, AMB-025)
        MappingProxyType({account.id: _list_errors(log, day, account.id) for account in config.accounts}),
        end_of_day_rows,
    )


def _list_processed_events(log: Log, day: Day) -> tuple[Processed, ...]:
    """Every incoming event processed that day, in log order, with the instalments it fired (tech-docs 002)."""
    processed_events: list[Processed] = []
    for entry in log:
        event = _select_incoming_event(entry)
        if event is not None and entry.processed_day == day:
            instalments = list_instalments(log, event.id) if isinstance(entry, Accepted) else ()
            processed_events.append(Processed(event, entry, instalments))
    return tuple(processed_events)


def _select_incoming_event(entry: LogEntry) -> IncomingEvent | None:
    """The entry's event if it came from the stream, or ``None`` if the ledger fired it."""
    match entry.event:
        case Credit() | Debit() | Authorization() | Settlement() | Reversal() as event:
            return event
        case _:
            return None


def _build_end_of_day_rows(log: Log, day: Day, config: LedgerConfig) -> tuple[Fired | Capitalized | NothingFired, ...]:
    """Each step's events in the order fired, with a row for a step that fired nothing of its kind (tech-docs 002)."""
    fired_events = [entry.event for entry in log if isinstance(entry, Accepted) and entry.processed_day == day]
    everyone = tuple(account.id for account in config.accounts)
    rows = _build_fee_rows(fired_events, everyone) + _build_interest_rows(fired_events, everyone)
    if day in config.capitalization_days:  # step 3 has no row on any other day
        rows += _build_capitalization_rows(log, fired_events, config.accounts)
    return tuple(rows)


def _build_fee_rows(
    fired_events: Sequence[LoggedEvent], everyone: tuple[AccountId, ...]
) -> list[Fired | Capitalized | NothingFired]:
    """Step 1: each fee or refund fired, then a note when no fee was."""
    fees = [event for event in fired_events if isinstance(event, Fee | FeeRefund)]
    rows: list[Fired | Capitalized | NothingFired] = [Fired(Step.FEES, event) for event in fees]
    if not any(isinstance(event, Fee) for event in fees):
        rows.append(NothingFired(Step.FEES, everyone, Note.NO_NEW_FEE if fees else Note.NO_FEE))
    return rows


def _build_interest_rows(
    fired_events: Sequence[LoggedEvent], everyone: tuple[AccountId, ...]
) -> list[Fired | Capitalized | NothingFired]:
    """Step 2: each account's interest events fired, then a note for each account that accrued none."""
    rows: list[Fired | Capitalized | NothingFired] = []
    for account in everyone:
        interest = [
            event
            for event in fired_events
            if isinstance(event, InterestAccrual | InterestAdjustment) and event.account == account
        ]
        rows.extend(Fired(Step.INTEREST, event) for event in interest)
        if not any(isinstance(event, InterestAccrual) for event in interest):
            rows.append(NothingFired(Step.INTEREST, (account,), Note.NO_INTEREST))
    return rows


def _build_capitalization_rows(
    log: Log, fired_events: Sequence[LoggedEvent], accounts: tuple[AnyAccount, ...]
) -> list[Fired | Capitalized | NothingFired]:
    """Step 3: each account's capitalization with the days it gathers, or a note when none was paid."""
    rows: list[Fired | Capitalized | NothingFired] = []
    for account in accounts:
        capitalizations = [
            event for event in fired_events if isinstance(event, Capitalization) and event.account == account.id
        ]
        rows.extend(Capitalized(event, list_accrued_days_of(log, account, event.id)) for event in capitalizations)
        if not capitalizations:
            rows.append(NothingFired(Step.CAPITALIZATION, (account.id,), Note.NO_CAPITALIZATION))
    return rows


def _list_errors(log: Log, day: Day, account_id: AccountId) -> tuple[Rejected, ...]:
    """Each event refused that day on the account, in log order (AMB-014); a duplicate is not an error."""
    return tuple(
        entry
        for entry in log
        if isinstance(entry, Rejected) and entry.processed_day == day and entry.event.account == account_id
    )


def _list_restatements(
    log: Log, day: Day, config: LedgerConfig, reported_closings: ReportedClosings
) -> tuple[Restatement, ...]:
    """Each earlier closing that now differs from the one last reported, oldest first (AMB-022)."""
    restatements: list[Restatement] = []
    for earlier_day in sorted(reported_day for reported_day in reported_closings if reported_day < day):
        changes: dict[AccountId, Money | None] = {}
        for account in config.accounts:
            current_closing = compute_closing_of(log, account, earlier_day)
            changes[account.id] = (
                None if current_closing == reported_closings[earlier_day][account.id] else current_closing
            )
        if any(money is not None for money in changes.values()):
            restatements.append(Restatement(earlier_day, MappingProxyType(changes)))
    return tuple(restatements)


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
