"""Reversals: which are refused (AMB-028, AMB-035), and what an accepted one undoes (AMB-035)."""

from dataclasses import replace

import pytest

from account_ledger.domain.authorizations import Settled
from account_ledger.domain.balances import closing, closing_of, holds
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
from account_ledger.domain.replay import replay
from support.brief_stream import brief_stream
from support.states import entries_for, state_of
from support.streams import ACC_001, ACC_002, authorization, credit, debit, reversal, settlement, through
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


def test_amb_035_a_reversed_settlement_leaves_its_authorization_settled() -> None:
    """AMB-035: a reversal undoes only what its target moved, so reversing a settlement credits its debit back and
    leaves its authorization settled, with no hold restored."""
    stream = (
        credit("E1", 1, "100.00"),
        authorization("E2", 1, "Auth-A", "50.00"),
        settlement("E3", 2, "Auth-A", "30.00"),
        reversal("E4", 3, "E3", value=2),
    )

    log = replay(stream, CHALLENGE).log_at(Day(3))

    assert state_of(log, "Auth-A") == [Settled(Amount(aed("30.00")))]
    assert holds(log, ACC_001, Day(3)) == aed("0.00")
    assert closing(log, ACC_001, Day(3)) == aed("100.00")


def test_amb_035_a_reversed_instalment_stays_reversed() -> None:
    """AMB-035: an instalment is fired when its credit is processed, not at a close, so once reversed it stays
    reversed at every later close."""
    stream = (
        credit("E1", 1, "10.000", account="ACC-002", instalments=3),
        reversal("E2", 2, "E1-2", account="ACC-002", value=1),
    )

    result = replay(stream, CHALLENGE)

    assert [closing(result.log_at(Day(day)), ACC_002, Day(1)) for day in (1, 2, 6)] == [
        bhd("10.000"),
        bhd("6.667"),
        bhd("6.667"),
    ]
    assert [entry.event.id for entry in result.log_at(Day(6)) if isinstance(entry.event.id, InstalmentId)] == [
        InstalmentId(IncomingId("E1"), n) for n in (1, 2, 3)
    ]
