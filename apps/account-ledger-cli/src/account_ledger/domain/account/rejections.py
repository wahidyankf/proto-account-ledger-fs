"""Every reason an event is refused, recorded in ``EventRejected``: by the Ledger for a reused ID or another account's
target, and by the Account aggregate for the rest."""

from dataclasses import dataclass

from account_ledger.domain.model.ids import AccountId, EventId, IncomingId


@dataclass(frozen=True, slots=True)
class IdReused:
    """The event's ID is already used by an event with different content (AMB-034); the event names the ID."""


@dataclass(frozen=True, slots=True)
class AlreadyReversed:
    """The target is already reversed by a posted reversal (AMB-028)."""

    target: EventId
    undoing_id: IncomingId


@dataclass(frozen=True, slots=True)
class ReversesAReversal:
    """The target is itself a reversal; a mistaken reversal is corrected by a new debit or credit (AMB-028)."""

    target: EventId


@dataclass(frozen=True, slots=True)
class UnknownTarget:
    """The target is not in the log (AMB-035)."""

    target: EventId


@dataclass(frozen=True, slots=True)
class TargetOnAnotherAccount:
    """The target is on another account; a reversal undoes an event on its own account only (AMB-036)."""

    target: EventId
    target_account: AccountId


@dataclass(frozen=True, slots=True)
class MovedNoMoney:
    """The target moved no money: an authorization, approved or declined, or a refused event (AMB-035)."""

    target: EventId


@dataclass(frozen=True, slots=True)
class AlreadyUndone:
    """A part of the target's money is already undone another way, by the event named (AMB-035)."""

    part: EventId
    undoing_id: EventId


type Rejection = (
    IdReused
    | AlreadyReversed
    | ReversesAReversal
    | UnknownTarget
    | TargetOnAnotherAccount
    | MovedNoMoney
    | AlreadyUndone
)
