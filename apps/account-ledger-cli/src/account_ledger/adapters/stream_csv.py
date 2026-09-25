"""Parsing the stream file: text in, incoming events or the first fault out.

Every cell is text; each value is built through its domain type's ``parse``, so a fault is refused by the type that
would have held it, and this module adds only the line number and the column. Faults are returned as ``Err`` (S3).
"""

import csv
import io
from dataclasses import dataclass

from account_ledger.domain.model.config import AnyAccount, LedgerConfig
from account_ledger.domain.model.events import (
    AnyAmount,
    Authorization,
    Capture,
    Credit,
    Debit,
    IncomingEvent,
    Instalments,
    Posting,
    Reversal,
    Settlement,
    Whole,
)
from account_ledger.domain.model.ids import (
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
    Bhd,
    Money,
    MoneyFault,
    NotADecimal,
    NotPositive,
    TooManyPlaces,
    format_digits,
    split_amount_of,
)
from account_ledger.domain.model.result import Err, Ok, Result

COLUMNS = ("event", "booked", "type", "account", "amount", "value_date", "reference", "instalments", "final")
KINDS = ("CREDIT", "DEBIT", "AUTHORIZATION", "SETTLEMENT", "REVERSAL")
_EVERY = frozenset({"event", "booked", "type", "account", "value_date"})
REQUIRED = {
    "CREDIT": _EVERY | {"amount"},
    "DEBIT": _EVERY | {"amount"},
    "AUTHORIZATION": _EVERY | {"amount", "reference"},
    "SETTLEMENT": _EVERY | {"amount", "reference"},
    "REVERSAL": _EVERY | {"reference"},
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


def _parse_amount(text: str, sample: Money) -> Result[AnyAmount, RowFault]:
    """An amount in the account's currency, or a fault saying why the text is not one."""
    match sample:
        case Aed():
            amount = Aed.parse(text).flat_map(Amount.make)
        case Bhd():
            amount = Bhd.parse(text).flat_map(Amount.make)
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


def _parse_posting(text: str) -> Result[Posting, RowFault]:
    """A whole credit for a blank cell, or the instalment count it holds."""
    if not text:
        return Ok(Whole())
    return InstalmentCount.parse(text).map(Instalments).map_err(lambda _: RowFault("instalments must be at least 2"))


def _parse_capture(text: str) -> Result[Capture, RowFault]:
    """`yes` or blank is a final settlement, `no` one followed by more captures (AMB-013)."""
    match text:
        case "" | "yes":
            return Ok(Capture.FINAL)
        case "no":
            return Ok(Capture.PARTIAL)
        case _:
            return Err(RowFault("final must be yes or no"))


type _Head = tuple[IncomingId, Day, AccountId, Day]  # the event, booked, account, and value_date every row carries


def _parse_row(cells: dict[str, str], config: LedgerConfig) -> Result[IncomingEvent, RowFault]:
    """The row's event, checked in column order: its type, which columns it fills, its head, then its own cells."""
    if (kind := cells["type"]) not in KINDS:
        return Err(RowFault(f"type '{kind}' is not one of {', '.join(KINDS)}"))
    if isinstance(checked_columns := _check_columns(cells, kind), Err):
        return checked_columns
    if isinstance(parsed_head := _parse_head(cells, config), Err):
        return parsed_head
    head, account = parsed_head.value
    if kind == "REVERSAL":
        return _parse_reversal(cells["reference"], head)
    if isinstance(parsed_amount := _parse_amount(cells["amount"], account.opening), Err):
        return parsed_amount
    match kind:
        case "CREDIT":
            return _parse_credit(cells["instalments"], head, parsed_amount.value)
        case "DEBIT":
            return Ok(Debit(*head, parsed_amount.value))
        case _:
            return _parse_held_event(cells, kind, head, parsed_amount.value)


def _check_columns(cells: dict[str, str], kind: str) -> Result[None, RowFault]:
    """Nothing when the row fills exactly the columns its kind takes, or a fault naming the first column it leaves
    empty though required, or fills though the kind does not take it."""
    for column in COLUMNS:
        if column in REQUIRED[kind] and not cells[column]:
            return Err(RowFault(f"column '{column}' is required for {kind}"))
        if column not in REQUIRED[kind] | OPTIONAL[kind] and cells[column]:
            return Err(RowFault(f"column '{column}' does not apply to {kind}"))
    return Ok(None)


def _parse_head(cells: dict[str, str], config: LedgerConfig) -> Result[tuple[_Head, AnyAccount], RowFault]:
    """The row's head, and the account it names, which must be one this ledger holds."""
    if isinstance(event_id := _check_id(IncomingId.parse(cells["event"])), Err):
        return event_id
    if isinstance(booked := _parse_day(cells["booked"], config), Err):
        return booked
    if isinstance(account_id := _check_id(AccountId.parse(cells["account"])), Err):
        return account_id
    if (account := config.find_account(account_id.value)) is None:
        return Err(RowFault(f"account '{cells['account']}' is not held by this ledger"))
    if isinstance(value_day := _parse_day(cells["value_date"], config), Err):
        return value_day
    return Ok(((event_id.value, booked.value, account_id.value, value_day.value), account))


def _parse_reversal(reference: str, head: _Head) -> Result[Reversal, RowFault]:
    """A reversal of the event its reference names, which must be an event ID."""
    return (
        parse_event_id(reference)
        .map(lambda target: Reversal(*head, target))
        .map_err(lambda fault: RowFault(f"reference '{fault.text}' is not an event ID"))
    )


def _parse_credit(instalments: str, head: _Head, amount: AnyAmount) -> Result[Credit, RowFault]:
    """A credit, whole or in instalments; one whose amount cannot be split that many ways is refused."""
    if isinstance(parsed_posting := _parse_posting(instalments), Err):
        return parsed_posting
    posting = parsed_posting.value
    if isinstance(posting, Instalments) and isinstance(split_amount_of(amount, posting.count), Err):
        return Err(RowFault(f"{format_digits(amount.money)} cannot be split into {posting.count.number} instalments"))
    return Ok(Credit(*head, amount, posting))


def _parse_held_event(
    cells: dict[str, str], kind: str, head: _Head, amount: AnyAmount
) -> Result[Authorization | Settlement, RowFault]:
    """An authorization, or a settlement against one, each naming its hold in the reference."""
    if isinstance(hold := _check_id(AuthorizationId.parse(cells["reference"])), Err):
        return hold
    if kind == "AUTHORIZATION":
        return Ok(Authorization(*head, hold.value, amount))
    return _parse_capture(cells["final"]).map(lambda capture: Settlement(*head, hold.value, amount, capture))


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
