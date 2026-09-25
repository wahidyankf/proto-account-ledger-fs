"""Money: places, positive amounts, one currency per sum, rounding, the split, and the fee."""

from decimal import Decimal

import pytest

from account_ledger.common.result import Err, Ok
from account_ledger.domain.model.ids import InstalmentCount
from account_ledger.domain.model.money import (
    AboveLimit,
    Aed,
    AmountIn,
    Bhd,
    CurrencyMismatch,
    Money,
    NotADecimal,
    NotPositive,
    TooManyInstalments,
    TooManyPlaces,
    compute_daily_interest,
    require_same_currency,
    sum_money,
)
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


def test_an_amount_at_the_limit_or_beyond_is_refused() -> None:
    """NUMBERS.md: money read from the stream stays below 10^12 in either direction, so no sum of it can outgrow the
    28-digit working precision."""
    assert Aed.parse("999999999999.99") == Ok(Aed(Decimal("999999999999.99")))
    assert Aed.parse("1000000000000.00") == Err(AboveLimit("1000000000000.00"))
    assert Aed.parse("-1000000000000") == Err(AboveLimit("-1000000000000"))
    assert Bhd.parse("1e30") == Err(AboveLimit("1E+30"))


def test_an_amount_must_be_above_zero() -> None:
    """An amount is money above zero; zero or below is a fault."""
    assert AmountIn.make(make_aed("0.00")) == Err(NotPositive("0.00"))
    assert AmountIn.make(make_aed("-400.00")) == Err(NotPositive("-400.00"))
    assert AmountIn.make(make_aed("0.01")) == Ok(AmountIn(make_aed("0.01")))
    with pytest.raises(ValueError, match="an amount is above zero"):
        AmountIn(make_aed("0.00"))


def test_aed_and_bhd_values_never_combine() -> None:
    """AED and BHD each combine only with their own kind, in the types and at run time."""
    unknown_money: Money = make_bhd("1.000")
    assert require_same_currency(make_aed("1.00"), unknown_money) == Err(
        CurrencyMismatch(expected_currency="AED", found_currency="BHD")
    )
    known_money: Money = make_aed("2.00")
    assert require_same_currency(make_aed("1.00"), known_money) == Ok(make_aed("2.00"))
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


def test_a_sum_or_comparison_across_currencies_returns_the_mismatch() -> None:
    """Every sum, rest, and comparison of money known only at run time returns a mismatch, never a wrong total; only
    a bug could bring one, since the reader keeps every effect in its account's currency."""
    aed_to_bhd = Err(CurrencyMismatch(expected_currency="AED", found_currency="BHD"))
    aed_amount, bhd_amount = AmountIn(make_aed("5.00")), AmountIn(make_bhd("1.000"))
    assert sum_money(make_aed("1.00"), [make_aed("2.00"), make_aed("0.50")]) == Ok(make_aed("3.50"))
    assert sum_money(make_aed("1.00"), [make_aed("2.00"), make_bhd("1.000")]) == aed_to_bhd
    assert aed_amount.add(bhd_amount) == aed_to_bhd
    assert aed_amount.compute_rest(bhd_amount) == aed_to_bhd
    assert make_aed("1.00").is_below(bhd_amount) == aed_to_bhd
    assert (aed_amount.add(aed_amount), make_aed("1.00").is_below(aed_amount)) == (
        Ok(AmountIn(make_aed("10.00"))),
        Ok(True),
    )


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
    assert AmountIn(make_bhd("10.000")).split(InstalmentCount(3)) == Ok(
        (AmountIn(make_bhd("3.333")), AmountIn(make_bhd("3.333")), AmountIn(make_bhd("3.334")))
    )
    assert AmountIn(make_aed("100.00")).split(InstalmentCount(4)) == Ok(
        tuple(AmountIn(make_aed("25.00")) for _ in range(4))
    )
    assert AmountIn(make_bhd("0.002")).split(InstalmentCount(3)) == Err(TooManyInstalments("0.002", count=3))


def test_amb_027_the_bhd_fee_is_2_560() -> None:
    """AMB-027: the overdraft fee is AED 25.00, and BHD 2.560 at the configured rate."""
    assert make_aed("0.00").compute_overdraft_fee() == AmountIn(make_aed("25.00"))
    assert make_bhd("0.000").compute_overdraft_fee() == AmountIn(make_bhd("2.560"))
