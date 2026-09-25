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

    def process_event(self, event: IncomingEvent, config: LedgerConfig) -> Result[_ProcessingState, CurrencyMismatch]:
        """The state with the event processed on the current day."""
        return process_event(self.log, event, self.day, config).map(lambda log: replace(self, log=log))

    def close_days_before(self, booked: Day | None, config: LedgerConfig) -> Result[_ProcessingState, CurrencyMismatch]:
        """Close each day before ``booked``, or every day left in the window when there is none."""
        state = self
        while state.day <= config.last_day and (booked is None or booked > state.day):
            if isinstance(closed_state := state.close_current_day(config), Err):
                return closed_state
            state = closed_state.value
        return Ok(state)

    def close_current_day(self, config: LedgerConfig) -> Result[_ProcessingState, CurrencyMismatch]:
        """The current day's close: its end of day runs, its report and log are kept, and the next day opens."""
        if isinstance(closed_log := close_day(self.log, self.day, config), Err):
            return closed_log
        log = closed_log.value
        if isinstance(day_report := build_report(log, self.day, config, self.reported_closings), Err):
            return day_report
        return Ok(
            _ProcessingState(
                log,
                (*self.reports, day_report.value),
                (*self.logs, log),
                update_reported(self.reported_closings, day_report.value),
                self.day.advance(),
            )
        )


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
        if isinstance(processed_state := state.close_days_before(event.booked, config), Err):
            return processed_state
        if isinstance(processed_state := processed_state.value.process_event(event, config), Err):
            return processed_state
        state = processed_state.value
    return state.close_days_before(None, config).map(lambda final: ProcessedStream(final.reports, final.logs))
