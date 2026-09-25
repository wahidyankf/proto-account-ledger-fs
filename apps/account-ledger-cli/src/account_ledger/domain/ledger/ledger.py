"""The Ledger: every configured account and the one log they share, and what spans accounts: IDs, cross-account
checks, and the day's close."""

from collections.abc import Callable
from dataclasses import dataclass

from account_ledger.common.result import Err, Ok, Result
from account_ledger.domain.account.account import Account, AccountIn
from account_ledger.domain.account.domain_events import DuplicateIgnored, EventRejected, LogEntry
from account_ledger.domain.account.event_log import EventLog
from account_ledger.domain.account.rejections import IdReused, TargetOnAnotherAccount
from account_ledger.domain.model.config import AccountOpening, LedgerConfig, is_aed
from account_ledger.domain.model.events import (
    IncomingEvent,
    Reversal,
)
from account_ledger.domain.model.ids import AccountId, Day
from account_ledger.domain.model.money import CurrencyMismatch


@dataclass(frozen=True, slots=True)
class UnknownAccount:
    """An event on an account the ledger does not hold; only a bug brings it, since the stream reader refuses one."""

    account: AccountId


type InternalFault = CurrencyMismatch | UnknownAccount

type _Step = Callable[[Account], Result[tuple[LogEntry, ...], CurrencyMismatch]]


@dataclass(frozen=True, slots=True)
class Ledger:
    """The configured accounts and the log of every account's entries, the only state the ledger keeps (AMB-004, D7);
    each operation returns a new ledger and changes none."""

    config: LedgerConfig
    log: EventLog

    @staticmethod
    def open(config: LedgerConfig) -> Ledger:
        """The ledger before any event: the configured accounts and an empty log."""
        return Ledger(config, EventLog(()))

    def find_account(self, opening: AccountOpening) -> Account:
        """The Account aggregate: the account as opened, with its own entries in the log, in log order."""
        # Both branches read alike; each builds the generic account from an opening of one known currency.
        if is_aed(opening):
            return AccountIn(opening.id, opening.balance, self.log.select(opening.id))
        return AccountIn(opening.id, opening.balance, self.log.select(opening.id))

    def list_accounts(self) -> tuple[Account, ...]:
        """Every account, in the configured order."""
        return tuple(self.find_account(opening) for opening in self.config.accounts)

    def process_event(self, event: IncomingEvent, today: Day) -> Result[Ledger, InternalFault]:
        """The ledger with the event's entries appended; ``today`` is the day it is processed on (AMB-015). What spans
        accounts is checked here, against the whole log: a repeated event ID (AMB-034) and a reversal whose target is on
        another account (AMB-036). Everything else the event's own account decides, from its own entries alone."""
        known_entry = self.log.find_first_entry(event.id)  # the event ID is the idempotency key (AMB-034)
        if known_entry is not None:
            if known_entry.event == event:
                return Ok(self._append(DuplicateIgnored(event, today)))
            return Ok(self._append(EventRejected(event, today, IdReused())))
        if isinstance(event, Reversal) and isinstance(target_check := self._check_target_account(event), Err):
            return Ok(self._append(EventRejected(event, today, target_check.error)))
        if isinstance(opening := self._find_opening(event.account), Err):
            return opening
        if isinstance(entries := self.find_account(opening.value).decide_event(event, today), Err):
            return entries
        return Ok(self._append(*entries.value))

    def close_day(self, today: Day) -> Result[Ledger, CurrencyMismatch]:
        """The ledger with every event the close of ``today`` generates: fees, interest, then capitalization, in that
        order (AMB-002, AMB-004, AMB-005, AMB-023). Each step runs on every account before the next step, so the log
        holds each step's events together, in account order."""
        steps: list[_Step] = [
            lambda account: account.assess_fees(today, self.config.first_day),
            lambda account: account.accrue_interest(today, self.config.first_day),
        ]
        if today in self.config.capitalization_days:
            steps.append(lambda account: account.capitalize_interest(today))
        ledger = self
        for step in steps:
            for opening in self.config.accounts:
                if isinstance(entries := step(ledger.find_account(opening)), Err):
                    return entries
                ledger = ledger._append(*entries.value)
        return Ok(ledger)

    def _check_target_account(self, reversal: Reversal) -> Result[None, TargetOnAnotherAccount]:
        """Nothing when the reversal's target is on its own account or nowhere, else the account that holds it."""
        target = self.log.find_first_entry(reversal.target)
        if target is None or target.event.account == reversal.account:
            return Ok(None)
        return Err(TargetOnAnotherAccount(reversal.target, target.event.account))

    def _find_opening(self, account_id: AccountId) -> Result[AccountOpening, UnknownAccount]:
        """The account's opening, or the fault of an account the ledger does not hold."""
        opening = self.config.find_account(account_id)
        return Err(UnknownAccount(account_id)) if opening is None else Ok(opening)

    def _append(self, *entries: LogEntry) -> Ledger:
        """This ledger with the entries at the end of its log; nothing is ever changed or removed."""
        return Ledger(self.config, self.log.append(*entries))
