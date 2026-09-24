"""The day report: what one day's close shows, as data."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import assert_never

from account_ledger.authorizations import AuthorizationRecord, records
from account_ledger.balances import available_of, closing_of
from account_ledger.config import LedgerConfig
from account_ledger.events import Capitalization, Fee, FeeRefund, InterestAccrual, InterestAdjustment
from account_ledger.ids import AccountId, Day, text
from account_ledger.log import (
    Accepted,
    AlreadyReversed,
    AlreadyUndone,
    IdReused,
    Log,
    LoggedEvent,
    MovedNoMoney,
    Rejected,
    Rejection,
    ReversesAReversal,
    UnknownTarget,
)
from account_ledger.money import Money


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
    """The row a step prints when it fires nothing of its kind (tech-docs 002)."""

    NO_FEE = "no fee assessed or refunded"
    NO_NEW_FEE = "no new fee assessed"
    NO_INTEREST = "no interest accrued"
    NO_CAPITALIZATION = "no interest capitalized"


type EndOfDayEvent = Fee | FeeRefund | InterestAccrual | InterestAdjustment | Capitalization


@dataclass(frozen=True, slots=True)
class Fired:
    """An event a step fired at the day's close."""

    step: Step
    event: EndOfDayEvent


@dataclass(frozen=True, slots=True)
class NothingFired:
    """A step that fired nothing of its kind for these accounts."""

    step: Step
    accounts: tuple[AccountId, ...]
    note: Note


@dataclass(frozen=True, slots=True)
class DayReport:
    """One day's close; each per-account field maps an account ID to its money."""

    day: Day
    closing: Mapping[AccountId, Money]
    available: Mapping[AccountId, Money]
    restated: tuple[Restatement, ...]
    authorizations: tuple[AuthorizationRecord, ...]
    errors: Mapping[AccountId, tuple[str, ...]]
    end_of_day: tuple[Fired | NothingFired, ...]


def report(log: Log, day: Day, config: LedgerConfig, reported: Reported) -> DayReport:
    """The report for ``day`` from the log as it stands at that day's close, restating each earlier closing that
    differs from the one last reported for it (AMB-022)."""
    closings: dict[AccountId, Money] = {account.id: closing_of(log, account, day) for account in config.accounts}
    availables: dict[AccountId, Money] = {account.id: available_of(log, account, day) for account in config.accounts}
    return DayReport(
        day,
        MappingProxyType(closings),
        MappingProxyType(availables),
        _restated(log, day, config, reported),
        records(log),  # every authorization known by the day's end, with its state then (AMB-019, AMB-025)
        MappingProxyType({account.id: _errors(log, day, account.id) for account in config.accounts}),
        _end_of_day(log, day, config) if day >= config.first_day else (),  # Day 0 is the opening, never closed
    )


def _end_of_day(log: Log, day: Day, config: LedgerConfig) -> tuple[Fired | NothingFired, ...]:
    """Each step's events in the order fired, with a row for a step that fired nothing of its kind (tech-docs 002)."""
    fired = [entry.event for entry in log if isinstance(entry, Accepted) and entry.processed_day == day]
    everyone = tuple(account.id for account in config.accounts)
    rows = _fee_rows(fired, everyone) + _interest_rows(fired, everyone)
    if day in config.capitalization_days:  # step 3 has no row on any other day
        rows += _capitalization_rows(fired, everyone)
    return tuple(rows)


def _fee_rows(fired: Sequence[LoggedEvent], everyone: tuple[AccountId, ...]) -> list[Fired | NothingFired]:
    fees = [event for event in fired if isinstance(event, Fee | FeeRefund)]
    rows: list[Fired | NothingFired] = [Fired(Step.FEES, event) for event in fees]
    if not any(isinstance(event, Fee) for event in fees):
        rows.append(NothingFired(Step.FEES, everyone, Note.NO_NEW_FEE if fees else Note.NO_FEE))
    return rows


def _interest_rows(fired: Sequence[LoggedEvent], everyone: tuple[AccountId, ...]) -> list[Fired | NothingFired]:
    rows: list[Fired | NothingFired] = []
    for account in everyone:
        interest = [e for e in fired if isinstance(e, InterestAccrual | InterestAdjustment) and e.account == account]
        rows.extend(Fired(Step.INTEREST, event) for event in interest)
        if not any(isinstance(event, InterestAccrual) for event in interest):
            rows.append(NothingFired(Step.INTEREST, (account,), Note.NO_INTEREST))
    return rows


def _capitalization_rows(fired: Sequence[LoggedEvent], everyone: tuple[AccountId, ...]) -> list[Fired | NothingFired]:
    rows: list[Fired | NothingFired] = []
    for account in everyone:
        paid = [event for event in fired if isinstance(event, Capitalization) and event.account == account]
        rows.extend(Fired(Step.CAPITALIZATION, event) for event in paid)
        if not paid:
            rows.append(NothingFired(Step.CAPITALIZATION, (account,), Note.NO_CAPITALIZATION))
    return rows


def _errors(log: Log, day: Day, account_id: AccountId) -> tuple[str, ...]:
    """Each event refused that day on the account, in log order (AMB-014); a duplicate is not an error."""
    return tuple(
        refusal(entry)
        for entry in log
        if isinstance(entry, Rejected) and entry.processed_day == day and entry.event.account == account_id
    )


def refusal(rejected: Rejected) -> str:
    """A refusal's error text (tech-docs 001, D22)."""
    return f"{text(rejected.event.id)} refused: {_reason(rejected.reason)}"


def _reason(reason: Rejection) -> str:
    match reason:
        case IdReused():
            return "ID already used with different content"
        case AlreadyReversed(target=target, by=by):
            return f"{text(target)} is already reversed by {text(by)}"
        case ReversesAReversal(target=target):
            return f"{text(target)} is a reversal"
        case UnknownTarget(target=target):
            return f"{text(target)} is not in the log"
        case MovedNoMoney(target=target):
            return f"{text(target)} moved no money"
        case AlreadyUndone(part=part, by=by):
            return f"{text(part)} is already undone by {text(by)}"
        case _:
            assert_never(reason)


def _restated(log: Log, day: Day, config: LedgerConfig, reported: Reported) -> tuple[Restatement, ...]:
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
