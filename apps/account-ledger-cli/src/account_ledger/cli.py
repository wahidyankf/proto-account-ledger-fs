"""The shell: the command-line entry point, which binds every real effect and composes the adapters and the use case."""

import io
import os
import sys
from collections.abc import Sequence
from typing import assert_never

from account_ledger.adapters.csv_file import CsvFileSource, Reader, read_file
from account_ledger.adapters.text_report import TextOutput, TextReportSink
from account_ledger.application.ports import RunFault, RunLedger, SourceFault
from account_ledger.application.run import LedgerRun
from account_ledger.challenge import CHALLENGE
from account_ledger.common.result import Err
from account_ledger.domain.ledger.ledger import UnknownAccount
from account_ledger.domain.model.money import CurrencyMismatch

USAGE = "usage: account-ledger-cli <stream.csv>"
CLOSED_PIPE = 141  # the reader has gone, as a shell reports SIGPIPE: 128 + 13
INTERRUPTED = 130  # as a shell reports SIGINT: 128 + 2


def run_cli(argv: Sequence[str], read_text: Reader, out: TextOutput, err: TextOutput, run_ledger: RunLedger) -> int:
    """Read the one named stream, process it, and write its report to ``out``; return the process exit code (D13)."""

    try:
        return _run_file(argv, read_text, out, err, run_ledger)

    except BrokenPipeError:
        return CLOSED_PIPE

    except KeyboardInterrupt:
        return INTERRUPTED

    except Exception as fault:  # the floor tier's last resort: a status and a line, never a traceback
        err.write(f"error: internal failure: {type(fault).__name__}\n")

        return 2


def _run_file(argv: Sequence[str], read_text: Reader, out: TextOutput, err: TextOutput, run_ledger: RunLedger) -> int:
    """The exit code: 0 for a written report, 2 for a wrong argument count, an unreadable file, a bad stream, or an
    internal fault."""

    if len(argv) != 1:
        err.write(f"{USAGE}\n")

        return 2

    if isinstance(outcome := run_ledger.run(CsvFileSource(argv[0], read_text), TextReportSink(out)), Err):
        err.write(f"error: {_describe_run_fault(outcome.error)}\n")

        return 2

    return 0


def _describe_run_fault(fault: RunFault) -> str:
    """The text after `error: `: a source fault's own message, or `internal: ` and what a fault only a bug brings
    met, the currency found where another was required or an account the ledger does not hold."""

    match fault:
        case SourceFault():
            return fault.message
        case CurrencyMismatch():
            return f"internal: {fault.found_currency} met where {fault.expected_currency} was required"
        case UnknownAccount():
            return f"internal: {fault.account.value} is not a configured account"
        case _:
            assert_never(fault)


def main() -> int:
    """The entry point: binds the process's arguments, a UTF-8 file reader, UTF-8 standard streams, and the run over the
    brief's configuration (D13)."""

    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(encoding="utf-8")  # the report prints `−` whatever the locale

    status = run_cli(sys.argv[1:], read_file, sys.stdout, sys.stderr, LedgerRun(CHALLENGE))

    if status == CLOSED_PIPE:  # the exit-time flush would raise again, so it writes to the null device instead
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())

    return status
