"""The program as its own process, through its public entry point."""

import os
import subprocess
import sys
from pathlib import Path

from support.output_target import read_expected_output

APP = Path(__file__).resolve().parents[2]
SOURCE = APP / "src"
CHALLENGE_STREAM = APP / "streams" / "challenge.csv"
HEADER = "event,booked,type,account,amount,value_date,reference,instalments,final"


def run_program(*args: str) -> subprocess.CompletedProcess[str]:
    """The program run as its own process from the application's directory."""
    return subprocess.run(
        [sys.executable, "-m", "account_ledger", *args],
        cwd=APP,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONPATH": str(SOURCE)},
        timeout=30,
        check=False,
    )


def test_the_brief_stream_prints_output_target() -> None:
    """AC-01: the program processes the brief's stream and prints OUTPUT_TARGET byte for byte, exiting 0."""
    completed_process = run_program(str(CHALLENGE_STREAM))

    assert completed_process.stdout.split("\n") == read_expected_output().split(
        "\n"
    )  # a failure names the first line that differs
    assert (completed_process.stderr, completed_process.returncode) == ("", 0)


def test_a_missing_stream_file_exits_2() -> None:
    """AC-02: a file that cannot be read prints its reason to standard error and exits 2."""
    assert not (APP / "streams" / "missing.csv").exists()

    completed_process = run_program("streams/missing.csv")

    assert (completed_process.stdout, completed_process.stderr, completed_process.returncode) == (
        "",
        "error: cannot read streams/missing.csv: no such file\n",
        2,
    )


def test_a_malformed_amount_names_its_line(tmp_path: Path) -> None:
    """AC-03: a malformed stream prints the first fault with its line and exits 2."""
    stream = tmp_path / "stream.csv"
    stream.write_text(f"{HEADER}\nE1,1,CREDIT,ACC-001,10.00,1,,,\nE2,1,CREDIT,ACC-001,12.00x,1,,,\n", encoding="utf-8")

    completed_process = run_program(str(stream))

    assert (completed_process.stdout, completed_process.stderr, completed_process.returncode) == (
        "",
        "error: line 3: amount '12.00x' is not a decimal number\n",
        2,
    )


def test_an_unheld_account_names_its_line(tmp_path: Path) -> None:
    """AC-03: a row naming an account the ledger does not hold is a fault in the input, never a refusal (D21)."""
    stream = tmp_path / "stream.csv"
    stream.write_text(f"{HEADER}\nE1,1,CREDIT,ACC-009,10.00,1,,,\n", encoding="utf-8")

    completed_process = run_program(str(stream))

    assert (completed_process.stdout, completed_process.stderr, completed_process.returncode) == (
        "",
        "error: line 2: account 'ACC-009' is not held by this ledger\n",
        2,
    )


def test_no_argument_prints_usage_and_exits_2() -> None:
    """AC-04: no argument is a usage error."""
    completed_process = run_program()

    assert (completed_process.stdout, completed_process.stderr, completed_process.returncode) == (
        "",
        "usage: account-ledger-cli <stream.csv>\n",
        2,
    )


def test_a_closed_pipe_exits_141_quietly() -> None:
    """AC-36: standard output whose reader has already gone ends the program with 141 and nothing on standard error,
    the exit-time flush included (D13)."""
    read_end, write_end = os.pipe()
    os.close(read_end)

    completed_process = subprocess.run(
        [sys.executable, "-m", "account_ledger", str(CHALLENGE_STREAM)],
        cwd=APP,
        stdout=write_end,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONPATH": str(SOURCE)},
        timeout=30,
        check=False,
    )
    os.close(write_end)

    assert (completed_process.stderr, completed_process.returncode) == ("", 141)
