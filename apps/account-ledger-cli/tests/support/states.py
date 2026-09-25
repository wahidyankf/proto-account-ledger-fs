"""Reading entries and authorization states out of a log, for the tests."""

from account_ledger.domain.authorizations import AuthorizationState, list_records
from account_ledger.domain.model.event_log import (
    Log,
    LogEntry,
    SettlementApplied,
    SettlementForcePosted,
)
from account_ledger.domain.model.ids import AuthorizationId, IncomingId


def list_states(log: Log, hold: str) -> list[AuthorizationState]:
    """The state of every authorization with this authorization ID, in the order first seen."""
    return [record.state for record in list_records(log) if record.authorization.authorization == AuthorizationId(hold)]


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
