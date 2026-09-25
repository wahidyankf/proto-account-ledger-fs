"""Processing an incoming event: idempotency (AMB-034)."""

import pytest

from account_ledger.domain.authorizations import holds
from account_ledger.domain.balances import closing
from account_ledger.domain.model.config import CHALLENGE
from account_ledger.domain.model.event_log import Accepted, Duplicate, IdReused, Rejected
from account_ledger.domain.model.ids import Day
from account_ledger.domain.replay import replay
from support.states import entries_for
from support.streams import ACC_001, ACC_002, authorization, credit, debit, reversal, settlement
from support.values import aed


def test_amb_034_a_repeated_event_is_logged_as_a_duplicate_with_no_effect() -> None:
    """AMB-034: the event ID is the idempotency key, so E1 delivered twice with identical content is logged again as a
    duplicate and credits once; a duplicate is not an error, so Day 1's errors read none."""
    e1 = credit("E1", 1, "100.00")

    result = replay((e1, e1), CHALLENGE)
    log = result.log_at(Day(1))

    assert entries_for(log, "E1") == [Accepted(e1, Day(1)), Duplicate(e1, Day(1))]
    assert closing(log, ACC_001, Day(1)) == aed("100.00")
    assert dict(result.report(Day(1)).errors) == {ACC_001.id: (), ACC_002.id: ()}


@pytest.mark.parametrize(
    "kind",
    ["reversal", "settlement"],
)
def test_amb_034_a_repeated_reversal_or_settlement_is_a_duplicate(kind: str) -> None:
    """AMB-028, AMB-029, AMB-034: a reversal or a settlement delivered again with identical content is a retry, logged
    as a duplicate with no effect and no error."""
    opening = (credit("E1", 1, "100.00"), debit("E2", 1, "30.00"), authorization("E3", 1, "Auth-A", "20.00"))
    repeated = reversal("E4", 1, "E2") if kind == "reversal" else settlement("E4", 1, "Auth-A", "20.00")

    result = replay((*opening, repeated, repeated), CHALLENGE)
    once = replay((*opening, repeated), CHALLENGE).log_at(Day(1))
    log = result.log_at(Day(1))

    assert entries_for(log, "E4")[1:] == [Duplicate(repeated, Day(1))]
    assert (closing(log, ACC_001, Day(1)), holds(log, ACC_001, Day(1))) == (
        closing(once, ACC_001, Day(1)),
        holds(once, ACC_001, Day(1)),
    )
    assert dict(result.report(Day(1)).errors) == {ACC_001.id: (), ACC_002.id: ()}


def test_amb_034_the_same_event_booked_another_day_is_refused() -> None:
    """AMB-034: a duplicate equals the first in every field, the booked day included, so E1 booked again on Day 2 with
    the same value day and amount reuses its ID and is refused."""
    first, again = credit("E1", 1, "100.00"), credit("E1", 2, "100.00", value=1)

    log = replay((first, again), CHALLENGE).log_at(Day(2))

    assert entries_for(log, "E1") == [Accepted(first, Day(1)), Rejected(again, Day(2), IdReused())]
    assert closing(log, ACC_001, Day(2)) == aed("100.00")


def test_amb_034_a_reused_id_with_different_content_is_refused() -> None:
    """AMB-034: a second E1 that differs from the first in any field is refused and moves no balance."""
    first, reused = credit("E1", 1, "100.00"), credit("E1", 1, "90.00")

    log = replay((first, reused), CHALLENGE).log_at(Day(1))

    assert entries_for(log, "E1") == [Accepted(first, Day(1)), Rejected(reused, Day(1), IdReused())]
    assert closing(log, ACC_001, Day(1)) == aed("100.00")
