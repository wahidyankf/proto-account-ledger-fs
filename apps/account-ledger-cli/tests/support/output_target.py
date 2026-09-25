"""The text the program must print for the brief's stream: OUTPUT_TARGET.md's fenced block and one newline."""

from pathlib import Path

OUTPUT_TARGET = Path(__file__).resolve().parents[4] / "OUTPUT_TARGET.md"


def read_expected_output() -> str:
    """The fenced block of OUTPUT_TARGET.md, followed by one newline (tech-docs 003)."""

    lines = OUTPUT_TARGET.read_text(encoding="utf-8").split("\n")
    start = lines.index("```text") + 1
    end = lines.index("```", start)

    return "\n".join(lines[start:end]) + "\n"
