"""Result: each combinator acts on its own side and hands the other back unchanged."""

from account_ledger.domain.model.result import Err, Ok, Result


def check_positive(number: int) -> Result[int, str]:
    """A number above zero, or a fault naming it."""
    return Ok(number) if number > 0 else Err(f"{number} is not positive")


def test_map_and_map_err_change_only_their_own_side() -> None:
    """`map` transforms a value and passes a fault on; `map_err` transforms a fault and passes a value on."""
    assert Ok(2).map(lambda number: number * 10) == Ok(20)
    assert Err("bad").map(lambda number: number * 10) == Err("bad")
    assert Err("bad").map_err(len) == Err(3)
    assert Ok(2).map_err(len) == Ok(2)


def test_flat_map_and_flat_map_err_continue_with_a_fallible_step() -> None:
    """`flat_map` runs the next fallible step on a value and skips it on a fault; `flat_map_err` recovers a fault."""
    assert Ok(2).flat_map(check_positive) == Ok(2)
    assert Ok(-1).flat_map(check_positive) == Err("-1 is not positive")
    assert Err("bad").flat_map(check_positive) == Err("bad")
    assert Err("bad").flat_map_err(lambda fault: check_positive(len(fault))) == Ok(3)
    assert Ok(2).flat_map_err(lambda fault: check_positive(len(fault))) == Ok(2)


def test_tap_and_tap_err_see_their_own_side_and_pass_the_result_on() -> None:
    """`tap` shows a value to its action and `tap_err` a fault to its own; each returns the result unchanged, and
    neither action runs on the other side."""
    seen_values: list[object] = []

    assert Ok(2).tap(seen_values.append) == Ok(2)
    assert Err("bad").tap(seen_values.append) == Err("bad")
    assert Err("bad").tap_err(seen_values.append) == Err("bad")
    assert Ok(2).tap_err(seen_values.append) == Ok(2)
    assert seen_values == [2, "bad"]


def test_ok_and_err_compare_by_side_and_content() -> None:
    """An `Ok` equals only an `Ok` of an equal value, an `Err` only an `Err` of an equal fault; each prints its side."""
    assert Ok(1) != Err(1)
    assert Err(1) != Ok(1)
    assert Ok(1) != Ok(2)
    assert (repr(Ok(1)), repr(Err("bad"))) == ("Ok(1)", "Err('bad')")
