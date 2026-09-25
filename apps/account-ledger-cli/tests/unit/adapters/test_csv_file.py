"""The CSV file source: a valid stream parses to its events; each fault names its line."""

from account_ledger.adapters.csv_file import CsvFileSource, StreamError
from account_ledger.application.stream import IncomingStream
from account_ledger.challenge import CHALLENGE
from account_ledger.common.result import Err, Ok
from account_ledger.domain.model.events import Authorization, Credit, Debit, Reversal, Settlement, SettlementKind, Whole
from account_ledger.domain.model.ids import AccountId, AuthorizationId, Day, FeeId, IncomingId, InstalmentCount
from account_ledger.domain.model.money import AmountIn
from support.results import unwrap_ok
from support.streams import HEADER, format_csv, make_instalment_credit
from support.values import make_aed, make_bhd

ACC_001, ACC_002 = AccountId("ACC-001"), AccountId("ACC-002")


def test_a_valid_stream_parses_to_its_events() -> None:
    """A valid stream parses to its events, in the order listed."""

    text = format_csv(
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

    assert CsvFileSource.parse(text, CHALLENGE) == Ok(
        IncomingStream(
            (
                Credit(IncomingId("E1"), Day(1), ACC_001, Day(1), AmountIn(make_aed("1200.00")), Whole()),
                Debit(IncomingId("E2"), Day(1), ACC_001, Day(1), AmountIn(make_aed("950.00"))),
                Authorization(
                    IncomingId("E3"), Day(2), ACC_001, Day(2), AuthorizationId("Auth-A"), AmountIn(make_aed("200.00"))
                ),
                Settlement(
                    IncomingId("E5"),
                    Day(4),
                    ACC_001,
                    Day(4),
                    AuthorizationId("Auth-A"),
                    AmountIn(make_aed("185.00")),
                    SettlementKind.FINAL,
                ),
                Reversal(IncomingId("E9"), Day(6), ACC_001, Day(2), IncomingId("E7")),
                make_instalment_credit(
                    IncomingId("E10"), Day(5), ACC_002, Day(5), AmountIn(make_bhd("10.000")), InstalmentCount(3)
                ),
            )
        )
    )


E1 = {"event": "E1", "booked": "1", "type": "CREDIT", "account": "ACC-001", "amount": "100.00", "value_date": "1"}


def find_fault(**cells: str) -> StreamError | None:
    """The fault the event source reports for one row, E1 changed by ``cells``."""

    match CsvFileSource.parse(format_csv([{**E1, **cells}]), CHALLENGE):
        case Err(fault):
            return fault
        case Ok():
            return None


def test_a_wrong_header_or_cell_count_is_refused() -> None:
    """A wrong or missing header is refused on line 1, and a row with the wrong cell count on its own line."""

    header = ",".join(HEADER)
    wrong_header = Err(StreamError(1, f"line 1: expected the header {header}"))
    assert CsvFileSource.parse("event,booked\nE1,1\n", CHALLENGE) == wrong_header
    assert CsvFileSource.parse(f"{header}\nE1,1,CREDIT,ACC-001,100.00,1,\n", CHALLENGE) == Err(
        StreamError(2, "line 2: expected 9 cells, found 7")
    )
    assert CsvFileSource.parse("", CHALLENGE) == wrong_header


def test_an_id_of_the_wrong_form_is_refused() -> None:
    """An event, account, or authorization ID of the wrong form is refused, naming the kind of ID."""

    assert find_fault(event="7") == StreamError(2, "line 2: event ID '7' is not valid")
    assert find_fault(account="ACC-1") == StreamError(2, "line 2: account ID 'ACC-1' is not valid")
    assert find_fault(type="AUTHORIZATION", reference="Auth A") == StreamError(
        2, "line 2: authorization ID 'Auth A' is not valid"
    )


def test_an_unknown_type_or_account_is_refused() -> None:
    """A type outside the five kinds, or an account the ledger does not hold, is refused."""

    assert find_fault(type="REFUND") == StreamError(
        2, "line 2: type 'REFUND' is not one of CREDIT, DEBIT, AUTHORIZATION, SETTLEMENT, REVERSAL"
    )
    assert find_fault(account="ACC-009") == StreamError(2, "line 2: account 'ACC-009' is not a configured account")


def test_an_amount_that_is_not_a_valid_amount_is_refused() -> None:
    """An amount that is not a decimal, has too many places for its currency, or is not above zero is refused."""

    assert find_fault(amount="12.00x") == StreamError(2, "line 2: amount '12.00x' is not a decimal number")
    assert find_fault(amount="12.345") == StreamError(2, "line 2: amount '12.345' has more than 2 places for AED")
    assert find_fault(account="ACC-002", amount="1.0001") == StreamError(
        2, "line 2: amount '1.0001' has more than 3 places for BHD"
    )
    assert find_fault(amount="0.00") == StreamError(2, "line 2: amount '0.00' must be above zero")
    assert find_fault(amount="-400.00") == StreamError(2, "line 2: amount '-400.00' must be above zero")
    assert find_fault(amount="1e30") == StreamError(2, "line 2: amount '1e30' must be below 1000000000000")


def test_a_cell_past_the_csv_field_limit_is_refused() -> None:
    """A cell longer than the CSV reader's field limit is refused on its line, as the reader words it."""

    assert find_fault(reference="x" * 200_000) == StreamError(2, "line 2: field larger than field limit (131072)")


def test_a_missing_or_inapplicable_cell_is_refused() -> None:
    """A column the kind requires but the row leaves empty, or fills but the kind does not take, is refused."""

    assert find_fault(event="") == StreamError(2, "line 2: column 'event' is required for CREDIT")
    assert find_fault(amount="") == StreamError(2, "line 2: column 'amount' is required for CREDIT")
    assert find_fault(type="SETTLEMENT") == StreamError(2, "line 2: column 'reference' is required for SETTLEMENT")
    assert find_fault(reference="E7") == StreamError(2, "line 2: column 'reference' does not apply to CREDIT")
    assert find_fault(type="DEBIT", instalments="3") == StreamError(
        2, "line 2: column 'instalments' does not apply to DEBIT"
    )
    assert find_fault(type="REVERSAL", reference="E7") == StreamError(
        2, "line 2: column 'amount' does not apply to REVERSAL"
    )


def test_a_day_outside_the_window_is_refused() -> None:
    """A booked or value date outside the window, or not a whole number, is refused."""

    assert find_fault(booked="7") == StreamError(2, "line 2: day '7' is outside the window 1 to 6")
    assert find_fault(value_date="0") == StreamError(2, "line 2: day '0' is outside the window 1 to 6")
    assert find_fault(booked="1.5") == StreamError(2, "line 2: day '1.5' is outside the window 1 to 6")


def test_a_reversal_reference_must_be_an_event_id() -> None:
    """A reversal's reference must be an event ID, a generated ID included."""

    assert find_fault(type="REVERSAL", amount="", reference="Auth-A") == StreamError(
        2, "line 2: reference 'Auth-A' is not an event ID"
    )
    assert CsvFileSource.parse(
        format_csv([{**E1, "type": "REVERSAL", "amount": "", "reference": "FEE-001-D2@D5"}]), CHALLENGE
    ) == Ok(IncomingStream((Reversal(IncomingId("E1"), Day(1), ACC_001, Day(1), FeeId(ACC_001, Day(2), Day(5))),)))


def test_an_instalment_count_outside_2_to_360_is_refused() -> None:
    """An instalment count below 2 or above 360 (NUMBERS.md), or not a whole number, is refused."""

    must_be_from_2_to_360 = StreamError(2, "line 2: instalments must be a whole number from 2 to 360")
    assert find_fault(instalments="1") == must_be_from_2_to_360
    assert find_fault(instalments="two") == must_be_from_2_to_360
    assert find_fault(instalments="361") == must_be_from_2_to_360
    assert find_fault(instalments="99999999999999999999") == must_be_from_2_to_360


def test_more_instalments_than_minor_units_are_refused() -> None:
    """A credit with more instalments than its amount has minor units is refused."""

    assert find_fault(account="ACC-002", amount="0.002", instalments="3") == StreamError(
        2, "line 2: 0.002 cannot be split into 3 instalments"
    )


def test_a_final_cell_other_than_yes_or_no_is_refused() -> None:
    """AMB-013, tech-docs 003: a settlement's `final` cell is `yes`, `no`, or blank for `yes`; any other is a fault, and
    the cell applies to a settlement only."""

    header = ",".join(HEADER)
    settlement = "E5,4,SETTLEMENT,ACC-001,185.00,4,Auth-A,,"

    def parse_settlement_kind(cell: str) -> SettlementKind:
        """The kind a settlement row parses to when its `final` cell is ``cell``."""

        (event,) = unwrap_ok(CsvFileSource.parse(f"{header}\n{settlement}{cell}\n", CHALLENGE)).events
        assert isinstance(event, Settlement)

        return event.kind

    assert CsvFileSource.parse(f"{header}\n{settlement}maybe\n", CHALLENGE) == Err(
        StreamError(2, "line 2: final must be yes or no")
    )
    assert [parse_settlement_kind("yes"), parse_settlement_kind(""), parse_settlement_kind("no")] == [
        SettlementKind.FINAL,
        SettlementKind.FINAL,
        SettlementKind.PARTIAL,
    ]
    assert CsvFileSource.parse(f"{header}\nE1,1,CREDIT,ACC-001,10.00,1,,,no\n", CHALLENGE) == Err(
        StreamError(2, "line 2: column 'final' does not apply to CREDIT")
    )
