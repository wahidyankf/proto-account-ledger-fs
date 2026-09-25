"""The authorization state machine (D8, D17): one frozen dataclass per state, and the table as one ``match``."""

from dataclasses import dataclass
from typing import assert_never

from account_ledger.core.events import AnyAmount, Authorization, Capture, Settlement
from account_ledger.core.log import (
    Accepted,
    AuthorizationDecided,
    Captured,
    Decision,
    Duplicate,
    Log,
    Rejected,
    SettlementAccepted,
)
from account_ledger.core.money import Money, NotPositive, amount_of, below, rest_of, sum_of


@dataclass(frozen=True, slots=True)
class Approved:
    """Approved, holding its whole amount."""

    hold: AnyAmount


@dataclass(frozen=True, slots=True)
class Declined:
    """Declined on arrival; it holds nothing."""

    requested: AnyAmount


@dataclass(frozen=True, slots=True)
class PartiallySettled:
    """Captured in part, still holding the rest."""

    captured: AnyAmount
    hold: AnyAmount


@dataclass(frozen=True, slots=True)
class Settled:
    """Settled; it holds nothing more."""

    captured: AnyAmount


type AuthorizationState = Approved | PartiallySettled | Declined | Settled


@dataclass(frozen=True, slots=True)
class SettleFinal:
    """The trigger a final settlement fires, with its amount."""

    amount: AnyAmount


@dataclass(frozen=True, slots=True)
class SettlePartial:
    """The trigger a settlement followed by more captures fires, with its amount."""

    amount: AnyAmount


type Trigger = SettleFinal | SettlePartial


@dataclass(frozen=True, slots=True)
class NoTransition:
    """The table has no transition from this state for this trigger, so the state stands."""


def transition(state: AuthorizationState, trigger: Trigger) -> AuthorizationState | NoTransition:
    """The declared table (tech-docs 001): one case per source, trigger, and guard."""
    pair = state, trigger
    match pair:
        case Approved(), SettleFinal(amount=a):
            return Settled(a)
        case Approved(hold=h), SettlePartial(amount=a) if below(a.money, h):
            return PartiallySettled(a, _rest(h, a))
        case Approved(), SettlePartial(amount=a):  # a >= h: it reaches the hold, so nothing is left to keep
            return Settled(a)
        case PartiallySettled(captured=c), SettleFinal(amount=a):
            return Settled(sum_of(c, a))
        case PartiallySettled(captured=c, hold=h), SettlePartial(amount=a) if below(a.money, h):
            return PartiallySettled(sum_of(c, a), _rest(h, a))
        case PartiallySettled(captured=c), SettlePartial(amount=a):  # a >= h
            return Settled(sum_of(c, a))
        case Settled() | Declined(), _:
            return NoTransition()
        case _:
            assert_never(pair)


def _rest(hold: AnyAmount, taken: AnyAmount) -> AnyAmount:
    """The hold left after a partial capture, above zero as every hold is."""
    rest = amount_of(rest_of(hold, taken))
    if isinstance(rest, NotPositive):
        raise ValueError(f"a hold is above zero, not {rest.text}")
    return rest


def trigger_of(settlement: Settlement) -> Trigger:
    """The trigger a settlement fires, from its capture and amount."""
    match settlement.capture:
        case Capture.FINAL:
            return SettleFinal(settlement.amount)
        case Capture.PARTIAL:
            return SettlePartial(settlement.amount)
        case _:
            assert_never(settlement.capture)


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
            case _:
                assert_never(entry)
    return tuple(found)


def record_for(log: Log, settlement: Settlement) -> AuthorizationRecord | None:
    """The authorization a settlement names, on its account, if the log knows it."""
    return next((record for record in records(log) if _holds(record, settlement)), None)


def _holds(record: AuthorizationRecord, settlement: Settlement) -> bool:
    opened = record.authorization
    return opened.authorization == settlement.authorization and opened.account == settlement.account
