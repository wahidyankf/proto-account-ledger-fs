"""Processing one incoming event at the ledger level: what spans accounts first, then the account decides."""

from account_ledger.common.result import Err, Ok, Result
from account_ledger.domain.account.domain_events import DuplicateIgnored, EventRejected
from account_ledger.domain.account.event_log import EventLog
from account_ledger.domain.account.rejections import IdReused, TargetOnAnotherAccount
from account_ledger.domain.ledger.event_log import (
    Log,
    append_entry,
    find_history_of,
)
from account_ledger.domain.model.config import LedgerConfig
from account_ledger.domain.model.events import (
    IncomingEvent,
    Reversal,
)
from account_ledger.domain.model.ids import Day
from account_ledger.domain.model.money import CurrencyMismatch


def process_event(log: Log, event: IncomingEvent, today: Day, config: LedgerConfig) -> Result[Log, CurrencyMismatch]:
    """The log with the event's entries appended; ``today`` is the day it is processed on (AMB-015). What spans
    accounts is checked here, against the whole log: a repeated event ID (AMB-034) and a reversal whose target is on
    another account (AMB-036). Everything else the event's own account decides, from its history alone."""
    known_entry = EventLog(log).find_first_entry(event.id)  # the event ID is the idempotency key (AMB-034)
    if known_entry is not None:
        if known_entry.event == event:
            return Ok(append_entry(log, DuplicateIgnored(event, today)))
        return Ok(append_entry(log, EventRejected(event, today, IdReused())))
    if isinstance(event, Reversal) and isinstance(target_check := _check_target_account(log, event), Err):
        return Ok(append_entry(log, EventRejected(event, today, target_check.error)))
    account = config.find_account(event.account)
    assert account is not None  # the stream reader refuses an account the ledger does not hold
    if isinstance(entries := find_history_of(log, account).decide_event(event, today), Err):
        return entries
    return Ok((*log, *entries.value))


def _check_target_account(log: Log, reversal: Reversal) -> Result[None, TargetOnAnotherAccount]:
    """Nothing when the reversal's target is on its own account or nowhere, else the account that holds it."""
    target = EventLog(log).find_first_entry(reversal.target)
    if target is None or target.event.account == reversal.account:
        return Ok(None)
    return Err(TargetOnAnotherAccount(reversal.target, target.event.account))
