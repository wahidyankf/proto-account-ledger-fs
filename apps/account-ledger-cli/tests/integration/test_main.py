"""The real entry point on the process's real standard output, captured at the file-descriptor level."""

import pytest

from account_ledger.cli import main


def test_main_prints_the_greeting_and_exits_0(capfd: pytest.CaptureFixture[str]) -> None:
    exit_code = main()

    assert capfd.readouterr().out == "Hello, world!\n"
    assert exit_code == 0
