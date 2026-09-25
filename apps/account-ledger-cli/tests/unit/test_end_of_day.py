"""Closing a day: interest (AMB-005), capitalization (AMB-023), and a settlement above its hold (AMB-030)."""

from dataclasses import replace

from account_ledger.domain.authorizations import Settled
from account_ledger.domain.balances import closing, holds
from account_ledger.domain.model.config import CHALLENGE
from account_ledger.domain.model.ids import Day
from account_ledger.domain.model.money import Amount
from account_ledger.domain.replay import replay
from account_ledger.domain.report import Capitalized
from support.states import state_of
from support.streams import (
    ACC_001,
    authorization,
    capitalization_amounts,
    credit,
    debit,
    fee_markers,
    interest_amounts,
    reversal,
    settlement,
)
from support.values import aed


def test_amb_030_a_settlement_above_its_hold_debits_in_full() -> None:
    """AMB-030: a settlement above its hold posts its whole amount and releases the hold; the balance may go negative,
    and the fee rule then applies as for any negative day."""
    stream = (
        credit("E1", 1, "100.00"),
        authorization("E2", 1, "Auth-A", "80.00"),
        settlement("E3", 2, "Auth-A", "120.00"),
    )

    log = replay(stream, CHALLENGE).log_at(Day(2))

    assert state_of(log, "Auth-A") == [Settled(Amount(aed("120.00")))]
    assert holds(log, ACC_001, Day(2)) == aed("0.00")
    assert fee_markers(log) == ["FEE-001-D2@D2"]
    assert closing(log, ACC_001, Day(2)) == aed("-45.00")


def test_amb_005_interest_accrues_on_a_positive_closing() -> None:
    """AMB-005: each day's accrual is an event fired at that day's close, on the closing ledger balance as known
    then."""
    log = replay((credit("E1", 1, "1000.00"),), CHALLENGE).log_at(Day(1))

    assert interest_amounts(log) == [("INT-001-D1@D1", aed("0.40"))]


def test_amb_005_a_changed_closing_adjusts_its_interest() -> None:
    """AMB-005: a late event that changes a past day's closing fires an adjustment for that day, value-dated the day it
    is recognised and naming the day it is for."""
    stream = (credit("E1", 1, "1000.00"), debit("E2", 2, "500.00", value=1))

    log = replay(stream, CHALLENGE).log_at(Day(2))

    assert interest_amounts(log) == [
        ("INT-001-D1@D1", aed("0.40")),
        ("INT-001-D1@D2", aed("-0.20")),
        ("INT-001-D2@D2", aed("0.20")),
    ]


def test_amb_023_a_days_interest_never_counts_its_own_capitalization() -> None:
    """AMB-023: a day closes in three steps, interest before capitalization, so re-evaluating a capitalization day
    reads its interest on the balance before the capitalization, and AED 50,000.00's Day 1 interest stays 20.00."""
    config = replace(CHALLENGE, last_day=Day(2), capitalization_days=frozenset({Day(1)}))

    log = replay((credit("E1", 1, "50000.00"),), config).log_at(Day(2))

    assert interest_amounts(log) == [("INT-001-D1@D1", aed("20.00")), ("INT-001-D2@D2", aed("20.01"))]


def test_amb_035_a_reversed_interest_event_is_fired_again() -> None:
    """AMB-035: a reversed interest event drops out of what was fired for its day, so the next close fires the day's
    interest again, as an adjustment under a marker for that close (tech-docs 002)."""
    stream = (credit("E1", 1, "1000.00"), reversal("E2", 2, "INT-001-D1@D1"))

    log = replay(stream, CHALLENGE).log_at(Day(2))

    assert interest_amounts(log) == [
        ("INT-001-D1@D1", aed("0.40")),
        ("INT-001-D1@D2", aed("0.40")),
        ("INT-001-D2@D2", aed("0.40")),
    ]


def test_amb_035_a_reversed_capitalization_returns_its_interest_to_accrued() -> None:
    """AMB-035: a reversed capitalization returns its interest to accrued interest, to be paid on the next
    capitalization day with the interest accrued since (tech-docs 002)."""
    config = replace(CHALLENGE, last_day=Day(2), capitalization_days=frozenset({Day(1), Day(2)}))
    stream = (credit("E1", 1, "1000.00"), reversal("E2", 2, "CAP-001@D1"))

    result = replay(stream, config)

    assert capitalization_amounts(result.log_at(Day(2))) == [("CAP-001@D1", aed("0.40")), ("CAP-001@D2", aed("0.80"))]
    assert [row.days for row in result.report(Day(2)).end_of_day if isinstance(row, Capitalized)] == [(Day(1), Day(2))]


def test_amb_035_a_capitalization_reversed_on_its_own_day_leaves_that_days_interest() -> None:
    """AMB-035, AMB-023: a capitalization reversed with its own value day no longer counts in that day's closing, so
    that day's interest base takes nothing more out, and AED 50,000.00's Day 1 interest stays 20.00."""
    config = replace(CHALLENGE, last_day=Day(2), capitalization_days=frozenset({Day(1), Day(2)}))
    stream = (credit("E1", 1, "50000.00"), reversal("E2", 2, "CAP-001@D1", value=1))

    log = replay(stream, config).log_at(Day(2))

    assert interest_amounts(log) == [("INT-001-D1@D1", aed("20.00")), ("INT-001-D2@D2", aed("20.00"))]
