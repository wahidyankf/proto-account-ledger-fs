"""The authorization state machine (D8, D17): the states, one frozen dataclass each, the table as one ``match``, and
the record of each authorization."""

from dataclasses import dataclass
from typing import assert_never

from account_ledger.common.result import Err, Ok, Result
from account_ledger.domain.model.events import Authorization, Settlement, SettlementKind
from account_ledger.domain.model.money import Amount, AmountIn, CurrencyMismatch


@dataclass(frozen=True, slots=True)
class Approved:
    """Approved, holding its whole amount."""

    hold: Amount


@dataclass(frozen=True, slots=True)
class Declined:
    """Declined on arrival; it holds nothing."""

    requested_amount: Amount


@dataclass(frozen=True, slots=True)
class PartiallySettled:
    """Settled in part, still holding the rest."""

    settled_amount: Amount
    hold: Amount


@dataclass(frozen=True, slots=True)
class Settled:
    """Settled; it holds nothing more."""

    settled_amount: Amount


type AuthorizationState = Approved | PartiallySettled | Declined | Settled


@dataclass(frozen=True, slots=True)
class CannotSettle:
    """The table has no transition from this state for this settlement, so the state stands."""


def apply_settlement(
    state: AuthorizationState, kind: SettlementKind, amount: Amount
) -> Result[AuthorizationState, CannotSettle | CurrencyMismatch]:
    """The declared table (D8): one case per state, settlement kind, and what the settlement leaves of the hold. What
    it leaves is taken first, so a mismatch a bug would bring is returned rather than hidden in it."""
    if isinstance(taken := _take_from_hold(state, amount), Err):
        return taken
    triple = (state, kind, taken.value)
    match triple:
        case Approved(), SettlementKind.FINAL, _:
            return Ok(Settled(amount))
        case Approved(), SettlementKind.PARTIAL, AmountIn() as kept:
            return Ok(PartiallySettled(amount, kept))
        case Approved(), SettlementKind.PARTIAL, None:  # it reaches the hold, so nothing is left
            return Ok(Settled(amount))
        case PartiallySettled(settled_amount=settled), SettlementKind.FINAL, _:
            return settled.add(amount).map(Settled)
        case PartiallySettled(settled_amount=settled), SettlementKind.PARTIAL, AmountIn() as kept:
            return settled.add(amount).map(lambda total: PartiallySettled(total, kept))
        case PartiallySettled(settled_amount=settled), SettlementKind.PARTIAL, None:  # it reaches the hold
            return settled.add(amount).map(Settled)
        case Settled() | Declined(), _, _:
            return Err(CannotSettle())
        case _:
            assert_never(triple)


def _take_from_hold(state: AuthorizationState, amount: Amount) -> Result[Amount | None, CurrencyMismatch]:
    """What the settlement leaves of the hold the state keeps, or ``None`` when it reaches the hold; no hold is kept
    once settled or declined."""
    match state:
        case Approved(hold=hold) | PartiallySettled(hold=hold):
            return hold.take(amount)
        case Settled() | Declined():
            return Ok(None)
        case _:
            assert_never(state)


@dataclass(frozen=True, slots=True)
class AuthorizationRecord:
    """An authorization as the account's entries leave it: the event that opened it and its state now."""

    authorization: Authorization
    state: AuthorizationState

    def is_referenced_by(self, settlement: Settlement) -> bool:
        """Whether the settlement names this record's hold on the same account."""
        authorization = self.authorization
        return authorization.authorization == settlement.authorization and authorization.account == settlement.account
