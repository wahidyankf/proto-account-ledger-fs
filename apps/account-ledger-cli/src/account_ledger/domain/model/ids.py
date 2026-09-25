"""Identifiers, days, and counts: value objects whose constructors refuse a malformed value."""

import re
from collections.abc import Iterator
from dataclasses import dataclass
from typing import assert_never

from account_ledger.common.result import Err, Ok, Result

_ACCOUNT = re.compile(r"ACC-[0-9]{3}")
_AUTHORIZATION = re.compile(r"Auth-[A-Za-z0-9]+")
_INCOMING = re.compile(r"E[0-9]+")
MAX_INSTALMENTS = 360  # a monthly plan over thirty years; a split never grows past it (NUMBERS.md)


def _is_instalment_count(number: int) -> bool:
    """Whether the number is from 2 to ``MAX_INSTALMENTS``: the one rule the guard and ``make`` both apply."""
    return 2 <= number <= MAX_INSTALMENTS


@dataclass(frozen=True, slots=True)
class InstalmentCount:
    """How many instalments a credit is posted in, from 2 to ``MAX_INSTALMENTS``."""

    number: int

    def __post_init__(self) -> None:
        if not _is_instalment_count(self.number):
            raise ValueError(f"an instalment count is from 2 to {MAX_INSTALMENTS}, not {self.number}")

    @staticmethod
    def make(number: int) -> Result[InstalmentCount, IdFault]:
        """The count, or a fault for one below 2 or above ``MAX_INSTALMENTS``."""
        if _is_instalment_count(number):
            return Ok(InstalmentCount(number))
        return Err(IdFault("instalment count", str(number)))

    @staticmethod
    def parse(text: str) -> Result[InstalmentCount, IdFault]:
        """The count the text holds, or a fault for one outside 2 to ``MAX_INSTALMENTS`` or not a whole number."""
        if re.fullmatch(r"[0-9]+", text):
            return InstalmentCount.make(int(text))
        return Err(IdFault("instalment count", text))


@dataclass(frozen=True, slots=True)
class IdFault:
    """A text that is not a valid value of its kind."""

    kind: str
    text: str


def _is_day_number(number: int) -> bool:
    """Whether the number is a day, 0 or later: the one rule the guard and ``make`` both apply."""
    return number >= 0


@dataclass(frozen=True, slots=True, order=True)
class Day:
    """A day of the ledger, counted from 0, the opening."""

    number: int

    def __post_init__(self) -> None:
        if not _is_day_number(self.number):
            raise ValueError(f"a day is at least 0, not {self.number}")

    @staticmethod
    def make(number: int) -> Result[Day, IdFault]:
        """The day, or a fault for one before Day 0."""
        return Ok(Day(number)) if _is_day_number(number) else Err(IdFault("day", str(number)))

    @staticmethod
    def parse(text: str) -> Result[Day, IdFault]:
        """The day the text holds, or a fault for one that is not a whole number."""
        return Day.make(int(text)) if re.fullmatch(r"[0-9]+", text) else Err(IdFault("day", text))

    def advance(self) -> Day:
        """The day after this one."""
        return Day(self.number + 1)

    def span_to(self, last_day: Day) -> Iterator[Day]:
        """Each day from this one to ``last_day``, both included, in order."""
        day = self
        while day <= last_day:
            yield day
            day = day.advance()


@dataclass(frozen=True, slots=True)
class AccountId:
    """An account, such as ACC-001."""

    value: str

    def __post_init__(self) -> None:
        if not _ACCOUNT.fullmatch(self.value):
            raise ValueError(f"an account ID is ACC- and three digits, not {self.value!r}")

    @staticmethod
    def parse(text: str) -> Result[AccountId, IdFault]:
        """The account ID the text holds, or a fault for one not of the form `ACC-001`."""
        return Ok(AccountId(text)) if _ACCOUNT.fullmatch(text) else Err(IdFault("account ID", text))

    @property
    def number(self) -> str:
        """The three digits a generated ID carries."""
        return self.value.removeprefix("ACC-")


@dataclass(frozen=True, slots=True)
class AuthorizationId:
    """A hold, such as Auth-A."""

    value: str

    def __post_init__(self) -> None:
        if not _AUTHORIZATION.fullmatch(self.value):
            raise ValueError(f"a authorization ID is Auth- and letters or digits, not {self.value!r}")

    @staticmethod
    def parse(text: str) -> Result[AuthorizationId, IdFault]:
        """The authorization ID the text holds, or a fault for one not of the form `Auth-A`."""
        return Ok(AuthorizationId(text)) if _AUTHORIZATION.fullmatch(text) else Err(IdFault("authorization ID", text))


@dataclass(frozen=True, slots=True)
class IncomingId:
    """An incoming event, such as E1."""

    value: str

    def __post_init__(self) -> None:
        if not _INCOMING.fullmatch(self.value):
            raise ValueError(f"an incoming event ID is E and digits, not {self.value!r}")

    @staticmethod
    def parse(text: str) -> Result[IncomingId, IdFault]:
        """The event ID the text holds, or a fault for one not of the form `E1`."""
        return Ok(IncomingId(text)) if _INCOMING.fullmatch(text) else Err(IdFault("event ID", text))


@dataclass(frozen=True, slots=True)
class InstalmentId:
    """An instalment a credit generated, such as E10-1."""

    parent: IncomingId
    number: int

    def __post_init__(self) -> None:
        if self.number < 1:
            raise ValueError(f"an instalment is numbered from 1, not {self.number}")


@dataclass(frozen=True, slots=True)
class FeeId:
    """FEE-001-D2@D5: an account's fee for a day, generated at the close of another."""

    account: AccountId
    for_day: Day
    generated_day: Day


@dataclass(frozen=True, slots=True)
class RefundId:
    """REFUND-001-D2@D6: the refund of an account's fee for a day."""

    account: AccountId
    for_day: Day
    generated_day: Day


@dataclass(frozen=True, slots=True)
class InterestId:
    """INT-001-D2@D5: an account's interest event for a day."""

    account: AccountId
    for_day: Day
    generated_day: Day


@dataclass(frozen=True, slots=True)
class CapitalizationId:
    """CAP-001@D6: an account's capitalization at the close of a day."""

    account: AccountId
    generated_day: Day


type EventId = IncomingId | InstalmentId | FeeId | RefundId | InterestId | CapitalizationId


_EVENT = re.compile(
    r"(?P<incoming>E[0-9]+)(?:-(?P<part>[1-9][0-9]*))?"
    r"|(?P<kind>FEE|REFUND|INT)-(?P<account>[0-9]{3})-D(?P<for_day>[0-9]+)@D(?P<generated>[0-9]+)"
    r"|CAP-(?P<cap_account>[0-9]{3})@D(?P<cap_generated>[0-9]+)"
)


def parse_event_id(text: str) -> Result[EventId, IdFault]:
    """An incoming ID, an instalment, or a generated ID, as a reversal names its target (AMB-035)."""
    event_match = _EVENT.fullmatch(text)
    return Err(IdFault("event ID", text)) if event_match is None else Ok(_build_event_id(event_match))


def _build_event_id(event_match: re.Match[str]) -> EventId:
    """The ID a matched text names; the pattern admits only valid parts, so every constructor here accepts them."""
    group = event_match.group
    if group("incoming"):
        incoming_id = IncomingId(group("incoming"))
        return InstalmentId(incoming_id, int(group("part"))) if group("part") else incoming_id
    if group("kind"):
        account, for_day, generated_day = (
            AccountId(f"ACC-{group('account')}"),
            Day(int(group("for_day"))),
            Day(int(group("generated"))),
        )
        match group("kind"):
            case "FEE":
                return FeeId(account, for_day, generated_day)
            case "REFUND":
                return RefundId(account, for_day, generated_day)
            case _:
                return InterestId(account, for_day, generated_day)
    return CapitalizationId(AccountId(f"ACC-{group('cap_account')}"), Day(int(group("cap_generated"))))


def format_id(event_id: EventId) -> str:
    """The ID as the report prints it; a generated ID is built from its parts, never stored as a string."""
    match event_id:
        case IncomingId(value):
            return value
        case InstalmentId(parent, number):
            return f"{parent.value}-{number}"
        case FeeId(account, for_day, generated_day):
            return f"FEE-{account.number}-D{for_day.number}@D{generated_day.number}"
        case RefundId(account, for_day, generated_day):
            return f"REFUND-{account.number}-D{for_day.number}@D{generated_day.number}"
        case InterestId(account, for_day, generated_day):
            return f"INT-{account.number}-D{for_day.number}@D{generated_day.number}"
        case CapitalizationId(account, generated_day):
            return f"CAP-{account.number}@D{generated_day.number}"
        case _:
            assert_never(event_id)
