"""The driver: replays a stream day by day, closing each day as the booked days advance."""

from dataclasses import dataclass

from account_ledger.config import LedgerConfig
from account_ledger.events import IncomingEvent
from account_ledger.ids import Day
from account_ledger.log import Log
from account_ledger.processing import process
from account_ledger.report import DayReport, report


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
    """Replay the stream in listed order through the configured window."""
    log: Log = ()
    reports: list[DayReport] = [report(log, Day(0), config)]
    logs: list[Log] = [log]
    day = config.first_day
    for event in stream:
        while event.booked > day:
            reports.append(report(log, day, config))
            logs.append(log)
            day = day.next()
        log = process(log, event, day, config)
    while day <= config.last_day:
        reports.append(report(log, day, config))
        logs.append(log)
        day = day.next()
    return Replay(tuple(reports), tuple(logs))
