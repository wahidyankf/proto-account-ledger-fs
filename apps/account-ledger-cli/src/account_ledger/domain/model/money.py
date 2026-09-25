"""Money: one type per currency, so AED and BHD values never combine.

No ``Decimal`` leaves this module: values are built from text through ``parse``, and every computation on money
happens here.
"""

from dataclasses import dataclass
from decimal import ROUND_DOWN, ROUND_HALF_EVEN, Decimal, InvalidOperation
from enum import Enum

from account_ledger.domain.model.ids import InstalmentCount


@dataclass(frozen=True, slots=True)
class NotADecimal:
    """The text is not a decimal number."""

    text: str


@dataclass(frozen=True, slots=True)
class TooManyPlaces:
    """The text has more places than its currency's minor unit."""

    text: str
    places: int
    currency: str


type MoneyFault = NotADecimal | TooManyPlaces


def _read(text: str, places: int, currency: str) -> Decimal | MoneyFault:
    try:
        value = Decimal(text)
    except InvalidOperation:
        return NotADecimal(text)
    if not value.is_finite():
        return NotADecimal(text)
    exponent = value.as_tuple().exponent
    if isinstance(exponent, int) and exponent < -places:
        return TooManyPlaces(text, places=places, currency=currency)
    return value.quantize(Decimal(1).scaleb(-places))


def _check(value: Decimal, places: int, currency: str) -> None:
    if not value.is_finite() or value.as_tuple().exponent != -places:
        raise ValueError(f"{currency} holds exactly {places} places, not {value}")


@dataclass(frozen=True, slots=True, order=True)
class Aed:
    """An amount in UAE dirhams, with exactly two places."""

    value: Decimal

    def __post_init__(self) -> None:
        _check(self.value, 2, "AED")

    @staticmethod
    def parse(text: str) -> Aed | MoneyFault:
        read = _read(text, 2, "AED")
        return Aed(read) if isinstance(read, Decimal) else read

    @staticmethod
    def zero() -> Aed:
        return Aed(Decimal("0.00"))

    def __add__(self, other: Aed) -> Aed:
        if type(other) is not Aed:
            return NotImplemented
        return Aed(self.value + other.value)

    def __sub__(self, other: Aed) -> Aed:
        if type(other) is not Aed:
            return NotImplemented
        return Aed(self.value - other.value)

    def __neg__(self) -> Aed:
        return Aed(-self.value)


@dataclass(frozen=True, slots=True, order=True)
class Bhd:
    """An amount in Bahraini dinars, with exactly three places."""

    value: Decimal

    def __post_init__(self) -> None:
        _check(self.value, 3, "BHD")

    @staticmethod
    def parse(text: str) -> Bhd | MoneyFault:
        read = _read(text, 3, "BHD")
        return Bhd(read) if isinstance(read, Decimal) else read

    @staticmethod
    def zero() -> Bhd:
        return Bhd(Decimal("0.000"))

    def __add__(self, other: Bhd) -> Bhd:
        if type(other) is not Bhd:
            return NotImplemented
        return Bhd(self.value + other.value)

    def __sub__(self, other: Bhd) -> Bhd:
        if type(other) is not Bhd:
            return NotImplemented
        return Bhd(self.value - other.value)

    def __neg__(self) -> Bhd:
        return Bhd(-self.value)


type Money = Aed | Bhd


@dataclass(frozen=True, slots=True)
class NotPositive:
    """An amount must be above zero."""

    text: str


@dataclass(frozen=True, slots=True)
class Amount[M: (Aed, Bhd)]:
    """What an event carries: money above zero."""

    money: M

    def __post_init__(self) -> None:
        if self.money.value <= 0:
            raise ValueError(f"an amount is above zero, not {self.money.value}")

    @staticmethod
    def of[N: (Aed, Bhd)](money: N) -> Amount[N] | NotPositive:
        return Amount(money) if money.value > 0 else NotPositive(str(money.value))


class Direction(Enum):
    """Which way an interest adjustment moves accrued interest; its amount stays above zero (D18)."""

    UP = "up"
    DOWN = "down"


@dataclass(frozen=True, slots=True)
class CurrencyMismatch:
    """A value of one currency met where another was required."""

    expected: str
    found: str


def currency(money: Money) -> str:
    """The currency code of a value."""
    match money:
        case Aed():
            return "AED"
        case Bhd():
            return "BHD"


def same_as[M: (Aed, Bhd)](like: M, money: Money) -> M | CurrencyMismatch:
    """Narrow a value known only as ``Money`` to the currency of ``like``."""
    if isinstance(money, type(like)):
        return money
    return CurrencyMismatch(expected=currency(like), found=currency(money))


DAILY_RATE = Decimal("0.0004")


def same[M: (Aed, Bhd)](like: M, money: Money) -> M:
    """``like``'s currency's own value of ``money``; a mismatch is a bug the reader prevents."""
    same = same_as(like, money)
    if isinstance(same, CurrencyMismatch):
        raise ValueError(f"an {same.found} effect on an {same.expected} account")  # the reader makes this unreachable
    return same


def _minor_unit(money: Money) -> Decimal:
    match money:
        case Aed():
            return Decimal("0.01")
        case Bhd():
            return Decimal("0.001")


def _round[M: (Aed, Bhd)](like: M, value: Decimal) -> M:
    """A computed value, rounded half-even to the places of ``like``'s currency (AMB-006)."""
    return type(like)(value.quantize(_minor_unit(like), rounding=ROUND_HALF_EVEN))


def daily_interest[M: (Aed, Bhd)](balance: M) -> M:
    """One day's interest on a closing balance: zero unless the balance is above zero (AMB-005)."""
    return _round(balance, balance.value * DAILY_RATE if balance.value > 0 else Decimal(0))


@dataclass(frozen=True, slots=True)
class TooManyInstalments:
    """A part would fall below one minor unit."""

    text: str
    count: int


def split[M: (Aed, Bhd)](amount: Amount[M], count: InstalmentCount) -> tuple[Amount[M], ...] | TooManyInstalments:
    """Equal parts rounded down, the remainder on the last (AMB-020); each part at least one minor unit."""
    total = amount.money
    part = type(total)((total.value / count.n).quantize(_minor_unit(total), rounding=ROUND_DOWN))
    if part.value <= 0:
        return TooManyInstalments(str(total.value), count=count.n)
    last = type(total)(total.value - part.value * (count.n - 1))
    return (*(Amount(part) for _ in range(count.n - 1)), Amount(last))


AED_FEE = Decimal("25.00")
AED_TO_BHD = Decimal("0.10238257")


def overdraft_fee[M: (Aed, Bhd)](like: M) -> Amount[M]:
    """The fee in ``like``'s currency: AED 25.00, and for BHD its conversion, rounded half-even (AMB-027)."""
    match like:
        case Aed():
            return Amount(_round(like, AED_FEE))
        case Bhd():
            return Amount(_round(like, AED_FEE * AED_TO_BHD))


def split_of(
    amount: Amount[Aed] | Amount[Bhd], count: InstalmentCount
) -> tuple[Amount[Aed], ...] | tuple[Amount[Bhd], ...] | TooManyInstalments:
    """``split`` for an amount whose currency is known only at run time."""
    match amount.money:
        case Aed() as money:
            return split(Amount(money), count)
        case Bhd() as money:
            return split(Amount(money), count)


def overdraft_fee_of(like: Money) -> Amount[Aed] | Amount[Bhd]:
    """``overdraft_fee`` for a currency known only at run time."""
    match like:
        case Aed():
            return overdraft_fee(like)
        case Bhd():
            return overdraft_fee(like)


def amount_of(money: Money) -> Amount[Aed] | Amount[Bhd] | NotPositive:
    """``Amount.of`` for a currency known only at run time."""
    match money:
        case Aed():
            return Amount.of(money)
        case Bhd():
            return Amount.of(money)


def rest_of(hold: Amount[Aed] | Amount[Bhd], taken: Amount[Aed] | Amount[Bhd]) -> Money:
    """What a hold keeps once an amount of its own currency is taken; a mismatch is a bug the reader prevents."""
    match (hold.money, taken.money):
        case (Aed() as kept, Aed() as out):
            return kept - out
        case (Bhd() as kept, Bhd() as out):
            return kept - out
        case _:
            raise ValueError(f"{currency(taken.money)} taken from {currency(hold.money)}")


def sum_of(first: Amount[Aed] | Amount[Bhd], second: Amount[Aed] | Amount[Bhd]) -> Amount[Aed] | Amount[Bhd]:
    """Two amounts of one currency added, above zero as both are; a mismatch is a bug the reader prevents."""
    match (first.money, second.money):
        case (Aed() as one, Aed() as other):
            return Amount(one + other)
        case (Bhd() as one, Bhd() as other):
            return Amount(one + other)
        case _:
            raise ValueError(f"{currency(first.money)} added to {currency(second.money)}")


def digits(money: Money) -> str:
    """The value's text, for the renderer and messages: its places, no sign change, no separators."""
    return str(money.value)


def below(money: Money, amount: Amount[Aed] | Amount[Bhd]) -> bool:
    """Whether a balance is below an amount of its own currency; a mismatch is a bug the reader prevents."""
    match (money, amount.money):
        case (Aed(), Aed()) | (Bhd(), Bhd()):
            return money.value < amount.money.value
        case _:
            raise ValueError(f"{currency(money)} compared with {currency(amount.money)}")
