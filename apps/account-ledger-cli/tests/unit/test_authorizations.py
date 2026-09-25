"""The authorization machine: every state and settlement input against the table, and the three decision rules."""

import pytest

from account_ledger.common.result import Err, Ok, Result
from account_ledger.domain.authorizations import (
    Approved,
    AuthorizationState,
    CannotSettle,
    Declined,
    FinalSettlement,
    PartiallySettled,
    PartialSettlement,
    Settled,
    SettlementInput,
    apply_settlement,
    sum_holds,
)
from account_ledger.domain.balances import compute_closing
from account_ledger.domain.model.config import CHALLENGE
from account_ledger.domain.model.event_log import (
    SettlementForcePosted,
)
from account_ledger.domain.model.events import SettlementKind
from account_ledger.domain.model.ids import Day
from account_ledger.domain.model.money import Aed, Amount
from account_ledger.domain.stream_processing import process_stream
from support.results import unwrap_ok
from support.states import list_settlements, list_states
from support.streams import ACC_001, list_fee_ids, make_authorization, make_credit, make_settlement
from support.values import make_aed


def test_amb_008_a_future_dated_credit_does_not_count_for_an_authorization() -> None:
    """AMB-008: an event value-dated in the future counts from its value date only."""
    stream = (make_credit("E1", 2, "100.00", value=3), make_authorization("E2", 2, "Auth-A", "50.00"))

    log = unwrap_ok(process_stream(stream, CHALLENGE)).find_log(Day(2))

    assert list_states(log, "Auth-A") == [Declined(Amount(make_aed("50.00")))]


def test_amb_009_a_later_credit_the_same_day_does_not_change_a_decline() -> None:
    """AMB-009: an authorization is decided when it arrives, and the decision is final."""
    stream = (make_authorization("E1", 2, "Auth-A", "50.00"), make_credit("E2", 2, "100.00"))

    log = unwrap_ok(process_stream(stream, CHALLENGE)).find_log(Day(2))

    assert list_states(log, "Auth-A") == [Declined(Amount(make_aed("50.00")))]


def test_amb_010_a_hold_counts_from_its_value_date() -> None:
    """AMB-010: a hold reduces the available balance from its authorization's value date."""
    stream = (make_credit("E1", 1, "100.00"), make_authorization("E2", 2, "Auth-A", "40.00", value=3))

    result = unwrap_ok(process_stream(stream, CHALLENGE))

    assert result.find_report(Day(2)).available_balances[ACC_001.id] == make_aed("100.00")
    assert result.find_report(Day(3)).available_balances[ACC_001.id] == make_aed("60.00")


@pytest.mark.parametrize("state", [Settled(Amount(make_aed("185.00"))), Declined(Amount(make_aed("90.00")))])
def test_an_unconfigured_transition_leaves_the_state_unchanged(state: AuthorizationState) -> None:
    """A settled or declined authorization has no configured transition for any settlement (tech-docs 001)."""
    assert apply_settlement(state, FinalSettlement(Amount(make_aed("10.00")))) == Err(CannotSettle())


def test_amb_029_a_settlement_against_a_declined_authorization_is_force_posted() -> None:
    """AMB-029: a settlement against a declined authorization posts its debit and releases no hold, as E6 does."""
    later_settlement = make_settlement("E3", 3, "Auth-A", "10.00")
    stream = (make_credit("E1", 1, "20.00"), make_authorization("E2", 2, "Auth-A", "50.00"), later_settlement)

    log = unwrap_ok(process_stream(stream, CHALLENGE)).find_log(Day(3))

    assert list_settlements(log, "E3") == [SettlementForcePosted(later_settlement, Day(3))]
    assert list_states(log, "Auth-A") == [Declined(Amount(make_aed("50.00")))]
    assert unwrap_ok(compute_closing(log, ACC_001, Day(3))) == make_aed("10.00")


def test_amb_029_a_settlement_after_a_final_one_is_force_posted() -> None:
    """AMB-029: a new settlement against an authorization whose hold a final settlement already released posts its
    debit and releases no hold."""
    second_settlement = make_settlement("E4", 4, "Auth-A", "20.00")
    stream = (
        make_credit("E1", 1, "100.00"),
        make_authorization("E2", 2, "Auth-A", "40.00"),
        make_settlement("E3", 3, "Auth-A", "40.00"),
        second_settlement,
    )

    log = unwrap_ok(process_stream(stream, CHALLENGE)).find_log(Day(4))

    assert list_settlements(log, "E4") == [SettlementForcePosted(second_settlement, Day(4))]
    assert list_states(log, "Auth-A") == [Settled(Amount(make_aed("40.00")))]
    assert unwrap_ok(compute_closing(log, ACC_001, Day(4))) == make_aed("40.00")


def test_amb_013_a_non_final_settlement_keeps_the_rest_of_the_hold() -> None:
    """AMB-013: a settlement marked as followed by more settlements debits its amount and keeps the rest on hold; a
    final one of the rest then settles the authorization for the settlements' sum and releases what is left."""
    stream = (
        make_credit("E1", 1, "500.00"),
        make_authorization("E2", 1, "Auth-A", "200.00"),
        make_settlement("E3", 2, "Auth-A", "120.00", kind=SettlementKind.PARTIAL),
        make_settlement("E4", 3, "Auth-A", "40.00"),
    )

    result = unwrap_ok(process_stream(stream, CHALLENGE))

    assert list_states(result.find_log(Day(2)), "Auth-A") == [
        PartiallySettled(Amount(make_aed("120.00")), Amount(make_aed("80.00")))
    ]
    assert result.find_report(Day(2)).available_balances[ACC_001.id] == make_aed("300.00")
    assert list_states(result.find_log(Day(3)), "Auth-A") == [Settled(Amount(make_aed("160.00")))]
    assert result.find_report(Day(3)).available_balances[ACC_001.id] == make_aed("340.00")


@pytest.mark.parametrize(
    ("partial_amounts", "settled_amount"),
    [
        (("200.00",), "200.00"),
        (("250.00",), "250.00"),
        (("120.00", "80.00"), "200.00"),
        (("120.00", "95.00"), "215.00"),
    ],
)
def test_amb_013_partial_settlements_reaching_the_hold_settle(
    partial_amounts: tuple[str, ...], settled_amount: str
) -> None:
    """AMB-013, tech-docs 001: a partial settlement that reaches the remaining hold leaves nothing to keep, so it
    settles the authorization for the settlements' sum, since a partially settled hold is always above zero."""
    parts = tuple(
        make_settlement(f"E{3 + index}", 2, "Auth-A", amount, kind=SettlementKind.PARTIAL)
        for index, amount in enumerate(partial_amounts)
    )
    stream = (make_credit("E1", 1, "500.00"), make_authorization("E2", 1, "Auth-A", "200.00"), *parts)

    result = unwrap_ok(process_stream(stream, CHALLENGE))

    assert list_states(result.find_log(Day(2)), "Auth-A") == [Settled(Amount(make_aed(settled_amount)))]
    assert (
        result.find_report(Day(2)).available_balances[ACC_001.id]
        == result.find_report(Day(2)).closing_balances[ACC_001.id]
    )


def make_aed_amount(text: str) -> Amount[Aed]:
    """An AED amount for the transition table."""
    return Amount(make_aed(text))


TABLE: list[tuple[AuthorizationState, SettlementInput, Result[AuthorizationState, CannotSettle]]] = [
    (
        Approved(make_aed_amount("200.00")),
        FinalSettlement(make_aed_amount("185.00")),
        Ok(Settled(make_aed_amount("185.00"))),
    ),
    (
        Approved(make_aed_amount("200.00")),
        PartialSettlement(make_aed_amount("120.00")),
        Ok(PartiallySettled(make_aed_amount("120.00"), make_aed_amount("80.00"))),
    ),
    (
        Approved(make_aed_amount("200.00")),
        PartialSettlement(make_aed_amount("200.00")),
        Ok(Settled(make_aed_amount("200.00"))),
    ),
    (
        PartiallySettled(make_aed_amount("120.00"), make_aed_amount("80.00")),
        FinalSettlement(make_aed_amount("40.00")),
        Ok(Settled(make_aed_amount("160.00"))),
    ),
    (
        PartiallySettled(make_aed_amount("120.00"), make_aed_amount("80.00")),
        PartialSettlement(make_aed_amount("30.00")),
        Ok(PartiallySettled(make_aed_amount("150.00"), make_aed_amount("50.00"))),
    ),
    (
        PartiallySettled(make_aed_amount("120.00"), make_aed_amount("80.00")),
        PartialSettlement(make_aed_amount("80.00")),
        Ok(Settled(make_aed_amount("200.00"))),
    ),
    (Settled(make_aed_amount("185.00")), FinalSettlement(make_aed_amount("10.00")), Err(CannotSettle())),
    (Settled(make_aed_amount("185.00")), PartialSettlement(make_aed_amount("10.00")), Err(CannotSettle())),
    (Declined(make_aed_amount("90.00")), FinalSettlement(make_aed_amount("10.00")), Err(CannotSettle())),
    (Declined(make_aed_amount("90.00")), PartialSettlement(make_aed_amount("10.00")), Err(CannotSettle())),
]


@pytest.mark.parametrize(("state", "settlement_input", "expected_state"), TABLE)
def test_every_state_and_settlement_input_pair_follows_the_table(
    state: AuthorizationState,
    settlement_input: SettlementInput,
    expected_state: Result[AuthorizationState, CannotSettle],
) -> None:
    """AMB-012, AMB-013, AMB-029, tech-docs 001: every state meets both settlement inputs, each guard on both sides,
    and each pair goes where the declared table says."""
    assert apply_settlement(state, settlement_input) == expected_state


def test_amb_030_a_settlement_above_its_hold_debits_in_full() -> None:
    """AMB-030: a settlement above its hold posts its whole amount and releases the hold; the balance may go negative,
    and the fee rule then applies as for any negative day."""
    stream = (
        make_credit("E1", 1, "100.00"),
        make_authorization("E2", 1, "Auth-A", "80.00"),
        make_settlement("E3", 2, "Auth-A", "120.00"),
    )

    log = unwrap_ok(process_stream(stream, CHALLENGE)).find_log(Day(2))

    assert list_states(log, "Auth-A") == [Settled(Amount(make_aed("120.00")))]
    assert unwrap_ok(sum_holds(log, ACC_001, Day(2))) == make_aed("0.00")
    assert list_fee_ids(log) == ["FEE-001-D2@D2"]
    assert unwrap_ok(compute_closing(log, ACC_001, Day(2))) == make_aed("-45.00")
