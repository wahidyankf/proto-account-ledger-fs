"""The authorization machine: every state against both settlement kinds and each guard, as the declared table (D8)
says."""

import pytest

from account_ledger.common.result import Err, Ok, Result
from account_ledger.domain.account.authorizations import (
    Approved,
    AuthorizationState,
    CannotSettle,
    Declined,
    PartiallySettled,
    Settled,
    apply_settlement,
)
from account_ledger.domain.model.events import SettlementKind
from account_ledger.domain.model.money import Aed, Amount, AmountIn
from support.values import make_aed


@pytest.mark.parametrize("state", [Settled(AmountIn(make_aed("185.00"))), Declined(AmountIn(make_aed("90.00")))])
def test_an_unconfigured_transition_leaves_the_state_unchanged(state: AuthorizationState) -> None:
    """A settled or declined authorization has no configured transition for any settlement (tech-docs 001)."""
    assert apply_settlement(state, SettlementKind.FINAL, AmountIn(make_aed("10.00"))) == Err(CannotSettle())


def make_aed_amount(text: str) -> AmountIn[Aed]:
    """An AED amount for the transition table."""
    return AmountIn(make_aed(text))


TABLE: list[tuple[AuthorizationState, SettlementKind, Amount, Result[AuthorizationState, CannotSettle]]] = [
    (
        Approved(make_aed_amount("200.00")),
        SettlementKind.FINAL,
        make_aed_amount("185.00"),
        Ok(Settled(make_aed_amount("185.00"))),
    ),
    (
        Approved(make_aed_amount("200.00")),
        SettlementKind.PARTIAL,
        make_aed_amount("120.00"),
        Ok(PartiallySettled(make_aed_amount("120.00"), make_aed_amount("80.00"))),
    ),
    (
        Approved(make_aed_amount("200.00")),
        SettlementKind.PARTIAL,
        make_aed_amount("200.00"),
        Ok(Settled(make_aed_amount("200.00"))),
    ),
    (
        PartiallySettled(make_aed_amount("120.00"), make_aed_amount("80.00")),
        SettlementKind.FINAL,
        make_aed_amount("40.00"),
        Ok(Settled(make_aed_amount("160.00"))),
    ),
    (
        PartiallySettled(make_aed_amount("120.00"), make_aed_amount("80.00")),
        SettlementKind.PARTIAL,
        make_aed_amount("30.00"),
        Ok(PartiallySettled(make_aed_amount("150.00"), make_aed_amount("50.00"))),
    ),
    (
        PartiallySettled(make_aed_amount("120.00"), make_aed_amount("80.00")),
        SettlementKind.PARTIAL,
        make_aed_amount("80.00"),
        Ok(Settled(make_aed_amount("200.00"))),
    ),
    (Settled(make_aed_amount("185.00")), SettlementKind.FINAL, make_aed_amount("10.00"), Err(CannotSettle())),
    (Settled(make_aed_amount("185.00")), SettlementKind.PARTIAL, make_aed_amount("10.00"), Err(CannotSettle())),
    (Declined(make_aed_amount("90.00")), SettlementKind.FINAL, make_aed_amount("10.00"), Err(CannotSettle())),
    (Declined(make_aed_amount("90.00")), SettlementKind.PARTIAL, make_aed_amount("10.00"), Err(CannotSettle())),
]


@pytest.mark.parametrize(("state", "kind", "amount", "expected_state"), TABLE)
def test_every_state_and_settlement_input_pair_follows_the_table(
    state: AuthorizationState,
    kind: SettlementKind,
    amount: Amount,
    expected_state: Result[AuthorizationState, CannotSettle],
) -> None:
    """AMB-012, AMB-013, AMB-029, tech-docs 001: every state meets both settlement inputs, each guard on both sides,
    and each pair goes where the declared table says."""
    assert apply_settlement(state, kind, amount) == expected_state
