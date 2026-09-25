"""The report as text: each day's banner and its three blocks, as OUTPUT_TARGET prints them (tech-docs 003)."""

from collections.abc import Sequence
from typing import assert_never

from account_ledger.core.authorizations import Approved, AuthorizationRecord, Declined, PartiallySettled, Settled
from account_ledger.core.event_log import Captured, Duplicate, ForcePosted, LogEntry, SettlementAccepted
from account_ledger.core.events import (
    AnyAmount,
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
from account_ledger.core.ids import AccountId, Day, text
from account_ledger.core.money import Direction, Money, currency, digits
from account_ledger.core.report import Capitalized, DayReport, EndOfDayEvent, Fired, NothingFired, Processed, Step

RULE = "=" * 120

type Row = Sequence[str]

EVENTS = ("Event", "Booked", "Type", "Account", "Detail", "Value date")
APPLIED = ("Step", "Event", "Type", "Account", "Detail", "Value date")


def render(reports: Sequence[DayReport]) -> str:
    """Every day's report, in order, each after one blank line, ending with a newline."""
    return "\n\n".join(_day(report) for report in reports) + "\n"


def _day(report: DayReport) -> str:
    banner = f"{RULE}\nDay {report.day.number}\n{RULE}"
    blocks = (
        _block("Events processed", _table(EVENTS, [row for each in report.processed for row in _processed(each)])),
        _block("EOD applied", _table(APPLIED, [_applied(row) for row in report.end_of_day])),
        _block("Closing summary", _table(_summary_header(report), _summary(report))),
    )
    return "\n\n".join((banner, *blocks))


def _block(title: str, body: list[str]) -> str:
    """A titled block; one with no rows prints two spaces and `none` (AMB-033)."""
    return "\n".join((title, *(body or ["  none"])))


def _table(header: Row, rows: Sequence[Row]) -> list[str]:
    """A box of `+`, `-`, and `|`, every column left-aligned and as wide as its widest cell, header included."""
    if not rows:
        return []
    widths = [max(len(row[n]) for row in (header, *rows)) for n in range(len(header))]
    border = "+" + "+".join("-" * (width + 2) for width in widths) + "+"

    def line(row: Row) -> str:
        return "|" + "|".join(f" {cell.ljust(width)} " for cell, width in zip(row, widths, strict=True)) + "|"

    return [border, line(header), border, *(line(row) for row in rows), border]


def _processed(processed: Processed) -> list[Row]:
    """The event's row, then a row per instalment it fired, each printing as a credit."""
    event, booked = processed.event, _day_cell(processed.event.booked)
    row = (text(event.id), booked, _type(event), event.account.value, _detail(processed), _day_cell(event.value_day))
    count = len(processed.instalments)
    return [row, *(_instalment(part, booked, count) for part in processed.instalments)]


def _instalment(part: Instalment, booked: str, count: int) -> Row:
    detail = f"{_money(part.amount)}, instalment {part.id.n} of {count}"
    return (text(part.id), booked, "Credit", part.account.value, detail, _day_cell(part.value_day))


def _type(event: IncomingEvent) -> str:
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


def _detail(processed: Processed) -> str:
    """OUTPUT_TARGET's Detail text for an incoming event (tech-docs 003); a duplicate names what it repeats (D22)."""
    event = processed.event
    if isinstance(processed.entry, Duplicate):
        return f"duplicate of {text(event.id)}, no effect"
    match event:
        case Credit(amount=amount, posting=posting):
            return _money(amount) + _posting(posting)
        case Debit(amount=amount):
            return _money(amount)
        case Authorization(authorization=hold, amount=amount):
            return f"{hold.value}, hold {_money(amount)}"
        case Settlement(authorization=hold, amount=amount):
            return f"{hold.value} {_settles(processed.entry)} {_money(amount)}{_kept(processed.entry)}"
        case Reversal(reverses=target):
            return f"reverses {text(target)}"
        case _:
            assert_never(event)


def _posting(posting: Posting) -> str:
    match posting:
        case Whole():
            return ""
        case Instalments(count=count):
            return f" in {_count(count.n)} equal instalments"
        case _:
            assert_never(posting)


SPELLED = dict(zip(range(2, 11), ("two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"), strict=True))


def _count(n: int) -> str:
    """An instalment count as an English word from two to ten, and as digits above (tech-docs 003)."""
    return SPELLED.get(n, str(n))


def _settles(entry: LogEntry) -> str:
    """A settlement the table could not apply force-posts (AMB-012); any other settles for its amount."""
    forced = isinstance(entry, SettlementAccepted) and isinstance(entry.effect, ForcePosted)
    return "force-posts" if forced else "settles for"


def _kept(entry: LogEntry) -> str:
    """A partial capture that leaves part of the hold says so (D22)."""
    match entry:
        case SettlementAccepted(effect=Captured(after=PartiallySettled())):
            return ", hold kept"
        case _:
            return ""


def _applied(row: Fired | Capitalized | NothingFired) -> Row:
    match row:
        case Fired(step=step, event=event):
            kind, detail = _fired(event)
            return (str(step.value), text(event.id), kind, event.account.value, detail, _day_cell(event.value_day))
        case Capitalized(event=event, days=days):
            step, kind = Step.CAPITALIZATION, "Interest capitalization"
            detail = f"{_money(event.amount)}, accrued {_days(days)}"
            return (str(step.value), text(event.id), kind, event.account.value, detail, _day_cell(event.value_day))
        case NothingFired(step=step, accounts=accounts, note=note):
            return (str(step.value), "-", _step(step), ", ".join(each.value for each in accounts), note.value, "-")
        case _:
            assert_never(row)


def _fired(event: EndOfDayEvent) -> tuple[str, str]:
    """An end-of-day event's Type and Detail texts (tech-docs 003)."""
    match event:
        case Fee(id=fee, amount=amount):
            return "Overdraft fee", f"{_money(amount)}, for {_day_cell(fee.for_day)}"
        case FeeRefund(fee=fee, amount=amount):
            return "Fee refund", f"{_money(amount)}, for {_day_cell(fee.for_day)}"
        case InterestAccrual(id=interest, amount=amount):
            return "Interest accrual", f"{_amount(amount.money)}, for {_day_cell(interest.for_day)}"
        case InterestAdjustment(id=interest, direction=direction, amount=amount):
            sign = MINUS if direction is Direction.DOWN else ""
            return "Interest adjustment", f"{sign}{_amount(amount.money)}, for {_day_cell(interest.for_day)}"
        case _:
            assert_never(event)


def _days(days: Sequence[Day]) -> str:
    """`Days 1 to 6` for three or more in a row, `Days 5 and 6` for two, `Day 5` for one, else `Days 1, 2, and 4`."""
    numbers = [day.number for day in days]
    if len(numbers) == 1:
        return f"Day {numbers[0]}"
    if len(numbers) == 2:
        return f"Days {numbers[0]} and {numbers[1]}"
    if numbers == list(range(numbers[0], numbers[-1] + 1)):
        return f"Days {numbers[0]} to {numbers[-1]}"
    return f"Days {', '.join(map(str, numbers[:-1]))}, and {numbers[-1]}"


def _step(step: Step) -> str:
    """The Type a step's row prints when the step fired nothing of its kind."""
    match step:
        case Step.FEES:
            return "Fee re-evaluation"
        case Step.INTEREST:
            return "Interest accrual"
        case Step.CAPITALIZATION:
            return "Interest capitalization"
        case _:
            assert_never(step)


def _summary_header(report: DayReport) -> Row:
    return ("Item", *(f"{account.value} ({currency(money)})" for account, money in report.closing.items()))


def _summary(report: DayReport) -> list[Row]:
    """Restated closings, oldest day first, then the day's balances, authorizations, and errors (tech-docs 003)."""
    accounts = tuple(report.closing)
    restated = [
        (f"Day {each.day.number} closing, restated", *(_or_dash(each.closing[account]) for account in accounts))
        for each in report.restated
    ]
    return [
        *restated,
        ("Closing ledger balance", *(_amount(report.closing[account]) for account in accounts)),
        ("Available balance", *(_amount(report.available[account]) for account in accounts)),
        ("Authorizations", *(_authorizations(report.authorizations, account) for account in accounts)),
        ("Errors", *("; ".join(report.errors[account]) or "none" for account in accounts)),
    ]


def _authorizations(known: Sequence[AuthorizationRecord], account: AccountId) -> str:
    states = [_state(record) for record in known if record.authorization.account == account]
    return "; ".join(states) or "none"


def _state(record: AuthorizationRecord) -> str:
    """An authorization's state as OUTPUT_TARGET prints it, with no currency code (AMB-019)."""
    hold, state = record.authorization.authorization.value, record.state
    match state:
        case Approved(hold=amount):
            return f"{hold} approved, hold {_amount(amount.money)}"
        case PartiallySettled(captured=captured, hold=kept):
            return f"{hold} partially settled for {_amount(captured.money)}, hold {_amount(kept.money)}"
        case Declined(requested=amount):
            return f"{hold} declined, {_amount(amount.money)}"
        case Settled(captured=amount):
            return f"{hold} settled for {_amount(amount.money)}"
        case _:
            assert_never(state)


MINUS = "\u2212"


def _money(amount: AnyAmount) -> str:
    """An amount with its currency code, as a Detail cell prints it."""
    return f"{currency(amount.money)} {_amount(amount.money)}"


def _amount(money: Money) -> str:
    """Its currency's places, a comma every three digits, and `−` for a negative (tech-docs 003)."""
    text = digits(money)
    whole, places = text.removeprefix("-").split(".")
    return f"{MINUS if text.startswith('-') else ''}{int(whole):,}.{places}"


def _or_dash(money: Money | None) -> str:
    return "-" if money is None else _amount(money)


def _day_cell(day: Day) -> str:
    return f"Day {day.number}"
