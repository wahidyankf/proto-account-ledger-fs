"""Domain values for tests, built through the same ``parse`` functions the stream reader uses."""

from account_ledger.domain.money import Aed, Bhd


def aed(text: str) -> Aed:
    value = Aed.parse(text)
    assert isinstance(value, Aed), value
    return value


def bhd(text: str) -> Bhd:
    value = Bhd.parse(text)
    assert isinstance(value, Bhd), value
    return value
