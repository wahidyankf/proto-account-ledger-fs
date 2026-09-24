"""Unit bindings for the greeting feature: the shell runs in-process with its output stream injected."""

import io

from pytest_bdd import scenarios, when

from account_ledger.cli import run
from support.cli_run import CliRun

scenarios("greeting.feature")


@when("I run the CLI with no arguments", target_fixture="cli_run")
def run_with_no_arguments() -> CliRun:
    out = io.StringIO()
    exit_code = run(out)
    return CliRun(output=out.getvalue(), exit_code=exit_code)
