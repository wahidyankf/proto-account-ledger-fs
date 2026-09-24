"""The stream reader: a valid stream parses to its events; each fault names its line."""

from account_ledger.config import CHALLENGE
from account_ledger.events import Authorization, Capture, Credit, Debit, Instalments, Reversal, Settlement, Whole
from account_ledger.ids import AccountId, AuthorizationId, Day, FeeId, IncomingId, InstalmentCount
from account_ledger.money import Amount
from account_ledger.stream_csv import StreamError, parse_stream
from support.streams import HEADER, csv_text
from support.values import aed, bhd

ACC_001, ACC_002 = AccountId("ACC-001"), AccountId("ACC-002")


def test_a_valid_stream_parses_to_its_events() -> None:
    text = csv_text(
        [
            {
                "event": "E1",
                "booked": "1",
                "type": "CREDIT",
                "account": "ACC-001",
                "amount": "1200.00",
                "value_date": "1",
            },
            {
                "event": "E2",
                "booked": "1",
                "type": "DEBIT",
                "account": "ACC-001",
                "amount": "950.00",
                "value_date": "1",
            },
            {
                "event": "E3",
                "booked": "2",
                "type": "AUTHORIZATION",
                "account": "ACC-001",
                "amount": "200.00",
                "value_date": "2",
                "reference": "Auth-A",
            },
            {
                "event": "E5",
                "booked": "4",
                "type": "SETTLEMENT",
                "account": "ACC-001",
                "amount": "185.00",
                "value_date": "4",
                "reference": "Auth-A",
            },
            {
                "event": "E9",
                "booked": "6",
                "type": "REVERSAL",
                "account": "ACC-001",
                "value_date": "2",
                "reference": "E7",
            },
            {
                "event": "E10",
                "booked": "5",
                "type": "CREDIT",
                "account": "ACC-002",
                "amount": "10.000",
                "value_date": "5",
                "instalments": "3",
            },
        ]
    )

    assert parse_stream(text, CHALLENGE) == (
        Credit(IncomingId("E1"), Day(1), ACC_001, Day(1), Amount(aed("1200.00")), Whole()),
        Debit(IncomingId("E2"), Day(1), ACC_001, Day(1), Amount(aed("950.00"))),
        Authorization(IncomingId("E3"), Day(2), ACC_001, Day(2), AuthorizationId("Auth-A"), Amount(aed("200.00"))),
        Settlement(
            IncomingId("E5"), Day(4), ACC_001, Day(4), AuthorizationId("Auth-A"), Amount(aed("185.00")), Capture.FINAL
        ),
        Reversal(IncomingId("E9"), Day(6), ACC_001, Day(2), IncomingId("E7")),
        Credit(IncomingId("E10"), Day(5), ACC_002, Day(5), Amount(bhd("10.000")), Instalments(InstalmentCount(3))),
    )


E1 = {"event": "E1", "booked": "1", "type": "CREDIT", "account": "ACC-001", "amount": "100.00", "value_date": "1"}


def fault_of(**cells: str) -> StreamError | None:
    """The fault the reader reports for one row, E1 changed by ``cells``."""
    parsed = parse_stream(csv_text([{**E1, **cells}]), CHALLENGE)
    return parsed if isinstance(parsed, StreamError) else None


def test_a_wrong_header_or_cell_count_is_refused() -> None:
    header = ",".join(HEADER)
    assert parse_stream("event,booked\nE1,1\n", CHALLENGE) == StreamError(1, f"line 1: expected the header {header}")
    assert parse_stream(f"{header}\nE1,1,CREDIT,ACC-001,100.00,1,\n", CHALLENGE) == StreamError(
        2, "line 2: expected 9 cells, found 7"
    )
    assert parse_stream("", CHALLENGE) == StreamError(1, f"line 1: expected the header {header}")


def test_an_id_of_the_wrong_form_is_refused() -> None:
    assert fault_of(event="7") == StreamError(2, "line 2: event ID '7' is not valid")
    assert fault_of(account="ACC-1") == StreamError(2, "line 2: account ID 'ACC-1' is not valid")
    assert fault_of(type="AUTHORIZATION", reference="Auth A") == StreamError(2, "line 2: hold ID 'Auth A' is not valid")


def test_an_unknown_type_or_account_is_refused() -> None:
    assert fault_of(type="REFUND") == StreamError(
        2, "line 2: type 'REFUND' is not one of CREDIT, DEBIT, AUTHORIZATION, SETTLEMENT, REVERSAL"
    )
    assert fault_of(account="ACC-009") == StreamError(2, "line 2: account 'ACC-009' is not held by this ledger")


def test_an_amount_that_is_not_a_valid_amount_is_refused() -> None:
    assert fault_of(amount="12.00x") == StreamError(2, "line 2: amount '12.00x' is not a decimal number")
    assert fault_of(amount="12.345") == StreamError(2, "line 2: amount '12.345' has more than 2 places for AED")
    assert fault_of(account="ACC-002", amount="1.0001") == StreamError(
        2, "line 2: amount '1.0001' has more than 3 places for BHD"
    )
    assert fault_of(amount="0.00") == StreamError(2, "line 2: amount '0.00' must be above zero")
    assert fault_of(amount="-400.00") == StreamError(2, "line 2: amount '-400.00' must be above zero")


def test_a_missing_or_inapplicable_cell_is_refused() -> None:
    assert fault_of(event="") == StreamError(2, "line 2: column 'event' is required for CREDIT")
    assert fault_of(amount="") == StreamError(2, "line 2: column 'amount' is required for CREDIT")
    assert fault_of(type="SETTLEMENT") == StreamError(2, "line 2: column 'reference' is required for SETTLEMENT")
    assert fault_of(reference="E7") == StreamError(2, "line 2: column 'reference' does not apply to CREDIT")
    assert fault_of(type="DEBIT", instalments="3") == StreamError(
        2, "line 2: column 'instalments' does not apply to DEBIT"
    )
    assert fault_of(type="REVERSAL", reference="E7") == StreamError(
        2, "line 2: column 'amount' does not apply to REVERSAL"
    )


def test_a_day_outside_the_window_is_refused() -> None:
    assert fault_of(booked="7") == StreamError(2, "line 2: day '7' is outside the window 1 to 6")
    assert fault_of(value_date="0") == StreamError(2, "line 2: day '0' is outside the window 1 to 6")
    assert fault_of(booked="1.5") == StreamError(2, "line 2: day '1.5' is outside the window 1 to 6")


def test_a_reversal_reference_must_be_an_event_id() -> None:
    assert fault_of(type="REVERSAL", amount="", reference="Auth-A") == StreamError(
        2, "line 2: reference 'Auth-A' is not an event ID"
    )
    assert parse_stream(
        csv_text([{**E1, "type": "REVERSAL", "amount": "", "reference": "FEE-001-D2@D5"}]), CHALLENGE
    ) == (Reversal(IncomingId("E1"), Day(1), ACC_001, Day(1), FeeId(ACC_001, Day(2), Day(5))),)


def test_an_instalment_count_below_2_is_refused() -> None:
    assert fault_of(instalments="1") == StreamError(2, "line 2: instalments must be at least 2")
    assert fault_of(instalments="two") == StreamError(2, "line 2: instalments must be at least 2")


def test_more_instalments_than_minor_units_are_refused() -> None:
    assert fault_of(account="ACC-002", amount="0.002", instalments="3") == StreamError(
        2, "line 2: 0.002 cannot be split into 3 instalments"
    )


def test_a_final_cell_other_than_yes_or_no_is_refused() -> None:
    """AMB-013, tech-docs 003: a settlement's `final` cell is `yes`, `no`, or blank for `yes`; any other is a fault, and
    the cell applies to a settlement only."""
    header = ",".join(HEADER)
    settlement = "E5,4,SETTLEMENT,ACC-001,185.00,4,Auth-A,,"

    def capture(cell: str) -> Capture:
        events = parse_stream(f"{header}\n{settlement}{cell}\n", CHALLENGE)
        assert not isinstance(events, StreamError), events
        (event,) = events
        assert isinstance(event, Settlement)
        return event.capture

    assert parse_stream(f"{header}\n{settlement}maybe\n", CHALLENGE) == StreamError(
        2, "line 2: final must be yes or no"
    )
    assert [capture("yes"), capture(""), capture("no")] == [Capture.FINAL, Capture.FINAL, Capture.PARTIAL]
    assert parse_stream(f"{header}\nE1,1,CREDIT,ACC-001,10.00,1,,,no\n", CHALLENGE) == StreamError(
        2, "line 2: column 'final' does not apply to CREDIT"
    )
