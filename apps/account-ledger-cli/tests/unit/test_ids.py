"""Identifiers, days, and counts refuse malformed values, and markers print their parts."""

import pytest

from account_ledger.ids import (
    AccountId,
    AuthorizationId,
    CapitalizationId,
    Day,
    FeeId,
    IdFault,
    IncomingId,
    InstalmentCount,
    InstalmentId,
    InterestId,
    RefundId,
    parse_event_id,
    text,
)


def test_day_refuses_a_malformed_value() -> None:
    assert Day.parse("-1") == IdFault("day", "-1")
    assert Day.parse("1.5") == IdFault("day", "1.5")
    assert Day.parse("x") == IdFault("day", "x")
    assert Day.parse("6") == Day(6)
    assert Day(5).next() == Day(6)
    assert Day(1) <= Day(2)
    with pytest.raises(ValueError, match="a day is at least 0"):
        Day(-1)


def test_account_id_refuses_a_malformed_value() -> None:
    assert AccountId.parse("ACC-1") == IdFault("account ID", "ACC-1")
    assert AccountId.parse("acc-001") == IdFault("account ID", "acc-001")
    assert AccountId.parse("ACC-002") == AccountId("ACC-002")
    assert AccountId("ACC-002").number == "002"
    with pytest.raises(ValueError, match="an account ID is ACC- and three digits"):
        AccountId("ACC-1")


def test_authorization_id_refuses_a_malformed_value() -> None:
    assert AuthorizationId.parse("Auth-") == IdFault("hold ID", "Auth-")
    assert AuthorizationId.parse("Auth-A B") == IdFault("hold ID", "Auth-A B")
    assert AuthorizationId.parse("Auth-Z") == AuthorizationId("Auth-Z")
    with pytest.raises(ValueError, match="a hold ID is Auth- and letters or digits"):
        AuthorizationId("Auth-")


def test_event_id_refuses_a_malformed_value() -> None:
    acc_001 = AccountId("ACC-001")
    for malformed in ("FEE-1", "E", "e7", "E7-", "FEE-001-D2", "CAP-001@D", "INT-01-D2@D5", "REFUND-001-D2@6"):
        assert parse_event_id(malformed) == IdFault("event ID", malformed)
    assert parse_event_id("E7") == IncomingId("E7")
    assert parse_event_id("E10-1") == InstalmentId(IncomingId("E10"), 1)
    assert parse_event_id("FEE-001-D2@D5") == FeeId(acc_001, Day(2), Day(5))
    assert parse_event_id("REFUND-001-D2@D6") == RefundId(acc_001, Day(2), Day(6))
    assert parse_event_id("INT-001-D2@D5") == InterestId(acc_001, Day(2), Day(5))
    assert parse_event_id("CAP-001@D6") == CapitalizationId(acc_001, Day(6))
    with pytest.raises(ValueError, match="an incoming event ID is E and digits"):
        IncomingId("E")
    with pytest.raises(ValueError, match="an instalment is numbered from 1"):
        InstalmentId(IncomingId("E10"), 0)


def test_instalment_count_refuses_a_malformed_value() -> None:
    assert InstalmentCount.parse("1") == IdFault("instalment count", "1")
    assert InstalmentCount.parse("three") == IdFault("instalment count", "three")
    assert InstalmentCount.parse("3") == InstalmentCount(3)
    with pytest.raises(ValueError, match="an instalment count is at least 2"):
        InstalmentCount(1)


def test_a_marker_prints_its_kind_account_and_days() -> None:
    acc_002 = AccountId("ACC-002")
    for marker in ("E7", "E10-3", "FEE-002-D2@D5", "REFUND-002-D2@D6", "INT-002-D5@D6", "CAP-002@D6"):
        event_id = parse_event_id(marker)
        assert not isinstance(event_id, IdFault)
        assert text(event_id) == marker
    assert text(FeeId(acc_002, Day(4), Day(5))) == "FEE-002-D4@D5"
