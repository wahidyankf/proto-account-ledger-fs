"""The shell at the unit layer: ``run`` with every effect injected."""

import io

import pytest

from account_ledger import cli
from account_ledger.adapters.render import render
from account_ledger.cli import run
from account_ledger.domain.model.config import CHALLENGE
from account_ledger.domain.replay import replay
from support.brief_stream import BRIEF_CSV, brief_stream


def test_a_stream_file_prints_its_report_and_exits_0() -> None:
    """AC-01: `run` reads the named stream, replays it, and writes the report to standard output, exiting 0; the
    end-to-end golden run compares that report with OUTPUT_TARGET."""
    out, err = io.StringIO(), io.StringIO()

    exit_code = run(["streams/challenge.csv"], {"streams/challenge.csv": BRIEF_CSV}.__getitem__, out, err)

    assert (out.getvalue(), err.getvalue(), exit_code) == (render(replay(brief_stream(), CHALLENGE).reports), "", 0)


USAGE = "usage: account-ledger-cli <stream.csv>\n"


def read_brief(path: str) -> str:
    """A reader that holds only the brief's stream, at any path."""
    return BRIEF_CSV


@pytest.mark.parametrize("argv", [[], ["a.csv", "b.csv"]])
def test_no_argument_is_a_usage_error_exiting_2(argv: list[str]) -> None:
    """AC-04: no argument, or more than one, prints the usage line to standard error and exits 2 (D13)."""
    out, err = io.StringIO(), io.StringIO()

    exit_code = run(argv, read_brief, out, err)

    assert (out.getvalue(), err.getvalue(), exit_code) == ("", USAGE, 2)


@pytest.mark.parametrize(
    ("fault", "reason"),
    [
        (FileNotFoundError(2, "No such file or directory"), "no such file"),
        (PermissionError(13, "Permission denied"), "Permission denied"),
    ],
)
def test_an_unreadable_file_exits_2(fault: OSError, reason: str) -> None:
    """AC-02: a file that cannot be read prints `error: cannot read PATH: REASON` and exits 2; REASON is `no such file`
    for a missing file, and the operating system's message otherwise (tech-docs 003)."""
    out, err = io.StringIO(), io.StringIO()

    def unreadable(path: str) -> str:
        """A reader that fails as the operating system would."""
        raise fault

    exit_code = run(["streams/missing.csv"], unreadable, out, err)

    assert (out.getvalue(), err.getvalue(), exit_code) == ("", f"error: cannot read streams/missing.csv: {reason}\n", 2)


def test_a_malformed_stream_exits_2_naming_the_line() -> None:
    """AC-03: a malformed stream prints `error: ` and the first fault with its line, prints no report, and exits 2."""
    out, err = io.StringIO(), io.StringIO()
    malformed = BRIEF_CSV.replace("E2,1,DEBIT,ACC-001,950.00,", "E2,1,DEBIT,ACC-001,950.00x,")

    exit_code = run(["stream.csv"], lambda path: malformed, out, err)

    assert (out.getvalue(), err.getvalue(), exit_code) == (
        "",
        "error: line 3: amount '950.00x' is not a decimal number\n",
        2,
    )


def test_an_internal_failure_exits_2_without_a_traceback(monkeypatch: pytest.MonkeyPatch) -> None:
    """AC-36: any other exception prints `error: internal failure: ` and its type, prints no report, and exits 2."""
    out, err = io.StringIO(), io.StringIO()

    def broken(*_: object) -> object:
        """A replay that fails with a bug."""
        raise ZeroDivisionError("a bug in the domain")

    monkeypatch.setattr(cli, "replay", broken)

    exit_code = run(["streams/challenge.csv"], read_brief, out, err)

    assert (out.getvalue(), err.getvalue(), exit_code) == ("", "error: internal failure: ZeroDivisionError\n", 2)


class ClosedPipe(io.StringIO):
    """Standard output whose reader has gone, as `| head` leaves it."""

    def write(self, s: str, /) -> int:
        """A write that fails as one to a closed pipe does."""
        raise BrokenPipeError(32, "Broken pipe")


def test_a_closed_pipe_exits_141_quietly() -> None:
    """AC-36: standard output closed early ends the run quietly with 141, as a shell reports SIGPIPE (D13)."""
    err = io.StringIO()

    exit_code = run(["streams/challenge.csv"], read_brief, ClosedPipe(), err)

    assert (err.getvalue(), exit_code) == ("", 141)


def test_an_interrupt_exits_130() -> None:
    """AC-36: an interrupt ends the run quietly with 130, as a shell reports SIGINT (D13)."""
    out, err = io.StringIO(), io.StringIO()

    def interrupted(path: str) -> str:
        """A reader interrupted by Ctrl-C."""
        raise KeyboardInterrupt

    exit_code = run(["streams/challenge.csv"], interrupted, out, err)

    assert (out.getvalue(), err.getvalue(), exit_code) == ("", "", 130)
