"""The stream, processed day by day: opening reports, days closing as booked days advance, empty and late days, and
the window's end; one test per brief criterion, C1 to C8, each asserting MOVEMENT's figures, a refused one proven by a
test of what the ledger does instead (REJECTED.md); and the brief's one failing test against this design,
inline-annotated with what it reveals (AMB-018, AMB-031, D6)."""

from dataclasses import replace

import pytest

from account_ledger.application.stream import IncomingStream
from account_ledger.challenge import CHALLENGE
from account_ledger.domain.account.authorizations import Approved, Declined, Settled
from account_ledger.domain.account.domain_events import (
    FeeCharged,
    InstalmentPosted,
    SettlementApplied,
    SettlementForcePosted,
)
from account_ledger.domain.ledger.ledger import Ledger
from account_ledger.domain.model.events import Settlement
from account_ledger.domain.model.ids import AccountId, AuthorizationId, Day, IncomingId, InstalmentId
from account_ledger.domain.model.money import Aed, AmountIn, Bhd
from support.brief_stream import build_brief_stream
from support.entries import (
    list_capitalization_amounts,
    list_entries,
    list_fee_ids,
    list_interest_amounts,
    list_refund_ids,
    list_settlements,
    list_states,
)
from support.results import unwrap_ok
from support.streams import ACC_001_OPENING, ACC_002_OPENING, build_unsettled_auth_a, make_credit, take_through
from support.values import make_aed, make_bhd


def test_an_empty_stream_reports_the_opening_balances_for_day_0_to_6() -> None:
    """An empty stream still reports Day 0 to Day 6, each closing at the opening balances, with an empty log."""

    result = unwrap_ok(IncomingStream(()).process(CHALLENGE))

    assert [report.day for report in result.reports] == [Day(number) for number in range(7)]

    for report in result.reports:
        assert report.closing_balances == {
            AccountId("ACC-001"): make_aed("0.00"),
            AccountId("ACC-002"): make_bhd("0.000"),
        }

    assert result.find_log(Day(6)).entries == ()


def test_amb_015_a_late_event_is_processed_on_the_current_day() -> None:
    """AMB-015: E10, booked Day 5 but listed after E9, arrives once Day 5 has closed and is processed on Day 6."""

    result = unwrap_ok(IncomingStream(build_brief_stream()).process(CHALLENGE))

    assert IncomingId("E10") not in [entry.event.id for entry in result.find_log(Day(5)).entries]

    e10 = [entry for entry in result.find_log(Day(6)).entries if entry.event.id == IncomingId("E10")]
    assert [entry.processed_day for entry in e10] == [Day(6)]


def test_amb_001_a_day_without_events_still_closes() -> None:
    """AMB-001: an event booked on a later day closes every day before it, those with no events of their own
    included, so each still accrues its interest; the event is processed on its own booked day."""

    stream = (make_credit("E1", 1, "1000.00"), make_credit("E2", 4, "10.00"))
    result = unwrap_ok(IncomingStream(stream).process(CHALLENGE))

    assert [event_id for event_id, _ in list_interest_amounts(result.find_log(Day(3)))] == [
        "INT-001-D1@D1",
        "INT-001-D2@D2",
        "INT-001-D3@D3",
    ]
    assert [entry.processed_day for entry in list_entries(result.find_log(Day(4)), "E2")] == [Day(4)]


def test_amb_001_an_event_booked_after_the_window_reaches_no_day() -> None:
    """AMB-001: no day closes after the window's last, so an event booked after it reaches no day's log or report;
    the event source refuses such a day before it gets here."""

    stream = (make_credit("E1", 1, "100.00"), make_credit("E2", 9, "50.00"))
    result = unwrap_ok(IncomingStream(stream).process(CHALLENGE))

    assert [report.day for report in result.reports] == [Day(number) for number in range(7)]
    assert list_entries(result.find_log(Day(6)), "E2") == []


def test_c1_day_2_closes_at_minus_370_at_end_of_day_5_before_fees() -> None:
    """C1, accepted: "The Day 2 closing ledger balance, evaluated at end of Day 5 and before any fee is assessed, is
    AED −370.00." """

    log = unwrap_ok(IncomingStream(build_brief_stream()).process(CHALLENGE)).find_log(Day(5))

    assert unwrap_ok(Ledger(CHALLENGE, log).find_account(ACC_001_OPENING).compute_closing(Day(2))) == make_aed(
        "-370.00"
    )


def test_c5_a_hold_reduces_available_balance_but_not_ledger_balance() -> None:
    """C5, refused (AMB-021): "If Auth-B is approved, its hold reduces available balance but not ledger balance."
    Auth-B is declined, so the rule is proven on Auth-A's hold instead, on Day 2."""

    day_2 = unwrap_ok(IncomingStream(build_brief_stream()).process(CHALLENGE)).find_report(Day(2))

    assert day_2.closing_balances[ACC_001_OPENING.id] == make_aed("250.00")
    assert day_2.available_balances[ACC_001_OPENING.id] == make_aed("50.00")


def test_c5_auth_b_is_declined() -> None:
    """C5, refused (AMB-021): "If Auth-B is approved, its hold reduces available balance but not ledger balance."
    Auth-B arrives on Day 5 against an available balance of −335.00, so it is declined and holds nothing."""

    log = unwrap_ok(IncomingStream(build_brief_stream()).process(CHALLENGE)).find_log(Day(5))

    auth_b = [
        record.state
        for record in Ledger(CHALLENGE, log).find_account(ACC_001_OPENING).list_records()
        if record.authorization.authorization == AuthorizationId("Auth-B")
    ]

    assert auth_b == [Declined(AmountIn(make_aed("90.00")))]


def test_c3_auth_a_settlement_is_accepted_and_releases_the_hold() -> None:
    """C3, accepted: "The Day 4 settlement of Auth-A must be accepted." It settles 185.00 and, being final, releases
    the whole 200.00 hold (AMB-013)."""

    result = unwrap_ok(IncomingStream(build_brief_stream()).process(CHALLENGE))
    log = result.find_log(Day(4))

    assert list_states(log, "Auth-A") == [Settled(AmountIn(make_aed("185.00")))]

    day_4 = result.find_report(Day(4))
    assert day_4.available_balances[ACC_001_OPENING.id] == day_4.closing_balances[ACC_001_OPENING.id]

    settlement = next(event for event in build_brief_stream() if event.id == IncomingId("E5"))
    assert isinstance(settlement, Settlement)

    applied = SettlementApplied(
        settlement, Day(4), Approved(AmountIn(make_aed("200.00"))), Settled(AmountIn(make_aed("185.00")))
    )

    assert list_settlements(log, settlement.id.value) == [applied]


def test_c4_e6_is_force_posted_for_180() -> None:
    """C4, refused (AMB-012, AMB-029): "Any settlement referencing an authorization ID not present in the ledger must be
    rejected and the funds must not leave the account." E6 names Auth-Z, which the ledger never saw, so it is honoured
    as a force-post: ACC-001 is debited 180.00 value-dated Day 4 and no hold is released."""

    log = unwrap_ok(IncomingStream(take_through(build_brief_stream(), "E6")).process(CHALLENGE)).find_log(Day(4))

    settlement = next(event for event in build_brief_stream() if event.id == IncomingId("E6"))
    assert isinstance(settlement, Settlement)
    assert list_settlements(log, settlement.id.value) == [SettlementForcePosted(settlement, Day(4))]
    assert list_states(log, "Auth-Z") == []
    assert list_states(log, "Auth-A") == [Settled(AmountIn(make_aed("185.00")))]
    assert unwrap_ok(Ledger(CHALLENGE, log).find_account(ACC_001_OPENING).compute_closing(Day(4))) == make_aed("285.00")


def test_c7_e10_posts_3_333_3_333_3_334() -> None:
    """C7, refused (AMB-020): "The three BHD instalments in E10 must each be BHD 3.334." Three of 3.334 would credit
    10.002, so E10 posts 3.333, 3.333, and 3.334, each value-dated Day 5, summing to the 10.000 sent."""

    log = unwrap_ok(IncomingStream(build_brief_stream()).process(CHALLENGE)).find_log(Day(6))

    parts = [entry.event for entry in log.entries if isinstance(entry, InstalmentPosted)]
    assert [(part.id, part.amount, part.value_date) for part in parts] == [
        (InstalmentId(IncomingId("E10"), number), AmountIn(make_bhd(text)), Day(5))
        for number, text in ((1, "3.333"), (2, "3.333"), (3, "3.334"))
    ]
    assert unwrap_ok(Ledger(CHALLENGE, log).find_account(ACC_002_OPENING).compute_closing(Day(5))) == make_bhd("10.000")


def test_c2_e7_causes_three_fees_all_value_dated_day_5() -> None:
    """C2, refused (AMB-002, AMB-003): "E7 causes exactly one overdraft fee to be assessed, on Day 2." E7 arrives on
    Day 5 value-dated Day 2, so Day 5's close finds Days 2, 4, and 5 negative and charges each, value-dated Day 5."""

    log = unwrap_ok(IncomingStream(build_brief_stream()).process(CHALLENGE)).find_log(Day(5))

    assert list_fee_ids(log) == ["FEE-001-D2@D5", "FEE-001-D4@D5", "FEE-001-D5@D5"]

    fees = [entry.event for entry in log.entries if isinstance(entry, FeeCharged)]
    assert [(fee.amount, fee.value_date) for fee in fees] == [(AmountIn(make_aed("25.00")), Day(5))] * 3


def test_c6_e9_restores_days_2_to_4_and_refunds_the_fees() -> None:
    """C6, refused (AMB-004, AMB-005, AMB-024): "After E9, all balances and fees return to their pre-E7 values." Days
    2, 3, and 4 close at 250.00, 650.00, and 285.00 again, and the three fees stay in the log, each undone by a refund
    value-dated Day 6."""

    log = unwrap_ok(IncomingStream(build_brief_stream()).process(CHALLENGE)).find_log(Day(6))

    assert [
        unwrap_ok(Ledger(CHALLENGE, log).find_account(ACC_001_OPENING).compute_closing(Day(day))) for day in (2, 3, 4)
    ] == [
        make_aed("250.00"),
        make_aed("650.00"),
        make_aed("285.00"),
    ]
    assert list_fee_ids(log) == ["FEE-001-D2@D5", "FEE-001-D4@D5", "FEE-001-D5@D5"]
    assert list_refund_ids(log) == ["REFUND-001-D2@D6", "REFUND-001-D4@D6", "REFUND-001-D5@D6"]


def test_c8_capitalization_equals_the_sum_of_interest_events() -> None:
    """C8, refused (AMB-006, AMB-023): "If the rounded daily interest accruals do not sum to the capitalized total, the
    remainder is discarded." Each capitalization is the sum of its account's rounded interest events, so no remainder
    can exist."""

    log = unwrap_ok(IncomingStream(build_brief_stream()).process(CHALLENGE)).find_log(Day(6))

    assert list_capitalization_amounts(log) == [("CAP-001@D6", make_aed("0.76")), ("CAP-002@D6", make_bhd("0.008"))]

    aed_total, bhd_total = Aed.make_zero(), Bhd.make_zero()

    for event_id, money in list_interest_amounts(log):
        match money:
            case Aed() if event_id.startswith("INT-001"):
                aed_total = aed_total + money
            case Bhd() if event_id.startswith("INT-002"):
                bhd_total = bhd_total + money
            case _:
                raise AssertionError(f"{event_id} in the wrong currency")

    assert (aed_total, bhd_total) == (make_aed("0.76"), make_bhd("0.008"))


def test_c6_day_6_closes_at_285_76_not_285_79() -> None:
    """C6, refused (AMB-004, AMB-005, AMB-024): "After E9, all balances and fees return to their pre-E7 values." The
    fees are value-dated Day 5 and their refunds Day 6, so Day 5 closes at 210.00, earns 0.08 rather than 0.11, and
    ACC-001 capitalizes 0.76 and closes Day 6 at 285.76, not 285.79."""

    log = unwrap_ok(IncomingStream(build_brief_stream()).process(CHALLENGE)).find_log(Day(6))

    assert unwrap_ok(Ledger(CHALLENGE, log).find_account(ACC_001_OPENING).compute_closing(Day(5))) == make_aed("210.00")
    assert unwrap_ok(Ledger(CHALLENGE, log).find_account(ACC_001_OPENING).compute_closing(Day(6))) == make_aed("285.76")


# KNOWN WEAKNESS (AMB-018): a hold never expires.
# What it reveals: an approved authorization that is never settled keeps its hold, and so keeps reducing the
# available balance, for as long as the ledger runs. Visa's longest authorization-to-clearing time frame is 30
# calendar days (Visa Business News AI13522, effective 13 April 2024), so by Day 32 no network would still honour
# Auth-A, yet this ledger still reserves its AED 200.00.
# The fix: a hold lifetime after which the end of day generates a hold-expiry event that releases the hold.
@pytest.mark.xfail(strict=True, reason="AMB-018: holds never expire, so an unsettled hold is never released")
def test_known_weakness_an_unsettled_hold_never_expires() -> None:
    """AMB-018: Auth-A, never settled, should lapse by Day 32, but its hold still reduces the available balance."""

    processed = unwrap_ok(IncomingStream(build_unsettled_auth_a()).process(replace(CHALLENGE, last_day=Day(32))))
    day_32 = processed.find_report(Day(32))

    assert day_32.available_balances[ACC_001_OPENING.id] == day_32.closing_balances[ACC_001_OPENING.id]
