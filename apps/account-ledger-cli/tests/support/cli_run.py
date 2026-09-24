"""What one run of the CLI left behind, whichever test level produced it."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CliRun:
    """The text the CLI wrote to standard output and the exit code it returned."""

    output: str
    exit_code: int
