"""Money: one type per currency, so AED and BHD values never combine.

No ``Decimal`` leaves this module: values are built from text through ``parse``, and every computation on money
happens here.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import ROUND_DOWN, ROUND_HALF_EVEN, Decimal, InvalidOperation
from enum import Enum
from typing import ClassVar, Self

from account_ledger.common.result import Err, Ok, Result
from account_ledger.domain.model.ids import InstalmentCount

AMOUNT_LIMIT = Decimal(10) ** 12  # money read from the stream stays below it, so no sum outgrows 28 digits (NUMBERS.md)
DAILY_RATE = Decimal("0.0004")
AED_FEE = Decimal("25.00")
AED_TO_BHD = Decimal("0.10238257")


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


@dataclass(frozen=True, slots=True)
class AboveLimit:
    """The value is not below the amount limit in either direction."""

    text: str


type MoneyFault = NotADecimal | TooManyPlaces | AboveLimit


@dataclass(frozen=True, slots=True)
class NotPositive:
    """An amount must be above zero."""

    text: str


@dataclass(frozen=True, slots=True)
class CurrencyMismatch:
    """A value of one currency met where another was required."""

    expected_currency: str
    found_currency: str


@dataclass(frozen=True, slots=True)
class TooManyInstalments:
    """A part would fall below one minor unit."""

    text: str
    count: int


def _read_decimal(text: str) -> Result[Decimal, NotADecimal]:
    """The decimal the text holds, or a fault for one that is not a number; ``Decimal`` refuses by raising, so the
    refusal is caught here and returned."""
    try:
        return Ok(Decimal(text))
    except InvalidOperation:
        return Err(NotADecimal(text))


def _make_scaled_value(value: Decimal, places: int, currency: str) -> Result[Decimal, MoneyFault]:
    """The value at exactly the currency's places, or a fault for a non-finite value, one with more places, or one not
    below the amount limit."""
    if not value.is_finite():
        return Err(NotADecimal(str(value)))
    exponent = value.as_tuple().exponent
    if isinstance(exponent, int) and exponent < -places:
        return Err(TooManyPlaces(str(value), places=places, currency=currency))
    if abs(value) >= AMOUNT_LIMIT:
        return Err(AboveLimit(str(value)))
    return Ok(value.quantize(_find_minor_unit(places)))


def _find_minor_unit(places: int) -> Decimal:
    """The smallest unit at so many places: 0.01 at 2, 0.001 at 3."""
    return Decimal(1).scaleb(-places)


def _check_places(value: Decimal, places: int, currency: str) -> None:
    """A guard that raises unless the value is finite at exactly the currency's places; only a bug reaches it."""
    if not value.is_finite() or value.as_tuple().exponent != -places:
        raise ValueError(f"{currency} holds exactly {places} places, not {value}")


def _is_positive(money: Money) -> bool:
    """Whether the money is above zero: the one rule the guard and ``AmountIn.make`` both apply."""
    return money.value > 0


def _make_mismatch(expected_money: Money, found_money: Money) -> CurrencyMismatch:
    """The fault for a value of one currency met where the other's was required."""
    return CurrencyMismatch(expected_currency=expected_money.get_currency(), found_currency=found_money.get_currency())


def _round_money[M: (Aed, Bhd)](sample: M, value: Decimal) -> M:
    """A computed value, rounded half-even to the places of ``sample``'s currency (AMB-006)."""
    return type(sample)(value.quantize(_find_minor_unit(sample.PLACES), rounding=ROUND_HALF_EVEN))


def _require_same[M: (Aed, Bhd)](sample: M, money: Money) -> Result[M, CurrencyMismatch]:
    """The money as the currency of ``sample``, or a mismatch when it is in the other currency."""
    if isinstance(money, type(sample)):
        return Ok(money)
    return Err(_make_mismatch(sample, money))


def _add_all[M: (Aed, Bhd)](start: M, money_values: Iterable[Money]) -> Result[M, CurrencyMismatch]:
    """``start`` plus every value, each of ``start``'s currency, or the first value of another."""
    total = start
    for money in money_values:
        if isinstance(checked_money := _require_same(start, money), Err):
            return checked_money
        total = total + checked_money.value
    return Ok(total)


def _make_directed_amount[M: (Aed, Bhd)](change: M) -> tuple[Direction, AmountIn[M]] | None:
    """A change as the way it moves interest and its size above zero, or ``None`` for a change of zero."""
    direction = Direction.UP if change.value > 0 else Direction.DOWN
    match AmountIn.make(change if direction is Direction.UP else -change):
        case Ok(amount):
            return direction, amount
        case Err():
            return None


def _compute_daily_interest[M: (Aed, Bhd)](balance: M) -> M:
    """One day's interest on a closing balance: zero unless the balance is above zero (AMB-005)."""
    return _round_money(balance, balance.value * DAILY_RATE if balance.value > 0 else Decimal(0))


@dataclass(frozen=True, slots=True, order=True)
class Aed:
    """An amount in UAE dirhams, with exactly two places."""

    CURRENCY: ClassVar[str] = "AED"
    PLACES: ClassVar[int] = 2
    value: Decimal

    def __post_init__(self) -> None:
        _check_places(self.value, self.PLACES, self.CURRENCY)

    @classmethod
    def make(cls, value: Decimal) -> Result[Self, MoneyFault]:
        """The money of a decimal, or a fault for a non-finite one or one with more places than the currency's."""
        return _make_scaled_value(value, cls.PLACES, cls.CURRENCY).map(cls)

    @classmethod
    def parse(cls, text: str) -> Result[Self, MoneyFault]:
        """The money the text holds, or a fault saying why it is not money in this currency."""
        return _read_decimal(text).flat_map(cls.make)

    @classmethod
    def make_zero(cls) -> Self:
        """Zero at the currency's places: AED 0.00, BHD 0.000."""
        return cls(_find_minor_unit(cls.PLACES) * 0)

    def __add__(self, other: Self) -> Self:
        if type(other) is not type(self):
            return NotImplemented
        return type(self)(self.value + other.value)

    def __sub__(self, other: Self) -> Self:
        if type(other) is not type(self):
            return NotImplemented
        return type(self)(self.value - other.value)

    def __neg__(self) -> Self:
        return type(self)(-self.value)

    def get_currency(self) -> str:
        """The currency code, such as AED."""
        return self.CURRENCY

    def format_digits(self) -> str:
        """The value's text, for the renderer and messages: its places, no sign change, no separators."""
        return str(self.value)

    def is_below(self, amount: Amount) -> Result[bool, CurrencyMismatch]:
        """Whether this balance is below an amount of its own currency, or the mismatch a bug would bring."""
        if type(amount.money) is not type(self):
            return Err(_make_mismatch(self, amount.money))
        return Ok(self.value < amount.money.value)

    def require_same(self, money: Money) -> Result[Self, CurrencyMismatch]:
        """The money as this currency, or a mismatch when it is in the other currency."""
        return _require_same(self, money)

    def add_all(self, money_values: Iterable[Money]) -> Result[Self, CurrencyMismatch]:
        """This value plus every value, each of its currency, or the first value of another; the reader keeps every
        effect in its account's currency, so only a bug returns the mismatch."""
        return _add_all(self, money_values)

    def compute_daily_interest(self) -> Self:
        """One day's interest on this closing balance: zero unless the balance is above zero (AMB-005)."""
        return _compute_daily_interest(self)

    def compute_overdraft_fee(self) -> AmountIn[Aed]:
        """The overdraft fee in AED: AED 25.00 (AMB-027)."""
        return AmountIn(_round_money(self, AED_FEE))

    def make_amount(self) -> Result[AmountIn[Aed], NotPositive]:
        """This value as an amount, or a fault when it is zero or below."""
        return AmountIn.make(self)

    def make_directed_amount(self) -> tuple[Direction, AmountIn[Aed]] | None:
        """This change as the direction it moves interest and its size, or ``None`` for no change."""
        return _make_directed_amount(self)


@dataclass(frozen=True, slots=True, order=True)
class Bhd:
    """An amount in Bahraini dinars, with exactly three places."""

    CURRENCY: ClassVar[str] = "BHD"
    PLACES: ClassVar[int] = 3
    value: Decimal

    def __post_init__(self) -> None:
        _check_places(self.value, self.PLACES, self.CURRENCY)

    @classmethod
    def make(cls, value: Decimal) -> Result[Self, MoneyFault]:
        """The money of a decimal, or a fault for a non-finite one or one with more places than the currency's."""
        return _make_scaled_value(value, cls.PLACES, cls.CURRENCY).map(cls)

    @classmethod
    def parse(cls, text: str) -> Result[Self, MoneyFault]:
        """The money the text holds, or a fault saying why it is not money in this currency."""
        return _read_decimal(text).flat_map(cls.make)

    @classmethod
    def make_zero(cls) -> Self:
        """Zero at the currency's places: AED 0.00, BHD 0.000."""
        return cls(_find_minor_unit(cls.PLACES) * 0)

    def __add__(self, other: Self) -> Self:
        if type(other) is not type(self):
            return NotImplemented
        return type(self)(self.value + other.value)

    def __sub__(self, other: Self) -> Self:
        if type(other) is not type(self):
            return NotImplemented
        return type(self)(self.value - other.value)

    def __neg__(self) -> Self:
        return type(self)(-self.value)

    def get_currency(self) -> str:
        """The currency code, such as AED."""
        return self.CURRENCY

    def format_digits(self) -> str:
        """The value's text, for the renderer and messages: its places, no sign change, no separators."""
        return str(self.value)

    def is_below(self, amount: Amount) -> Result[bool, CurrencyMismatch]:
        """Whether this balance is below an amount of its own currency, or the mismatch a bug would bring."""
        if type(amount.money) is not type(self):
            return Err(_make_mismatch(self, amount.money))
        return Ok(self.value < amount.money.value)

    def require_same(self, money: Money) -> Result[Self, CurrencyMismatch]:
        """The money as this currency, or a mismatch when it is in the other currency."""
        return _require_same(self, money)

    def add_all(self, money_values: Iterable[Money]) -> Result[Self, CurrencyMismatch]:
        """This value plus every value, each of its currency, or the first value of another; the reader keeps every
        effect in its account's currency, so only a bug returns the mismatch."""
        return _add_all(self, money_values)

    def compute_daily_interest(self) -> Self:
        """One day's interest on this closing balance: zero unless the balance is above zero (AMB-005)."""
        return _compute_daily_interest(self)

    def compute_overdraft_fee(self) -> AmountIn[Bhd]:
        """The overdraft fee in BHD: AED 25.00 converted, rounded half-even (AMB-027)."""
        return AmountIn(_round_money(self, AED_FEE * AED_TO_BHD))

    def make_amount(self) -> Result[AmountIn[Bhd], NotPositive]:
        """This value as an amount, or a fault when it is zero or below."""
        return AmountIn.make(self)

    def make_directed_amount(self) -> tuple[Direction, AmountIn[Bhd]] | None:
        """This change as the direction it moves interest and its size, or ``None`` for no change."""
        return _make_directed_amount(self)


type Money = Aed | Bhd


@dataclass(frozen=True, slots=True)
class AmountIn[M: (Aed, Bhd)]:
    """What an event carries: money above zero."""

    money: M

    def __post_init__(self) -> None:
        if not _is_positive(self.money):
            raise ValueError(f"an amount is above zero, not {self.money.value}")

    @staticmethod
    def make[N: (Aed, Bhd)](money: N) -> Result[AmountIn[N], NotPositive]:
        """The money as an amount, or a fault when it is zero or below."""
        return Ok(AmountIn(money)) if _is_positive(money) else Err(NotPositive(str(money.value)))

    def split(self, count: InstalmentCount) -> Result[tuple[AmountIn[M], ...], TooManyInstalments]:
        """Equal parts rounded down, the remainder on the last (AMB-020); each part at least one minor unit."""
        total = self.money
        part = type(total)((total.value / count.number).quantize(_find_minor_unit(total.PLACES), rounding=ROUND_DOWN))
        if part.value <= 0:
            return Err(TooManyInstalments(str(total.value), count=count.number))
        last_part = type(total)(total.value - part.value * (count.number - 1))
        return Ok((*(AmountIn(part) for _ in range(count.number - 1)), AmountIn(last_part)))

    def add(self, other: Amount) -> Result[AmountIn[M], CurrencyMismatch]:
        """This amount and another of its currency added, above zero as both are, or the mismatch a bug would bring."""
        if isinstance(other_money := self.money.require_same(other.money), Err):
            return other_money
        return Ok(AmountIn(self.money + other_money.value))

    def take(self, taken_amount: Amount) -> Result[AmountIn[M] | None, CurrencyMismatch]:
        """The hold left once a settlement takes an amount, or ``None`` when the amount reaches or passes the hold."""
        if isinstance(taken_money := self.money.require_same(taken_amount.money), Err):
            return taken_money
        rest = self.money - taken_money.value
        return Ok(AmountIn(rest) if _is_positive(rest) else None)

    def compute_rest(self, taken_amount: Amount) -> Result[M, CurrencyMismatch]:
        """What this hold keeps once an amount of its own currency is taken, or the mismatch a bug would bring."""
        if isinstance(taken_money := self.money.require_same(taken_amount.money), Err):
            return taken_money
        return Ok(self.money - taken_money.value)


type Amount = AmountIn[Aed] | AmountIn[Bhd]


class Direction(Enum):
    """Which way an interest adjustment moves accrued interest; its amount stays above zero (D18)."""

    UP = "up"
    DOWN = "down"
