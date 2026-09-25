"""The driver: replays a stream day by day, closing each day as the booked days advance."""

from dataclasses import dataclass, replace

from account_ledger.domain.end_of_day import close_day
from account_ledger.domain.model.config import LedgerConfig
from account_ledger.domain.model.event_log import Log
from account_ledger.domain.model.events import IncomingEvent
from account_ledger.domain.model.ids import Day
from account_ledger.domain.model.money import CurrencyMismatch
from account_ledger.domain.model.result import Err, Ok, Result
from account_ledger.domain.processing import process_event
from account_ledger.domain.report import DayReport, ReportedClosings, build_report, update_reported


@dataclass(frozen=True, slots=True)
class Replay:
    """Day 0, then one report per day of the window, each beside the log as it stood at that day's close."""

    reports: tuple[DayReport, ...]
    logs: tuple[Log, ...]

    def find_report(self, day: Day) -> DayReport:
        """The report for the day."""
        return self.reports[self._find_index(day)]

    def find_log(self, day: Day) -> Log:
        """The log as it stood at the day's close."""
        return self.logs[self._find_index(day)]

    def _find_index(self, day: Day) -> int:
        """Where the day sits in the reports and the logs alike."""
        return [report.day for report in self.reports].index(day)


@dataclass(frozen=True, slots=True)
class _Progress:
    """The replay so far: the log, the reports and logs kept, the closings last reported, and the open day."""

    log: Log
    reports: tuple[DayReport, ...]
    logs: tuple[Log, ...]
    reported_closings: ReportedClosings
    day: Day


def replay_stream(stream: tuple[IncomingEvent, ...], config: LedgerConfig) -> Result[Replay, CurrencyMismatch]:
    """Replay the stream in listed order through the configured window (AMB-001, AMB-015).

    Each event is processed on the day that is open. An event booked on a later day is the sign to close the open day
    first, and every day up to its own, those with no events included; it is processed only once its day is open. An
    event listed after one booked later is late and is processed on the open day. Once the stream is spent, every day
    left in the window still closes. No day closes after the window, so an event booked after it reaches no day's log or
    report. A currency mismatch, which only a bug brings, ends the replay and is returned."""
    if isinstance(opening_report := build_report((), Day(0), config, {}), Err):
        return opening_report
    progress = _Progress((), (opening_report.value,), ((),), {}, config.first_day)
    for event in stream:
        if isinstance(closed_progress := _close_days_before(progress, event.booked, config), Err):
            return closed_progress
        progress = closed_progress.value
        if isinstance(processed_log := process_event(progress.log, event, progress.day, config), Err):
            return processed_log
        progress = replace(progress, log=processed_log.value)
    return _close_days_before(progress, None, config).map(lambda final: Replay(final.reports, final.logs))


def _close_days_before(
    progress: _Progress, booked: Day | None, config: LedgerConfig
) -> Result[_Progress, CurrencyMismatch]:
    """Close each open day before ``booked``, or every day left in the window when there is none."""
    while progress.day <= config.last_day and (booked is None or booked > progress.day):
        if isinstance(closed_progress := _close_open_day(progress, config), Err):
            return closed_progress
        progress = closed_progress.value
    return Ok(progress)


def _close_open_day(progress: _Progress, config: LedgerConfig) -> Result[_Progress, CurrencyMismatch]:
    """The open day's close: its end of day runs, its report and log are kept, and the next day opens."""
    if isinstance(closed_log := close_day(progress.log, progress.day, config), Err):
        return closed_log
    log = closed_log.value
    if isinstance(day_report := build_report(log, progress.day, config, progress.reported_closings), Err):
        return day_report
    return Ok(
        _Progress(
            log,
            (*progress.reports, day_report.value),
            (*progress.logs, log),
            update_reported(progress.reported_closings, day_report.value),
            progress.day.advance(),
        )
    )
