"""Then steps shared by every test level; each level binds its own When step to the ``cli_run`` fixture."""

from pytest_bdd import parsers, then

from support.cli_run import CliRun


@then(parsers.parse('the output is "{expected}"'))
def output_is(cli_run: CliRun, expected: str) -> None:
    assert cli_run.output.rstrip("\r\n") == expected


@then(parsers.parse("the exit code is {expected:d}"))
def exit_code_is(cli_run: CliRun, expected: int) -> None:
    assert cli_run.exit_code == expected
