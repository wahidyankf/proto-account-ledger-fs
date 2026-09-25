"""The report sink: each day's banner and its three blocks, written as text as OUTPUT_TARGET prints them
(tech-docs 003)."""

from collections.abc import Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Protocol, assert_never

from account_ledger.application.report import (
    Capitalized,
    DayReport,
    EndOfDayEvent,
    Generated,
    Note,
    NothingGenerated,
    Processed,
    Step,
)
from account_ledger.domain.account.authorizations import (
    Approved,
    AuthorizationRecord,
    Declined,
    PartiallySettled,
    Settled,
)
from account_ledger.domain.account.domain_events import (
    DuplicateIgnored,
    EventRejected,
    LogEntry,
    SettlementApplied,
    SettlementForcePosted,
)
from account_ledger.domain.account.rejections import (
    AlreadyReversed,
    AlreadyUndone,
    IdReused,
    MovedNoMoney,
    Rejection,
    ReversesAReversal,
    TargetOnAnotherAccount,
    UnknownTarget,
)
from account_ledger.domain.model.events import (
    Authorization,
    Credit,
    Debit,
    Fee,
    FeeRefund,
    IncomingEvent,
    Instalment,
    Instalments,
    InterestAccrual,
    InterestAdjustment,
    Posting,
    Reversal,
    Settlement,
    Whole,
)
from account_ledger.domain.model.ids import AccountId, Day
from account_ledger.domain.model.money import Amount, Direction, Money

SEPARATOR = "=" * 120

type Row = Sequence[str]

EVENTS = ("Event", "Booked", "Type", "Account", "Detail", "Value date")
APPLIED = ("Step", "Event", "Type", "Account", "Detail", "Value date")


class TextOutput(Protocol):
    """A text stream the report and the CLI write to: standard output or error, or a test's stand-in."""

    def write(self, text: str, /) -> int:
        """Write the text; return how many characters were written."""
        ...

    def flush(self) -> None:
        """Push what was written on to its destination."""
        ...


@dataclass(frozen=True, slots=True)
class TextReportSink:
    """The report sink that writes every day's report to ``out`` as text."""

    out: TextOutput

    def publish(self, reports: tuple[DayReport, ...]) -> None:
        """The whole report in one write, then a flush, so a closed pipe surfaces here, inside the CLI's handlers, not
        at the exit-time flush."""
        self.out.write(TextReportSink.render(reports))
        self.out.flush()

    @staticmethod
    def render(reports: Sequence[DayReport]) -> str:
        """Every day's report, in order, each after one blank line, ending with a newline."""
        return "\n\n".join(_format_day(report) for report in reports) + "\n"


def _format_day(report: DayReport) -> str:
    """One day's banner, then its events, its end-of-day steps, and its closing summary."""
    banner = f"{SEPARATOR}\nDay {report.day.number}\n{SEPARATOR}"
    blocks = (
        _format_block("Events processed", _format_table(EVENTS, _build_event_rows(report))),
        _format_block("EOD applied", _format_table(APPLIED, [_build_applied_row(row) for row in report.end_of_day])),
        _format_block("Closing summary", _format_table(_build_summary_header(report), _build_summary_rows(report))),
    )
    return "\n\n".join((banner, *blocks))


def _build_event_rows(report: DayReport) -> list[Row]:
    """A row per event the day processed, each followed by the rows of the instalments it generated."""
    rows: list[Row] = []
    for processed_event in report.processed_events:
        rows.extend(_build_processed_rows(processed_event))
    return rows


def _format_block(title: str, body: list[str]) -> str:
    """A titled block; one with no rows prints two spaces and `none` (AMB-033)."""
    return "\n".join((title, *(body or ["  none"])))


def _format_table(header: Row, rows: Sequence[Row]) -> list[str]:
    """A box of `+`, `-`, and `|`, every column left-aligned and as wide as its widest cell, header included."""
    if not rows:
        return []
    widths = [max(len(cell) for cell in column) for column in zip(header, *rows, strict=True)]
    border = "+" + "+".join("-" * (width + 2) for width in widths) + "+"

    def format_line(row: Row) -> str:
        """One table row, each cell padded to its column's width."""
        return "|" + "|".join(f" {cell.ljust(width)} " for cell, width in zip(row, widths, strict=True)) + "|"

    return [border, format_line(header), border, *(format_line(row) for row in rows), border]


def _build_processed_rows(processed_event: Processed) -> list[Row]:
    """The event's row, then a row per instalment it generated, each printing as a credit."""
    event, booked = processed_event.event, _format_day_cell(processed_event.event.booked)
    row = (
        event.id.format(),
        booked,
        _format_type(event),
        event.account.value,
        _format_detail(processed_event),
        _format_day_cell(event.value_date),
    )
    count = len(processed_event.instalments)
    return [row, *(_build_instalment_row(part, booked, count) for part in processed_event.instalments)]


def _build_instalment_row(part: Instalment, booked: str, count: int) -> Row:
    """An instalment's row, printed as a credit booked with the credit that generated it."""
    detail = f"{_format_money(part.amount)}, instalment {part.id.number} of {count}"
    return (part.id.format(), booked, "Credit", part.account.value, detail, _format_day_cell(part.value_date))


def _format_type(event: IncomingEvent) -> str:
    """The event's kind as the Type column prints it."""
    match event:
        case Credit():
            return "Credit"
        case Debit():
            return "Debit"
        case Authorization():
            return "Authorization"
        case Settlement():
            return "Settlement"
        case Reversal():
            return "Reversal"
        case _:
            assert_never(event)


def _format_detail(processed_event: Processed) -> str:
    """OUTPUT_TARGET's Detail text for an incoming event (tech-docs 003); a duplicate names what it repeats (D22)."""
    event = processed_event.event
    if isinstance(processed_event.entry, DuplicateIgnored):
        return f"duplicate of {event.id.format()}, no effect"
    match event:
        case Credit(amount=amount, posting=posting):
            return _format_money(amount) + _format_posting(posting)
        case Debit(amount=amount):
            return _format_money(amount)
        case Authorization(authorization=hold, amount=amount):
            return f"{hold.value}, hold {_format_money(amount)}"
        case Settlement(authorization=hold, amount=amount):
            settlement_text, hold_text = (
                _format_settlement(processed_event.entry),
                _format_kept_hold(processed_event.entry),
            )
            return f"{hold.value} {settlement_text} {_format_money(amount)}{hold_text}"
        case Reversal(target=target):
            return f"reverses {target.format()}"
        case _:
            assert_never(event)


def _format_posting(posting: Posting) -> str:
    """What a credit's detail adds for its posting: nothing when whole, the count when in instalments."""
    match posting:
        case Whole():
            return ""
        case Instalments(count=count):
            return f" in {_format_count(count.number)} equal instalments"
        case _:
            assert_never(posting)


NUMBER_WORDS = MappingProxyType(
    dict(zip(range(2, 11), ("two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"), strict=True))
)


def _format_count(count: int) -> str:
    """An instalment count as an English word from two to ten, and as digits above (tech-docs 003)."""
    return NUMBER_WORDS.get(count, str(count))


def _format_settlement(entry: LogEntry) -> str:
    """A settlement the table could not apply force-posts (AMB-012); any other settles for its amount."""
    is_force_post = isinstance(entry, SettlementForcePosted)
    return "force-posts" if is_force_post else "settles for"


def _format_kept_hold(entry: LogEntry) -> str:
    """A partial settlement that leaves part of the hold says so (D22)."""
    match entry:
        case SettlementApplied(state_after=PartiallySettled()):
            return ", hold kept"
        case _:
            return ""


def _build_applied_row(row: Generated | Capitalized | NothingGenerated) -> Row:
    """An end-of-day row: the step, the event it generated or `-`, and its detail or the note for nothing generated."""
    match row:
        case Generated(step=step, event=event):
            kind, detail = _format_generated_event(event)
            return (
                str(step.value),
                event.id.format(),
                kind,
                event.account.value,
                detail,
                _format_day_cell(event.value_date),
            )
        case Capitalized(event=event, days=days):
            step, kind = Step.CAPITALIZATION, "Interest capitalization"
            detail = f"{_format_money(event.amount)}, accrued {_format_days(days)}"
            return (
                str(step.value),
                event.id.format(),
                kind,
                event.account.value,
                detail,
                _format_day_cell(event.value_date),
            )
        case NothingGenerated(step=step, accounts=accounts, note=note):
            return (
                str(step.value),
                "-",
                _format_step(step),
                ", ".join(account_id.value for account_id in accounts),
                _format_note(note),
                "-",
            )
        case _:
            assert_never(row)


def _format_generated_event(event: EndOfDayEvent) -> tuple[str, str]:
    """An end-of-day event's Type and Detail texts (tech-docs 003)."""
    match event:
        case Fee(id=fee, amount=amount):
            return "Overdraft fee", f"{_format_money(amount)}, for {_format_day_cell(fee.for_day)}"
        case FeeRefund(fee=fee, amount=amount):
            return "Fee refund", f"{_format_money(amount)}, for {_format_day_cell(fee.for_day)}"
        case InterestAccrual(id=interest, amount=amount):
            return "Interest accrual", f"{_format_amount(amount.money)}, for {_format_day_cell(interest.for_day)}"
        case InterestAdjustment(id=interest, direction=direction, amount=amount):
            sign = MINUS if direction is Direction.DOWN else ""
            return (
                "Interest adjustment",
                f"{sign}{_format_amount(amount.money)}, for {_format_day_cell(interest.for_day)}",
            )
        case _:
            assert_never(event)


def _format_days(days: Sequence[Day]) -> str:
    """`Days 1 to 6` for three or more in a row, `Days 5 and 6` for two, `Day 5` for one, else `Days 1, 2, and 4`."""
    numbers = [day.number for day in days]
    if len(numbers) == 1:
        return f"Day {numbers[0]}"
    if len(numbers) == 2:
        return f"Days {numbers[0]} and {numbers[1]}"
    if numbers == list(range(numbers[0], numbers[-1] + 1)):
        return f"Days {numbers[0]} to {numbers[-1]}"
    return f"Days {', '.join(map(str, numbers[:-1]))}, and {numbers[-1]}"


def _format_step(step: Step) -> str:
    """The Type a step's row prints when the step generated nothing of its kind."""
    match step:
        case Step.FEES:
            return "Fee re-evaluation"
        case Step.INTEREST:
            return "Interest accrual"
        case Step.CAPITALIZATION:
            return "Interest capitalization"
        case _:
            assert_never(step)


def _format_note(note: Note) -> str:
    """The row a step prints when it generates nothing of its kind (tech-docs 002)."""
    match note:
        case Note.NO_FEE:
            return "no fee assessed or refunded"
        case Note.NO_NEW_FEE:
            return "no new fee assessed"
        case Note.NO_INTEREST:
            return "no interest accrued"
        case Note.NO_CAPITALIZATION:
            return "no interest capitalized"
        case _:
            assert_never(note)


def _build_summary_header(report: DayReport) -> Row:
    """`Item`, then a column per account, headed by its ID and currency."""
    return (
        "Item",
        *(f"{account.value} ({money.get_currency()})" for account, money in report.closing_balances.items()),
    )


def _build_summary_rows(report: DayReport) -> list[Row]:
    """Restated closings, oldest day first, then the day's balances, authorizations, and errors (tech-docs 003)."""
    accounts = tuple(report.closing_balances)
    restated_rows = [
        (
            f"Day {restatement.day.number} closing, restated",
            *(_format_restated_amount(restatement.closing_balances[account]) for account in accounts),
        )
        for restatement in report.restatements
    ]
    return [
        *restated_rows,
        ("Closing ledger balance", *(_format_amount(report.closing_balances[account]) for account in accounts)),
        ("Available balance", *(_format_amount(report.available_balances[account]) for account in accounts)),
        ("Authorizations", *(_format_authorizations(report.authorizations, account) for account in accounts)),
        ("Errors", *(_format_errors(report.errors[account]) for account in accounts)),
    ]


def _format_errors(entries: tuple[EventRejected, ...]) -> str:
    """The day's refusals for one account, joined by `; `, or `none` (AMB-014)."""
    return "; ".join(_format_refusal(entry) for entry in entries) or "none"


def _format_authorizations(records: Sequence[AuthorizationRecord], account: AccountId) -> str:
    """The account's authorizations with their states, joined by `; `, or `none`."""
    states = [_format_state(record) for record in records if record.authorization.account == account]
    return "; ".join(states) or "none"


def _format_refusal(entry: EventRejected) -> str:
    """A refusal's error text (tech-docs 001, D22)."""
    return f"{entry.event.id.format()} refused: {_format_reason(entry.reason, entry.event.account)}"


def _format_reason(reason: Rejection, account: AccountId) -> str:
    """Why the ledger refused an event on the account, as the Errors row prints it."""
    match reason:
        case IdReused():
            return "ID already used with different content"
        case AlreadyReversed(target=target, undoing_id=undoing_id):
            return f"{target.format()} is already reversed by {undoing_id.format()}"
        case ReversesAReversal(target=target):
            return f"{target.format()} is a reversal"
        case UnknownTarget(target=target):
            return f"{target.format()} is not in the log"
        case TargetOnAnotherAccount(target=target, target_account=target_account):
            return f"{target.format()} is on {target_account.value}, not {account.value}"
        case MovedNoMoney(target=target):
            return f"{target.format()} moved no money"
        case AlreadyUndone(part=part, undoing_id=undoing_id):
            return f"{part.format()} is already undone by {undoing_id.format()}"
        case _:
            assert_never(reason)


def _format_state(record: AuthorizationRecord) -> str:
    """An authorization's state as OUTPUT_TARGET prints it, with no currency code (AMB-019)."""
    hold, state = record.authorization.authorization.value, record.state
    match state:
        case Approved(hold=amount):
            return f"{hold} approved, hold {_format_amount(amount.money)}"
        case PartiallySettled(settled_amount=settled_amount, hold=remaining_hold):
            settled_text, hold_text = _format_amount(settled_amount.money), _format_amount(remaining_hold.money)
            return f"{hold} partially settled for {settled_text}, hold {hold_text}"
        case Declined(requested_amount=amount):
            return f"{hold} declined, {_format_amount(amount.money)}"
        case Settled(settled_amount=amount):
            return f"{hold} settled for {_format_amount(amount.money)}"
        case _:
            assert_never(state)


MINUS = "\u2212"


def _format_money(amount: Amount) -> str:
    """An amount with its currency code, as a Detail cell prints it."""
    return f"{amount.money.get_currency()} {_format_amount(amount.money)}"


def _format_amount(money: Money) -> str:
    """Its currency's places, a comma every three digits, and `−` for a negative (tech-docs 003)."""
    text = money.format_digits()
    integer_part, places = text.removeprefix("-").split(".")
    sign = MINUS if text.startswith("-") else ""
    return f"{sign}{int(integer_part):,}.{places}"


def _format_restated_amount(money: Money | None) -> str:
    """The amount, or `-` for a closing that did not change."""
    return "-" if money is None else _format_amount(money)


def _format_day_cell(day: Day) -> str:
    """A day as a table cell prints it: `Day N`."""
    return f"Day {day.number}"
