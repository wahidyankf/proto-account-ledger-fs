"""Imperative shell: every effect of the command-line entry point lives here."""

import io
import os
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TextIO, assert_never

from account_ledger.adapters.render import render_reports
from account_ledger.adapters.stream_csv import parse_stream
from account_ledger.challenge import CHALLENGE
from account_ledger.common.result import Err, Ok, Result
from account_ledger.domain.ledger.ledger import InternalFault, UnknownAccount
from account_ledger.domain.model.money import CurrencyMismatch
from account_ledger.domain.stream_processing import (
    process_stream,
)

USAGE = "usage: account-ledger-cli <stream.csv>"
CLOSED_PIPE = 141  # the reader has gone, as a shell reports SIGPIPE: 128 + 13
INTERRUPTED = 130  # as a shell reports SIGINT: 128 + 2


type Reader = Callable[[str], Result[str, OSError | UnicodeDecodeError]]


def run_cli(argv: Sequence[str], read_text: Reader, out: TextIO, err: TextIO) -> int:
    """Read the one named stream, process it, and write its report to ``out``; return the process exit code (D13)."""
    try:
        return _process_file(argv, read_text, out, err)
    except BrokenPipeError:
        return CLOSED_PIPE
    except KeyboardInterrupt:
        return INTERRUPTED
    except Exception as fault:  # the floor tier's last resort: a status and a line, never a traceback
        err.write(f"error: internal failure: {type(fault).__name__}\n")
        return 2


def _process_file(argv: Sequence[str], read_text: Reader, out: TextIO, err: TextIO) -> int:
    """The exit code: 0 for a written report, 2 for a wrong argument count, an unreadable file, a bad stream, or an
    internal fault."""
    if len(argv) != 1:
        err.write(f"{USAGE}\n")
        return 2
    path = argv[0]
    text = read_text(path)
    if isinstance(text, Err):
        err.write(f"error: cannot read {path}: {_describe_fault(text.error)}\n")
        return 2
    events = parse_stream(text.value, CHALLENGE)
    if isinstance(events, Err):
        err.write(f"error: {events.error.message}\n")
        return 2
    processed = process_stream(events.value, CHALLENGE)
    if isinstance(processed, Err):
        err.write(f"error: internal: {_describe_internal_fault(processed.error)}\n")
        return 2
    out.write(render_reports(processed.value.reports))
    out.flush()  # a closed pipe surfaces here, inside the handlers, not at the exit-time flush
    return 0


def _describe_internal_fault(fault: InternalFault) -> str:
    """What a fault only a bug brings met: the currency found where another was required, or an account the ledger
    does not hold."""
    match fault:
        case CurrencyMismatch():
            return f"{fault.found_currency} met where {fault.expected_currency} was required"
        case UnknownAccount():
            return f"{fault.account.value} is not a configured account"
        case _:
            assert_never(fault)


def _describe_fault(fault: OSError | UnicodeDecodeError) -> str:
    """`no such file` for a missing file, `not UTF-8 text` for one that does not decode, and the operating system's
    message otherwise (tech-docs 003)."""
    match fault:
        case FileNotFoundError():
            return "no such file"
        case UnicodeDecodeError():
            return "not UTF-8 text"
        case OSError():
            return fault.strerror or str(fault)


def main() -> int:
    """The entry point: binds the process's arguments, a UTF-8 file reader, and UTF-8 standard streams (D13)."""
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(encoding="utf-8")  # the report prints `−` whatever the locale
    status = run_cli(sys.argv[1:], _read_file, sys.stdout, sys.stderr)
    if status == CLOSED_PIPE:  # the exit-time flush would raise again, so it writes to the null device instead
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
    return status


def _read_file(path: str) -> Result[str, OSError | UnicodeDecodeError]:
    """The stream file's text, read as UTF-8, or the refusal of a file that cannot be read or decoded; ``read_text``
    refuses by raising, so the refusal is caught here and returned."""
    try:
        return Ok(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as fault:
        return Err(fault)
