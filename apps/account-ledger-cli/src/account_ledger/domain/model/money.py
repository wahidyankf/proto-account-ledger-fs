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


def _read_decimal(text: str, places: int, currency: str) -> Decimal | MoneyFault:
    """The text as a decimal at the currency's places, or a fault for a non-number or too many places."""
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


def _check_places(value: Decimal, places: int, currency: str) -> None:
    """A guard that raises unless the value is finite at exactly the currency's places; only a bug reaches it."""
    if not value.is_finite() or value.as_tuple().exponent != -places:
        raise ValueError(f"{currency} holds exactly {places} places, not {value}")


@dataclass(frozen=True, slots=True, order=True)
class Aed:
    """An amount in UAE dirhams, with exactly two places."""

    value: Decimal

    def __post_init__(self) -> None:
        _check_places(self.value, 2, "AED")

    @staticmethod
    def parse(text: str) -> Aed | MoneyFault:
        """The AED amount the text holds, or a fault saying why it is not one."""
        parsed_value = _read_decimal(text, 2, "AED")
        return Aed(parsed_value) if isinstance(parsed_value, Decimal) else parsed_value

    @staticmethod
    def make_zero() -> Aed:
        """AED 0.00."""
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
        _check_places(self.value, 3, "BHD")

    @staticmethod
    def parse(text: str) -> Bhd | MoneyFault:
        """The BHD amount the text holds, or a fault saying why it is not one."""
        parsed_value = _read_decimal(text, 3, "BHD")
        return Bhd(parsed_value) if isinstance(parsed_value, Decimal) else parsed_value

    @staticmethod
    def make_zero() -> Bhd:
        """BHD 0.000."""
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
    def make[N: (Aed, Bhd)](money: N) -> Amount[N] | NotPositive:
        """The money as an amount, or a fault when it is zero or below."""
        return Amount(money) if money.value > 0 else NotPositive(str(money.value))


class Direction(Enum):
    """Which way an interest adjustment moves accrued interest; its amount stays above zero (D18)."""

    UP = "up"
    DOWN = "down"


@dataclass(frozen=True, slots=True)
class CurrencyMismatch:
    """A value of one currency met where another was required."""

    expected_currency: str
    found_currency: str


def get_currency(money: Money) -> str:
    """The currency code of a value."""
    match money:
        case Aed():
            return "AED"
        case Bhd():
            return "BHD"


def try_narrow_currency[M: (Aed, Bhd)](sample: M, money: Money) -> M | CurrencyMismatch:
    """Narrow a value known only as ``Money`` to the currency of ``like``."""
    if isinstance(money, type(sample)):
        return money
    return CurrencyMismatch(expected_currency=get_currency(sample), found_currency=get_currency(money))


DAILY_RATE = Decimal("0.0004")


def narrow_currency[M: (Aed, Bhd)](sample: M, money: Money) -> M:
    """``like``'s currency's own value of ``money``; a mismatch is a bug the reader prevents."""
    narrowed_money = try_narrow_currency(sample, money)
    if isinstance(narrowed_money, CurrencyMismatch):
        raise ValueError(
            f"an {narrowed_money.found_currency} effect on an {narrowed_money.expected_currency} account"
        )  # the reader makes this unreachable
    return narrowed_money


def _get_minor_unit(money: Money) -> Decimal:
    """The currency's smallest unit: 0.01 for AED, 0.001 for BHD."""
    match money:
        case Aed():
            return Decimal("0.01")
        case Bhd():
            return Decimal("0.001")


def _round_money[M: (Aed, Bhd)](sample: M, value: Decimal) -> M:
    """A computed value, rounded half-even to the places of ``like``'s currency (AMB-006)."""
    return type(sample)(value.quantize(_get_minor_unit(sample), rounding=ROUND_HALF_EVEN))


def compute_daily_interest[M: (Aed, Bhd)](balance: M) -> M:
    """One day's interest on a closing balance: zero unless the balance is above zero (AMB-005)."""
    return _round_money(balance, balance.value * DAILY_RATE if balance.value > 0 else Decimal(0))


@dataclass(frozen=True, slots=True)
class TooManyInstalments:
    """A part would fall below one minor unit."""

    text: str
    count: int


def split_amount[M: (Aed, Bhd)](
    amount: Amount[M], count: InstalmentCount
) -> tuple[Amount[M], ...] | TooManyInstalments:
    """Equal parts rounded down, the remainder on the last (AMB-020); each part at least one minor unit."""
    total = amount.money
    part = type(total)((total.value / count.number).quantize(_get_minor_unit(total), rounding=ROUND_DOWN))
    if part.value <= 0:
        return TooManyInstalments(str(total.value), count=count.number)
    last_part = type(total)(total.value - part.value * (count.number - 1))
    return (*(Amount(part) for _ in range(count.number - 1)), Amount(last_part))


AED_FEE = Decimal("25.00")
AED_TO_BHD = Decimal("0.10238257")


def compute_overdraft_fee[M: (Aed, Bhd)](sample: M) -> Amount[M]:
    """The fee in ``like``'s currency: AED 25.00, and for BHD its conversion, rounded half-even (AMB-027)."""
    match sample:
        case Aed():
            return Amount(_round_money(sample, AED_FEE))
        case Bhd():
            return Amount(_round_money(sample, AED_FEE * AED_TO_BHD))


def split_amount_of(
    amount: Amount[Aed] | Amount[Bhd], count: InstalmentCount
) -> tuple[Amount[Aed], ...] | tuple[Amount[Bhd], ...] | TooManyInstalments:
    """``split_amount`` for an amount whose currency is known only at run time."""
    match amount.money:
        case Aed() as money:
            return split_amount(Amount(money), count)
        case Bhd() as money:
            return split_amount(Amount(money), count)


def compute_overdraft_fee_of(sample: Money) -> Amount[Aed] | Amount[Bhd]:
    """``compute_overdraft_fee`` for a currency known only at run time."""
    match sample:
        case Aed():
            return compute_overdraft_fee(sample)
        case Bhd():
            return compute_overdraft_fee(sample)


def make_amount_of(money: Money) -> Amount[Aed] | Amount[Bhd] | NotPositive:
    """``Amount.of`` for a currency known only at run time."""
    match money:
        case Aed():
            return Amount.make(money)
        case Bhd():
            return Amount.make(money)


def compute_rest_of(hold: Amount[Aed] | Amount[Bhd], taken_amount: Amount[Aed] | Amount[Bhd]) -> Money:
    """What a hold keeps once an amount of its own currency is taken; a mismatch is a bug the reader prevents."""
    match (hold.money, taken_amount.money):
        case (Aed() as hold_money, Aed() as taken_money):
            return hold_money - taken_money
        case (Bhd() as hold_money, Bhd() as taken_money):
            return hold_money - taken_money
        case _:
            raise ValueError(f"{get_currency(taken_amount.money)} taken from {get_currency(hold.money)}")


def sum_amounts(
    first_amount: Amount[Aed] | Amount[Bhd], second_amount: Amount[Aed] | Amount[Bhd]
) -> Amount[Aed] | Amount[Bhd]:
    """Two amounts of one currency added, above zero as both are; a mismatch is a bug the reader prevents."""
    match (first_amount.money, second_amount.money):
        case (Aed() as first_money, Aed() as second_money):
            return Amount(first_money + second_money)
        case (Bhd() as first_money, Bhd() as second_money):
            return Amount(first_money + second_money)
        case _:
            raise ValueError(f"{get_currency(first_amount.money)} added to {get_currency(second_amount.money)}")


def format_digits(money: Money) -> str:
    """The value's text, for the renderer and messages: its places, no sign change, no separators."""
    return str(money.value)


def is_below(money: Money, amount: Amount[Aed] | Amount[Bhd]) -> bool:
    """Whether a balance is below an amount of its own currency; a mismatch is a bug the reader prevents."""
    match (money, amount.money):
        case (Aed(), Aed()) | (Bhd(), Bhd()):
            return money.value < amount.money.value
        case _:
            raise ValueError(f"{get_currency(money)} compared with {get_currency(amount.money)}")
