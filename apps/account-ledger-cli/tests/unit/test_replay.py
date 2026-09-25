"""The driver: opening reports, days closing as booked days advance, late events, and the log at each day."""

from account_ledger.domain.model.config import CHALLENGE
from account_ledger.domain.model.ids import AccountId, Day, IncomingId
from account_ledger.domain.replay import replay
from support.brief_stream import brief_stream
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
