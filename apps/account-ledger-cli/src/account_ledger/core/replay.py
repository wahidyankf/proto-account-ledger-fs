"""The driver: replays a stream day by day, closing each day as the booked days advance."""

from dataclasses import dataclass

from account_ledger.core.config import LedgerConfig
from account_ledger.core.end_of_day import close_day
from account_ledger.core.events import IncomingEvent
from account_ledger.core.ids import Day
from account_ledger.core.log import Log
from account_ledger.core.processing import process
from account_ledger.core.report import DayReport, Reported, report, reported_after


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
    """Replay the stream in listed order through the configured window (AMB-015).

    Each day processes the events listed next whose booked day has come, then closes on time; an event listed after
    one booked later waits for it, and is processed as a late event on the day that is open."""
    log: Log = ()
    reports: list[DayReport] = [report(log, Day(0), config, {})]
    logs: list[Log] = [log]
    reported: Reported = {}
    day, index = config.first_day, 0
    while day <= config.last_day:
        while index < len(stream) and stream[index].booked <= day:
            log = process(log, stream[index], day, config)
            index += 1
        log = close_day(log, day, config)
        day_report = report(log, day, config, reported)
        reported = reported_after(reported, day_report)
        reports.append(day_report)
        logs.append(log)
        day = day.next()
    return Replay(tuple(reports), tuple(logs))
