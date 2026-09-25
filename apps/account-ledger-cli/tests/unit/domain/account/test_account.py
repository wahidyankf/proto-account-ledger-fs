"""The Account aggregate, topic by topic as its class reads: authorizations and settlements (AMB-008 to AMB-013,
AMB-029, AMB-030), reversals (AMB-028, AMB-035), fees (AMB-011, AMB-027, AMB-035), and interest (AMB-005, AMB-023,
AMB-035)."""

from dataclasses import replace

import pytest

from account_ledger.application.report import Capitalized
from account_ledger.application.stream import IncomingStream
from account_ledger.challenge import CHALLENGE
from account_ledger.domain.account.authorizations import Declined, PartiallySettled, Settled
from account_ledger.domain.account.domain_events import EventRejected, FeeCharged, SettlementForcePosted
from account_ledger.domain.account.rejections import (
    AlreadyReversed,
    AlreadyUndone,
    MovedNoMoney,
    ReversesAReversal,
    UnknownTarget,
)
from account_ledger.domain.ledger.ledger import Ledger
from account_ledger.domain.model.config import AccountOpening
from account_ledger.domain.model.events import IncomingEvent, SettlementKind
from account_ledger.domain.model.ids import Day, FeeId, IncomingId, InstalmentId, RefundId
from account_ledger.domain.model.money import AmountIn
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
from support.streams import (
    ACC_001_OPENING,
    ACC_002_OPENING,
    make_authorization,
    make_credit,
    make_debit,
    make_reversal,
    make_settlement,
    take_through,
)
from support.values import make_aed, make_bhd


def test_amb_008_a_future_dated_credit_does_not_count_for_an_authorization() -> None:
    """AMB-008: an event value-dated in the future counts from its value date only."""

    stream = (make_credit("E1", 2, "100.00", value=3), make_authorization("E2", 2, "Auth-A", "50.00"))

    log = unwrap_ok(IncomingStream(stream).process(CHALLENGE)).find_log(Day(2))

    assert list_states(log, "Auth-A") == [Declined(AmountIn(make_aed("50.00")))]


def test_amb_009_a_later_credit_the_same_day_does_not_change_a_decline() -> None:
    """AMB-009: an authorization is decided when it arrives, and the decision is final."""

    stream = (make_authorization("E1", 2, "Auth-A", "50.00"), make_credit("E2", 2, "100.00"))

    log = unwrap_ok(IncomingStream(stream).process(CHALLENGE)).find_log(Day(2))

    assert list_states(log, "Auth-A") == [Declined(AmountIn(make_aed("50.00")))]


def test_amb_010_a_hold_counts_from_its_value_date() -> None:
    """AMB-010: a hold reduces the available balance from its authorization's value date."""

    stream = (make_credit("E1", 1, "100.00"), make_authorization("E2", 2, "Auth-A", "40.00", value=3))

    result = unwrap_ok(IncomingStream(stream).process(CHALLENGE))

    assert result.find_report(Day(2)).available_balances[ACC_001_OPENING.id] == make_aed("100.00")
    assert result.find_report(Day(3)).available_balances[ACC_001_OPENING.id] == make_aed("60.00")


def test_amb_029_a_settlement_against_a_declined_authorization_is_force_posted() -> None:
    """AMB-029: a settlement against a declined authorization posts its debit and releases no hold, as E6 does."""

    later_settlement = make_settlement("E3", 3, "Auth-A", "10.00")
    stream = (make_credit("E1", 1, "20.00"), make_authorization("E2", 2, "Auth-A", "50.00"), later_settlement)

    log = unwrap_ok(IncomingStream(stream).process(CHALLENGE)).find_log(Day(3))

    assert list_settlements(log, "E3") == [SettlementForcePosted(later_settlement, Day(3))]
    assert list_states(log, "Auth-A") == [Declined(AmountIn(make_aed("50.00")))]
    assert unwrap_ok(Ledger(CHALLENGE, log).find_account(ACC_001_OPENING).compute_closing(Day(3))) == make_aed("10.00")


def test_amb_029_a_settlement_after_a_final_one_is_force_posted() -> None:
    """AMB-029: a new settlement against an authorization whose hold a final settlement already released posts its
    debit and releases no hold."""

    second_settlement = make_settlement("E4", 4, "Auth-A", "20.00")

    stream = (
        make_credit("E1", 1, "100.00"),
        make_authorization("E2", 2, "Auth-A", "40.00"),
        make_settlement("E3", 3, "Auth-A", "40.00"),
        second_settlement,
    )

    log = unwrap_ok(IncomingStream(stream).process(CHALLENGE)).find_log(Day(4))

    assert list_settlements(log, "E4") == [SettlementForcePosted(second_settlement, Day(4))]
    assert list_states(log, "Auth-A") == [Settled(AmountIn(make_aed("40.00")))]
    assert unwrap_ok(Ledger(CHALLENGE, log).find_account(ACC_001_OPENING).compute_closing(Day(4))) == make_aed("40.00")


def test_amb_013_a_non_final_settlement_keeps_the_rest_of_the_hold() -> None:
    """AMB-013: a settlement marked as followed by more settlements debits its amount and keeps the rest on hold; a
    final one of the rest then settles the authorization for the settlements' sum and releases what is left."""

    stream = (
        make_credit("E1", 1, "500.00"),
        make_authorization("E2", 1, "Auth-A", "200.00"),
        make_settlement("E3", 2, "Auth-A", "120.00", kind=SettlementKind.PARTIAL),
        make_settlement("E4", 3, "Auth-A", "40.00"),
    )

    result = unwrap_ok(IncomingStream(stream).process(CHALLENGE))

    assert list_states(result.find_log(Day(2)), "Auth-A") == [
        PartiallySettled(AmountIn(make_aed("120.00")), AmountIn(make_aed("80.00")))
    ]
    assert result.find_report(Day(2)).available_balances[ACC_001_OPENING.id] == make_aed("300.00")
    assert list_states(result.find_log(Day(3)), "Auth-A") == [Settled(AmountIn(make_aed("160.00")))]
    assert result.find_report(Day(3)).available_balances[ACC_001_OPENING.id] == make_aed("340.00")


@pytest.mark.parametrize(
    ("partial_amounts", "settled_amount"),
    [
        (("200.00",), "200.00"),
        (("250.00",), "250.00"),
        (("120.00", "80.00"), "200.00"),
        (("120.00", "95.00"), "215.00"),
    ],
)
def test_amb_013_partial_settlements_reaching_the_hold_settle(
    partial_amounts: tuple[str, ...], settled_amount: str
) -> None:
    """AMB-013, tech-docs 001: a partial settlement that reaches the remaining hold leaves nothing to keep, so it
    settles the authorization for the settlements' sum, since a partially settled hold is always above zero."""

    parts = tuple(
        make_settlement(f"E{3 + index}", 2, "Auth-A", amount, kind=SettlementKind.PARTIAL)
        for index, amount in enumerate(partial_amounts)
    )

    stream = (make_credit("E1", 1, "500.00"), make_authorization("E2", 1, "Auth-A", "200.00"), *parts)

    result = unwrap_ok(IncomingStream(stream).process(CHALLENGE))

    assert list_states(result.find_log(Day(2)), "Auth-A") == [Settled(AmountIn(make_aed(settled_amount)))]
    assert (
        result.find_report(Day(2)).available_balances[ACC_001_OPENING.id]
        == result.find_report(Day(2)).closing_balances[ACC_001_OPENING.id]
    )


def test_amb_030_a_settlement_above_its_hold_debits_in_full() -> None:
    """AMB-030: a settlement above its hold posts its whole amount and releases the hold; the balance may go negative,
    and the fee rule then applies as for any negative day."""

    stream = (
        make_credit("E1", 1, "100.00"),
        make_authorization("E2", 1, "Auth-A", "80.00"),
        make_settlement("E3", 2, "Auth-A", "120.00"),
    )

    log = unwrap_ok(IncomingStream(stream).process(CHALLENGE)).find_log(Day(2))

    assert list_states(log, "Auth-A") == [Settled(AmountIn(make_aed("120.00")))]
    assert unwrap_ok(Ledger(CHALLENGE, log).find_account(ACC_001_OPENING).sum_holds(Day(2))) == make_aed("0.00")
    assert list_fee_ids(log) == ["FEE-001-D2@D2"]
    assert unwrap_ok(Ledger(CHALLENGE, log).find_account(ACC_001_OPENING).compute_closing(Day(2))) == make_aed("-45.00")


def test_amb_035_a_reversal_undoes_what_its_target_moved() -> None:
    """AMB-035: E9 reverses E7's 620.00 debit from E9's own value date, Day 2, so Days 2 to 4 restate to 250.00,
    650.00, and 285.00."""

    log = unwrap_ok(IncomingStream(take_through(build_brief_stream(), "E9")).process(CHALLENGE)).find_log(Day(6))

    assert [
        unwrap_ok(Ledger(CHALLENGE, log).find_account(ACC_001_OPENING).compute_closing(Day(day))) for day in (2, 3, 4)
    ] == [
        make_aed("250.00"),
        make_aed("650.00"),
        make_aed("285.00"),
    ]


def test_amb_028_a_second_reversal_of_the_same_event_is_refused() -> None:
    """AMB-028: an event is reversed at most once, so a second reversal of E7 is refused and moves no balance."""

    second_reversal = make_reversal("E12", 3, "E7")

    stream = (
        make_credit("E1", 1, "1000.00"),
        make_debit("E7", 1, "620.00"),
        make_reversal("E9", 2, "E7"),
        second_reversal,
    )

    log = unwrap_ok(IncomingStream(stream).process(CHALLENGE)).find_log(Day(3))

    assert list_entries(log, "E12") == [
        EventRejected(second_reversal, Day(3), AlreadyReversed(IncomingId("E7"), IncomingId("E9")))
    ]
    assert unwrap_ok(Ledger(CHALLENGE, log).find_account(ACC_001_OPENING).compute_closing(Day(3))) == make_aed(
        "1000.00"
    )


def test_amb_028_a_reversal_of_a_reversal_is_refused() -> None:
    """AMB-028: a reversal cannot itself be reversed, since a mistaken one is corrected by a new debit or credit."""

    undoing_reversal = make_reversal("E12", 3, "E9")

    stream = (
        make_credit("E1", 1, "1000.00"),
        make_debit("E7", 1, "620.00"),
        make_reversal("E9", 2, "E7"),
        undoing_reversal,
    )

    log = unwrap_ok(IncomingStream(stream).process(CHALLENGE)).find_log(Day(3))

    assert list_entries(log, "E12") == [EventRejected(undoing_reversal, Day(3), ReversesAReversal(IncomingId("E9")))]
    assert unwrap_ok(Ledger(CHALLENGE, log).find_account(ACC_001_OPENING).compute_closing(Day(3))) == make_aed(
        "1000.00"
    )


def test_amb_035_a_reversal_of_an_unknown_event_is_refused() -> None:
    """AMB-035: a reversal whose target is not in the log is refused and moves no balance."""

    stray_reversal = make_reversal("E12", 2, "E99")
    stream = (make_credit("E1", 1, "100.00"), stray_reversal)

    log = unwrap_ok(IncomingStream(stream).process(CHALLENGE)).find_log(Day(2))

    assert list_entries(log, "E12") == [EventRejected(stray_reversal, Day(2), UnknownTarget(IncomingId("E99")))]
    assert unwrap_ok(Ledger(CHALLENGE, log).find_account(ACC_001_OPENING).compute_closing(Day(2))) == make_aed("100.00")


@pytest.mark.parametrize("target", ["E8", "E3"])
def test_amb_035_a_reversal_of_an_event_that_moved_no_money_is_refused(target: str) -> None:
    """AMB-035: an authorization is approved or declined, never accepted, so neither the declined E8 nor the approved
    E3 moved money to undo."""

    undoing_reversal = make_reversal("E12", 2, target)

    stream = (
        make_credit("E1", 1, "100.00"),
        make_authorization("E3", 1, "Auth-A", "50.00"),
        make_authorization("E8", 1, "Auth-B", "90.00"),
        undoing_reversal,
    )

    log = unwrap_ok(IncomingStream(stream).process(CHALLENGE)).find_log(Day(2))

    assert list_entries(log, "E12") == [EventRejected(undoing_reversal, Day(2), MovedNoMoney(IncomingId(target)))]
    assert unwrap_ok(Ledger(CHALLENGE, log).find_account(ACC_001_OPENING).compute_closing(Day(2))) == make_aed("100.00")


def test_amb_035_reversing_a_credit_in_instalments_undoes_every_instalment() -> None:
    """AMB-035: E10 posts nothing itself, so its reversal undoes the three instalments it generated."""

    stream = (
        make_credit("E10", 5, "10.000", account="ACC-002", instalments=3),
        make_reversal("E11", 5, "E10", account="ACC-002"),
    )

    log = unwrap_ok(IncomingStream(stream).process(CHALLENGE)).find_log(Day(5))

    assert unwrap_ok(Ledger(CHALLENGE, log).find_account(ACC_002_OPENING).compute_closing(Day(5))) == make_bhd("0.000")


WEEK = replace(CHALLENGE, last_day=Day(7))


INSTALMENTS = (make_credit("E10", 5, "10.000", account="ACC-002", instalments=3),)


UNDONE = {
    "part": (
        (
            *INSTALMENTS,
            make_reversal("E11", 5, "E10", account="ACC-002"),
            make_reversal("E12", 5, "E10-1", account="ACC-002"),
        ),
        ACC_002_OPENING,
        Day(5),
        AlreadyUndone(InstalmentId(IncomingId("E10"), 1), IncomingId("E11")),
    ),
    "whole": (
        (
            *INSTALMENTS,
            make_reversal("E11", 5, "E10-1", account="ACC-002"),
            make_reversal("E12", 5, "E10", account="ACC-002"),
        ),
        ACC_002_OPENING,
        Day(5),
        AlreadyUndone(InstalmentId(IncomingId("E10"), 1), IncomingId("E11")),
    ),
    "refunded-fee": (
        (*build_brief_stream(), make_reversal("E12", 7, "FEE-001-D2@D5")),
        ACC_001_OPENING,
        Day(7),
        AlreadyUndone(
            FeeId(ACC_001_OPENING.id, Day(2), Day(5)),
            RefundId(ACC_001_OPENING.id, Day(2), Day(6)),
        ),
    ),
}


@pytest.mark.parametrize(("stream", "account", "day", "reason"), UNDONE.values(), ids=UNDONE.keys())
def test_amb_035_money_already_undone_cannot_be_undone_again(
    stream: tuple[IncomingEvent, ...], account: AccountOpening, day: Day, reason: AlreadyUndone
) -> None:
    """AMB-035: each event's money is undone at most once, whichever event undoes it: an instalment of a reversed
    credit, a credit one of whose instalments is reversed, or a fee already refunded."""

    log = unwrap_ok(IncomingStream(stream).process(WEEK)).find_log(day)
    baseline_log = unwrap_ok(IncomingStream(stream[:-1]).process(WEEK)).find_log(day)

    assert list_entries(log, "E12") == [EventRejected(stream[-1], day, reason)]
    assert Ledger(CHALLENGE, log).find_account(account).compute_closing(day) == Ledger(
        CHALLENGE, baseline_log
    ).find_account(account).compute_closing(day)


def test_amb_035_a_reversed_settlement_leaves_its_authorization_settled() -> None:
    """AMB-035: a reversal undoes only what its target moved, so reversing a settlement credits its debit back and
    leaves its authorization settled, with no hold restored."""

    stream = (
        make_credit("E1", 1, "100.00"),
        make_authorization("E2", 1, "Auth-A", "50.00"),
        make_settlement("E3", 2, "Auth-A", "30.00"),
        make_reversal("E4", 3, "E3", value=2),
    )

    log = unwrap_ok(IncomingStream(stream).process(CHALLENGE)).find_log(Day(3))

    assert list_states(log, "Auth-A") == [Settled(AmountIn(make_aed("30.00")))]
    assert unwrap_ok(Ledger(CHALLENGE, log).find_account(ACC_001_OPENING).sum_holds(Day(3))) == make_aed("0.00")
    assert unwrap_ok(Ledger(CHALLENGE, log).find_account(ACC_001_OPENING).compute_closing(Day(3))) == make_aed("100.00")


def test_amb_035_a_reversed_instalment_stays_reversed() -> None:
    """AMB-035: an instalment is generated when its credit is processed, not at a close, so once reversed it stays
    reversed at every later close."""

    stream = (
        make_credit("E1", 1, "10.000", account="ACC-002", instalments=3),
        make_reversal("E2", 2, "E1-2", account="ACC-002", value=1),
    )

    result = unwrap_ok(IncomingStream(stream).process(CHALLENGE))

    assert [
        unwrap_ok(Ledger(CHALLENGE, result.find_log(Day(day))).find_account(ACC_002_OPENING).compute_closing(Day(1)))
        for day in (1, 2, 6)
    ] == [
        make_bhd("10.000"),
        make_bhd("6.667"),
        make_bhd("6.667"),
    ]
    assert [
        entry.event.id for entry in result.find_log(Day(6)).entries if isinstance(entry.event.id, InstalmentId)
    ] == [InstalmentId(IncomingId("E1"), number) for number in (1, 2, 3)]


def test_amb_011_a_day_still_negative_is_not_charged_again() -> None:
    """AMB-002, AMB-011: a fee is charged "once per day per account", so a day that has its fee is not charged again,
    however many closes find it negative."""

    log = unwrap_ok(IncomingStream((make_debit("E1", 1, "10.00"),)).process(CHALLENGE)).find_log(Day(2))

    assert list_fee_ids(log) == ["FEE-001-D1@D1", "FEE-001-D2@D2"]


def test_amb_011_a_fee_counts_in_the_closings_after_it() -> None:
    """AMB-011: a fee is an event like any other, so the Day 1 fee, value-dated Day 2, takes Day 2 from 10.00 to
    −15.00, and Day 2 is charged too."""

    stream = (make_debit("E1", 2, "20.00", value=1), make_credit("E2", 2, "30.00"))

    log = unwrap_ok(IncomingStream(stream).process(CHALLENGE)).find_log(Day(2))

    assert list_fee_ids(log) == ["FEE-001-D1@D2", "FEE-001-D2@D2"]


def test_amb_027_a_bhd_account_is_charged_bhd_2_560() -> None:
    """AMB-027: the fee is AED 25.00 converted at the configured rate and rounded half-even to BHD's three places, so
    ACC-002 is charged FEE-002-D1@D1 and closes Day 1 at −3.560."""

    stream = (make_debit("E1", 1, "1.000", account="ACC-002"),)
    log = unwrap_ok(IncomingStream(stream).process(CHALLENGE)).find_log(Day(1))

    fees = [entry.event for entry in log.entries if isinstance(entry, FeeCharged)]
    assert [fee.amount for fee in fees] == [AmountIn(make_bhd("2.560"))]
    assert list_fee_ids(log) == ["FEE-002-D1@D1"]
    assert unwrap_ok(Ledger(CHALLENGE, log).find_account(ACC_002_OPENING).compute_closing(Day(1))) == make_bhd("-3.560")


def test_amb_035_a_fee_reversed_on_a_negative_day_is_charged_again() -> None:
    """AMB-035: a fee reversed while its day is still negative is charged again, under a generated ID for today."""

    stream = (make_debit("E1", 1, "10.00"), make_reversal("E2", 2, "FEE-001-D1@D1"))

    log = unwrap_ok(IncomingStream(stream).process(CHALLENGE)).find_log(Day(2))

    assert list_fee_ids(log) == ["FEE-001-D1@D1", "FEE-001-D1@D2", "FEE-001-D2@D2"]


def test_amb_035_a_reversed_refund_puts_its_fee_back_in_force() -> None:
    """AMB-035: a refund may itself be reversed, which puts its fee back in force for the next close to judge again;
    Day 2 still closes at 250.00, so Day 7's close refunds FEE-001-D2@D5 once more."""

    week = replace(CHALLENGE, last_day=Day(7))
    stream = (*build_brief_stream(), make_reversal("E12", 7, "REFUND-001-D2@D6"))

    log = unwrap_ok(IncomingStream(stream).process(week)).find_log(Day(7))

    assert list_refund_ids(log) == ["REFUND-001-D2@D6", "REFUND-001-D4@D6", "REFUND-001-D5@D6", "REFUND-001-D2@D7"]


def test_amb_005_interest_accrues_on_a_positive_closing() -> None:
    """AMB-005: each day's accrual is an event generated at that day's close, on the closing ledger balance as known
    then."""

    log = unwrap_ok(IncomingStream((make_credit("E1", 1, "1000.00"),)).process(CHALLENGE)).find_log(Day(1))

    assert list_interest_amounts(log) == [("INT-001-D1@D1", make_aed("0.40"))]


def test_amb_005_a_changed_closing_adjusts_its_interest() -> None:
    """AMB-005: a late event that changes a past day's closing generates an adjustment for that day, value-dated the
    day it is recognised and naming the day it is for."""

    stream = (make_credit("E1", 1, "1000.00"), make_debit("E2", 2, "500.00", value=1))

    log = unwrap_ok(IncomingStream(stream).process(CHALLENGE)).find_log(Day(2))

    assert list_interest_amounts(log) == [
        ("INT-001-D1@D1", make_aed("0.40")),
        ("INT-001-D1@D2", make_aed("-0.20")),
        ("INT-001-D2@D2", make_aed("0.20")),
    ]


def test_amb_023_a_days_interest_never_counts_its_own_capitalization() -> None:
    """AMB-023: a day closes in three steps, interest before capitalization, so re-evaluating a capitalization day
    reads its interest on the balance before the capitalization, and AED 50,000.00's Day 1 interest stays 20.00."""

    config = replace(CHALLENGE, last_day=Day(2), capitalization_days=frozenset({Day(1)}))

    log = unwrap_ok(IncomingStream((make_credit("E1", 1, "50000.00"),)).process(config)).find_log(Day(2))

    assert list_interest_amounts(log) == [("INT-001-D1@D1", make_aed("20.00")), ("INT-001-D2@D2", make_aed("20.01"))]


def test_amb_035_a_reversed_interest_event_is_generated_again() -> None:
    """AMB-035: a reversed interest event drops out of what was generated for its day, so the next close generates the
    day's interest again, as an adjustment under a generated ID for that close (tech-docs 002)."""

    stream = (make_credit("E1", 1, "1000.00"), make_reversal("E2", 2, "INT-001-D1@D1"))

    log = unwrap_ok(IncomingStream(stream).process(CHALLENGE)).find_log(Day(2))

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

    result = unwrap_ok(IncomingStream(stream).process(config))

    assert list_capitalization_amounts(result.find_log(Day(2))) == [
        ("CAP-001@D1", make_aed("0.40")),
        ("CAP-001@D2", make_aed("0.80")),
    ]
    assert [row.days for row in result.find_report(Day(2)).end_of_day if isinstance(row, Capitalized)] == [
        (Day(1), Day(2))
    ]


def test_amb_035_a_capitalization_reversed_on_its_own_day_leaves_that_days_interest() -> None:
    """AMB-035, AMB-023: a capitalization reversed with its own value date no longer counts in that day's closing, so
    that day's interest base takes nothing more out, and AED 50,000.00's Day 1 interest stays 20.00."""

    config = replace(CHALLENGE, last_day=Day(2), capitalization_days=frozenset({Day(1), Day(2)}))
    stream = (make_credit("E1", 1, "50000.00"), make_reversal("E2", 2, "CAP-001@D1", value=1))

    log = unwrap_ok(IncomingStream(stream).process(config)).find_log(Day(2))

    assert list_interest_amounts(log) == [("INT-001-D1@D1", make_aed("20.00")), ("INT-001-D2@D2", make_aed("20.00"))]
