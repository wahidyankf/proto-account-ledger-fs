"""The shipped stream file, read from disk, is the brief's stream."""

from pathlib import Path

from account_ledger.adapters.stream_csv import parse_stream
from account_ledger.domain.model.config import CHALLENGE
from support.brief_stream import build_brief_stream

STREAM = Path(__file__).resolve().parents[2] / "streams" / "challenge.csv"


def test_the_shipped_stream_is_the_brief() -> None:
    """The shipped `streams/challenge.csv` parses to E1 to E10 exactly as the brief lists them."""
    assert parse_stream(STREAM.read_text(encoding="utf-8"), CHALLENGE) == build_brief_stream()
