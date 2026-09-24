"""End-to-end bindings for the greeting feature: the CLI runs as its own process through its public entry point."""

import os
import subprocess
import sys
from pathlib import Path

from pytest_bdd import scenarios, when

from support.cli_run import CliRun

scenarios("greeting.feature")

SOURCE = Path(__file__).resolve().parents[3] / "src"


@when("I run the CLI with no arguments", target_fixture="cli_run")
def run_with_no_arguments() -> CliRun:
    completed = subprocess.run(
        [sys.executable, "-m", "account_ledger"],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(SOURCE)},
        timeout=30,
        check=False,
    )
    return CliRun(output=completed.stdout, exit_code=completed.returncode)
