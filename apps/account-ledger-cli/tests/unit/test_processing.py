"""Processing an incoming event: reversals (AMB-028, AMB-035) and idempotency (AMB-034)."""

from dataclasses import replace

import pytest

from account_ledger.balances import closing, closing_of
from account_ledger.config import CHALLENGE, AnyAccount
from account_ledger.events import IncomingEvent
from account_ledger.ids import Day, FeeId, IncomingId, InstalmentId, RefundId
from account_ledger.log import (
    Accepted,
    AlreadyReversed,
    AlreadyUndone,
    Duplicate,
    IdReused,
    MovedNoMoney,
    Rejected,
    ReversesAReversal,
    UnknownTarget,
)
from account_ledger.replay import replay
from support.brief_stream import brief_stream
from support.states import entries_for
from support.streams import ACC_001, ACC_002, authorization, credit, debit, reversal, through
from support.values import aed, bhd


def test_amb_035_a_reversal_undoes_what_its_target_moved() -> None:
    """AMB-035: E9 reverses E7's 620.00 debit from E9's own value day, Day 2, so Days 2 to 4 restate to 250.00,
    650.00, and 285.00."""
    log = replay(through(brief_stream(), "E9"), CHALLENGE).log_at(Day(6))

    assert [closing(log, ACC_001, Day(day)) for day in (2, 3, 4)] == [aed("250.00"), aed("650.00"), aed("285.00")]


def test_amb_028_a_second_reversal_of_the_same_event_is_refused() -> None:
    """AMB-028: an event is reversed at most once, so a second reversal of E7 is refused and moves no balance."""
    second = reversal("E12", 3, "E7")
    stream = (credit("E1", 1, "1000.00"), debit("E7", 1, "620.00"), reversal("E9", 2, "E7"), second)

    log = replay(stream, CHALLENGE).log_at(Day(3))

    assert entries_for(log, "E12") == [Rejected(second, Day(3), AlreadyReversed(IncomingId("E7"), IncomingId("E9")))]
    assert closing(log, ACC_001, Day(3)) == aed("1000.00")


def test_amb_028_a_reversal_of_a_reversal_is_refused() -> None:
    """AMB-028: a reversal cannot itself be reversed, since a mistaken one is corrected by a new debit or credit."""
    undo = reversal("E12", 3, "E9")
    stream = (credit("E1", 1, "1000.00"), debit("E7", 1, "620.00"), reversal("E9", 2, "E7"), undo)

    log = replay(stream, CHALLENGE).log_at(Day(3))

    assert entries_for(log, "E12") == [Rejected(undo, Day(3), ReversesAReversal(IncomingId("E9")))]
    assert closing(log, ACC_001, Day(3)) == aed("1000.00")


def test_amb_035_a_reversal_of_an_unknown_event_is_refused() -> None:
    """AMB-035: a reversal whose target is not in the log is refused and moves no balance."""
    stray = reversal("E12", 2, "E99")
    stream = (credit("E1", 1, "100.00"), stray)

    log = replay(stream, CHALLENGE).log_at(Day(2))

    assert entries_for(log, "E12") == [Rejected(stray, Day(2), UnknownTarget(IncomingId("E99")))]
    assert closing(log, ACC_001, Day(2)) == aed("100.00")


@pytest.mark.parametrize("target", ["E8", "E3"])
def test_amb_035_a_reversal_of_an_event_that_moved_no_money_is_refused(target: str) -> None:
    """AMB-035: an authorization is approved or declined, never accepted, so neither the declined E8 nor the approved
    E3 moved money to undo."""
    undo = reversal("E12", 2, target)
    stream = (
        credit("E1", 1, "100.00"),
        authorization("E3", 1, "Auth-A", "50.00"),
        authorization("E8", 1, "Auth-B", "90.00"),
        undo,
    )

    log = replay(stream, CHALLENGE).log_at(Day(2))

    assert entries_for(log, "E12") == [Rejected(undo, Day(2), MovedNoMoney(IncomingId(target)))]
    assert closing(log, ACC_001, Day(2)) == aed("100.00")


def test_amb_035_reversing_a_credit_in_instalments_undoes_every_instalment() -> None:
    """AMB-035: E10 posts nothing itself, so its reversal undoes the three instalments it fired."""
    stream = (
        credit("E10", 5, "10.000", account="ACC-002", instalments=3),
        reversal("E11", 5, "E10", account="ACC-002"),
    )

    log = replay(stream, CHALLENGE).log_at(Day(5))

    assert closing(log, ACC_002, Day(5)) == bhd("0.000")


WEEK = replace(CHALLENGE, last_day=Day(7))
INSTALMENTS = (credit("E10", 5, "10.000", account="ACC-002", instalments=3),)
UNDONE = {
    "part": (
        (*INSTALMENTS, reversal("E11", 5, "E10", account="ACC-002"), reversal("E12", 5, "E10-1", account="ACC-002")),
        ACC_002,
        Day(5),
        AlreadyUndone(InstalmentId(IncomingId("E10"), 1), IncomingId("E11")),
    ),
    "whole": (
        (*INSTALMENTS, reversal("E11", 5, "E10-1", account="ACC-002"), reversal("E12", 5, "E10", account="ACC-002")),
        ACC_002,
        Day(5),
        AlreadyUndone(InstalmentId(IncomingId("E10"), 1), IncomingId("E11")),
    ),
    "refunded-fee": (
        (*brief_stream(), reversal("E12", 7, "FEE-001-D2@D5")),
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
    log = replay(stream, WEEK).log_at(day)
    without = replay(stream[:-1], WEEK).log_at(day)

    assert entries_for(log, "E12") == [Rejected(stream[-1], day, reason)]
    assert closing_of(log, account, day) == closing_of(without, account, day)


def test_amb_034_a_repeated_event_is_logged_as_a_duplicate_with_no_effect() -> None:
    """AMB-034: the event ID is the idempotency key, so E1 delivered twice with identical content is logged again as a
    duplicate and credits once."""
    e1 = credit("E1", 1, "100.00")

    log = replay((e1, e1), CHALLENGE).log_at(Day(1))

    assert entries_for(log, "E1") == [Accepted(e1, Day(1)), Duplicate(e1, Day(1))]
    assert closing(log, ACC_001, Day(1)) == aed("100.00")


def test_amb_034_a_reused_id_with_different_content_is_refused() -> None:
    """AMB-034: a second E1 that differs from the first in any field is refused and moves no balance."""
    first, reused = credit("E1", 1, "100.00"), credit("E1", 1, "90.00")

    log = replay((first, reused), CHALLENGE).log_at(Day(1))

    assert entries_for(log, "E1") == [Accepted(first, Day(1)), Rejected(reused, Day(1), IdReused())]
    assert closing(log, ACC_001, Day(1)) == aed("100.00")
