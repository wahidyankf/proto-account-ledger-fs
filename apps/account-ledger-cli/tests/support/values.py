"""Domain values for tests, built through the same ``parse`` functions the stream reader uses."""

from account_ledger.domain.model.money import Aed, Bhd


def make_aed(text: str) -> Aed:
    """The AED money the text holds; a malformed text fails the test."""
    value = Aed.parse(text)
    assert isinstance(value, Aed), value
    return value


def make_bhd(text: str) -> Bhd:
    """The BHD money the text holds; a malformed text fails the test."""
    value = Bhd.parse(text)
    assert isinstance(value, Bhd), value
    return value
