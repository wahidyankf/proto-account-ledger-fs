"""Reading entries and authorization states out of a log, for the tests."""

from account_ledger.domain.authorizations import AuthorizationState, list_records_of
from account_ledger.domain.model.config import AnyAccount
from account_ledger.domain.model.event_log import (
    Log,
    LogEntry,
    SettlementApplied,
    SettlementForcePosted,
    find_history_of,
)
from account_ledger.domain.model.ids import AuthorizationId, IncomingId
from support.streams import ACC_001


def list_states(log: Log, hold: str, account: AnyAccount = ACC_001) -> list[AuthorizationState]:
    """The state of every authorization with this authorization ID on the account, ACC-001 unless named, in the order
    first seen."""
    history = find_history_of(log, account)
    return [
        record.state
        for record in list_records_of(history)
        if record.authorization.authorization == AuthorizationId(hold)
    ]


def list_settlements(log: Log, event: str) -> list[SettlementApplied | SettlementForcePosted]:
    """Every settlement entry for this event ID, in log order."""
    return [
        entry
        for entry in log
        if isinstance(entry, SettlementApplied | SettlementForcePosted) and entry.event.id == IncomingId(event)
    ]


def list_entries(log: Log, event: str) -> list[LogEntry]:
    """Every entry for this incoming event ID, in log order."""
    return [entry for entry in log if entry.event.id == IncomingId(event)]
