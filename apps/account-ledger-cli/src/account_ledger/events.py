"""Incoming events: one frozen dataclass per kind, joined in the union ``IncomingEvent``."""

from dataclasses import dataclass
from enum import Enum

from account_ledger.ids import AccountId, AuthorizationId, Day, EventId, IncomingId, InstalmentCount
from account_ledger.money import Aed, Amount, Bhd

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
    id: IncomingId
    booked: Day
    account: AccountId
    value_day: Day
    amount: AnyAmount
    posting: Posting


@dataclass(frozen=True, slots=True)
class Debit:
    id: IncomingId
    booked: Day
    account: AccountId
    value_day: Day
    amount: AnyAmount


@dataclass(frozen=True, slots=True)
class Authorization:
    id: IncomingId
    booked: Day
    account: AccountId
    value_day: Day
    authorization: AuthorizationId
    amount: AnyAmount


@dataclass(frozen=True, slots=True)
class Settlement:
    id: IncomingId
    booked: Day
    account: AccountId
    value_day: Day
    authorization: AuthorizationId
    amount: AnyAmount
    capture: Capture


@dataclass(frozen=True, slots=True)
class Reversal:
    id: IncomingId
    booked: Day
    account: AccountId
    value_day: Day
    reverses: EventId


type IncomingEvent = Credit | Debit | Authorization | Settlement | Reversal
