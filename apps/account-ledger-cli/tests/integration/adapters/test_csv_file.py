"""The shipped stream file, read from disk, is the brief's stream."""

from pathlib import Path

from account_ledger.adapters.csv_file import CsvFileSource
from account_ledger.application.stream import IncomingStream
from account_ledger.challenge import CHALLENGE
from account_ledger.common.result import Ok
from support.brief_stream import build_brief_stream

STREAM = Path(__file__).resolve().parents[3] / "streams" / "challenge.csv"


def test_the_shipped_stream_is_the_brief() -> None:
    """The shipped `streams/challenge.csv` parses to E1 to E10 exactly as the brief lists them."""

    assert CsvFileSource.parse(STREAM.read_text(encoding="utf-8"), CHALLENGE) == Ok(
        IncomingStream(build_brief_stream())
    )
