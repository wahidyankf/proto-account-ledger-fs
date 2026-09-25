"""The real entry point on real files and the process's real file descriptors, captured at the descriptor level."""

import io
import sys
from pathlib import Path

import pytest

from account_ledger.adapters.render import render
from account_ledger.cli import main
from account_ledger.core.config import CHALLENGE
from account_ledger.core.replay import replay
from support.brief_stream import brief_stream

APP = Path(__file__).resolve().parents[2]


def test_main_reads_a_real_file_and_reports_a_missing_one(
    capfd: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC-02: `main` reads the named file from disk and writes the report as UTF-8 whatever the locale, here an ASCII
    standard output on the real descriptor 1; a missing file prints its reason to standard error and exits 2."""
    monkeypatch.chdir(APP)
    monkeypatch.setattr(sys, "stdout", io.TextIOWrapper(io.FileIO(1, "w", closefd=False), encoding="ascii"))
    monkeypatch.setattr(sys, "argv", ["account-ledger-cli", "streams/challenge.csv"])

    read = main()
    sys.stdout.flush()
    printed = capfd.readouterr()

    monkeypatch.setattr(sys, "argv", ["account-ledger-cli", "streams/missing.csv"])
    missing = main()

    assert (printed.out, printed.err, read) == (render(replay(brief_stream(), CHALLENGE).reports), "", 0)
    assert (capfd.readouterr().err, missing) == ("error: cannot read streams/missing.csv: no such file\n", 2)
