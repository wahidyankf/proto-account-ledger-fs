"""Imperative shell: every effect of the command-line entry point lives here."""

import sys
from typing import TextIO

from account_ledger.greeting import greeting


def run(out: TextIO) -> int:
    """Write the greeting to ``out`` and return the process exit code."""
    out.write(f"{greeting()}\n")
    return 0


def main() -> int:
    """The entry point: run against the process's real standard output."""
    return run(sys.stdout)
