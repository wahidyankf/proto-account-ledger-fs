"""Domain values for tests, built through the same ``parse`` functions the stream reader uses."""

from account_ledger.domain.model.money import Aed, Bhd
from support.results import unwrap_ok


def make_aed(text: str) -> Aed:
    """The AED money the text holds; a malformed text fails the test."""
    return unwrap_ok(Aed.parse(text))


def make_bhd(text: str) -> Bhd:
    """The BHD money the text holds; a malformed text fails the test."""
    return unwrap_ok(Bhd.parse(text))
