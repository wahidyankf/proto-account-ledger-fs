"""Events: one frozen dataclass per kind, joined in the unions ``IncomingEvent`` and ``FiredEvent``."""

from dataclasses import dataclass
from enum import Enum

from account_ledger.domain.model.ids import (
    AccountId,
    AuthorizationId,
    CapitalizationId,
    Day,
    EventId,
    FeeId,
    IncomingId,
    InstalmentCount,
    InstalmentId,
    InterestId,
    RefundId,
)
from account_ledger.domain.model.money import Aed, Amount, Bhd, Direction

type AnyAmount = Amount[Aed] | Amount[Bhd]


class Capture(Enum):
    """Whether a settlement is the last capture against its hold (AMB-013)."""

    FINAL = "final"
    PARTIAL = "partial"


@dataclass(frozen=True, slots=True)
class Whole:
    """A credit posted as one amount."""


@dataclass(frozen=True, slots=True)
class Instalments:
    """A credit posted in parts, each an instalment event (AMB-017, AMB-020)."""

    count: InstalmentCount


type Posting = Whole | Instalments


@dataclass(frozen=True, slots=True)
class Credit:
    """Money in, posted whole or in instalments."""

    id: IncomingId
    booked: Day
    account: AccountId
    value_day: Day
    amount: AnyAmount
    posting: Posting


@dataclass(frozen=True, slots=True)
class Debit:
    """Money out, posted at once."""

    id: IncomingId
    booked: Day
    account: AccountId
    value_day: Day
    amount: AnyAmount


@dataclass(frozen=True, slots=True)
class Authorization:
    """A request to hold an amount, approved or declined against the available balance."""

    id: IncomingId
    booked: Day
    account: AccountId
    value_day: Day
    authorization: AuthorizationId
    amount: AnyAmount


@dataclass(frozen=True, slots=True)
class Settlement:
    """A capture against an authorization's hold, final or partial (AMB-013)."""

    id: IncomingId
    booked: Day
    account: AccountId
    value_day: Day
    authorization: AuthorizationId
    amount: AnyAmount
    capture: Capture


@dataclass(frozen=True, slots=True)
class Reversal:
    """An undo of an earlier event, named by its ID."""

    id: IncomingId
    booked: Day
    account: AccountId
    value_day: Day
    target: EventId


type IncomingEvent = Credit | Debit | Authorization | Settlement | Reversal


@dataclass(frozen=True, slots=True)
class Instalment:
    """A part of a credit in instalments, fired by the ledger with the credit's value day (AMB-017, AMB-020)."""

    id: InstalmentId
    account: AccountId
    value_day: Day
    amount: AnyAmount


@dataclass(frozen=True, slots=True)
class Fee:
    """The overdraft fee for a day that closed negative, fired at a close and value-dated that close (AMB-002)."""

    id: FeeId
    account: AccountId
    value_day: Day
    amount: AnyAmount


@dataclass(frozen=True, slots=True)
class FeeRefund:
    """The refund of a fee in force whose day closes at or above zero again, value-dated the close (AMB-004)."""

    id: RefundId
    account: AccountId
    value_day: Day
    fee: FeeId
    amount: AnyAmount


@dataclass(frozen=True, slots=True)
class InterestAccrual:
    """A day's interest, fired at its own close; its ID is for the day it fires (AMB-005)."""

    id: InterestId
    account: AccountId
    value_day: Day
    amount: AnyAmount

    def __post_init__(self) -> None:
        if self.id.covered_day != self.id.fired_day:
            raise ValueError("an accrual is for the day it fires; an earlier day takes an adjustment")


@dataclass(frozen=True, slots=True)
class InterestAdjustment:
    """A correction of an earlier day's interest, fired when a changed closing is recognised (AMB-005)."""

    id: InterestId
    account: AccountId
    value_day: Day
    direction: Direction
    amount: AnyAmount

    def __post_init__(self) -> None:
        if self.id.covered_day >= self.id.fired_day:
            raise ValueError("an adjustment is for an earlier day; the day it fires takes an accrual")


@dataclass(frozen=True, slots=True)
class Capitalization:
    """The accrued interest, credited to the ledger balance on a capitalization day (AMB-007, AMB-023)."""

    id: CapitalizationId
    account: AccountId
    value_day: Day
    amount: AnyAmount


type FiredEvent = Instalment | Fee | FeeRefund | InterestAccrual | InterestAdjustment | Capitalization
