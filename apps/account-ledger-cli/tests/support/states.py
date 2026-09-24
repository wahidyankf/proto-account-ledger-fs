"""Reading entries and authorization states out of a log, for the tests."""

from account_ledger.authorizations import AuthorizationState, records
from account_ledger.ids import AuthorizationId, IncomingId
from account_ledger.log import Log, LogEntry, SettlementAccepted


def state_of(log: Log, hold: str) -> list[AuthorizationState]:
    """The state of every authorization with this hold ID, in the order first seen."""
    return [record.state for record in records(log) if record.authorization.authorization == AuthorizationId(hold)]


def settlements_of(log: Log, event: str) -> list[SettlementAccepted]:
    """Every settlement entry for this event ID, in log order."""
    return [entry for entry in log if isinstance(entry, SettlementAccepted) and entry.event.id == IncomingId(event)]


def entries_for(log: Log, event: str) -> list[LogEntry]:
    """Every entry for this incoming event ID, in log order."""
    return [entry for entry in log if entry.event.id == IncomingId(event)]
