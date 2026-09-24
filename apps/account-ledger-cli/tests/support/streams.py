"""Builders for the short streams the rule tests replay, and readers that turn log entries into plain values."""

from account_ledger.config import Account
from account_ledger.events import (
    AnyAmount,
    Authorization,
    Capture,
    Credit,
    Debit,
    IncomingEvent,
    Instalments,
    Reversal,
    Settlement,
    Whole,
)
from account_ledger.ids import AccountId, AuthorizationId, Day, IdFault, IncomingId, InstalmentCount, parse_event_id
from account_ledger.money import Aed, Amount, Bhd
from support.values import aed, bhd

HEADER = ("event", "booked", "type", "account", "amount", "value_date", "reference", "instalments")

ACC_001: Account[Aed] = Account(AccountId("ACC-001"), Aed.zero())
ACC_002: Account[Bhd] = Account(AccountId("ACC-002"), Bhd.zero())


def csv_text(rows: list[dict[str, str]]) -> str:
    """The stream file for these rows under the current header; a column a row omits is empty."""
    lines = [",".join(HEADER), *(",".join(row.get(column, "") for column in HEADER) for row in rows)]
    return "\n".join(lines) + "\n"


def through(stream: tuple[IncomingEvent, ...], event_id: str) -> tuple[IncomingEvent, ...]:
    """The stream up to and including the event with this ID."""
    ids = [event.id.value for event in stream]
    return stream[: ids.index(event_id) + 1]


def _amount(account: str, text: str) -> AnyAmount:
    """An amount in the account's currency: AED for ACC-001, BHD otherwise."""
    return Amount(aed(text)) if account == "ACC-001" else Amount(bhd(text))


def credit(
    event: str, day: int, amount: str, value: int | None = None, account: str = "ACC-001", instalments: int = 0
) -> Credit:
    posting = Instalments(InstalmentCount(instalments)) if instalments else Whole()
    return Credit(IncomingId(event), Day(day), AccountId(account), Day(value or day), _amount(account, amount), posting)


def debit(event: str, day: int, amount: str, value: int | None = None, account: str = "ACC-001") -> Debit:
    return Debit(IncomingId(event), Day(day), AccountId(account), Day(value or day), _amount(account, amount))


def authorization(
    event: str, day: int, hold: str, amount: str, value: int | None = None, account: str = "ACC-001"
) -> Authorization:
    return Authorization(
        IncomingId(event),
        Day(day),
        AccountId(account),
        Day(value or day),
        AuthorizationId(hold),
        _amount(account, amount),
    )


def settlement(
    event: str,
    day: int,
    hold: str,
    amount: str,
    value: int | None = None,
    account: str = "ACC-001",
    capture: Capture = Capture.FINAL,
) -> Settlement:
    return Settlement(
        IncomingId(event),
        Day(day),
        AccountId(account),
        Day(value or day),
        AuthorizationId(hold),
        _amount(account, amount),
        capture,
    )


def reversal(event: str, day: int, reverses: str, value: int | None = None, account: str = "ACC-001") -> Reversal:
    target = parse_event_id(reverses)
    assert not isinstance(target, IdFault), target
    return Reversal(IncomingId(event), Day(day), AccountId(account), Day(value or day), target)
