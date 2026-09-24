"""The authorization machine: every state and trigger against the table, and the three decision rules."""

import pytest

from account_ledger.authorizations import AuthorizationState, Declined, NoTransition, Settled, SettleFinal, transition
from account_ledger.balances import closing
from account_ledger.config import CHALLENGE
from account_ledger.ids import Day
from account_ledger.log import ForcePosted, SettlementAccepted
from account_ledger.money import Amount
from account_ledger.replay import replay
from support.states import settlements_of, state_of
from support.streams import ACC_001, authorization, credit, settlement
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
