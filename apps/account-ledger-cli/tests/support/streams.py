"""Builders for the short streams the rule tests process, and readers that turn log entries into plain values."""

from account_ledger.domain.account.domain_events import (
    FeeCharged,
    FeeRefunded,
    InterestAccrued,
    InterestAdjusted,
    InterestCapitalized,
)
from account_ledger.domain.account.event_log import EventLog
from account_ledger.domain.model.config import AccountOpeningIn
from account_ledger.domain.model.events import (
    Authorization,
    Credit,
    Debit,
    IncomingEvent,
    Instalments,
    InterestAccrual,
    InterestAdjustment,
    Reversal,
    Settlement,
    SettlementKind,
    Whole,
)
from account_ledger.domain.model.ids import (
    AccountId,
    AuthorizationId,
    Day,
    IncomingId,
    InstalmentCount,
    parse_event_id,
)
from account_ledger.domain.model.money import Aed, Amount, AmountIn, Bhd, Direction, Money
from support.results import unwrap_ok
from support.values import make_aed, make_bhd

HEADER = ("event", "booked", "type", "account", "amount", "value_date", "reference", "instalments", "final")

ACC_001: AccountOpeningIn[Aed] = AccountOpeningIn(AccountId("ACC-001"), Aed.make_zero())
ACC_002: AccountOpeningIn[Bhd] = AccountOpeningIn(AccountId("ACC-002"), Bhd.make_zero())


def format_csv(rows: list[dict[str, str]]) -> str:
    """The stream file for these rows under the current header; a column a row omits is empty."""
    lines = [",".join(HEADER), *(",".join(row.get(column, "") for column in HEADER) for row in rows)]
    return "\n".join(lines) + "\n"


def take_through(stream: tuple[IncomingEvent, ...], event_id: str) -> tuple[IncomingEvent, ...]:
    """The stream up to and including the event with this ID."""
    ids = [event.id.value for event in stream]
    return stream[: ids.index(event_id) + 1]


def _make_amount(account: str, text: str) -> Amount:
    """An amount in the account's currency: AED for ACC-001, BHD otherwise."""
    return AmountIn(make_aed(text)) if account == "ACC-001" else AmountIn(make_bhd(text))


def make_credit(
    event: str, day: int, amount: str, value: int | None = None, account: str = "ACC-001", instalments: int = 0
) -> Credit:
    """A credit on ACC-001 unless named, value-dated its booked day unless given, whole unless in instalments."""
    event_id, value_date, credit_amount = IncomingId(event), Day(value or day), _make_amount(account, amount)
    if instalments:
        return make_instalment_credit(
            event_id, Day(day), AccountId(account), value_date, credit_amount, InstalmentCount(instalments)
        )
    return Credit(event_id, Day(day), AccountId(account), value_date, credit_amount, Whole())


def make_instalment_credit(
    event_id: IncomingId, booked: Day, account: AccountId, value_date: Day, amount: Amount, count: InstalmentCount
) -> Credit:
    """A credit in instalments, its parts split from its amount as the stream reader splits them; an amount that
    cannot be split that many ways fails the test."""
    return Credit(event_id, booked, account, value_date, amount, unwrap_ok(Instalments.make(amount, count)))


def make_debit(event: str, day: int, amount: str, value: int | None = None, account: str = "ACC-001") -> Debit:
    """A debit on ACC-001 unless named, value-dated its booked day unless given."""
    return Debit(IncomingId(event), Day(day), AccountId(account), Day(value or day), _make_amount(account, amount))


def make_authorization(
    event: str, day: int, hold: str, amount: str, value: int | None = None, account: str = "ACC-001"
) -> Authorization:
    """An authorization for the hold, on ACC-001 unless named, value-dated its booked day unless given."""
    return Authorization(
        IncomingId(event),
        Day(day),
        AccountId(account),
        Day(value or day),
        AuthorizationId(hold),
        _make_amount(account, amount),
    )


def make_settlement(
    event: str,
    day: int,
    hold: str,
    amount: str,
    value: int | None = None,
    account: str = "ACC-001",
    kind: SettlementKind = SettlementKind.FINAL,
) -> Settlement:
    """A settlement of the hold, final unless partial, on ACC-001 unless named, value-dated its booked day."""
    return Settlement(
        IncomingId(event),
        Day(day),
        AccountId(account),
        Day(value or day),
        AuthorizationId(hold),
        _make_amount(account, amount),
        kind,
    )


def make_reversal(event: str, day: int, reverses: str, value: int | None = None, account: str = "ACC-001") -> Reversal:
    """A reversal of the event ID, on ACC-001 unless named, value-dated its booked day unless given."""
    target = unwrap_ok(parse_event_id(reverses))
    return Reversal(IncomingId(event), Day(day), AccountId(account), Day(value or day), target)


def list_fee_ids(log: EventLog) -> list[str]:
    """The generated ID of every fee in the log, in the order generated."""
    return [entry.event.id.format() for entry in log.entries if isinstance(entry, FeeCharged)]


def list_refund_ids(log: EventLog) -> list[str]:
    """The generated ID of every fee refund in the log, in the order generated."""
    return [entry.event.id.format() for entry in log.entries if isinstance(entry, FeeRefunded)]


def list_interest_amounts(log: EventLog) -> list[tuple[str, Money]]:
    """The generated ID and signed amount of every interest event in the log, in the order generated."""
    amounts: list[tuple[str, Money]] = []
    for entry in log.entries:
        match entry:
            case InterestAccrued(event=InterestAccrual(id=interest_id, amount=amount)):
                amounts.append((interest_id.format(), amount.money))
            case InterestAdjusted(event=InterestAdjustment(id=interest_id, direction=direction, amount=amount)):
                amounts.append((interest_id.format(), amount.money if direction is Direction.UP else -amount.money))
            case _:
                pass
    return amounts


def list_capitalization_amounts(log: EventLog) -> list[tuple[str, Money]]:
    """The generated ID and amount of every capitalization in the log, in the order generated."""
    return [
        (entry.event.id.format(), entry.event.amount.money)
        for entry in log.entries
        if isinstance(entry, InterestCapitalized)
    ]


def build_unsettled_auth_a() -> tuple[IncomingEvent, ...]:
    """Auth-A approved on Day 1 against a credit, and never settled or reversed (AMB-018)."""
    return (make_credit("E1", 1, "1000.00"), make_authorization("E2", 1, "Auth-A", "200.00"))
