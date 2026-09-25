"""Processes a stream day by day, closing each day as the booked days advance."""

from dataclasses import dataclass, replace

from account_ledger.common.result import Err, Ok, Result
from account_ledger.domain.ledger.end_of_day import (
    close_day,
)
from account_ledger.domain.ledger.event_log import (
    Log,
)
from account_ledger.domain.ledger.processing import (
    process_event,
)
from account_ledger.domain.model.config import LedgerConfig
from account_ledger.domain.model.events import IncomingEvent
from account_ledger.domain.model.ids import Day
from account_ledger.domain.model.money import CurrencyMismatch
from account_ledger.domain.report import DayReport, ReportedClosings, build_report, update_reported


@dataclass(frozen=True, slots=True)
class ProcessedStream:
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
class _ProcessingState:
    """The processing so far: the log, the reports and logs kept, the closings last reported, and the current day."""

    log: Log
    reports: tuple[DayReport, ...]
    logs: tuple[Log, ...]
    reported_closings: ReportedClosings
    day: Day


def process_stream(
    stream: tuple[IncomingEvent, ...], config: LedgerConfig
) -> Result[ProcessedStream, CurrencyMismatch]:
    """Process the stream in listed order through the configured window (AMB-001, AMB-015).

    Each event is processed on the current day. An event booked on a later day is the sign to close the current day
    first, and every day up to its own, those with no events included; it is processed only once its day is open. An
    event listed after one booked later is late and is processed on the current day. Once every event is processed,
    every day left in the window still closes. No day closes after the window, so an event booked after it reaches no
    day's log or report. A currency mismatch, which only a bug brings, ends the processing and is returned."""
    if isinstance(opening_report := build_report((), Day(0), config, {}), Err):
        return opening_report
    state = _ProcessingState((), (opening_report.value,), ((),), {}, config.first_day)
    for event in stream:
        if isinstance(closed_state := _close_days_before(state, event.booked, config), Err):
            return closed_state
        state = closed_state.value
        if isinstance(processed_log := process_event(state.log, event, state.day, config), Err):
            return processed_log
        state = replace(state, log=processed_log.value)
    return _close_days_before(state, None, config).map(lambda final: ProcessedStream(final.reports, final.logs))


def _close_days_before(
    state: _ProcessingState, booked: Day | None, config: LedgerConfig
) -> Result[_ProcessingState, CurrencyMismatch]:
    """Close each day before ``booked``, or every day left in the window when there is none."""
    while state.day <= config.last_day and (booked is None or booked > state.day):
        if isinstance(closed_state := _close_current_day(state, config), Err):
            return closed_state
        state = closed_state.value
    return Ok(state)


def _close_current_day(state: _ProcessingState, config: LedgerConfig) -> Result[_ProcessingState, CurrencyMismatch]:
    """The current day's close: its end of day runs, its report and log are kept, and the next day opens."""
    if isinstance(closed_log := close_day(state.log, state.day, config), Err):
        return closed_log
    log = closed_log.value
    if isinstance(day_report := build_report(log, state.day, config, state.reported_closings), Err):
        return day_report
    return Ok(
        _ProcessingState(
            log,
            (*state.reports, day_report.value),
            (*state.logs, log),
            update_reported(state.reported_closings, day_report.value),
            state.day.advance(),
        )
    )
