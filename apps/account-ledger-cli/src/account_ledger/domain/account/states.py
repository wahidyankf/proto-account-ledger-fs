"""The authorization states (D8, D17): one frozen dataclass per state, each holding only its own data."""

from dataclasses import dataclass

from account_ledger.domain.model.events import AnyAmount


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
    """Settled in part, still holding the rest."""

    settled_amount: AnyAmount
    hold: AnyAmount


@dataclass(frozen=True, slots=True)
class Settled:
    """Settled; it holds nothing more."""

    settled_amount: AnyAmount


type AuthorizationState = Approved | PartiallySettled | Declined | Settled
