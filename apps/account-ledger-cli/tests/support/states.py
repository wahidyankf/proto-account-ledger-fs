"""Reading entries and authorization states out of a log, for the tests."""

from account_ledger.challenge import CHALLENGE
from account_ledger.domain.account.authorizations import AuthorizationState
from account_ledger.domain.account.domain_events import (
    LogEntry,
    SettlementApplied,
    SettlementForcePosted,
)
from account_ledger.domain.account.event_log import EventLog
from account_ledger.domain.ledger.ledger import Ledger
from account_ledger.domain.model.config import AccountOpening
from account_ledger.domain.model.ids import AuthorizationId, IncomingId
from support.streams import ACC_001


def list_states(log: EventLog, hold: str, account: AccountOpening = ACC_001) -> list[AuthorizationState]:
    """The state of every authorization with this authorization ID on the account, ACC-001 unless named, in the order
    first seen."""
    history = Ledger(CHALLENGE, log).find_account(account)
    return [
        record.state for record in history.list_records() if record.authorization.authorization == AuthorizationId(hold)
    ]


def list_settlements(log: EventLog, event: str) -> list[SettlementApplied | SettlementForcePosted]:
    """Every settlement entry for this event ID, in log order."""
    return [
        entry
        for entry in log.entries
        if isinstance(entry, SettlementApplied | SettlementForcePosted) and entry.event.id == IncomingId(event)
    ]


def list_entries(log: EventLog, event: str) -> list[LogEntry]:
    """Every entry for this incoming event ID, in log order."""
    return [entry for entry in log.entries if entry.event.id == IncomingId(event)]
