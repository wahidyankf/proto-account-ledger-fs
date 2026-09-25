"""Identifiers, days, and counts refuse malformed values, and generated IDs print their parts."""

import pytest

from account_ledger.common.result import Err, Ok
from account_ledger.domain.model.ids import (
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
    format_id,
    parse_event_id,
)
from support.results import unwrap_ok


def test_day_refuses_a_malformed_value() -> None:
    """A day is a whole number from 0; any other text is a fault, and a negative day is a bug."""
    assert Day.parse("-1") == Err(IdFault("day", "-1"))
    assert Day.parse("1.5") == Err(IdFault("day", "1.5"))
    assert Day.parse("x") == Err(IdFault("day", "x"))
    assert Day.parse("6") == Ok(Day(6))
    assert Day.make(-1) == Err(IdFault("day", "-1"))
    assert Day.make(0) == Ok(Day(0))
    assert Day(5).advance() == Day(6)
    assert Day(1) <= Day(2)
    with pytest.raises(ValueError, match="a day is at least 0"):
        Day(-1)


def test_account_id_refuses_a_malformed_value() -> None:
    """An account ID is `ACC-` and three digits; any other text is a fault."""
    assert AccountId.parse("ACC-1") == Err(IdFault("account ID", "ACC-1"))
    assert AccountId.parse("acc-001") == Err(IdFault("account ID", "acc-001"))
    assert AccountId.parse("ACC-002") == Ok(AccountId("ACC-002"))
    assert AccountId("ACC-002").number == "002"
    with pytest.raises(ValueError, match="an account ID is ACC- and three digits"):
        AccountId("ACC-1")


def test_authorization_id_refuses_a_malformed_value() -> None:
    """A hold ID is `Auth-` and letters or digits; any other text is a fault."""
    assert AuthorizationId.parse("Auth-") == Err(IdFault("hold ID", "Auth-"))
    assert AuthorizationId.parse("Auth-A B") == Err(IdFault("hold ID", "Auth-A B"))
    assert AuthorizationId.parse("Auth-Z") == Ok(AuthorizationId("Auth-Z"))
    with pytest.raises(ValueError, match="a hold ID is Auth- and letters or digits"):
        AuthorizationId("Auth-")


def test_event_id_refuses_a_malformed_value() -> None:
    """Every event ID form parses, the incoming ones and each ID the ledger generates; any other text is a fault."""
    acc_001 = AccountId("ACC-001")
    for malformed_id in ("FEE-1", "E", "e7", "E7-", "FEE-001-D2", "CAP-001@D", "INT-01-D2@D5", "REFUND-001-D2@6"):
        assert parse_event_id(malformed_id) == Err(IdFault("event ID", malformed_id))
    assert parse_event_id("E7") == Ok(IncomingId("E7"))
    assert parse_event_id("E10-1") == Ok(InstalmentId(IncomingId("E10"), 1))
    assert parse_event_id("FEE-001-D2@D5") == Ok(FeeId(acc_001, Day(2), Day(5)))
    assert parse_event_id("REFUND-001-D2@D6") == Ok(RefundId(acc_001, Day(2), Day(6)))
    assert parse_event_id("INT-001-D2@D5") == Ok(InterestId(acc_001, Day(2), Day(5)))
    assert parse_event_id("CAP-001@D6") == Ok(CapitalizationId(acc_001, Day(6)))
    with pytest.raises(ValueError, match="an incoming event ID is E and digits"):
        IncomingId("E")
    with pytest.raises(ValueError, match="an instalment is numbered from 1"):
        InstalmentId(IncomingId("E10"), 0)


def test_instalment_count_refuses_a_malformed_value() -> None:
    """An instalment count is a whole number from 2 to 360 (NUMBERS.md); any other text is a fault."""
    assert InstalmentCount.parse("1") == Err(IdFault("instalment count", "1"))
    assert InstalmentCount.parse("three") == Err(IdFault("instalment count", "three"))
    assert InstalmentCount.parse("3") == Ok(InstalmentCount(3))
    assert InstalmentCount.make(1) == Err(IdFault("instalment count", "1"))
    assert InstalmentCount.parse("360") == Ok(InstalmentCount(360))
    assert InstalmentCount.parse("361") == Err(IdFault("instalment count", "361"))
    with pytest.raises(ValueError, match="an instalment count is from 2 to 360"):
        InstalmentCount(1)
    with pytest.raises(ValueError, match="an instalment count is from 2 to 360"):
        InstalmentCount(361)


def test_a_generated_id_prints_its_kind_account_and_days() -> None:
    """Every event ID prints back as the text it was parsed from."""
    acc_002 = AccountId("ACC-002")
    for event_id in ("E7", "E10-3", "FEE-002-D2@D5", "REFUND-002-D2@D6", "INT-002-D5@D6", "CAP-002@D6"):
        assert format_id(unwrap_ok(parse_event_id(event_id))) == event_id
    assert format_id(FeeId(acc_002, Day(4), Day(5))) == "FEE-002-D4@D5"
