"""The Account aggregate's domain events: one kind per fact the ledger records, and every reason it refuses an event."""

from dataclasses import dataclass

from account_ledger.domain.account.states import AuthorizationState
from account_ledger.domain.model.events import (
    Authorization,
    Capitalization,
    Credit,
    Debit,
    Fee,
    FeeRefund,
    GeneratedEvent,
    IncomingEvent,
    Instalment,
    InterestAccrual,
    InterestAdjustment,
    Reversal,
    Settlement,
)
from account_ledger.domain.model.ids import AccountId, Day, EventId, IncomingId


@dataclass(frozen=True, slots=True)
class CreditPosted:
    """A credit the ledger posted; one in instalments posts through the instalments it generates (AMB-017)."""

    event: Credit
    processed_day: Day


@dataclass(frozen=True, slots=True)
class DebitPosted:
    """A debit the ledger posted."""

    event: Debit
    processed_day: Day


@dataclass(frozen=True, slots=True)
class ReversalPosted:
    """A reversal the ledger posted: it undoes what its target moved, from its own value date (AMB-035)."""

    event: Reversal
    processed_day: Day


@dataclass(frozen=True, slots=True)
class InstalmentPosted:
    """An instalment of a credit, posted when the credit is processed (AMB-017, AMB-020)."""

    event: Instalment
    processed_day: Day


@dataclass(frozen=True, slots=True)
class FeeCharged:
    """An overdraft fee charged at a close (AMB-002)."""

    event: Fee
    processed_day: Day


@dataclass(frozen=True, slots=True)
class FeeRefunded:
    """A fee refunded at a close, once its day closes at or above zero again (AMB-004)."""

    event: FeeRefund
    processed_day: Day


@dataclass(frozen=True, slots=True)
class InterestAccrued:
    """A day's interest, accrued at its own close (AMB-005)."""

    event: InterestAccrual
    processed_day: Day


@dataclass(frozen=True, slots=True)
class InterestAdjusted:
    """An earlier day's interest, adjusted at a close once its closing changed (AMB-005)."""

    event: InterestAdjustment
    processed_day: Day


@dataclass(frozen=True, slots=True)
class InterestCapitalized:
    """The accrued interest, capitalized into the ledger balance on a capitalization day (AMB-007)."""

    event: Capitalization
    processed_day: Day


@dataclass(frozen=True, slots=True)
class AuthorizationApproved:
    """An authorization approved on arrival; it holds its amount (AMB-008, AMB-009)."""

    event: Authorization
    processed_day: Day


@dataclass(frozen=True, slots=True)
class AuthorizationDeclined:
    """An authorization declined on arrival; the decision is final, and it holds nothing (AMB-009)."""

    event: Authorization
    processed_day: Day


@dataclass(frozen=True, slots=True)
class SettlementApplied:
    """A settlement applied to its authorization's hold, with the states it moved the authorization between."""

    event: Settlement
    processed_day: Day
    state_before: AuthorizationState
    state_after: AuthorizationState


@dataclass(frozen=True, slots=True)
class SettlementForcePosted:
    """A settlement with no transition to apply: it debits its amount and releases no hold (AMB-012, AMB-029)."""

    event: Settlement
    processed_day: Day


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


@dataclass(frozen=True, slots=True)
class IdReused:
    """The event's ID is already used by an event with different content (AMB-034); the event names the ID."""


type Rejection = (
    IdReused
    | AlreadyReversed
    | ReversesAReversal
    | UnknownTarget
    | TargetOnAnotherAccount
    | MovedNoMoney
    | AlreadyUndone
)


@dataclass(frozen=True, slots=True)
class EventRejected:
    """An event the ledger refused, with the reason; it moves no balance (AMB-014)."""

    event: IncomingEvent
    processed_day: Day
    reason: Rejection


@dataclass(frozen=True, slots=True)
class DuplicateIgnored:
    """An event delivered again, equal to the first with its ID; a retry, not an error, with no effect (AMB-034)."""

    event: IncomingEvent
    processed_day: Day


type LogEntry = (
    CreditPosted
    | DebitPosted
    | ReversalPosted
    | InstalmentPosted
    | FeeCharged
    | FeeRefunded
    | InterestAccrued
    | InterestAdjusted
    | InterestCapitalized
    | AuthorizationApproved
    | AuthorizationDeclined
    | SettlementApplied
    | SettlementForcePosted
    | EventRejected
    | DuplicateIgnored
)
type LoggedEvent = Credit | Debit | Reversal | GeneratedEvent | Authorization | Settlement  # any entry's event
