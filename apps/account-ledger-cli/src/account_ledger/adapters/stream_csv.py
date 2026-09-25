"""Parsing the stream file: text in, incoming events or the first fault out.

Every cell is text; each value is built through its domain type's ``parse``, so a fault is refused by the type that
would have held it, and this module adds only the line number and the column. Faults are returned as ``Err`` (S3).
"""

import csv
import io
from dataclasses import dataclass

from account_ledger.common.result import Err, Ok, Result
from account_ledger.domain.model.config import AccountOpening, LedgerConfig
from account_ledger.domain.model.events import (
    Authorization,
    Credit,
    Debit,
    IncomingEvent,
    Instalments,
    Posting,
    Reversal,
    Settlement,
    SettlementKind,
    Whole,
)
from account_ledger.domain.model.ids import (
    MAX_INSTALMENTS,
    AccountId,
    AuthorizationId,
    Day,
    IdFault,
    IncomingId,
    InstalmentCount,
    parse_event_id,
)
from account_ledger.domain.model.money import (
    AMOUNT_LIMIT,
    AboveLimit,
    Aed,
    Amount,
    AmountIn,
    Bhd,
    Money,
    MoneyFault,
    NotADecimal,
    NotPositive,
    TooManyPlaces,
)

COLUMNS = ("event", "booked", "type", "account", "amount", "value_date", "reference", "instalments", "final")
KINDS = ("CREDIT", "DEBIT", "AUTHORIZATION", "SETTLEMENT", "REVERSAL")
_COMMON_COLUMNS = frozenset({"event", "booked", "type", "account", "value_date"})
REQUIRED = {
    "CREDIT": _COMMON_COLUMNS | {"amount"},
    "DEBIT": _COMMON_COLUMNS | {"amount"},
    "AUTHORIZATION": _COMMON_COLUMNS | {"amount", "reference"},
    "SETTLEMENT": _COMMON_COLUMNS | {"amount", "reference"},
    "REVERSAL": _COMMON_COLUMNS | {"reference"},
}
OPTIONAL: dict[str, frozenset[str]] = {
    "CREDIT": frozenset({"instalments"}),
    "DEBIT": frozenset(),
    "AUTHORIZATION": frozenset(),
    "SETTLEMENT": frozenset({"final"}),
    "REVERSAL": frozenset(),
}


@dataclass(frozen=True, slots=True)
class StreamError:
    """The first fault in a stream, with its physical line number."""

    line: int
    message: str


@dataclass(frozen=True, slots=True)
class RowFault:
    """What is wrong with one row, before its line number is known."""

    message: str


def _check_id[T](parsed_id: Result[T, IdFault]) -> Result[T, RowFault]:
    """The parsed value, or a fault naming the kind of ID and the text it refused."""
    return parsed_id.map_err(lambda fault: RowFault(f"{fault.kind} '{fault.text}' is not valid"))


def _parse_amount(text: str, sample: Money) -> Result[Amount, RowFault]:
    """An amount in the account's currency, or a fault saying why the text is not one."""
    match sample:
        case Aed():
            amount = Aed.parse(text).flat_map(AmountIn.make)
        case Bhd():
            amount = Bhd.parse(text).flat_map(AmountIn.make)
    return amount.map_err(lambda fault: RowFault(_describe_amount_fault(text, fault)))


def _describe_amount_fault(text: str, fault: MoneyFault | NotPositive) -> str:
    """Why the text is not an amount, as the error line says it."""
    match fault:
        case NotADecimal():
            return f"amount '{text}' is not a decimal number"
        case TooManyPlaces(places=places, currency=currency):
            return f"amount '{text}' has more than {places} places for {currency}"
        case AboveLimit():
            return f"amount '{text}' must be below {AMOUNT_LIMIT}"
        case NotPositive():
            return f"amount '{text}' must be above zero"


def _parse_day(text: str, config: LedgerConfig) -> Result[Day, RowFault]:
    """A day inside the ledger's window, or a fault naming the window."""
    match Day.parse(text):
        case Ok(day) if config.first_day <= day <= config.last_day:
            return Ok(day)
        case _:
            window = f"{config.first_day.number} to {config.last_day.number}"
            return Err(RowFault(f"day '{text}' is outside the window {window}"))


def _parse_posting(text: str, amount: Amount) -> Result[Posting, RowFault]:
    """A whole credit for a blank cell, or the amount in as many instalments as the cell counts; an amount that cannot
    be split that many ways is refused."""
    if not text:
        return Ok(Whole())
    if isinstance(count := InstalmentCount.parse(text), Err):
        return Err(RowFault(f"instalments must be a whole number from 2 to {MAX_INSTALMENTS}"))
    return Instalments.make(amount, count.value).map_err(
        lambda _: RowFault(f"{amount.money.format_digits()} cannot be split into {count.value.number} instalments")
    )


def _parse_settlement_kind(text: str) -> Result[SettlementKind, RowFault]:
    """`yes` or blank is a final settlement, `no` one followed by more settlements (AMB-013)."""
    match text:
        case "" | "yes":
            return Ok(SettlementKind.FINAL)
        case "no":
            return Ok(SettlementKind.PARTIAL)
        case _:
            return Err(RowFault("final must be yes or no"))


type _CommonFields = tuple[
    IncomingId, Day, AccountId, Day
]  # the event, booked, account, and value_date every row carries


def _parse_row(cells: dict[str, str], config: LedgerConfig) -> Result[IncomingEvent, RowFault]:
    """The row's event, checked in column order: its type, the columns it fills, its common fields, then the rest."""
    if (kind := cells["type"]) not in KINDS:
        return Err(RowFault(f"type '{kind}' is not one of {', '.join(KINDS)}"))
    if isinstance(checked_columns := _check_columns(cells, kind), Err):
        return checked_columns
    if isinstance(parsed_fields := _parse_common_fields(cells, config), Err):
        return parsed_fields
    fields, account = parsed_fields.value
    if kind == "REVERSAL":
        return _parse_reversal(cells["reference"], fields)
    if isinstance(parsed_amount := _parse_amount(cells["amount"], account.balance), Err):
        return parsed_amount
    match kind:
        case "CREDIT":
            return _parse_credit(cells["instalments"], fields, parsed_amount.value)
        case "DEBIT":
            return Ok(Debit(*fields, parsed_amount.value))
        case _:
            return _parse_authorization_or_settlement(cells, kind, fields, parsed_amount.value)


def _check_columns(cells: dict[str, str], kind: str) -> Result[None, RowFault]:
    """Nothing when the row fills exactly the columns its kind takes, or a fault naming the first column it leaves
    empty though required, or fills though the kind does not take it."""
    for column in COLUMNS:
        if column in REQUIRED[kind] and not cells[column]:
            return Err(RowFault(f"column '{column}' is required for {kind}"))
        if column not in REQUIRED[kind] | OPTIONAL[kind] and cells[column]:
            return Err(RowFault(f"column '{column}' does not apply to {kind}"))
    return Ok(None)


def _parse_common_fields(
    cells: dict[str, str], config: LedgerConfig
) -> Result[tuple[_CommonFields, AccountOpening], RowFault]:
    """The row's common fields, and the account it names, which must be a configured account."""
    if isinstance(event_id := _check_id(IncomingId.parse(cells["event"])), Err):
        return event_id
    if isinstance(booked := _parse_day(cells["booked"], config), Err):
        return booked
    if isinstance(account_id := _check_id(AccountId.parse(cells["account"])), Err):
        return account_id
    if (account := config.find_account(account_id.value)) is None:
        return Err(RowFault(f"account '{cells['account']}' is not a configured account"))
    if isinstance(value_date := _parse_day(cells["value_date"], config), Err):
        return value_date
    return Ok(((event_id.value, booked.value, account_id.value, value_date.value), account))


def _parse_reversal(reference: str, fields: _CommonFields) -> Result[Reversal, RowFault]:
    """A reversal of the event its reference names, which must be an event ID."""
    return (
        parse_event_id(reference)
        .map(lambda target: Reversal(*fields, target))
        .map_err(lambda fault: RowFault(f"reference '{fault.text}' is not an event ID"))
    )


def _parse_credit(instalments: str, fields: _CommonFields, amount: Amount) -> Result[Credit, RowFault]:
    """A credit, whole or in instalments; one whose amount cannot be split that many ways is refused."""
    return _parse_posting(instalments, amount).map(lambda posting: Credit(*fields, amount, posting))


def _parse_authorization_or_settlement(
    cells: dict[str, str], kind: str, fields: _CommonFields, amount: Amount
) -> Result[Authorization | Settlement, RowFault]:
    """An authorization, or a settlement against one, each naming its hold in the reference."""
    if isinstance(hold := _check_id(AuthorizationId.parse(cells["reference"])), Err):
        return hold
    if kind == "AUTHORIZATION":
        return Ok(Authorization(*fields, hold.value, amount))
    return _parse_settlement_kind(cells["final"]).map(
        lambda settlement_kind: Settlement(*fields, hold.value, amount, settlement_kind)
    )


def parse_stream(text: str, config: LedgerConfig) -> Result[tuple[IncomingEvent, ...], StreamError]:
    """The stream's events in listed order, or the first fault; the header is line 1."""
    if isinstance(read_rows := _read_rows(text), Err):
        return read_rows
    rows = read_rows.value
    if not rows or tuple(rows[0]) != COLUMNS:
        return Err(StreamError(1, f"line 1: expected the header {','.join(COLUMNS)}"))
    events: list[IncomingEvent] = []
    for line, cells in enumerate(rows[1:], start=2):
        if len(cells) != len(COLUMNS):
            return Err(StreamError(line, f"line {line}: expected {len(COLUMNS)} cells, found {len(cells)}"))
        event = _parse_row(dict(zip(COLUMNS, cells, strict=True)), config)
        if isinstance(event, Err):
            return Err(StreamError(line, f"line {line}: {event.error.message}"))
        events.append(event.value)
    return Ok(tuple(events))


def _read_rows(text: str) -> Result[list[list[str]], StreamError]:
    """The stream's rows as CSV, or a fault on the line where the reader refuses one, such as a cell past its field
    limit; the reader refuses by raising, so the refusal is caught here and returned."""
    reader = csv.reader(io.StringIO(text))
    try:
        return Ok(list(reader))
    except csv.Error as fault:
        return Err(StreamError(reader.line_num, f"line {reader.line_num}: {fault}"))
