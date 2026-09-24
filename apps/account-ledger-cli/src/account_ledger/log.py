"""The log: the append-only tuple of every entry, the only state the ledger keeps (AMB-004, D7)."""

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from account_ledger.events import (
    Authorization,
    Credit,
    Debit,
    FiredEvent,
    IncomingEvent,
    Instalment,
    Reversal,
    Settlement,
)
from account_ledger.ids import Day, EventId, IncomingId

if TYPE_CHECKING:  # authorizations reads the log, so the states are imported for annotations only
    from account_ledger.authorizations import AuthorizationState


@dataclass(frozen=True, slots=True)
class Accepted:
    """An event the ledger accepted; it counts in every aggregation. A fired event is always accepted."""

    event: Credit | Debit | Reversal | FiredEvent
    processed_day: Day


class Decision(Enum):
    """How an authorization was decided on arrival; the decision is final (AMB-009)."""

    APPROVED = "approved"
    DECLINED = "declined"


@dataclass(frozen=True, slots=True)
class AuthorizationDecided:
    """An authorization and its decision; only an approved one holds funds."""

    event: Authorization
    processed_day: Day
    decision: Decision


@dataclass(frozen=True, slots=True)
class Captured:
    """The transition a settlement completed on its authorization: the past-tense event and its audit record."""

    before: AuthorizationState
    after: AuthorizationState


@dataclass(frozen=True, slots=True)
class ForcePosted:
    """A settlement with no transition to complete: it debits its amount and releases no hold (AMB-012)."""


@dataclass(frozen=True, slots=True)
class SettlementAccepted:
    """A settlement, always accepted: it captured against its hold, or it was force-posted (AMB-012)."""

    event: Settlement
    processed_day: Day
    effect: Captured | ForcePosted


@dataclass(frozen=True, slots=True)
class AlreadyReversed:
    """The target is already reversed by an accepted reversal (AMB-028)."""

    target: EventId
    by: IncomingId


@dataclass(frozen=True, slots=True)
class ReversesAReversal:
    """The target is itself a reversal; a mistaken reversal is corrected by a new debit or credit (AMB-028)."""

    target: EventId


@dataclass(frozen=True, slots=True)
class UnknownTarget:
    """The target is not in the log (AMB-035)."""

    target: EventId


@dataclass(frozen=True, slots=True)
class MovedNoMoney:
    """The target moved no money: an authorization, approved or declined, or a refused event (AMB-035)."""

    target: EventId


@dataclass(frozen=True, slots=True)
class AlreadyUndone:
    """A part of the target's money is already undone another way, by the event named (AMB-035)."""

    part: EventId
    by: EventId


@dataclass(frozen=True, slots=True)
class IdReused:
    """The event's ID is already used by an event with different content (AMB-034); the event names the ID."""


type Rejection = IdReused | AlreadyReversed | ReversesAReversal | UnknownTarget | MovedNoMoney | AlreadyUndone


@dataclass(frozen=True, slots=True)
class Rejected:
    """An event the ledger refused, with the reason; it moves no balance."""

    event: IncomingEvent
    processed_day: Day
    reason: Rejection


@dataclass(frozen=True, slots=True)
class Duplicate:
    """An event delivered again, equal to the first with its ID; a retry, not an error, with no effect (AMB-034)."""

    event: IncomingEvent
    processed_day: Day


type LogEntry = Accepted | AuthorizationDecided | SettlementAccepted | Rejected | Duplicate
type Log = tuple[LogEntry, ...]
type LoggedEvent = Credit | Debit | Reversal | FiredEvent | Authorization | Settlement  # any entry's event


def append(log: Log, entry: LogEntry) -> Log:
    """A new log with the entry at the end; nothing is ever changed or removed."""
    return (*log, entry)


def first(log: Log, event_id: EventId) -> LogEntry | None:
    """The first entry for an event ID, the one a reversal targets (AMB-028, AMB-035)."""
    return next((entry for entry in log if entry.event.id == event_id), None)


def instalments_of(log: Log, credit: IncomingId) -> tuple[Instalment, ...]:
    """The instalments a credit fired, in order (AMB-017)."""
    return tuple(
        entry.event
        for entry in log
        if isinstance(entry, Accepted) and isinstance(entry.event, Instalment) and entry.event.id.parent == credit
    )
