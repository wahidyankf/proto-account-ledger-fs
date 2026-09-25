"""Reading a ``Result`` in a test: the success's value, or a failed test naming the fault."""

from account_ledger.domain.model.result import Err, Result


def unwrap_ok[T, E](result: Result[T, E]) -> T:
    """The value of an ``Ok``; an ``Err`` fails the test with its fault."""
    assert not isinstance(result, Err), result.error
    return result.value
