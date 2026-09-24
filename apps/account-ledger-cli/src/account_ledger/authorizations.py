"""The authorization state machine (D8, D17): one frozen dataclass per state, and the table as one ``match``."""

from dataclasses import dataclass
from typing import assert_never

from account_ledger.events import AnyAmount, Authorization, Settlement
from account_ledger.log import (
    Accepted,
    AuthorizationDecided,
    Captured,
    Decision,
    Duplicate,
    Log,
    Rejected,
    SettlementAccepted,
)
from account_ledger.money import Money, below


@dataclass(frozen=True, slots=True)
class Approved:
    """Approved, holding its whole amount."""

    hold: AnyAmount


@dataclass(frozen=True, slots=True)
class Declined:
    """Declined on arrival; it holds nothing."""

    requested: AnyAmount


@dataclass(frozen=True, slots=True)
class Settled:
    """Settled; it holds nothing more."""

    captured: AnyAmount


type AuthorizationState = Approved | Declined | Settled


@dataclass(frozen=True, slots=True)
class SettleFinal:
    """The trigger a final settlement fires, with its amount."""

    amount: AnyAmount


type Trigger = SettleFinal


@dataclass(frozen=True, slots=True)
class NoTransition:
    """The table has no transition from this state for this trigger, so the state stands."""


def transition(state: AuthorizationState, trigger: Trigger) -> AuthorizationState | NoTransition:
    """The declared table (tech-docs 001): one case per source, trigger, and guard."""
    pair = state, trigger
    match pair:
        case Approved(), SettleFinal(amount=a):
            return Settled(a)
        case Settled() | Declined(), _:
            return NoTransition()
        case _:
            assert_never(pair)


def trigger_of(settlement: Settlement) -> Trigger:
    """The trigger a settlement fires, from its capture and amount."""
    return SettleFinal(settlement.amount)


@dataclass(frozen=True, slots=True)
class AuthorizationRecord:
    """An authorization as the log leaves it: the event that opened it and its state now."""

    authorization: Authorization
    state: AuthorizationState


def decide(available: Money, amount: AnyAmount) -> Decision:
    """The decision on arrival, from the available balance before the hold (AMB-008, AMB-009)."""
    return Decision.DECLINED if below(available, amount) else Decision.APPROVED


def records(log: Log) -> tuple[AuthorizationRecord, ...]:
    """Every authorization known to the log, in the order first seen, with its state."""
    found: list[AuthorizationRecord] = []
    for entry in log:
        match entry:
            case AuthorizationDecided(event=event, decision=decision):
                state = Approved(event.amount) if decision is Decision.APPROVED else Declined(event.amount)
                found.append(AuthorizationRecord(event, state))
            case SettlementAccepted(event=event, effect=Captured(after=after)):
                found = [
                    AuthorizationRecord(record.authorization, after) if _holds(record, event) else record
                    for record in found
                ]
            case Accepted() | SettlementAccepted() | Rejected() | Duplicate():
                pass  # a posting, a force-post, a refusal, or a retry moves no authorization
    return tuple(found)


def record_for(log: Log, settlement: Settlement) -> AuthorizationRecord | None:
    """The authorization a settlement names, on its account, if the log knows it."""
    return next((record for record in records(log) if _holds(record, settlement)), None)


def _holds(record: AuthorizationRecord, settlement: Settlement) -> bool:
    opened = record.authorization
    return opened.authorization == settlement.authorization and opened.account == settlement.account
