"""Interest: accrued on a positive closing, adjusted when it changes, and capitalized (AMB-005, AMB-023, AMB-035)."""

from dataclasses import replace

from account_ledger.domain.model.config import CHALLENGE
from account_ledger.domain.model.ids import Day
from account_ledger.domain.report import Capitalized
from account_ledger.domain.stream_processing import process_stream
from support.results import unwrap_ok
from support.streams import list_capitalization_amounts, list_interest_amounts, make_credit, make_debit, make_reversal
from support.values import make_aed


def test_amb_005_interest_accrues_on_a_positive_closing() -> None:
    """AMB-005: each day's accrual is an event fired at that day's close, on the closing ledger balance as known
    then."""
    log = unwrap_ok(process_stream((make_credit("E1", 1, "1000.00"),), CHALLENGE)).find_log(Day(1))

    assert list_interest_amounts(log) == [("INT-001-D1@D1", make_aed("0.40"))]


def test_amb_005_a_changed_closing_adjusts_its_interest() -> None:
    """AMB-005: a late event that changes a past day's closing fires an adjustment for that day, value-dated the day it
    is recognised and naming the day it is for."""
    stream = (make_credit("E1", 1, "1000.00"), make_debit("E2", 2, "500.00", value=1))

    log = unwrap_ok(process_stream(stream, CHALLENGE)).find_log(Day(2))

    assert list_interest_amounts(log) == [
        ("INT-001-D1@D1", make_aed("0.40")),
        ("INT-001-D1@D2", make_aed("-0.20")),
        ("INT-001-D2@D2", make_aed("0.20")),
    ]


def test_amb_023_a_days_interest_never_counts_its_own_capitalization() -> None:
    """AMB-023: a day closes in three steps, interest before capitalization, so re-evaluating a capitalization day
    reads its interest on the balance before the capitalization, and AED 50,000.00's Day 1 interest stays 20.00."""
    config = replace(CHALLENGE, last_day=Day(2), capitalization_days=frozenset({Day(1)}))

    log = unwrap_ok(process_stream((make_credit("E1", 1, "50000.00"),), config)).find_log(Day(2))

    assert list_interest_amounts(log) == [("INT-001-D1@D1", make_aed("20.00")), ("INT-001-D2@D2", make_aed("20.01"))]


def test_amb_035_a_reversed_interest_event_is_fired_again() -> None:
    """AMB-035: a reversed interest event drops out of what was fired for its day, so the next close fires the day's
    interest again, as an adjustment under a marker for that close (tech-docs 002)."""
    stream = (make_credit("E1", 1, "1000.00"), make_reversal("E2", 2, "INT-001-D1@D1"))

    log = unwrap_ok(process_stream(stream, CHALLENGE)).find_log(Day(2))

    assert list_interest_amounts(log) == [
        ("INT-001-D1@D1", make_aed("0.40")),
        ("INT-001-D1@D2", make_aed("0.40")),
        ("INT-001-D2@D2", make_aed("0.40")),
    ]


def test_amb_035_a_reversed_capitalization_returns_its_interest_to_accrued() -> None:
    """AMB-035: a reversed capitalization returns its interest to accrued interest, to be paid on the next
    capitalization day with the interest accrued since (tech-docs 002)."""
    config = replace(CHALLENGE, last_day=Day(2), capitalization_days=frozenset({Day(1), Day(2)}))
    stream = (make_credit("E1", 1, "1000.00"), make_reversal("E2", 2, "CAP-001@D1"))

    result = unwrap_ok(process_stream(stream, config))

    assert list_capitalization_amounts(result.find_log(Day(2))) == [
        ("CAP-001@D1", make_aed("0.40")),
        ("CAP-001@D2", make_aed("0.80")),
    ]
    assert [row.days for row in result.find_report(Day(2)).end_of_day if isinstance(row, Capitalized)] == [
        (Day(1), Day(2))
    ]


def test_amb_035_a_capitalization_reversed_on_its_own_day_leaves_that_days_interest() -> None:
    """AMB-035, AMB-023: a capitalization reversed with its own value day no longer counts in that day's closing, so
    that day's interest base takes nothing more out, and AED 50,000.00's Day 1 interest stays 20.00."""
    config = replace(CHALLENGE, last_day=Day(2), capitalization_days=frozenset({Day(1), Day(2)}))
    stream = (make_credit("E1", 1, "50000.00"), make_reversal("E2", 2, "CAP-001@D1", value=1))

    log = unwrap_ok(process_stream(stream, config)).find_log(Day(2))

    assert list_interest_amounts(log) == [("INT-001-D1@D1", make_aed("20.00")), ("INT-001-D2@D2", make_aed("20.00"))]
