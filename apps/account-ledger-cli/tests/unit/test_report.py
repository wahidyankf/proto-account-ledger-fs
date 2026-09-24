"""The day report as data: restated closings (AMB-022), authorizations (AMB-019), errors (AMB-014), and rows."""

import pytest

from account_ledger.authorizations import Approved, AuthorizationState, Declined, Settled
from account_ledger.config import CHALLENGE
from account_ledger.events import IncomingEvent
from account_ledger.ids import AccountId, AuthorizationId, Day, text
from account_ledger.money import Amount
from account_ledger.replay import replay
from account_ledger.report import DayReport, Fired, NothingFired, Restatement
from support.brief_stream import brief_stream
from support.streams import ACC_001, ACC_002, authorization, credit, debit, reversal
from support.values import aed, bhd


def test_amb_022_a_day_restates_each_earlier_closing_it_changed() -> None:
    """AMB-022: when a backdated event changes an earlier closing, that day's report adds a restated closing for each
    earlier day it changed; an account whose closing for that day did not change shows none."""
    result = replay(brief_stream(), CHALLENGE)

    assert result.report(Day(5)).restated == (
        Restatement(Day(2), {ACC_001.id: aed("-370.00"), ACC_002.id: None}),
        Restatement(Day(3), {ACC_001.id: aed("30.00"), ACC_002.id: None}),
        Restatement(Day(4), {ACC_001.id: aed("-335.00"), ACC_002.id: None}),
    )
    assert result.report(Day(6)).restated == (
        Restatement(Day(2), {ACC_001.id: aed("250.00"), ACC_002.id: None}),
        Restatement(Day(3), {ACC_001.id: aed("650.00"), ACC_002.id: None}),
        Restatement(Day(4), {ACC_001.id: aed("285.00"), ACC_002.id: None}),
        Restatement(Day(5), {ACC_001.id: aed("210.00"), ACC_002.id: bhd("10.000")}),
    )


def test_amb_019_every_known_authorization_is_listed_with_its_state() -> None:
    """AMB-019, AMB-025: every authorization known by the end of the day is listed with its state then, in the order
    first seen; a declined authorization is a state, printed with the others."""
    result = replay(brief_stream(), CHALLENGE)

    def listed(day: int) -> list[tuple[AuthorizationId, AuthorizationState]]:
        return [(record.authorization.authorization, record.state) for record in result.report(Day(day)).authorizations]

    assert listed(1) == []
    assert listed(2) == [(AuthorizationId("Auth-A"), Approved(Amount(aed("200.00"))))]
    assert listed(5) == [
        (AuthorizationId("Auth-A"), Settled(Amount(aed("185.00")))),
        (AuthorizationId("Auth-B"), Declined(Amount(aed("90.00")))),
    ]


REFUSALS = {
    "IdReused": (
        (credit("E1", 1, "100.00"), credit("E1", 1, "90.00")),
        ACC_001.id,
        "E1 refused: ID already used with different content",
    ),
    "AlreadyReversed": (
        (credit("E1", 1, "1000.00"), debit("E7", 1, "620.00"), reversal("E9", 1, "E7"), reversal("E12", 1, "E7")),
        ACC_001.id,
        "E12 refused: E7 is already reversed by E9",
    ),
    "ReversesAReversal": (
        (credit("E1", 1, "1000.00"), debit("E7", 1, "620.00"), reversal("E9", 1, "E7"), reversal("E12", 1, "E9")),
        ACC_001.id,
        "E12 refused: E9 is a reversal",
    ),
    "UnknownTarget": (
        (credit("E1", 1, "100.00"), reversal("E12", 1, "E99")),
        ACC_001.id,
        "E12 refused: E99 is not in the log",
    ),
    "MovedNoMoney": (
        (credit("E1", 1, "100.00"), authorization("E8", 1, "Auth-B", "900.00"), reversal("E12", 1, "E8")),
        ACC_001.id,
        "E12 refused: E8 moved no money",
    ),
    "AlreadyUndone": (
        (
            credit("E10", 1, "10.000", account="ACC-002", instalments=3),
            reversal("E11", 1, "E10", account="ACC-002"),
            reversal("E12", 1, "E10-1", account="ACC-002"),
        ),
        ACC_002.id,
        "E12 refused: E10-1 is already undone by E11",
    ),
}


@pytest.mark.parametrize(("stream", "account", "text"), REFUSALS.values(), ids=REFUSALS.keys())
def test_amb_014_a_rejected_event_prints_as_that_days_error(
    stream: tuple[IncomingEvent, ...], account: AccountId, text: str
) -> None:
    """AMB-014: every event is recorded with its outcome, and a refused one prints as that day's error, by account,
    in the text tech-docs 001 fixes (D22)."""
    errors = replay(stream, CHALLENGE).report(Day(1)).errors

    assert errors == {each.id: (text,) if each.id == account else () for each in CHALLENGE.accounts}


def rows(day_report: DayReport) -> list[tuple[int, str, tuple[str, ...]]]:
    """Each end-of-day row as its step, its marker or note, and its accounts."""
    found: list[tuple[int, str, tuple[str, ...]]] = []
    for row in day_report.end_of_day:
        match row:
            case Fired(step=step, event=event):
                found.append((step.value, text(event.id), (event.account.value,)))
            case NothingFired(step=step, accounts=accounts, note=note):
                found.append((step.value, note.value, tuple(account.value for account in accounts)))
    return found


BOTH = ("ACC-001", "ACC-002")


def test_amb_033_a_step_that_fires_nothing_reports_its_row() -> None:
    """AMB-033: every end-of-day step is printed with the events it fires, and a step that fires nothing prints a row
    saying so (tech-docs 002)."""
    result = replay(brief_stream(), CHALLENGE)

    assert rows(result.report(Day(1))) == [
        (1, "no fee assessed or refunded", BOTH),
        (2, "INT-001-D1@D1", ("ACC-001",)),
        (2, "no interest accrued", ("ACC-002",)),
    ]
    assert rows(result.report(Day(5)))[3:] == [
        (2, "INT-001-D2@D5", ("ACC-001",)),
        (2, "INT-001-D3@D5", ("ACC-001",)),
        (2, "INT-001-D4@D5", ("ACC-001",)),
        (2, "no interest accrued", ("ACC-001",)),
        (2, "no interest accrued", ("ACC-002",)),
    ]
    assert rows(result.report(Day(6)))[:4] == [
        (1, "REFUND-001-D2@D6", ("ACC-001",)),
        (1, "REFUND-001-D4@D6", ("ACC-001",)),
        (1, "REFUND-001-D5@D6", ("ACC-001",)),
        (1, "no new fee assessed", BOTH),
    ]
    assert rows(result.report(Day(6)))[-2:] == [(3, "CAP-001@D6", ("ACC-001",)), (3, "CAP-002@D6", ("ACC-002",))]
    only_aed = replay((credit("E1", 1, "100.00"),), CHALLENGE).report(Day(6))
    assert rows(only_aed)[-2:] == [(3, "CAP-001@D6", ("ACC-001",)), (3, "no interest capitalized", ("ACC-002",))]
