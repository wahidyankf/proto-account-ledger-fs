"""Processing a stream: opening reports, days closing as booked days advance, empty and late days, the window's end."""

from account_ledger.domain.model.config import CHALLENGE
from account_ledger.domain.model.ids import AccountId, Day, IncomingId
from account_ledger.domain.stream_processing import (
    process_stream,
)
from support.brief_stream import build_brief_stream
from support.results import unwrap_ok
from support.states import list_entries
from support.streams import list_interest_amounts, make_credit
from support.values import make_aed, make_bhd


def test_an_empty_stream_reports_the_opening_balances_for_day_0_to_6() -> None:
    """An empty stream still reports Day 0 to Day 6, each closing at the opening balances, with an empty log."""
    result = unwrap_ok(process_stream((), CHALLENGE))

    assert [report.day for report in result.reports] == [Day(number) for number in range(7)]
    for report in result.reports:
        assert report.closing_balances == {
            AccountId("ACC-001"): make_aed("0.00"),
            AccountId("ACC-002"): make_bhd("0.000"),
        }
    assert result.find_log(Day(6)) == ()


def test_amb_015_a_late_event_is_processed_on_the_current_day() -> None:
    """AMB-015: E10, booked Day 5 but listed after E9, arrives once Day 5 has closed and is processed on Day 6."""
    result = unwrap_ok(process_stream(build_brief_stream(), CHALLENGE))

    assert IncomingId("E10") not in [entry.event.id for entry in result.find_log(Day(5))]
    e10 = [entry for entry in result.find_log(Day(6)) if entry.event.id == IncomingId("E10")]
    assert [entry.processed_day for entry in e10] == [Day(6)]


def test_amb_001_a_day_without_events_still_closes() -> None:
    """AMB-001: an event booked on a later day closes every day before it, those with no events of their own
    included, so each still accrues its interest; the event is processed on its own booked day."""
    result = unwrap_ok(process_stream((make_credit("E1", 1, "1000.00"), make_credit("E2", 4, "10.00")), CHALLENGE))

    assert [event_id for event_id, _ in list_interest_amounts(result.find_log(Day(3)))] == [
        "INT-001-D1@D1",
        "INT-001-D2@D2",
        "INT-001-D3@D3",
    ]
    assert [entry.processed_day for entry in list_entries(result.find_log(Day(4)), "E2")] == [Day(4)]


def test_amb_001_an_event_booked_after_the_window_reaches_no_day() -> None:
    """AMB-001: no day closes after the window's last, so an event booked after it reaches no day's log or report;
    the stream reader refuses such a day before it gets here."""
    result = unwrap_ok(process_stream((make_credit("E1", 1, "100.00"), make_credit("E2", 9, "50.00")), CHALLENGE))

    assert [report.day for report in result.reports] == [Day(number) for number in range(7)]
    assert list_entries(result.find_log(Day(6)), "E2") == []
