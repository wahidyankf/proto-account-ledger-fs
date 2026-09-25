"""The authorization state machine (D8, D17): one frozen dataclass per state, and the table as one ``match``."""

from dataclasses import dataclass
from typing import assert_never

from account_ledger.domain.model.config import Account
from account_ledger.domain.model.event_log import (
    Accepted,
    AuthorizationDecided,
    Captured,
    Decision,
    Duplicate,
    Log,
    Rejected,
    SettlementAccepted,
)
from account_ledger.domain.model.events import AnyAmount, Authorization, Capture, Settlement
from account_ledger.domain.model.ids import Day
from account_ledger.domain.model.money import (
    Aed,
    Bhd,
    Money,
    compute_rest_of,
    is_below,
    make_amount_of,
    narrow_currency,
    sum_amounts,
)
from account_ledger.domain.model.result import Err, Ok, Result


@dataclass(frozen=True, slots=True)
class Approved:
    """Approved, holding its whole amount."""

    hold: AnyAmount


@dataclass(frozen=True, slots=True)
class Declined:
    """Declined on arrival; it holds nothing."""

    requested_amount: AnyAmount


@dataclass(frozen=True, slots=True)
class PartiallySettled:
    """Captured in part, still holding the rest."""

    captured_amount: AnyAmount
    hold: AnyAmount


@dataclass(frozen=True, slots=True)
class Settled:
    """Settled; it holds nothing more."""

    captured_amount: AnyAmount


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


def apply_trigger(state: AuthorizationState, trigger: Trigger) -> Result[AuthorizationState, NoTransition]:
    """The declared table (tech-docs 001): one case per source, trigger, and guard."""
    pair = state, trigger
    match pair:
        case Approved(), SettleFinal(amount=amount):
            return Ok(Settled(amount))
        case Approved(hold=hold), SettlePartial(amount=amount) if is_below(amount.money, hold):
            return Ok(PartiallySettled(amount, _compute_rest(hold, amount)))
        case Approved(), SettlePartial(amount=amount):  # amount >= hold: it reaches the hold, so nothing is left
            return Ok(Settled(amount))
        case PartiallySettled(captured_amount=captured_amount), SettleFinal(amount=amount):
            return Ok(Settled(sum_amounts(captured_amount, amount)))
        case PartiallySettled(captured_amount=captured_amount, hold=hold), SettlePartial(amount=amount) if is_below(
            amount.money, hold
        ):
            return Ok(PartiallySettled(sum_amounts(captured_amount, amount), _compute_rest(hold, amount)))
        case PartiallySettled(captured_amount=captured_amount), SettlePartial(amount=amount):  # amount >= hold
            return Ok(Settled(sum_amounts(captured_amount, amount)))
        case Settled() | Declined(), _:
            return Err(NoTransition())
        case _:
            assert_never(pair)


def _compute_rest(hold: AnyAmount, taken_amount: AnyAmount) -> AnyAmount:
    """The hold left after a partial capture, above zero as every hold is."""
    match make_amount_of(compute_rest_of(hold, taken_amount)):
        case Ok(rest):
            return rest
        case Err(fault):
            raise ValueError(f"a hold is above zero, not {fault.text}")


def derive_trigger(settlement: Settlement) -> Trigger:
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


def decide_authorization(available_balance: Money, amount: AnyAmount) -> Decision:
    """The decision on arrival, from the available balance before the hold (AMB-008, AMB-009)."""
    return Decision.DECLINED if is_below(available_balance, amount) else Decision.APPROVED


def list_records(log: Log) -> tuple[AuthorizationRecord, ...]:
    """Every authorization known to the log, in the order first seen, with its state."""
    records: list[AuthorizationRecord] = []
    for entry in log:
        match entry:
            case AuthorizationDecided(event=event, decision=decision):
                state = Approved(event.amount) if decision is Decision.APPROVED else Declined(event.amount)
                records.append(AuthorizationRecord(event, state))
            case SettlementAccepted(event=event, effect=Captured(state_after=state_after)):
                records = [
                    AuthorizationRecord(record.authorization, state_after) if _is_named_by(record, event) else record
                    for record in records
                ]
            case Accepted() | SettlementAccepted() | Rejected() | Duplicate():
                pass  # a posting, a force-post, a refusal, or a retry moves no authorization
            case _:
                assert_never(entry)
    return tuple(records)


def find_record(log: Log, settlement: Settlement) -> AuthorizationRecord | None:
    """The authorization a settlement names, on its account, if the log knows it."""
    return next((record for record in list_records(log) if _is_named_by(record, settlement)), None)


def _is_named_by(record: AuthorizationRecord, settlement: Settlement) -> bool:
    """Whether the settlement names this record's hold on the same account."""
    authorization = record.authorization
    return authorization.authorization == settlement.authorization and authorization.account == settlement.account


def sum_holds[M: (Aed, Bhd)](log: Log, account: Account[M], day: Day) -> M:
    """The hold of every approved or partially settled authorization on the account whose value day is <= day
    (AMB-010, AMB-013)."""
    total = type(account.opening).make_zero()
    for record in list_records(log):
        authorization, state = record.authorization, record.state
        if authorization.account != account.id or authorization.value_day > day:
            continue
        match state:
            case Approved(hold=hold) | PartiallySettled(hold=hold):
                total = total + narrow_currency(total, hold.money)
            case Declined() | Settled():
                pass  # a declined authorization holds nothing, and a final settlement released the hold
            case _:
                assert_never(state)
    return total
