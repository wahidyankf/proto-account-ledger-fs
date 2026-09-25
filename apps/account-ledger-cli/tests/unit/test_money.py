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
    compute_daily_interest,
    compute_overdraft_fee,
    split_amount,
    try_narrow_currency,
)
from account_ledger.domain.model.result import Err, Ok
from support.values import make_aed, make_bhd


def test_aed_refuses_more_than_two_places() -> None:
    """AED holds two places: a third is refused, fewer are padded, and a non-number is a fault."""
    assert Aed.parse("12.345") == Err(TooManyPlaces("12.345", places=2, currency="AED"))
    assert Aed.parse("12.5") == Aed.parse("12.50")
    assert Aed.parse("12.00x") == Err(NotADecimal("12.00x"))
    assert Aed.make(Decimal("Infinity")) == Err(NotADecimal("Infinity"))
    with pytest.raises(ValueError, match="AED holds exactly 2 places"):
        Aed(Decimal("12.345"))


def test_bhd_refuses_more_than_three_places() -> None:
    """BHD holds three places: a fourth is refused, fewer are padded, and a non-number is a fault."""
    assert Bhd.parse("10.0001") == Err(TooManyPlaces("10.0001", places=3, currency="BHD"))
    assert Bhd.parse("10") == Bhd.parse("10.000")
    assert Bhd.parse("ten") == Err(NotADecimal("ten"))


def test_an_amount_must_be_above_zero() -> None:
    """An amount is money above zero; zero or below is a fault."""
    assert Amount.make(make_aed("0.00")) == Err(NotPositive("0.00"))
    assert Amount.make(make_aed("-400.00")) == Err(NotPositive("-400.00"))
    assert Amount.make(make_aed("0.01")) == Ok(Amount(make_aed("0.01")))
    with pytest.raises(ValueError, match="an amount is above zero"):
        Amount(make_aed("0.00"))


def test_aed_and_bhd_values_never_combine() -> None:
    """AED and BHD each combine only with their own kind, in the types and at run time."""
    unknown_money: Money = make_bhd("1.000")
    assert try_narrow_currency(make_aed("1.00"), unknown_money) == Err(
        CurrencyMismatch(expected_currency="AED", found_currency="BHD")
    )
    known_money: Money = make_aed("2.00")
    assert try_narrow_currency(make_aed("1.00"), known_money) == Ok(make_aed("2.00"))
    assert make_aed("1.00") + make_aed("2.50") == make_aed("3.50")
    assert make_aed("1.00") - make_aed("2.50") == make_aed("-1.50")
    assert -make_aed("1.00") == make_aed("-1.00")
    assert make_aed("1.00") < make_aed("2.50")
    assert make_bhd("1.000") + make_bhd("0.001") == make_bhd("1.001")
    # The type gate refuses these mixes; the operators refuse them at run time too.
    with pytest.raises(TypeError):
        make_aed("1.00") + make_bhd("1.000")  # pyright: ignore[reportOperatorIssue, reportUnusedExpression]
    with pytest.raises(TypeError):
        make_bhd("1.000") - make_aed("1.00")  # pyright: ignore[reportOperatorIssue, reportUnusedExpression]


def test_amb_006_daily_interest_rounds_half_even() -> None:
    """AMB-006: a day's interest rounds half-even to its currency's places, and is zero at or below zero."""
    assert compute_daily_interest(make_aed("312.50")) == make_aed("0.12")
    assert compute_daily_interest(make_aed("337.50")) == make_aed("0.14")
    assert compute_daily_interest(make_aed("285.00")) == make_aed("0.11")
    assert compute_daily_interest(make_bhd("10.000")) == make_bhd("0.004")
    assert compute_daily_interest(make_aed("0.00")) == make_aed("0.00")
    assert compute_daily_interest(make_aed("-370.00")) == make_aed("0.00")


def test_amb_020_ten_bhd_splits_3_333_3_333_3_334() -> None:
    """AMB-020: a split gives the remainder to the last part, and refuses more parts than minor units."""
    assert split_amount(Amount(make_bhd("10.000")), InstalmentCount(3)) == Ok(
        (Amount(make_bhd("3.333")), Amount(make_bhd("3.333")), Amount(make_bhd("3.334")))
    )
    assert split_amount(Amount(make_aed("100.00")), InstalmentCount(4)) == Ok(
        tuple(Amount(make_aed("25.00")) for _ in range(4))
    )
    assert split_amount(Amount(make_bhd("0.002")), InstalmentCount(3)) == Err(TooManyInstalments("0.002", count=3))


def test_amb_027_the_bhd_fee_is_2_560() -> None:
    """AMB-027: the overdraft fee is AED 25.00, and BHD 2.560 at the configured rate."""
    assert compute_overdraft_fee(make_aed("0.00")) == Amount(make_aed("25.00"))
    assert compute_overdraft_fee(make_bhd("0.000")) == Amount(make_bhd("2.560"))
