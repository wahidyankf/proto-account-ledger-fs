"""Money: places, positive amounts, one currency per sum, rounding, the split, and the fee."""

from decimal import Decimal

import pytest

from account_ledger.domain.model.ids import InstalmentCount
from account_ledger.domain.model.money import (
    Aed,
    Amount,
    Bhd,
    CurrencyMismatch,
    Money,
    NotADecimal,
    NotPositive,
    TooManyInstalments,
    TooManyPlaces,
    daily_interest,
    overdraft_fee,
    same_as,
    split,
)
from support.values import aed, bhd


def test_aed_refuses_more_than_two_places() -> None:
    assert Aed.parse("12.345") == TooManyPlaces("12.345", places=2, currency="AED")
    assert Aed.parse("12.5") == Aed.parse("12.50")
    assert Aed.parse("12.00x") == NotADecimal("12.00x")
    with pytest.raises(ValueError, match="AED holds exactly 2 places"):
        Aed(Decimal("12.345"))


def test_bhd_refuses_more_than_three_places() -> None:
    assert Bhd.parse("10.0001") == TooManyPlaces("10.0001", places=3, currency="BHD")
    assert Bhd.parse("10") == Bhd.parse("10.000")


def test_an_amount_must_be_above_zero() -> None:
    assert Amount.of(aed("0.00")) == NotPositive("0.00")
    assert Amount.of(aed("-400.00")) == NotPositive("-400.00")
    assert Amount.of(aed("0.01")) == Amount(aed("0.01"))
    with pytest.raises(ValueError, match="an amount is above zero"):
        Amount(aed("0.00"))


def test_aed_and_bhd_values_never_combine() -> None:
    unknown: Money = bhd("1.000")
    assert same_as(aed("1.00"), unknown) == CurrencyMismatch(expected="AED", found="BHD")
    known: Money = aed("2.00")
    assert same_as(aed("1.00"), known) == aed("2.00")
    assert aed("1.00") + aed("2.50") == aed("3.50")
    assert aed("1.00") - aed("2.50") == aed("-1.50")
    assert -aed("1.00") == aed("-1.00")
    assert aed("1.00") < aed("2.50")
    assert bhd("1.000") + bhd("0.001") == bhd("1.001")
    # The type gate refuses these mixes; the operators refuse them at run time too.
    with pytest.raises(TypeError):
        aed("1.00") + bhd("1.000")  # pyright: ignore[reportOperatorIssue, reportUnusedExpression]
    with pytest.raises(TypeError):
        bhd("1.000") - aed("1.00")  # pyright: ignore[reportOperatorIssue, reportUnusedExpression]


def test_amb_006_daily_interest_rounds_half_even() -> None:
    assert daily_interest(aed("312.50")) == aed("0.12")
    assert daily_interest(aed("337.50")) == aed("0.14")
    assert daily_interest(aed("285.00")) == aed("0.11")
    assert daily_interest(bhd("10.000")) == bhd("0.004")
    assert daily_interest(aed("0.00")) == aed("0.00")
    assert daily_interest(aed("-370.00")) == aed("0.00")


def test_amb_020_ten_bhd_splits_3_333_3_333_3_334() -> None:
    assert split(Amount(bhd("10.000")), InstalmentCount(3)) == (
        Amount(bhd("3.333")),
        Amount(bhd("3.333")),
        Amount(bhd("3.334")),
    )
    assert split(Amount(aed("100.00")), InstalmentCount(4)) == tuple(Amount(aed("25.00")) for _ in range(4))
    assert split(Amount(bhd("0.002")), InstalmentCount(3)) == TooManyInstalments("0.002", count=3)


def test_amb_027_the_bhd_fee_is_2_560() -> None:
    assert overdraft_fee(aed("0.00")) == Amount(aed("25.00"))
    assert overdraft_fee(bhd("0.000")) == Amount(bhd("2.560"))
