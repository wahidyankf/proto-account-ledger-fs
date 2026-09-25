"""The authorization state machine (D8, D17): one frozen dataclass per state, and the table as one ``match``."""

from dataclasses import dataclass
from typing import assert_never

from account_ledger.common.result import Err, Ok, Result
from account_ledger.domain.model.config import Account
from account_ledger.domain.model.event_log import (
    Accepted,
    AppliedToHold,
    AuthorizationDecided,
    Decision,
    Duplicate,
    Log,
    Rejected,
    SettlementAccepted,
)
from account_ledger.domain.model.events import AnyAmount, Authorization, Settlement, SettlementKind
from account_ledger.domain.model.ids import Day
from account_ledger.domain.model.money import (
    Aed,
    Bhd,
    CurrencyMismatch,
    Money,
    compute_rest_of,
    is_below,
    make_amount_of,
    sum_amounts,
    sum_money,
)


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
    """AppliedToHold in part, still holding the rest."""

    settled_amount: AnyAmount
    hold: AnyAmount


@dataclass(frozen=True, slots=True)
class Settled:
    """Settled; it holds nothing more."""

    settled_amount: AnyAmount


type AuthorizationState = Approved | PartiallySettled | Declined | Settled


@dataclass(frozen=True, slots=True)
class FinalSettlement:
    """A final settlement, as the state machine takes it, with its amount."""

    amount: AnyAmount


@dataclass(frozen=True, slots=True)
class PartialSettlement:
    """A settlement followed by more settlements, as the state machine takes it, with its amount."""

    amount: AnyAmount


type SettlementInput = FinalSettlement | PartialSettlement


@dataclass(frozen=True, slots=True)
class CannotSettle:
    """The table has no transition from this state for this settlement, so the state stands."""


def apply_settlement(
    state: AuthorizationState, settlement_input: SettlementInput
) -> Result[AuthorizationState, CannotSettle | CurrencyMismatch]:
    """The declared table (tech-docs 001): one case per source, settlement input, and guard. The guard, whether the
    settlement falls short of the hold, is decided first, so a mismatch a bug would bring is returned rather than
    hidden in it."""
    if isinstance(checked_settlement := _is_settlement_below_hold(state, settlement_input), Err):
        return checked_settlement
    is_short, pair = checked_settlement.value, (state, settlement_input)
    match pair:
        case Approved(), FinalSettlement(amount=amount):
            return Ok(Settled(amount))
        case Approved(hold=hold), PartialSettlement(amount=amount) if is_short:
            return _make_partial_settlement(amount, hold, amount)
        case Approved(), PartialSettlement(amount=amount):  # amount >= hold: it reaches the hold, so nothing is left
            return Ok(Settled(amount))
        case PartiallySettled(settled_amount=settled_amount), FinalSettlement(amount=amount):
            return sum_amounts(settled_amount, amount).map(Settled)
        case PartiallySettled(settled_amount=settled_amount, hold=hold), PartialSettlement(amount=amount) if is_short:
            return sum_amounts(settled_amount, amount).flat_map(
                lambda settled_total: _make_partial_settlement(settled_total, hold, amount)
            )
        case PartiallySettled(settled_amount=settled_amount), PartialSettlement(amount=amount):  # amount >= hold
            return sum_amounts(settled_amount, amount).map(Settled)
        case Settled() | Declined(), _:
            return Err(CannotSettle())
        case _:
            assert_never(pair)


def _is_settlement_below_hold(
    state: AuthorizationState, settlement_input: SettlementInput
) -> Result[bool, CurrencyMismatch]:
    """Whether the settlement's amount is below the hold the state keeps; no hold is kept once settled or declined."""
    match state:
        case Approved(hold=hold) | PartiallySettled(hold=hold):
            return is_below(settlement_input.amount.money, hold)
        case Settled() | Declined():
            return Ok(False)
        case _:
            assert_never(state)


def _make_partial_settlement(
    settled_amount: AnyAmount, hold: AnyAmount, taken_amount: AnyAmount
) -> Result[AuthorizationState, CurrencyMismatch]:
    """Partially settled for the settlements so far, keeping what a settlement below the hold leaves of it."""
    return _compute_rest(hold, taken_amount).map(lambda rest: PartiallySettled(settled_amount, rest))


def _compute_rest(hold: AnyAmount, taken_amount: AnyAmount) -> Result[AnyAmount, CurrencyMismatch]:
    """The hold left after a partial settlement below it, above zero as every hold is."""
    if isinstance(rest := compute_rest_of(hold, taken_amount), Err):
        return rest
    rest_amount = make_amount_of(rest.value)
    assert isinstance(rest_amount, Ok)  # the settlement is below the hold, so the rest is above zero
    return rest_amount


def derive_settlement_input(settlement: Settlement) -> SettlementInput:
    """The settlement as the state machine takes it, from its kind and amount."""
    match settlement.kind:
        case SettlementKind.FINAL:
            return FinalSettlement(settlement.amount)
        case SettlementKind.PARTIAL:
            return PartialSettlement(settlement.amount)
        case _:
            assert_never(settlement.kind)


@dataclass(frozen=True, slots=True)
class AuthorizationRecord:
    """An authorization as the log leaves it: the event that opened it and its state now."""

    authorization: Authorization
    state: AuthorizationState


def decide_authorization(available_balance: Money, amount: AnyAmount) -> Result[Decision, CurrencyMismatch]:
    """The decision on arrival, from the available balance before the hold (AMB-008, AMB-009)."""
    return is_below(available_balance, amount).map(
        lambda is_short: Decision.DECLINED if is_short else Decision.APPROVED
    )


def list_records(log: Log) -> tuple[AuthorizationRecord, ...]:
    """Every authorization known to the log, in the order first seen, with its state."""
    records: list[AuthorizationRecord] = []
    for entry in log:
        match entry:
            case AuthorizationDecided(event=event, decision=decision):
                state = Approved(event.amount) if decision is Decision.APPROVED else Declined(event.amount)
                records.append(AuthorizationRecord(event, state))
            case SettlementAccepted(event=event, effect=AppliedToHold(state_after=state_after)):
                records = [
                    AuthorizationRecord(record.authorization, state_after)
                    if _is_referenced_by(record, event)
                    else record
                    for record in records
                ]
            case Accepted() | SettlementAccepted() | Rejected() | Duplicate():
                pass  # a posting, a force-post, a refusal, or a retry moves no authorization
            case _:
                assert_never(entry)
    return tuple(records)


def find_record(log: Log, settlement: Settlement) -> AuthorizationRecord | None:
    """The authorization a settlement names, on its account, if the log knows it."""
    return next((record for record in list_records(log) if _is_referenced_by(record, settlement)), None)


def _is_referenced_by(record: AuthorizationRecord, settlement: Settlement) -> bool:
    """Whether the settlement names this record's hold on the same account."""
    authorization = record.authorization
    return authorization.authorization == settlement.authorization and authorization.account == settlement.account


def sum_holds[M: (Aed, Bhd)](log: Log, account: Account[M], day: Day) -> Result[M, CurrencyMismatch]:
    """The hold of every approved or partially settled authorization on the account whose value date is <= day
    (AMB-010, AMB-013)."""
    holds: list[Money] = []
    for record in list_records(log):
        authorization, state = record.authorization, record.state
        if authorization.account != account.id or authorization.value_date > day:
            continue
        match state:
            case Approved(hold=hold) | PartiallySettled(hold=hold):
                holds.append(hold.money)
            case Declined() | Settled():
                pass  # a declined authorization holds nothing, and a final settlement released the hold
            case _:
                assert_never(state)
    return sum_money(type(account.opening).make_zero(), holds)
