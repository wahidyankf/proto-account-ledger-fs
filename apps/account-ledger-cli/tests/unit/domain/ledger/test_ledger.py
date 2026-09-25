"""The Ledger: what spans accounts, checked before the account decides: a repeated event ID (AMB-034), a reversal of
another account's event (AMB-036), and an account the ledger does not hold."""

import pytest

from account_ledger.challenge import CHALLENGE
from account_ledger.common.result import Err
from account_ledger.domain.account.domain_events import CreditPosted, DuplicateIgnored, EventRejected
from account_ledger.domain.account.rejections import IdReused, TargetOnAnotherAccount
from account_ledger.domain.ledger.ledger import Ledger, UnknownAccount
from account_ledger.domain.model.ids import AccountId, Day, IncomingId
from account_ledger.domain.stream_processing import (
    process_stream,
)
from support.results import unwrap_ok
from support.states import list_entries
from support.streams import (
    ACC_001,
    ACC_002,
    make_authorization,
    make_credit,
    make_debit,
    make_reversal,
    make_settlement,
)
from support.values import make_aed, make_bhd


def test_amb_034_a_repeated_event_is_logged_as_a_duplicate_with_no_effect() -> None:
    """AMB-034: the event ID is the idempotency key, so E1 delivered twice with identical content is logged again as a
    duplicate and credits once; a duplicate is not an error, so Day 1's errors read none."""
    e1 = make_credit("E1", 1, "100.00")

    result = unwrap_ok(process_stream((e1, e1), CHALLENGE))
    log = result.find_log(Day(1))

    assert list_entries(log, "E1") == [CreditPosted(e1, Day(1)), DuplicateIgnored(e1, Day(1))]
    assert unwrap_ok(Ledger(CHALLENGE, log).find_account(ACC_001).compute_closing(Day(1))) == make_aed("100.00")
    assert dict(result.find_report(Day(1)).errors) == {ACC_001.id: (), ACC_002.id: ()}


@pytest.mark.parametrize(
    "kind",
    ["reversal", "settlement"],
)
def test_amb_034_a_repeated_reversal_or_settlement_is_a_duplicate(kind: str) -> None:
    """AMB-028, AMB-029, AMB-034: a reversal or a settlement delivered again with identical content is a retry, logged
    as a duplicate with no effect and no error."""
    opening = (
        make_credit("E1", 1, "100.00"),
        make_debit("E2", 1, "30.00"),
        make_authorization("E3", 1, "Auth-A", "20.00"),
    )
    repeated_event = make_reversal("E4", 1, "E2") if kind == "reversal" else make_settlement("E4", 1, "Auth-A", "20.00")

    result = unwrap_ok(process_stream((*opening, repeated_event, repeated_event), CHALLENGE))
    single_log = unwrap_ok(process_stream((*opening, repeated_event), CHALLENGE)).find_log(Day(1))
    log = result.find_log(Day(1))

    assert list_entries(log, "E4")[1:] == [DuplicateIgnored(repeated_event, Day(1))]
    assert (
        unwrap_ok(Ledger(CHALLENGE, log).find_account(ACC_001).compute_closing(Day(1))),
        unwrap_ok(Ledger(CHALLENGE, log).find_account(ACC_001).sum_holds(Day(1))),
    ) == (
        unwrap_ok(Ledger(CHALLENGE, single_log).find_account(ACC_001).compute_closing(Day(1))),
        unwrap_ok(Ledger(CHALLENGE, single_log).find_account(ACC_001).sum_holds(Day(1))),
    )
    assert dict(result.find_report(Day(1)).errors) == {ACC_001.id: (), ACC_002.id: ()}


def test_amb_034_the_same_event_booked_another_day_is_refused() -> None:
    """AMB-034: a duplicate equals the first in every field, the booked day included, so E1 booked again on Day 2 with
    the same value date and amount reuses its ID and is refused."""
    first_credit, retried_credit = make_credit("E1", 1, "100.00"), make_credit("E1", 2, "100.00", value=1)

    log = unwrap_ok(process_stream((first_credit, retried_credit), CHALLENGE)).find_log(Day(2))

    assert list_entries(log, "E1") == [
        CreditPosted(first_credit, Day(1)),
        EventRejected(retried_credit, Day(2), IdReused()),
    ]
    assert unwrap_ok(Ledger(CHALLENGE, log).find_account(ACC_001).compute_closing(Day(2))) == make_aed("100.00")


def test_amb_034_a_reused_id_with_different_content_is_refused() -> None:
    """AMB-034: a second E1 that differs from the first in any field is refused and moves no balance."""
    first_credit, reused_credit = make_credit("E1", 1, "100.00"), make_credit("E1", 1, "90.00")

    log = unwrap_ok(process_stream((first_credit, reused_credit), CHALLENGE)).find_log(Day(1))

    assert list_entries(log, "E1") == [
        CreditPosted(first_credit, Day(1)),
        EventRejected(reused_credit, Day(1), IdReused()),
    ]
    assert unwrap_ok(Ledger(CHALLENGE, log).find_account(ACC_001).compute_closing(Day(1))) == make_aed("100.00")


def test_amb_036_a_reversal_of_another_accounts_event_is_refused() -> None:
    """AMB-036: a reversal undoes an event on its own account only, so ACC-002's reversal of ACC-001's E7 is refused,
    moves neither balance, and leaves E7 for ACC-001 to reverse."""
    misplaced_reversal = make_reversal("E12", 2, "E7", account="ACC-002")
    stream = (
        make_credit("E1", 1, "1000.00"),
        make_debit("E7", 1, "620.00"),
        make_credit("E2", 1, "100.000", account="ACC-002"),
        misplaced_reversal,
        make_reversal("E9", 2, "E7"),
    )

    log = unwrap_ok(process_stream(stream, CHALLENGE)).find_log(Day(2))

    assert list_entries(log, "E12") == [
        EventRejected(misplaced_reversal, Day(2), TargetOnAnotherAccount(IncomingId("E7"), ACC_001.id))
    ]
    assert unwrap_ok(Ledger(CHALLENGE, log).find_account(ACC_002).compute_closing(Day(2))) == make_bhd("100.000")
    assert unwrap_ok(Ledger(CHALLENGE, log).find_account(ACC_001).compute_closing(Day(2))) == make_aed("1000.00")


def test_an_event_on_an_unconfigured_account_is_an_internal_fault() -> None:
    """An event on an account the ledger does not hold, which only a bug brings since the stream reader refuses one,
    is returned as an internal fault naming the account."""
    credit = make_credit("E1", 1, "100.00", account="ACC-003")

    assert Ledger.open(CHALLENGE).process_event(credit, Day(1)) == Err(UnknownAccount(AccountId("ACC-003")))
