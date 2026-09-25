"""The Account aggregate: one account's history, answering every rule about the account as a method."""

from dataclasses import dataclass

from account_ledger.common.result import Result
from account_ledger.domain.account.authorizations import AuthorizationRecord, list_records, sum_holds
from account_ledger.domain.account.balances import compute_available, compute_closing
from account_ledger.domain.account.decisions import decide_event
from account_ledger.domain.account.domain_events import LogEntry
from account_ledger.domain.account.fees import assess_fees
from account_ledger.domain.account.history import AccountHistoryIn
from account_ledger.domain.account.interest import accrue_interest, capitalize_interest, list_accrued_days
from account_ledger.domain.model.events import IncomingEvent
from account_ledger.domain.model.ids import CapitalizationId, Day
from account_ledger.domain.model.money import Aed, Bhd, CurrencyMismatch


@dataclass(frozen=True, slots=True)
class AccountAggregateIn[M: (Aed, Bhd)](AccountHistoryIn[M]):
    """The Account aggregate: its history, with each rule about the account as a method. Each method passes the
    history to the rule in its topic's module, so a caller outside the aggregate asks the account, and never needs to
    know its currency."""

    def compute_closing(self, day: Day) -> Result[M, CurrencyMismatch]:
        """The closing balance on the day (D7)."""
        return compute_closing(self, day)

    def compute_available(self, day: Day) -> Result[M, CurrencyMismatch]:
        """The available balance on the day: the closing less the holds."""
        return compute_available(self, day)

    def sum_holds(self, day: Day) -> Result[M, CurrencyMismatch]:
        """The money the account's approved authorizations hold on the day."""
        return sum_holds(self, day)

    def list_records(self) -> tuple[AuthorizationRecord, ...]:
        """Every authorization the account knows, with its state now."""
        return list_records(self)

    def decide_event(self, event: IncomingEvent, today: Day) -> Result[tuple[LogEntry, ...], CurrencyMismatch]:
        """The entries the account records for an incoming event."""
        return decide_event(self, event, today)

    def assess_fees(self, today: Day, first_day: Day) -> Result[tuple[LogEntry, ...], CurrencyMismatch]:
        """Step 1 of the close: the fees and refunds the account's days call for."""
        return assess_fees(self, today, first_day)

    def accrue_interest(self, today: Day, first_day: Day) -> Result[tuple[LogEntry, ...], CurrencyMismatch]:
        """Step 2 of the close: today's accrual and each earlier day's adjustment."""
        return accrue_interest(self, today, first_day)

    def capitalize_interest(self, today: Day) -> Result[tuple[LogEntry, ...], CurrencyMismatch]:
        """Step 3 of the close, on a capitalization day: the accrued interest credited."""
        return capitalize_interest(self, today)

    def list_accrued_days(self, capitalization: CapitalizationId) -> Result[tuple[Day, ...], CurrencyMismatch]:
        """The days whose interest a capitalization pays."""
        return list_accrued_days(self, capitalization)


type AccountAggregate = AccountAggregateIn[Aed] | AccountAggregateIn[Bhd]
