"""Reversals: which are refused (AMB-028, AMB-035), and what an accepted one undoes (AMB-035)."""

from dataclasses import replace

import pytest

from account_ledger.domain.authorizations import Settled, sum_holds
from account_ledger.domain.balances import compute_closing, compute_closing_of
from account_ledger.domain.model.config import CHALLENGE, AnyAccount
from account_ledger.domain.model.event_log import (
    AlreadyReversed,
    AlreadyUndone,
    MovedNoMoney,
    Rejected,
    ReversesAReversal,
    UnknownTarget,
)
from account_ledger.domain.model.events import IncomingEvent
from account_ledger.domain.model.ids import Day, FeeId, IncomingId, InstalmentId, RefundId
from account_ledger.domain.model.money import Amount
from account_ledger.domain.stream_processing import process_stream
from support.brief_stream import build_brief_stream
from support.results import unwrap_ok
from support.states import list_entries, list_states
from support.streams import (
    ACC_001,
    ACC_002,
    make_authorization,
    make_credit,
    make_debit,
    make_reversal,
    make_settlement,
    take_through,
)
from support.values import make_aed, make_bhd


def test_amb_035_a_reversal_undoes_what_its_target_moved() -> None:
    """AMB-035: E9 reverses E7's 620.00 debit from E9's own value day, Day 2, so Days 2 to 4 restate to 250.00,
    650.00, and 285.00."""
    log = unwrap_ok(process_stream(take_through(build_brief_stream(), "E9"), CHALLENGE)).find_log(Day(6))

    assert [unwrap_ok(compute_closing(log, ACC_001, Day(day))) for day in (2, 3, 4)] == [
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

    log = unwrap_ok(process_stream(stream, CHALLENGE)).find_log(Day(3))

    assert list_entries(log, "E12") == [
        Rejected(second_reversal, Day(3), AlreadyReversed(IncomingId("E7"), IncomingId("E9")))
    ]
    assert unwrap_ok(compute_closing(log, ACC_001, Day(3))) == make_aed("1000.00")


def test_amb_028_a_reversal_of_a_reversal_is_refused() -> None:
    """AMB-028: a reversal cannot itself be reversed, since a mistaken one is corrected by a new debit or credit."""
    undoing_reversal = make_reversal("E12", 3, "E9")
    stream = (
        make_credit("E1", 1, "1000.00"),
        make_debit("E7", 1, "620.00"),
        make_reversal("E9", 2, "E7"),
        undoing_reversal,
    )

    log = unwrap_ok(process_stream(stream, CHALLENGE)).find_log(Day(3))

    assert list_entries(log, "E12") == [Rejected(undoing_reversal, Day(3), ReversesAReversal(IncomingId("E9")))]
    assert unwrap_ok(compute_closing(log, ACC_001, Day(3))) == make_aed("1000.00")


def test_amb_035_a_reversal_of_an_unknown_event_is_refused() -> None:
    """AMB-035: a reversal whose target is not in the log is refused and moves no balance."""
    stray_reversal = make_reversal("E12", 2, "E99")
    stream = (make_credit("E1", 1, "100.00"), stray_reversal)

    log = unwrap_ok(process_stream(stream, CHALLENGE)).find_log(Day(2))

    assert list_entries(log, "E12") == [Rejected(stray_reversal, Day(2), UnknownTarget(IncomingId("E99")))]
    assert unwrap_ok(compute_closing(log, ACC_001, Day(2))) == make_aed("100.00")


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

    log = unwrap_ok(process_stream(stream, CHALLENGE)).find_log(Day(2))

    assert list_entries(log, "E12") == [Rejected(undoing_reversal, Day(2), MovedNoMoney(IncomingId(target)))]
    assert unwrap_ok(compute_closing(log, ACC_001, Day(2))) == make_aed("100.00")


def test_amb_035_reversing_a_credit_in_instalments_undoes_every_instalment() -> None:
    """AMB-035: E10 posts nothing itself, so its reversal undoes the three instalments it fired."""
    stream = (
        make_credit("E10", 5, "10.000", account="ACC-002", instalments=3),
        make_reversal("E11", 5, "E10", account="ACC-002"),
    )

    log = unwrap_ok(process_stream(stream, CHALLENGE)).find_log(Day(5))

    assert unwrap_ok(compute_closing(log, ACC_002, Day(5))) == make_bhd("0.000")


WEEK = replace(CHALLENGE, last_day=Day(7))
INSTALMENTS = (make_credit("E10", 5, "10.000", account="ACC-002", instalments=3),)
UNDONE = {
    "part": (
        (
            *INSTALMENTS,
            make_reversal("E11", 5, "E10", account="ACC-002"),
            make_reversal("E12", 5, "E10-1", account="ACC-002"),
        ),
        ACC_002,
        Day(5),
        AlreadyUndone(InstalmentId(IncomingId("E10"), 1), IncomingId("E11")),
    ),
    "whole": (
        (
            *INSTALMENTS,
            make_reversal("E11", 5, "E10-1", account="ACC-002"),
            make_reversal("E12", 5, "E10", account="ACC-002"),
        ),
        ACC_002,
        Day(5),
        AlreadyUndone(InstalmentId(IncomingId("E10"), 1), IncomingId("E11")),
    ),
    "refunded-fee": (
        (*build_brief_stream(), make_reversal("E12", 7, "FEE-001-D2@D5")),
        ACC_001,
        Day(7),
        AlreadyUndone(
            FeeId(ACC_001.id, Day(2), Day(5)),
            RefundId(ACC_001.id, Day(2), Day(6)),
        ),
    ),
}


@pytest.mark.parametrize(("stream", "account", "day", "reason"), UNDONE.values(), ids=UNDONE.keys())
def test_amb_035_money_already_undone_cannot_be_undone_again(
    stream: tuple[IncomingEvent, ...], account: AnyAccount, day: Day, reason: AlreadyUndone
) -> None:
    """AMB-035: each event's money is undone at most once, whichever event undoes it: an instalment of a reversed
    credit, a credit one of whose instalments is reversed, or a fee already refunded."""
    log = unwrap_ok(process_stream(stream, WEEK)).find_log(day)
    baseline_log = unwrap_ok(process_stream(stream[:-1], WEEK)).find_log(day)

    assert list_entries(log, "E12") == [Rejected(stream[-1], day, reason)]
    assert compute_closing_of(log, account, day) == compute_closing_of(baseline_log, account, day)


def test_amb_035_a_reversed_settlement_leaves_its_authorization_settled() -> None:
    """AMB-035: a reversal undoes only what its target moved, so reversing a settlement credits its debit back and
    leaves its authorization settled, with no hold restored."""
    stream = (
        make_credit("E1", 1, "100.00"),
        make_authorization("E2", 1, "Auth-A", "50.00"),
        make_settlement("E3", 2, "Auth-A", "30.00"),
        make_reversal("E4", 3, "E3", value=2),
    )

    log = unwrap_ok(process_stream(stream, CHALLENGE)).find_log(Day(3))

    assert list_states(log, "Auth-A") == [Settled(Amount(make_aed("30.00")))]
    assert unwrap_ok(sum_holds(log, ACC_001, Day(3))) == make_aed("0.00")
    assert unwrap_ok(compute_closing(log, ACC_001, Day(3))) == make_aed("100.00")


def test_amb_035_a_reversed_instalment_stays_reversed() -> None:
    """AMB-035: an instalment is fired when its credit is processed, not at a close, so once reversed it stays
    reversed at every later close."""
    stream = (
        make_credit("E1", 1, "10.000", account="ACC-002", instalments=3),
        make_reversal("E2", 2, "E1-2", account="ACC-002", value=1),
    )

    result = unwrap_ok(process_stream(stream, CHALLENGE))

    assert [unwrap_ok(compute_closing(result.find_log(Day(day)), ACC_002, Day(1))) for day in (1, 2, 6)] == [
        make_bhd("10.000"),
        make_bhd("6.667"),
        make_bhd("6.667"),
    ]
    assert [entry.event.id for entry in result.find_log(Day(6)) if isinstance(entry.event.id, InstalmentId)] == [
        InstalmentId(IncomingId("E1"), number) for number in (1, 2, 3)
    ]
