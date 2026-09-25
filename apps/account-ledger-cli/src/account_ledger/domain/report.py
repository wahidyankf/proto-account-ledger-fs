"""The day report: what one day's close shows, as data."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum, auto
from types import MappingProxyType

from account_ledger.domain.authorizations import AuthorizationRecord, records
from account_ledger.domain.balances import available_of, closing_of
from account_ledger.domain.interest import accrued_days_of
from account_ledger.domain.model.config import AnyAccount, LedgerConfig
from account_ledger.domain.model.event_log import (
    Accepted,
    Log,
    LogEntry,
    LoggedEvent,
    Rejected,
    instalments_of,
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
    closing: Mapping[AccountId, Money | None]


type Reported = Mapping[Day, Mapping[AccountId, Money]]


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
    processed: tuple[Processed, ...]
    closing: Mapping[AccountId, Money]
    available: Mapping[AccountId, Money]
    restated: tuple[Restatement, ...]
    authorizations: tuple[AuthorizationRecord, ...]
    errors: Mapping[AccountId, tuple[Rejected, ...]]
    end_of_day: tuple[Fired | Capitalized | NothingFired, ...]


def report(log: Log, day: Day, config: LedgerConfig, reported: Reported) -> DayReport:
    """The report for ``day`` from the log as it stands at that day's close, restating each earlier closing that
    differs from the one last reported for it (AMB-022)."""
    closings: dict[AccountId, Money] = {account.id: closing_of(log, account, day) for account in config.accounts}
    availables: dict[AccountId, Money] = {account.id: available_of(log, account, day) for account in config.accounts}
    applied = _end_of_day(log, day, config) if day >= config.first_day else ()  # Day 0 is the opening, never closed
    return DayReport(
        day,
        _processed(log, day),
        MappingProxyType(closings),
        MappingProxyType(availables),
        _restated(log, day, config, reported),
        records(log),  # every authorization known by the day's end, with its state then (AMB-019, AMB-025)
        MappingProxyType({account.id: _errors(log, day, account.id) for account in config.accounts}),
        applied,
    )


def _processed(log: Log, day: Day) -> tuple[Processed, ...]:
    """Every incoming event processed that day, in log order, with the instalments it fired (tech-docs 002)."""
    processed: list[Processed] = []
    for entry in log:
        event = _incoming(entry)
        if event is not None and entry.processed_day == day:
            fired = instalments_of(log, event.id) if isinstance(entry, Accepted) else ()
            processed.append(Processed(event, entry, fired))
    return tuple(processed)


def _incoming(entry: LogEntry) -> IncomingEvent | None:
    """The entry's event if it came from the stream, or ``None`` if the ledger fired it."""
    match entry.event:
        case Credit() | Debit() | Authorization() | Settlement() | Reversal() as event:
            return event
        case _:
            return None


def _end_of_day(log: Log, day: Day, config: LedgerConfig) -> tuple[Fired | Capitalized | NothingFired, ...]:
    """Each step's events in the order fired, with a row for a step that fired nothing of its kind (tech-docs 002)."""
    fired = [entry.event for entry in log if isinstance(entry, Accepted) and entry.processed_day == day]
    everyone = tuple(account.id for account in config.accounts)
    rows = _fee_rows(fired, everyone) + _interest_rows(fired, everyone)
    if day in config.capitalization_days:  # step 3 has no row on any other day
        rows += _capitalization_rows(log, fired, config.accounts)
    return tuple(rows)


def _fee_rows(
    fired: Sequence[LoggedEvent], everyone: tuple[AccountId, ...]
) -> list[Fired | Capitalized | NothingFired]:
    """Step 1: each fee or refund fired, then a note when no fee was."""
    fees = [event for event in fired if isinstance(event, Fee | FeeRefund)]
    rows: list[Fired | Capitalized | NothingFired] = [Fired(Step.FEES, event) for event in fees]
    if not any(isinstance(event, Fee) for event in fees):
        rows.append(NothingFired(Step.FEES, everyone, Note.NO_NEW_FEE if fees else Note.NO_FEE))
    return rows


def _interest_rows(
    fired: Sequence[LoggedEvent], everyone: tuple[AccountId, ...]
) -> list[Fired | Capitalized | NothingFired]:
    """Step 2: each account's interest events fired, then a note for each account that accrued none."""
    rows: list[Fired | Capitalized | NothingFired] = []
    for account in everyone:
        interest = [e for e in fired if isinstance(e, InterestAccrual | InterestAdjustment) and e.account == account]
        rows.extend(Fired(Step.INTEREST, event) for event in interest)
        if not any(isinstance(event, InterestAccrual) for event in interest):
            rows.append(NothingFired(Step.INTEREST, (account,), Note.NO_INTEREST))
    return rows


def _capitalization_rows(
    log: Log, fired: Sequence[LoggedEvent], accounts: tuple[AnyAccount, ...]
) -> list[Fired | Capitalized | NothingFired]:
    """Step 3: each account's capitalization with the days it gathers, or a note when none was paid."""
    rows: list[Fired | Capitalized | NothingFired] = []
    for account in accounts:
        paid = [event for event in fired if isinstance(event, Capitalization) and event.account == account.id]
        rows.extend(Capitalized(event, accrued_days_of(log, account, event.id)) for event in paid)
        if not paid:
            rows.append(NothingFired(Step.CAPITALIZATION, (account.id,), Note.NO_CAPITALIZATION))
    return rows


def _errors(log: Log, day: Day, account_id: AccountId) -> tuple[Rejected, ...]:
    """Each event refused that day on the account, in log order (AMB-014); a duplicate is not an error."""
    return tuple(
        entry
        for entry in log
        if isinstance(entry, Rejected) and entry.processed_day == day and entry.event.account == account_id
    )


def _restated(log: Log, day: Day, config: LedgerConfig, reported: Reported) -> tuple[Restatement, ...]:
    """Each earlier closing that now differs from the one last reported, oldest first (AMB-022)."""
    restated: list[Restatement] = []
    for earlier in sorted(each for each in reported if each < day):
        changed: dict[AccountId, Money | None] = {}
        for account in config.accounts:
            now = closing_of(log, account, earlier)
            changed[account.id] = None if now == reported[earlier][account.id] else now
        if any(money is not None for money in changed.values()):
            restated.append(Restatement(earlier, MappingProxyType(changed)))
    return tuple(restated)


def reported_after(reported: Reported, day_report: DayReport) -> Reported:
    """The closings last reported for each day, once this report is printed: its own, and each it restated."""
    updated = {each: dict(closings) for each, closings in reported.items()}
    updated[day_report.day] = dict(day_report.closing)
    for restatement in day_report.restated:
        for account_id, money in restatement.closing.items():
            if money is not None:
                updated[restatement.day][account_id] = money
    return MappingProxyType({each: MappingProxyType(closings) for each, closings in updated.items()})
