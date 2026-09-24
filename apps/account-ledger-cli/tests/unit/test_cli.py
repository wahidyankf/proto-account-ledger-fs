"""The shell at the unit layer: ``run`` with every effect injected."""

import io

from account_ledger.cli import run


def test_the_greeting_prints_and_exits_0() -> None:
    out = io.StringIO()

    exit_code = run(out)

    assert out.getvalue() == "Hello, world!\n"
    assert exit_code == 0
