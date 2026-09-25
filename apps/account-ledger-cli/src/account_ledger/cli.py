"""Imperative shell: every effect of the command-line entry point lives here."""

import io
import os
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TextIO

from account_ledger.adapters.render import render_reports
from account_ledger.adapters.stream_csv import parse_stream
from account_ledger.domain.model.config import CHALLENGE
from account_ledger.domain.model.result import Err
from account_ledger.domain.replay import replay_stream

USAGE = "usage: account-ledger-cli <stream.csv>"
CLOSED_PIPE = 141  # the reader has gone, as a shell reports SIGPIPE: 128 + 13
INTERRUPTED = 130  # as a shell reports SIGINT: 128 + 2


def run_cli(argv: Sequence[str], read_text: Callable[[str], str], out: TextIO, err: TextIO) -> int:
    """Read the one named stream, replay it, and write its report to ``out``; return the process exit code (D13)."""
    try:
        return _replay_file(argv, read_text, out, err)
    except BrokenPipeError:
        return CLOSED_PIPE
    except KeyboardInterrupt:
        return INTERRUPTED
    except Exception as fault:  # the floor tier's last resort: a status and a line, never a traceback
        err.write(f"error: internal failure: {type(fault).__name__}\n")
        return 2


def _replay_file(argv: Sequence[str], read_text: Callable[[str], str], out: TextIO, err: TextIO) -> int:
    """The exit code: 0 for a written report, 2 for a wrong argument count, an unreadable file, or a bad stream."""
    if len(argv) != 1:
        err.write(f"{USAGE}\n")
        return 2
    path = argv[0]
    try:
        text = read_text(path)
    except OSError as fault:
        err.write(f"error: cannot read {path}: {_describe_fault(fault)}\n")
        return 2
    events = parse_stream(text, CHALLENGE)
    if isinstance(events, Err):
        err.write(f"error: {events.error.message}\n")
        return 2
    out.write(render_reports(replay_stream(events.value, CHALLENGE).reports))
    out.flush()  # a closed pipe surfaces here, inside the handlers, not at the exit-time flush
    return 0


def _describe_fault(fault: OSError) -> str:
    """`no such file` for a missing file, and the operating system's message otherwise (tech-docs 003)."""
    return "no such file" if isinstance(fault, FileNotFoundError) else fault.strerror or str(fault)


def main() -> int:
    """The entry point: binds the process's arguments, a UTF-8 file reader, and UTF-8 standard streams (D13)."""
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(encoding="utf-8")  # the report prints `−` whatever the locale
    status = run_cli(sys.argv[1:], _read_file, sys.stdout, sys.stderr)
    if status == CLOSED_PIPE:  # the exit-time flush would raise again, so it writes to the null device instead
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
    return status


def _read_file(path: str) -> str:
    """The stream file's text, read as UTF-8."""
    return Path(path).read_text(encoding="utf-8")
