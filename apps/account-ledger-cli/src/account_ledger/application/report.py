"""The day report, the read model: what one day's close shows, as data, read from the Ledger and never written back."""

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum, auto
from types import MappingProxyType

from account_ledger.common.result import Err, Ok, Result
from account_ledger.domain.account.account import Account
from account_ledger.domain.account.authorizations import AuthorizationRecord
from account_ledger.domain.account.domain_events import CreditPosted, EventRejected, LogEntry, LoggedEvent
from account_ledger.domain.ledger.ledger import Ledger
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


class Step(Enum):
    """The three end-of-day steps, in the order a close runs them (AMB-023)."""

    FEES = 1
    INTEREST = 2
    CAPITALIZATION = 3


class Note(Enum):
    """Why a step's row shows nothing generated of its kind (tech-docs 002); the report sink prints its text."""

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
    errors: Mapping[AccountId, tuple[EventRejected, ...]]
    end_of_day: tuple[Generated | Capitalized | NothingGenerated, ...]

    @staticmethod
    def build(ledger: Ledger, day: Day, reported: ReportedClosings) -> Result[DayReport, CurrencyMismatch]:
        """The report for ``day`` from the ledger as it stands at that day's close, restating each earlier closing that
        differs from the one last reported for it (AMB-022)."""

        accounts = MappingProxyType({account.id: account for account in ledger.list_accounts()})
        closing_balances = _map_balances(accounts, day, lambda account, on: account.compute_closing(on))

        if isinstance(closing_balances, Err):
            return closing_balances

        available_balances = _map_balances(accounts, day, lambda account, on: account.compute_available(on))

        if isinstance(available_balances, Err):
            return available_balances

        if isinstance(restatements := _list_restatements(accounts, day, reported), Err):
            return restatements

        # Day 0 is the opening, never closed
        end_of_day_rows = _build_end_of_day_rows(ledger, accounts, day) if day >= ledger.config.first_day else Ok(())

        if isinstance(end_of_day_rows, Err):
            return end_of_day_rows

        return Ok(
            DayReport(
                day,
                _list_processed_events(ledger, accounts, day),
                closing_balances.value,
                available_balances.value,
                restatements.value,
                # every authorization known by the day's end, with its state then, account by account (AMB-019, AMB-025)
                tuple(record for account in accounts.values() for record in account.list_records()),
                MappingProxyType({account_id: _list_errors(ledger, day, account_id) for account_id in accounts}),
                end_of_day_rows.value,
            )
        )


@dataclass(frozen=True, slots=True)
class ReportedClosings:
    """The closings last reported for each day, by account: what a later report compares with to restate a day
    (AMB-022)."""

    closings: Mapping[Day, Mapping[AccountId, Money]]

    @staticmethod
    def make_empty() -> ReportedClosings:
        """No day reported yet."""

        return ReportedClosings(MappingProxyType({}))

    def update(self, report: DayReport) -> ReportedClosings:
        """The closings last reported for each day, once this report is printed: its own, and each it restated."""

        updated_closings = {
            reported_day: dict(closing_balances) for reported_day, closing_balances in self.closings.items()
        }

        updated_closings[report.day] = dict(report.closing_balances)

        for restatement in report.restatements:
            for account_id, money in restatement.closing_balances.items():
                if money is not None:
                    updated_closings[restatement.day][account_id] = money

        return ReportedClosings(
            MappingProxyType(
                {
                    reported_day: MappingProxyType(closing_balances)
                    for reported_day, closing_balances in updated_closings.items()
                }
            )
        )

    def list_days_before(self, day: Day) -> tuple[Day, ...]:
        """Each day reported before ``day``, oldest first."""

        return tuple(sorted(reported_day for reported_day in self.closings if reported_day < day))

    def find_closings(self, day: Day) -> Mapping[AccountId, Money]:
        """The closings last reported for the day, by account."""

        return self.closings[day]


def _map_balances(
    accounts: Mapping[AccountId, Account],
    day: Day,
    compute_balance: Callable[[Account, Day], Result[Money, CurrencyMismatch]],
) -> Result[Mapping[AccountId, Money], CurrencyMismatch]:
    """Each account's balance on the day, by its ID, in the configured order."""

    balances: dict[AccountId, Money] = {}

    for account_id, account in accounts.items():
        if isinstance(balance := compute_balance(account, day), Err):
            return balance

        balances[account_id] = balance.value

    return Ok(MappingProxyType(balances))


def _list_processed_events(ledger: Ledger, accounts: Mapping[AccountId, Account], day: Day) -> tuple[Processed, ...]:
    """Every incoming event processed that day, in log order, with the instalments it generated (tech-docs 002)."""

    processed_events: list[Processed] = []

    for entry in ledger.log.list_processed_on(day):
        event = _select_incoming_event(entry)

        if event is not None:
            instalments = accounts[event.account].list_instalments(event.id) if isinstance(entry, CreditPosted) else ()
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
    ledger: Ledger, accounts: Mapping[AccountId, Account], day: Day
) -> Result[tuple[Generated | Capitalized | NothingGenerated, ...], CurrencyMismatch]:
    """Each step's events in the order generated, with a row for a step that generated nothing of its kind
    (tech-docs 002)."""

    generated_events = [entry.event for entry in ledger.log.list_processed_on(day) if _is_generated(entry)]
    account_ids = tuple(accounts)
    rows = _build_fee_rows(generated_events, account_ids) + _build_interest_rows(generated_events, account_ids)

    if day not in ledger.config.capitalization_days:  # step 3 has no row on any other day
        return Ok(tuple(rows))

    if isinstance(capitalization_rows := _build_capitalization_rows(accounts, generated_events), Err):
        return capitalization_rows

    return Ok(tuple(rows + capitalization_rows.value))


def _is_generated(entry: LogEntry) -> bool:
    """Whether the ledger generated the entry's event, rather than taking it from the stream."""

    return _select_incoming_event(entry) is None


def _build_fee_rows(
    generated_events: Sequence[LoggedEvent], account_ids: tuple[AccountId, ...]
) -> list[Generated | Capitalized | NothingGenerated]:
    """Step 1: each fee or refund generated, then a note when no fee was."""

    fees = [event for event in generated_events if isinstance(event, Fee | FeeRefund)]
    rows: list[Generated | Capitalized | NothingGenerated] = [Generated(Step.FEES, event) for event in fees]

    if not any(isinstance(event, Fee) for event in fees):
        rows.append(NothingGenerated(Step.FEES, account_ids, Note.NO_NEW_FEE if fees else Note.NO_FEE))

    return rows


def _build_interest_rows(
    generated_events: Sequence[LoggedEvent], account_ids: tuple[AccountId, ...]
) -> list[Generated | Capitalized | NothingGenerated]:
    """Step 2: each account's interest events generated, then a note for each account that accrued none."""

    rows: list[Generated | Capitalized | NothingGenerated] = []

    for account in account_ids:
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
    accounts: Mapping[AccountId, Account], generated_events: Sequence[LoggedEvent]
) -> Result[list[Generated | Capitalized | NothingGenerated], CurrencyMismatch]:
    """Step 3: each account's capitalization with the days it gathers, or a note when none was paid."""

    rows: list[Generated | Capitalized | NothingGenerated] = []

    for account_id, account in accounts.items():
        capitalizations = [
            event for event in generated_events if isinstance(event, Capitalization) and event.account == account_id
        ]

        for event in capitalizations:
            if isinstance(accrued_days := account.list_accrued_days(event.id), Err):
                return accrued_days

            rows.append(Capitalized(event, accrued_days.value))

        if not capitalizations:
            rows.append(NothingGenerated(Step.CAPITALIZATION, (account_id,), Note.NO_CAPITALIZATION))

    return Ok(rows)


def _list_errors(ledger: Ledger, day: Day, account_id: AccountId) -> tuple[EventRejected, ...]:
    """Each event refused that day on the account, in log order (AMB-014); a duplicate is not an error."""

    return tuple(
        entry
        for entry in ledger.log.list_processed_on(day)
        if isinstance(entry, EventRejected) and entry.event.account == account_id
    )


def _list_restatements(
    accounts: Mapping[AccountId, Account], day: Day, reported: ReportedClosings
) -> Result[tuple[Restatement, ...], CurrencyMismatch]:
    """Each earlier closing that now differs from the one last reported, oldest first (AMB-022)."""

    restatements: list[Restatement] = []

    for earlier_day in reported.list_days_before(day):
        current_closings = _map_balances(accounts, earlier_day, lambda account, on: account.compute_closing(on))

        if isinstance(current_closings, Err):
            return current_closings

        reported_day_closings = reported.find_closings(earlier_day)

        changes: dict[AccountId, Money | None] = {
            account_id: None if closing == reported_day_closings[account_id] else closing
            for account_id, closing in current_closings.value.items()
        }

        if any(money is not None for money in changes.values()):
            restatements.append(Restatement(earlier_day, MappingProxyType(changes)))

    return Ok(tuple(restatements))
