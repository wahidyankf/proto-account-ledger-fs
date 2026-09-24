"""One test per brief criterion, C1 to C8, each replaying the brief's stream and asserting MOVEMENT's figures.

A refused criterion is proven by a test of what the ledger does instead (REJECTED.md).
"""

from account_ledger.authorizations import Approved, Declined, Settled, records
from account_ledger.balances import closing
from account_ledger.config import CHALLENGE
from account_ledger.events import Fee, Instalment, Settlement
from account_ledger.ids import AuthorizationId, Day, IncomingId, InstalmentId
from account_ledger.log import Accepted, Captured, ForcePosted, SettlementAccepted
from account_ledger.money import Aed, Amount, Bhd
from account_ledger.replay import replay
from support.brief_stream import brief_stream
from support.states import settlements_of, state_of
from support.streams import (
    ACC_001,
    ACC_002,
    capitalization_amounts,
    fee_markers,
    interest_amounts,
    refund_markers,
    through,
)
from support.values import aed, bhd


def test_c1_day_2_closes_at_minus_370_at_end_of_day_5_before_fees() -> None:
    """C1, accepted: "The Day 2 closing ledger balance, evaluated at end of Day 5 and before any fee is assessed, is
    AED −370.00." """
    log = replay(brief_stream(), CHALLENGE).log_at(Day(5))

    assert closing(log, ACC_001, Day(2)) == aed("-370.00")


def test_c5_a_hold_reduces_available_balance_but_not_ledger_balance() -> None:
    """C5, refused (AMB-021): "If Auth-B is approved, its hold reduces available balance but not ledger balance."
    Auth-B is declined, so the rule is proven on Auth-A's hold instead, on Day 2."""
    day_2 = replay(brief_stream(), CHALLENGE).report(Day(2))

    assert day_2.closing[ACC_001.id] == aed("250.00")
    assert day_2.available[ACC_001.id] == aed("50.00")


def test_c5_auth_b_is_declined() -> None:
    """C5, refused (AMB-021): "If Auth-B is approved, its hold reduces available balance but not ledger balance."
    Auth-B arrives on Day 5 against an available balance of −335.00, so it is declined and holds nothing."""
    log = replay(brief_stream(), CHALLENGE).log_at(Day(5))

    auth_b = [
        record.state for record in records(log) if record.authorization.authorization == AuthorizationId("Auth-B")
    ]
    assert auth_b == [Declined(Amount(aed("90.00")))]


def test_c3_auth_a_settlement_is_accepted_and_releases_the_hold() -> None:
    """C3, accepted: "The Day 4 settlement of Auth-A must be accepted." It captures 185.00 and, being final, releases
    the whole 200.00 hold (AMB-013)."""
    result = replay(brief_stream(), CHALLENGE)
    log = result.log_at(Day(4))

    assert state_of(log, "Auth-A") == [Settled(Amount(aed("185.00")))]
    day_4 = result.report(Day(4))
    assert day_4.available[ACC_001.id] == day_4.closing[ACC_001.id]
    settlement = next(event for event in brief_stream() if event.id == IncomingId("E5"))
    assert isinstance(settlement, Settlement)
    captured = Captured(Approved(Amount(aed("200.00"))), Settled(Amount(aed("185.00"))))
    assert settlements_of(log, settlement.id.value) == [SettlementAccepted(settlement, Day(4), captured)]


def test_c4_e6_is_force_posted_for_180() -> None:
    """C4, refused (AMB-012, AMB-029): "Any settlement referencing an authorization ID not present in the ledger must be
    rejected and the funds must not leave the account." E6 names Auth-Z, which the ledger never saw, so it is honoured
    as a force-post: ACC-001 is debited 180.00 value-dated Day 4 and no hold is released."""
    log = replay(through(brief_stream(), "E6"), CHALLENGE).log_at(Day(4))

    settlement = next(event for event in brief_stream() if event.id == IncomingId("E6"))
    assert isinstance(settlement, Settlement)
    assert settlements_of(log, settlement.id.value) == [SettlementAccepted(settlement, Day(4), ForcePosted())]
    assert state_of(log, "Auth-Z") == []
    assert state_of(log, "Auth-A") == [Settled(Amount(aed("185.00")))]
    assert closing(log, ACC_001, Day(4)) == aed("285.00")


def test_c7_e10_posts_3_333_3_333_3_334() -> None:
    """C7, refused (AMB-020): "The three BHD instalments in E10 must each be BHD 3.334." Three of 3.334 would credit
    10.002, so E10 posts 3.333, 3.333, and 3.334, each value-dated Day 5, summing to the 10.000 sent."""
    log = replay(brief_stream(), CHALLENGE).log_at(Day(6))

    parts = [entry.event for entry in log if isinstance(entry, Accepted) and isinstance(entry.event, Instalment)]
    assert [(part.id, part.amount, part.value_day) for part in parts] == [
        (InstalmentId(IncomingId("E10"), n), Amount(bhd(text)), Day(5))
        for n, text in ((1, "3.333"), (2, "3.333"), (3, "3.334"))
    ]
    assert closing(log, ACC_002, Day(5)) == bhd("10.000")


def test_c2_e7_causes_three_fees_all_value_dated_day_5() -> None:
    """C2, refused (AMB-002, AMB-003): "E7 causes exactly one overdraft fee to be assessed, on Day 2." E7 arrives on
    Day 5 value-dated Day 2, so Day 5's close finds Days 2, 4, and 5 negative and charges each, value-dated Day 5."""
    log = replay(brief_stream(), CHALLENGE).log_at(Day(5))

    assert fee_markers(log) == ["FEE-001-D2@D5", "FEE-001-D4@D5", "FEE-001-D5@D5"]
    fees = [entry.event for entry in log if isinstance(entry, Accepted) and isinstance(entry.event, Fee)]
    assert [(fee.amount, fee.value_day) for fee in fees] == [(Amount(aed("25.00")), Day(5))] * 3


def test_c6_e9_restores_days_2_to_4_and_refunds_the_fees() -> None:
    """C6, refused (AMB-004, AMB-005, AMB-024): "After E9, all balances and fees return to their pre-E7 values." Days
    2, 3, and 4 close at 250.00, 650.00, and 285.00 again, and the three fees stay in the log, each undone by a refund
    value-dated Day 6."""
    log = replay(brief_stream(), CHALLENGE).log_at(Day(6))

    assert [closing(log, ACC_001, Day(day)) for day in (2, 3, 4)] == [aed("250.00"), aed("650.00"), aed("285.00")]
    assert fee_markers(log) == ["FEE-001-D2@D5", "FEE-001-D4@D5", "FEE-001-D5@D5"]
    assert refund_markers(log) == ["REFUND-001-D2@D6", "REFUND-001-D4@D6", "REFUND-001-D5@D6"]


def test_c8_capitalization_equals_the_sum_of_interest_events() -> None:
    """C8, refused (AMB-006, AMB-023): "If the rounded daily interest accruals do not sum to the capitalized total, the
    remainder is discarded." Each capitalization is the sum of its account's rounded interest events, so no remainder
    can exist."""
    log = replay(brief_stream(), CHALLENGE).log_at(Day(6))

    assert capitalization_amounts(log) == [("CAP-001@D6", aed("0.76")), ("CAP-002@D6", bhd("0.008"))]
    aed_total, bhd_total = Aed.zero(), Bhd.zero()
    for marker, money in interest_amounts(log):
        match money:
            case Aed() if marker.startswith("INT-001"):
                aed_total = aed_total + money
            case Bhd() if marker.startswith("INT-002"):
                bhd_total = bhd_total + money
            case _:
                raise AssertionError(f"{marker} in the wrong currency")
    assert (aed_total, bhd_total) == (aed("0.76"), bhd("0.008"))


def test_c6_day_6_closes_at_285_76_not_285_79() -> None:
    """C6, refused (AMB-004, AMB-005, AMB-024): "After E9, all balances and fees return to their pre-E7 values." The
    fees are value-dated Day 5 and their refunds Day 6, so Day 5 closes at 210.00, earns 0.08 rather than 0.11, and
    ACC-001 capitalizes 0.76 and closes Day 6 at 285.76, not 285.79."""
    log = replay(brief_stream(), CHALLENGE).log_at(Day(6))

    assert closing(log, ACC_001, Day(5)) == aed("210.00")
    assert closing(log, ACC_001, Day(6)) == aed("285.76")
