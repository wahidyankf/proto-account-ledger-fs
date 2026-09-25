"""Fees: charged for a day that closes negative, refunded once it recovers (AMB-002, AMB-011, AMB-027, AMB-035)."""

from dataclasses import replace

from account_ledger.domain.account.domain_events import (
    FeeCharged,
)
from account_ledger.domain.ledger.event_log import (
    find_history,
)
from account_ledger.domain.model.config import CHALLENGE
from account_ledger.domain.model.ids import Day
from account_ledger.domain.model.money import AmountIn
from account_ledger.domain.stream_processing import (
    process_stream,
)
from support.brief_stream import build_brief_stream
from support.results import unwrap_ok
from support.streams import ACC_002, list_fee_ids, list_refund_ids, make_credit, make_debit, make_reversal
from support.values import make_bhd


def test_amb_011_a_day_still_negative_is_not_charged_again() -> None:
    """AMB-002, AMB-011: a fee is charged "once per day per account", so a day that has its fee is not charged again,
    however many closes find it negative."""
    log = unwrap_ok(process_stream((make_debit("E1", 1, "10.00"),), CHALLENGE)).find_log(Day(2))

    assert list_fee_ids(log) == ["FEE-001-D1@D1", "FEE-001-D2@D2"]


def test_amb_011_a_fee_counts_in_the_closings_after_it() -> None:
    """AMB-011: a fee is an event like any other, so the Day 1 fee, value-dated Day 2, takes Day 2 from 10.00 to
    −15.00, and Day 2 is charged too."""
    stream = (make_debit("E1", 2, "20.00", value=1), make_credit("E2", 2, "30.00"))

    log = unwrap_ok(process_stream(stream, CHALLENGE)).find_log(Day(2))

    assert list_fee_ids(log) == ["FEE-001-D1@D2", "FEE-001-D2@D2"]


def test_amb_027_a_bhd_account_is_charged_bhd_2_560() -> None:
    """AMB-027: the fee is AED 25.00 converted at the configured rate and rounded half-even to BHD's three places, so
    ACC-002 is charged FEE-002-D1@D1 and closes Day 1 at −3.560."""
    log = unwrap_ok(process_stream((make_debit("E1", 1, "1.000", account="ACC-002"),), CHALLENGE)).find_log(Day(1))

    fees = [entry.event for entry in log if isinstance(entry, FeeCharged)]
    assert [fee.amount for fee in fees] == [AmountIn(make_bhd("2.560"))]
    assert list_fee_ids(log) == ["FEE-002-D1@D1"]
    assert unwrap_ok(find_history(log, ACC_002).compute_closing(Day(1))) == make_bhd("-3.560")


def test_amb_035_a_fee_reversed_on_a_negative_day_is_charged_again() -> None:
    """AMB-035: a fee reversed while its day is still negative is charged again, under a generated ID for today."""
    stream = (make_debit("E1", 1, "10.00"), make_reversal("E2", 2, "FEE-001-D1@D1"))

    log = unwrap_ok(process_stream(stream, CHALLENGE)).find_log(Day(2))

    assert list_fee_ids(log) == ["FEE-001-D1@D1", "FEE-001-D1@D2", "FEE-001-D2@D2"]


def test_amb_035_a_reversed_refund_puts_its_fee_back_in_force() -> None:
    """AMB-035: a refund may itself be reversed, which puts its fee back in force for the next close to judge again;
    Day 2 still closes at 250.00, so Day 7's close refunds FEE-001-D2@D5 once more."""
    week = replace(CHALLENGE, last_day=Day(7))
    stream = (*build_brief_stream(), make_reversal("E12", 7, "REFUND-001-D2@D6"))

    log = unwrap_ok(process_stream(stream, week)).find_log(Day(7))

    assert list_refund_ids(log) == ["REFUND-001-D2@D6", "REFUND-001-D4@D6", "REFUND-001-D5@D6", "REFUND-001-D2@D7"]
