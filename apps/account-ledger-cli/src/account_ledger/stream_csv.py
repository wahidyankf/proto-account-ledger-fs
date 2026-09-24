"""Parsing the stream file: text in, incoming events or the first fault out.

Every cell is text; each value is built through its domain type's ``parse``, so a fault is refused by the type that
would have held it, and this module adds only the line number and the column. Faults are returned values (S3).
"""

import csv
import io
from dataclasses import dataclass

from account_ledger.config import LedgerConfig
from account_ledger.events import (
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
from account_ledger.ids import AccountId, AuthorizationId, Day, IdFault, IncomingId, InstalmentCount, parse_event_id
from account_ledger.money import (
    Aed,
    Amount,
    Bhd,
    Money,
    NotADecimal,
    NotPositive,
    TooManyInstalments,
    TooManyPlaces,
    digits,
    split_of,
)

COLUMNS = ("event", "booked", "type", "account", "amount", "value_date", "reference", "instalments")
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
    kind: frozenset({"instalments"}) if kind == "CREDIT" else frozenset[str]() for kind in KINDS
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


def _id[T](value: T | IdFault) -> T | RowFault:
    return RowFault(f"{value.kind} '{value.text}' is not valid") if isinstance(value, IdFault) else value


def _amount(text: str, like: Money) -> AnyAmount | RowFault:
    match like:
        case Aed():
            money = Aed.parse(text)
            amount = Amount.of(money) if isinstance(money, Aed) else money
        case Bhd():
            money = Bhd.parse(text)
            amount = Amount.of(money) if isinstance(money, Bhd) else money
    match amount:
        case Amount():
            return amount
        case NotADecimal():
            return RowFault(f"amount '{text}' is not a decimal number")
        case TooManyPlaces(places=places, currency=currency):
            return RowFault(f"amount '{text}' has more than {places} places for {currency}")
        case NotPositive():
            return RowFault(f"amount '{text}' must be above zero")


def _day(text: str, config: LedgerConfig) -> Day | RowFault:
    day = Day.parse(text)
    if isinstance(day, IdFault) or not config.first_day <= day <= config.last_day:
        return RowFault(f"day '{text}' is outside the window {config.first_day.number} to {config.last_day.number}")
    return day


def _posting(text: str) -> Posting | RowFault:
    if not text:
        return Whole()
    count = InstalmentCount.parse(text)
    return RowFault("instalments must be at least 2") if isinstance(count, IdFault) else Instalments(count)


def _row(cells: dict[str, str], config: LedgerConfig) -> IncomingEvent | RowFault:
    if (kind := cells["type"]) not in KINDS:
        return RowFault(f"type '{kind}' is not one of {', '.join(KINDS)}")
    for column in COLUMNS:
        if column in REQUIRED[kind] and not cells[column]:
            return RowFault(f"column '{column}' is required for {kind}")
        if column not in REQUIRED[kind] | OPTIONAL[kind] and cells[column]:
            return RowFault(f"column '{column}' does not apply to {kind}")
    if isinstance(event_id := _id(IncomingId.parse(cells["event"])), RowFault):
        return event_id
    if isinstance(booked := _day(cells["booked"], config), RowFault):
        return booked
    if isinstance(account_id := _id(AccountId.parse(cells["account"])), RowFault):
        return account_id
    if (account := config.account(account_id)) is None:
        return RowFault(f"account '{account_id.value}' is not held by this ledger")
    if isinstance(value_day := _day(cells["value_date"], config), RowFault):
        return value_day
    head = (event_id, booked, account_id, value_day)
    if kind == "REVERSAL":
        target = parse_event_id(cells["reference"])
        if isinstance(target, IdFault):
            return RowFault(f"reference '{target.text}' is not an event ID")
        return Reversal(*head, target)
    if isinstance(amount := _amount(cells["amount"], account.opening), RowFault):
        return amount
    match kind:
        case "CREDIT":
            posting = _posting(cells["instalments"])
            if isinstance(posting, RowFault):
                return posting
            if isinstance(posting, Instalments) and isinstance(split_of(amount, posting.count), TooManyInstalments):
                return RowFault(f"{digits(amount.money)} cannot be split into {posting.count.n} instalments")
            return Credit(*head, amount, posting)
        case "DEBIT":
            return Debit(*head, amount)
        case _:
            if isinstance(hold := _id(AuthorizationId.parse(cells["reference"])), RowFault):
                return hold
            if kind == "AUTHORIZATION":
                return Authorization(*head, hold, amount)
            return Settlement(*head, hold, amount, Capture.FINAL)


def parse_stream(text: str, config: LedgerConfig) -> tuple[IncomingEvent, ...] | StreamError:
    """The stream's events in listed order, or the first fault; the header is line 1."""
    rows = list(csv.reader(io.StringIO(text)))
    if not rows or tuple(rows[0]) != COLUMNS:
        return StreamError(1, f"line 1: expected the header {','.join(COLUMNS)}")
    events: list[IncomingEvent] = []
    for line, cells in enumerate(rows[1:], start=2):
        if len(cells) != len(COLUMNS):
            return StreamError(line, f"line {line}: expected {len(COLUMNS)} cells, found {len(cells)}")
        event = _row(dict(zip(COLUMNS, cells, strict=True)), config)
        if isinstance(event, RowFault):
            return StreamError(line, f"line {line}: {event.message}")
        events.append(event)
    return tuple(events)
