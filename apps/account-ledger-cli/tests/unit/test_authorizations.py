"""The authorization machine: every state and trigger against the table, and the three decision rules."""

import pytest

from account_ledger.domain.authorizations import (
    Approved,
    AuthorizationState,
    Declined,
    NoTransition,
    PartiallySettled,
    Settled,
    SettleFinal,
    SettlePartial,
    Trigger,
    holds,
    transition,
)
from account_ledger.domain.balances import closing
from account_ledger.domain.model.config import CHALLENGE
from account_ledger.domain.model.event_log import ForcePosted, SettlementAccepted
from account_ledger.domain.model.events import Capture
from account_ledger.domain.model.ids import Day
from account_ledger.domain.model.money import Aed, Amount
from account_ledger.domain.replay import replay
from support.states import settlements_of, state_of
from support.streams import ACC_001, authorization, credit, fee_markers, settlement
from support.values import aed


def test_amb_008_a_future_dated_credit_does_not_count_for_an_authorization() -> None:
    """AMB-008: an event value-dated in the future counts from its value date only."""
    stream = (credit("E1", 2, "100.00", value=3), authorization("E2", 2, "Auth-A", "50.00"))

    log = replay(stream, CHALLENGE).log_at(Day(2))

    assert state_of(log, "Auth-A") == [Declined(Amount(aed("50.00")))]


def test_amb_009_a_later_credit_the_same_day_does_not_rescue_a_decline() -> None:
    """AMB-009: an authorization is decided when it arrives, and the decision is final."""
    stream = (authorization("E1", 2, "Auth-A", "50.00"), credit("E2", 2, "100.00"))

    log = replay(stream, CHALLENGE).log_at(Day(2))

    assert state_of(log, "Auth-A") == [Declined(Amount(aed("50.00")))]


def test_amb_010_a_hold_counts_from_its_value_date() -> None:
    """AMB-010: a hold reduces the available balance from its authorization's value date."""
    stream = (credit("E1", 1, "100.00"), authorization("E2", 2, "Auth-A", "40.00", value=3))

    result = replay(stream, CHALLENGE)

    assert result.report(Day(2)).available[ACC_001.id] == aed("100.00")
    assert result.report(Day(3)).available[ACC_001.id] == aed("60.00")


@pytest.mark.parametrize("state", [Settled(Amount(aed("185.00"))), Declined(Amount(aed("90.00")))])
def test_an_unconfigured_transition_leaves_the_state_unchanged(state: AuthorizationState) -> None:
    """A settled or declined authorization has no configured transition for any trigger (tech-docs 001)."""
    assert transition(state, SettleFinal(Amount(aed("10.00")))) == NoTransition()


def test_amb_029_a_settlement_against_a_declined_authorization_is_force_posted() -> None:
    """AMB-029: a settlement against a declined authorization posts its debit and releases no hold, as E6 does."""
    later = settlement("E3", 3, "Auth-A", "10.00")
    stream = (credit("E1", 1, "20.00"), authorization("E2", 2, "Auth-A", "50.00"), later)

    log = replay(stream, CHALLENGE).log_at(Day(3))

    assert settlements_of(log, "E3") == [SettlementAccepted(later, Day(3), ForcePosted())]
    assert state_of(log, "Auth-A") == [Declined(Amount(aed("50.00")))]
    assert closing(log, ACC_001, Day(3)) == aed("10.00")


def test_amb_029_a_settlement_after_a_final_one_is_force_posted() -> None:
    """AMB-029: a new settlement against an authorization whose hold a final settlement already released posts its
    debit and releases no hold."""
    second = settlement("E4", 4, "Auth-A", "20.00")
    stream = (
        credit("E1", 1, "100.00"),
        authorization("E2", 2, "Auth-A", "40.00"),
        settlement("E3", 3, "Auth-A", "40.00"),
        second,
    )

    log = replay(stream, CHALLENGE).log_at(Day(4))

    assert settlements_of(log, "E4") == [SettlementAccepted(second, Day(4), ForcePosted())]
    assert state_of(log, "Auth-A") == [Settled(Amount(aed("40.00")))]
    assert closing(log, ACC_001, Day(4)) == aed("40.00")


def test_amb_013_a_non_final_settlement_keeps_the_rest_of_the_hold() -> None:
    """AMB-013: a settlement marked as followed by more captures debits its amount and keeps the rest on hold; a final
    one of the rest then settles the authorization for the captures' sum and releases what is left."""
    stream = (
        credit("E1", 1, "500.00"),
        authorization("E2", 1, "Auth-A", "200.00"),
        settlement("E3", 2, "Auth-A", "120.00", capture=Capture.PARTIAL),
        settlement("E4", 3, "Auth-A", "40.00"),
    )

    result = replay(stream, CHALLENGE)

    assert state_of(result.log_at(Day(2)), "Auth-A") == [PartiallySettled(Amount(aed("120.00")), Amount(aed("80.00")))]
    assert result.report(Day(2)).available[ACC_001.id] == aed("300.00")
    assert state_of(result.log_at(Day(3)), "Auth-A") == [Settled(Amount(aed("160.00")))]
    assert result.report(Day(3)).available[ACC_001.id] == aed("340.00")


@pytest.mark.parametrize(
    ("captures", "settled"),
    [
        (("200.00",), "200.00"),
        (("250.00",), "250.00"),
        (("120.00", "80.00"), "200.00"),
        (("120.00", "95.00"), "215.00"),
    ],
)
def test_amb_013_a_partial_capture_reaching_the_hold_settles(captures: tuple[str, ...], settled: str) -> None:
    """AMB-013, tech-docs 001: a partial settlement that reaches the remaining hold leaves nothing to keep, so it
    settles the authorization for the captures' sum, since a partially settled hold is always above zero."""
    parts = tuple(
        settlement(f"E{3 + n}", 2, "Auth-A", amount, capture=Capture.PARTIAL) for n, amount in enumerate(captures)
    )
    stream = (credit("E1", 1, "500.00"), authorization("E2", 1, "Auth-A", "200.00"), *parts)

    result = replay(stream, CHALLENGE)

    assert state_of(result.log_at(Day(2)), "Auth-A") == [Settled(Amount(aed(settled)))]
    assert result.report(Day(2)).available[ACC_001.id] == result.report(Day(2)).closing[ACC_001.id]


def aed_amount(text: str) -> Amount[Aed]:
    """An AED amount for the transition table."""
    return Amount(aed(text))


TABLE: list[tuple[AuthorizationState, Trigger, AuthorizationState | NoTransition]] = [
    (Approved(aed_amount("200.00")), SettleFinal(aed_amount("185.00")), Settled(aed_amount("185.00"))),
    (
        Approved(aed_amount("200.00")),
        SettlePartial(aed_amount("120.00")),
        PartiallySettled(aed_amount("120.00"), aed_amount("80.00")),
    ),
    (Approved(aed_amount("200.00")), SettlePartial(aed_amount("200.00")), Settled(aed_amount("200.00"))),
    (
        PartiallySettled(aed_amount("120.00"), aed_amount("80.00")),
        SettleFinal(aed_amount("40.00")),
        Settled(aed_amount("160.00")),
    ),
    (
        PartiallySettled(aed_amount("120.00"), aed_amount("80.00")),
        SettlePartial(aed_amount("30.00")),
        PartiallySettled(aed_amount("150.00"), aed_amount("50.00")),
    ),
    (
        PartiallySettled(aed_amount("120.00"), aed_amount("80.00")),
        SettlePartial(aed_amount("80.00")),
        Settled(aed_amount("200.00")),
    ),
    (Settled(aed_amount("185.00")), SettleFinal(aed_amount("10.00")), NoTransition()),
    (Settled(aed_amount("185.00")), SettlePartial(aed_amount("10.00")), NoTransition()),
    (Declined(aed_amount("90.00")), SettleFinal(aed_amount("10.00")), NoTransition()),
    (Declined(aed_amount("90.00")), SettlePartial(aed_amount("10.00")), NoTransition()),
]


@pytest.mark.parametrize(("state", "trigger", "after"), TABLE)
def test_every_state_and_trigger_pair_follows_the_table(
    state: AuthorizationState, trigger: Trigger, after: AuthorizationState | NoTransition
) -> None:
    """AMB-012, AMB-013, AMB-029, tech-docs 001: every state meets both triggers, each guard on both sides, and each
    pair goes where the declared table says."""
    assert transition(state, trigger) == after


def test_amb_030_a_settlement_above_its_hold_debits_in_full() -> None:
    """AMB-030: a settlement above its hold posts its whole amount and releases the hold; the balance may go negative,
    and the fee rule then applies as for any negative day."""
    stream = (
        credit("E1", 1, "100.00"),
        authorization("E2", 1, "Auth-A", "80.00"),
        settlement("E3", 2, "Auth-A", "120.00"),
    )

    log = replay(stream, CHALLENGE).log_at(Day(2))

    assert state_of(log, "Auth-A") == [Settled(Amount(aed("120.00")))]
    assert holds(log, ACC_001, Day(2)) == aed("0.00")
    assert fee_markers(log) == ["FEE-001-D2@D2"]
    assert closing(log, ACC_001, Day(2)) == aed("-45.00")
