"""The shipped stream file, read from disk, is the brief's stream."""

from pathlib import Path

from account_ledger.config import CHALLENGE
from account_ledger.stream_csv import parse_stream
from support.brief_stream import brief_stream

STREAM = Path(__file__).resolve().parents[2] / "streams" / "challenge.csv"


def test_the_shipped_stream_is_the_brief() -> None:
    assert parse_stream(STREAM.read_text(encoding="utf-8"), CHALLENGE) == brief_stream()
