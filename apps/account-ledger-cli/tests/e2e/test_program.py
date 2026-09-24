"""The program as its own process, through its public entry point."""

import os
import subprocess
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2] / "src"


def test_the_program_prints_the_greeting_and_exits_0() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "account_ledger"],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(SOURCE)},
        timeout=30,
        check=False,
    )

    assert completed.stdout == "Hello, world!\n"
    assert completed.returncode == 0
