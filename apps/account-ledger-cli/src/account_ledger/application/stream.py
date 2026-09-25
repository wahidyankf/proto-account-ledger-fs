"""The incoming stream, processed day by day, each day closed as the booked days advance."""

from dataclasses import dataclass, replace

from account_ledger.application.report import DayReport, ReportedClosings
from account_ledger.common.result import Err, Ok, Result
from account_ledger.domain.account.event_log import EventLog
from account_ledger.domain.ledger.ledger import InternalFault, Ledger
from account_ledger.domain.model.config import LedgerConfig
from account_ledger.domain.model.events import IncomingEvent
from account_ledger.domain.model.ids import Day
from account_ledger.domain.model.money import CurrencyMismatch


@dataclass(frozen=True, slots=True)
class IncomingStream:
    """The incoming events, in the order the stream lists them."""

    events: tuple[IncomingEvent, ...]

    def process(self, config: LedgerConfig) -> Result[ProcessedStream, InternalFault]:
        """Process the stream in listed order through the configured window (AMB-001, AMB-015).

        Each event is processed on the current day. An event booked on a later day is the sign to close the current day
        first, and every day up to its own, those with no events included; it is processed only once its day is open. An
        event listed after one booked later is late and is processed on the current day. Once every event is processed,
        every day left in the window still closes. No day closes after the window, so an event booked after it reaches
        no day's log or report. An internal fault, which only a bug brings, ends the processing and is returned."""
        ledger, reported = Ledger.open(config), ReportedClosings.make_empty()
        if isinstance(opening_report := DayReport.build(ledger, Day(0), reported), Err):
            return opening_report
        state = _ProcessingState(ledger, (opening_report.value,), (ledger.log,), reported, config.first_day)
        for event in self.events:
            if isinstance(processed_state := state.close_days_before(event.booked), Err):
                return processed_state
            if isinstance(processed_state := processed_state.value.process_event(event), Err):
                return processed_state
            state = processed_state.value
        return state.close_days_before(None).map(lambda final: ProcessedStream(final.reports, final.logs))


@dataclass(frozen=True, slots=True)
class ProcessedStream:
    """Day 0, then one report per day of the window, each beside the log as it stood at that day's close."""

    reports: tuple[DayReport, ...]
    logs: tuple[EventLog, ...]

    def find_report(self, day: Day) -> DayReport:
        """The report for the day."""
        return self.reports[self._find_index(day)]

    def find_log(self, day: Day) -> EventLog:
        """The log as it stood at the day's close."""
        return self.logs[self._find_index(day)]

    def _find_index(self, day: Day) -> int:
        """Where the day sits in the reports and the logs alike."""
        return [report.day for report in self.reports].index(day)


@dataclass(frozen=True, slots=True)
class _ProcessingState:
    """The processing so far: the ledger, the reports and logs kept, the closings last reported, and the current
    day."""

    ledger: Ledger
    reports: tuple[DayReport, ...]
    logs: tuple[EventLog, ...]
    reported: ReportedClosings
    day: Day

    def process_event(self, event: IncomingEvent) -> Result[_ProcessingState, InternalFault]:
        """The state with the event processed on the current day."""
        return self.ledger.process_event(event, self.day).map(lambda ledger: replace(self, ledger=ledger))

    def close_days_before(self, booked: Day | None) -> Result[_ProcessingState, InternalFault]:
        """Close each day before ``booked``, or every day left in the window when there is none."""
        state = self
        while state.day <= self.ledger.config.last_day and (booked is None or booked > state.day):
            if isinstance(closed_state := state.close_current_day(), Err):
                return closed_state
            state = closed_state.value
        return Ok(state)

    def close_current_day(self) -> Result[_ProcessingState, CurrencyMismatch]:
        """The current day's close: its end of day runs, its report and log are kept, and the next day opens."""
        if isinstance(closed_ledger := self.ledger.close_day(self.day), Err):
            return closed_ledger
        ledger = closed_ledger.value
        if isinstance(day_report := DayReport.build(ledger, self.day, self.reported), Err):
            return day_report
        return Ok(
            _ProcessingState(
                ledger,
                (*self.reports, day_report.value),
                (*self.logs, ledger.log),
                self.reported.update(day_report.value),
                self.day.advance(),
            )
        )
