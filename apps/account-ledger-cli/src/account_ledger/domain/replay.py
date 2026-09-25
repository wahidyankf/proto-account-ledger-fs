"""The driver: replays a stream day by day, closing each day as the booked days advance."""

from dataclasses import dataclass

from account_ledger.domain.end_of_day import close_day
from account_ledger.domain.model.config import LedgerConfig
from account_ledger.domain.model.event_log import Log
from account_ledger.domain.model.events import IncomingEvent
from account_ledger.domain.model.ids import Day
from account_ledger.domain.processing import process
from account_ledger.domain.report import DayReport, Reported, report, reported_after


@dataclass(frozen=True, slots=True)
class Replay:
    """Day 0, then one report per day of the window, each beside the log as it stood at that day's close."""

    reports: tuple[DayReport, ...]
    logs: tuple[Log, ...]

    def report(self, day: Day) -> DayReport:
        return self.reports[self._index(day)]

    def log_at(self, day: Day) -> Log:
        return self.logs[self._index(day)]

    def _index(self, day: Day) -> int:
        return [each.day for each in self.reports].index(day)


def replay(stream: tuple[IncomingEvent, ...], config: LedgerConfig) -> Replay:
    """Replay the stream in listed order through the configured window (AMB-001, AMB-015).

    Each event is processed on the day that is open. An event booked on a later day is the sign to close the open day
    first, and every day up to its own, those with no events included; it is processed only once its day is open. An
    event listed after one booked later is late and is processed on the open day. Once the stream is spent, every day
    left in the window still closes. No day closes after the window, so an event booked after it reaches no day's log or
    report."""
    log: Log = ()
    reports: list[DayReport] = [report(log, Day(0), config, {})]
    logs: list[Log] = [log]
    reported: Reported = {}

    def close(day: Day) -> None:
        nonlocal log, reported
        log = close_day(log, day, config)
        day_report = report(log, day, config, reported)
        reported = reported_after(reported, day_report)
        reports.append(day_report)
        logs.append(log)

    day = config.first_day
    for event in stream:
        while event.booked > day and day <= config.last_day:
            close(day)
            day = day.next()
        log = process(log, event, day, config)
    while day <= config.last_day:
        close(day)
        day = day.next()
    return Replay(tuple(reports), tuple(logs))
