"""The driver: opening reports, days closing as booked days advance, empty and late days, and the window's end."""

from account_ledger.domain.model.config import CHALLENGE
from account_ledger.domain.model.ids import AccountId, Day, IncomingId
from account_ledger.domain.replay import replay
from support.brief_stream import brief_stream
from support.states import entries_for
from support.streams import credit, interest_amounts
from support.values import aed, bhd


def test_an_empty_stream_reports_the_opening_balances_for_day_0_to_6() -> None:
    result = replay((), CHALLENGE)

    assert [report.day for report in result.reports] == [Day(n) for n in range(7)]
    for report in result.reports:
        assert report.closing == {AccountId("ACC-001"): aed("0.00"), AccountId("ACC-002"): bhd("0.000")}
    assert result.log_at(Day(6)) == ()


def test_amb_015_a_late_event_is_processed_on_the_open_day() -> None:
    """AMB-015: E10, booked Day 5 but listed after E9, arrives once Day 5 has closed and is processed on Day 6."""
    result = replay(brief_stream(), CHALLENGE)

    assert IncomingId("E10") not in [entry.event.id for entry in result.log_at(Day(5))]
    e10 = [entry for entry in result.log_at(Day(6)) if entry.event.id == IncomingId("E10")]
    assert [entry.processed_day for entry in e10] == [Day(6)]


def test_amb_001_a_day_without_events_still_closes() -> None:
    """AMB-001: an event booked on a later day closes every day before it, those with no events of their own
    included, so each still accrues its interest; the event is processed on its own booked day."""
    result = replay((credit("E1", 1, "1000.00"), credit("E2", 4, "10.00")), CHALLENGE)

    assert [marker for marker, _ in interest_amounts(result.log_at(Day(3)))] == [
        "INT-001-D1@D1",
        "INT-001-D2@D2",
        "INT-001-D3@D3",
    ]
    assert [entry.processed_day for entry in entries_for(result.log_at(Day(4)), "E2")] == [Day(4)]


def test_amb_001_an_event_booked_after_the_window_reaches_no_day() -> None:
    """AMB-001: no day closes after the window's last, so an event booked after it reaches no day's log or report;
    the stream reader refuses such a day before it gets here."""
    result = replay((credit("E1", 1, "100.00"), credit("E2", 9, "50.00")), CHALLENGE)

    assert [report.day for report in result.reports] == [Day(n) for n in range(7)]
    assert entries_for(result.log_at(Day(6)), "E2") == []
