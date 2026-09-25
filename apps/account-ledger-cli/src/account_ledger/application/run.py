"""The one use case: read the events, process them, and publish the reports."""

from dataclasses import dataclass

from account_ledger.application.ports import EventSource, ReportSink, RunFault
from account_ledger.common.result import Err, Ok, Result
from account_ledger.domain.model.config import LedgerConfig


@dataclass(frozen=True, slots=True)
class LedgerRun:
    """A run of the ledger over the configured accounts and window; the shell drives it as a ``RunLedger``."""

    config: LedgerConfig

    def run(self, source: EventSource, sink: ReportSink) -> Result[None, RunFault]:
        """Read the events, process them, and publish the reports; the first fault ends the run, so nothing is
        published unless every day is reported."""

        if isinstance(stream := source.read_events(self.config), Err):
            return stream

        if isinstance(processed := stream.value.process(self.config), Err):
            return processed

        sink.publish(processed.value.reports)

        return Ok(None)
