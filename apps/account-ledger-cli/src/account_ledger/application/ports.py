"""The ports the use case declares: where its events come from, where its reports go, and how the shell drives it."""

from dataclasses import dataclass
from typing import Protocol

from account_ledger.application.report import DayReport
from account_ledger.application.stream import IncomingStream
from account_ledger.common.result import Result
from account_ledger.domain.ledger.ledger import InternalFault
from account_ledger.domain.model.config import LedgerConfig


@dataclass(frozen=True, slots=True)
class SourceFault:
    """Why the events could not be read: the text the CLI prints after ``error: ``."""

    message: str


class EventSource(Protocol):
    """Where the use case reads the incoming events from (driven port)."""

    def read_events(self, config: LedgerConfig) -> Result[IncomingStream, SourceFault]:
        """The stream's events, or why they could not be read."""
        ...


class ReportSink(Protocol):
    """Where the use case publishes the day reports (driven port)."""

    def publish(self, reports: tuple[DayReport, ...]) -> None:
        """Publish every report at once; a write that fails raises."""
        ...


type RunFault = SourceFault | InternalFault


class RunLedger(Protocol):
    """One run of the ledger, from a source to a sink (driving port): what the shell calls."""

    def run(self, source: EventSource, sink: ReportSink) -> Result[None, RunFault]:
        """Read the events, process them, and publish the reports; the first fault ends the run."""
        ...
