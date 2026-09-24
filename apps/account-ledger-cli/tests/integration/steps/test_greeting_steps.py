"""Integration bindings for the greeting feature: the real entry point writes to the process's real standard output,
captured at the file-descriptor level. No network is involved."""

import pytest
from pytest_bdd import scenarios, when

from account_ledger.cli import main
from support.cli_run import CliRun

scenarios("greeting.feature")


@when("I run the CLI with no arguments", target_fixture="cli_run")
def run_with_no_arguments(capfd: pytest.CaptureFixture[str]) -> CliRun:
    exit_code = main()
    return CliRun(output=capfd.readouterr().out, exit_code=exit_code)
