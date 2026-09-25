"""Parsing the stream file: text in, incoming events or the first fault out.

Every cell is text; each value is built through its domain type's ``parse``, so a fault is refused by the type that
would have held it, and this module adds only the line number and the column. Faults are returned values (S3).
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
    Aed,
    Amount,
    Bhd,
    Money,
    NotADecimal,
    NotPositive,
    TooManyInstalments,
    TooManyPlaces,
    format_digits,
    split_amount_of,
)

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


def _check_id[T](value: T | IdFault) -> T | RowFault:
    """The parsed value, or a fault naming the kind of ID and the text it refused."""
    return RowFault(f"{value.kind} '{value.text}' is not valid") if isinstance(value, IdFault) else value


def _parse_amount(text: str, sample: Money) -> AnyAmount | RowFault:
    """An amount in the account's currency, or a fault saying why the text is not one."""
    match sample:
        case Aed():
            money = Aed.parse(text)
            amount = Amount.make(money) if isinstance(money, Aed) else money
        case Bhd():
            money = Bhd.parse(text)
            amount = Amount.make(money) if isinstance(money, Bhd) else money
    match amount:
        case Amount():
            return amount
        case NotADecimal():
            return RowFault(f"amount '{text}' is not a decimal number")
        case TooManyPlaces(places=places, currency=currency):
            return RowFault(f"amount '{text}' has more than {places} places for {currency}")
        case NotPositive():
            return RowFault(f"amount '{text}' must be above zero")


def _parse_day(text: str, config: LedgerConfig) -> Day | RowFault:
    """A day inside the ledger's window, or a fault naming the window."""
    day = Day.parse(text)
    if isinstance(day, IdFault) or not config.first_day <= day <= config.last_day:
        return RowFault(f"day '{text}' is outside the window {config.first_day.number} to {config.last_day.number}")
    return day


def _parse_posting(text: str) -> Posting | RowFault:
    """A whole credit for a blank cell, or the instalment count it holds."""
    if not text:
        return Whole()
    count = InstalmentCount.parse(text)
    return RowFault("instalments must be at least 2") if isinstance(count, IdFault) else Instalments(count)


def _parse_capture(text: str) -> Capture | RowFault:
    """`yes` or blank is a final settlement, `no` one followed by more captures (AMB-013)."""
    match text:
        case "" | "yes":
            return Capture.FINAL
        case "no":
            return Capture.PARTIAL
        case _:
            return RowFault("final must be yes or no")


type _Head = tuple[IncomingId, Day, AccountId, Day]  # the event, booked, account, and value_date every row carries


def _parse_row(cells: dict[str, str], config: LedgerConfig) -> IncomingEvent | RowFault:
    """The row's event, checked in column order: its type, which columns it fills, its head, then its own cells."""
    if (kind := cells["type"]) not in KINDS:
        return RowFault(f"type '{kind}' is not one of {', '.join(KINDS)}")
    if (misplaced_fault := _find_misplaced_column(cells, kind)) is not None:
        return misplaced_fault
    if isinstance(parsed_head := _parse_head(cells, config), RowFault):
        return parsed_head
    head, account = parsed_head
    if kind == "REVERSAL":
        return _parse_reversal(cells["reference"], head)
    if isinstance(amount := _parse_amount(cells["amount"], account.opening), RowFault):
        return amount
    match kind:
        case "CREDIT":
            return _parse_credit(cells["instalments"], head, amount)
        case "DEBIT":
            return Debit(*head, amount)
        case _:
            return _parse_held_event(cells, kind, head, amount)


def _find_misplaced_column(cells: dict[str, str], kind: str) -> RowFault | None:
    """The first column the kind requires but the row leaves empty, or fills but the kind does not take."""
    for column in COLUMNS:
        if column in REQUIRED[kind] and not cells[column]:
            return RowFault(f"column '{column}' is required for {kind}")
        if column not in REQUIRED[kind] | OPTIONAL[kind] and cells[column]:
            return RowFault(f"column '{column}' does not apply to {kind}")
    return None


def _parse_head(cells: dict[str, str], config: LedgerConfig) -> tuple[_Head, AnyAccount] | RowFault:
    """The row's head, and the account it names, which must be one this ledger holds."""
    if isinstance(event_id := _check_id(IncomingId.parse(cells["event"])), RowFault):
        return event_id
    if isinstance(booked := _parse_day(cells["booked"], config), RowFault):
        return booked
    if isinstance(account_id := _check_id(AccountId.parse(cells["account"])), RowFault):
        return account_id
    if (account := config.find_account(account_id)) is None:
        return RowFault(f"account '{account_id.value}' is not held by this ledger")
    if isinstance(value_day := _parse_day(cells["value_date"], config), RowFault):
        return value_day
    return (event_id, booked, account_id, value_day), account


def _parse_reversal(reference: str, head: _Head) -> Reversal | RowFault:
    """A reversal of the event its reference names, which must be an event ID."""
    target = parse_event_id(reference)
    if isinstance(target, IdFault):
        return RowFault(f"reference '{target.text}' is not an event ID")
    return Reversal(*head, target)


def _parse_credit(instalments: str, head: _Head, amount: AnyAmount) -> Credit | RowFault:
    """A credit, whole or in instalments; one whose amount cannot be split that many ways is refused."""
    if isinstance(posting := _parse_posting(instalments), RowFault):
        return posting
    if isinstance(posting, Instalments) and isinstance(split_amount_of(amount, posting.count), TooManyInstalments):
        return RowFault(f"{format_digits(amount.money)} cannot be split into {posting.count.number} instalments")
    return Credit(*head, amount, posting)


def _parse_held_event(
    cells: dict[str, str], kind: str, head: _Head, amount: AnyAmount
) -> Authorization | Settlement | RowFault:
    """An authorization, or a settlement against one, each naming its hold in the reference."""
    if isinstance(hold := _check_id(AuthorizationId.parse(cells["reference"])), RowFault):
        return hold
    if kind == "AUTHORIZATION":
        return Authorization(*head, hold, amount)
    if isinstance(capture := _parse_capture(cells["final"]), RowFault):
        return capture
    return Settlement(*head, hold, amount, capture)


def parse_stream(text: str, config: LedgerConfig) -> tuple[IncomingEvent, ...] | StreamError:
    """The stream's events in listed order, or the first fault; the header is line 1."""
    rows = list(csv.reader(io.StringIO(text)))
    if not rows or tuple(rows[0]) != COLUMNS:
        return StreamError(1, f"line 1: expected the header {','.join(COLUMNS)}")
    events: list[IncomingEvent] = []
    for line, cells in enumerate(rows[1:], start=2):
        if len(cells) != len(COLUMNS):
            return StreamError(line, f"line {line}: expected {len(COLUMNS)} cells, found {len(cells)}")
        event = _parse_row(dict(zip(COLUMNS, cells, strict=True)), config)
        if isinstance(event, RowFault):
            return StreamError(line, f"line {line}: {event.message}")
        events.append(event)
    return tuple(events)
