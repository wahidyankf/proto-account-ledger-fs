"""The event log: the append-only entries of the whole ledger or of one account, the only state the ledger keeps."""

from dataclasses import dataclass

from account_ledger.domain.account.domain_events import LogEntry
from account_ledger.domain.model.ids import AccountId, Day, EventId


@dataclass(frozen=True, slots=True)
class EventLog:
    """Entries in log order, never changed or removed (AMB-004, D7): the whole ledger's, or one account's own, which
    ``select`` gives."""

    entries: tuple[LogEntry, ...]

    def append(self, *entries: LogEntry) -> EventLog:
        """This log with the entries at the end."""
        return EventLog((*self.entries, *entries))

    def find_first_entry(self, event_id: EventId) -> LogEntry | None:
        """The first entry for an event ID: on one account's log, the one a reversal targets (AMB-028, AMB-035); on
        the whole ledger's, the one a repeated ID meets (AMB-034)."""
        return next((entry for entry in self.entries if entry.event.id == event_id), None)

    def select(self, account_id: AccountId) -> EventLog:
        """The account's own entries, in log order."""
        return EventLog(tuple(entry for entry in self.entries if entry.event.account == account_id))

    def list_processed_on(self, day: Day) -> tuple[LogEntry, ...]:
        """Every entry processed on the day, in log order."""
        return tuple(entry for entry in self.entries if entry.processed_day == day)
