"""Identifiers, days, and counts: value objects whose constructors refuse a malformed value."""

import re
from collections.abc import Iterator
from dataclasses import dataclass
from typing import ClassVar, Self

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
class _TextIdBase:
    """An ID the stream writes as text, checked against its kind's pattern: each kind names its PATTERN, the KIND a
    fault calls it, and the SHAPE its guard states."""

    PATTERN: ClassVar[re.Pattern[str]]
    KIND: ClassVar[str]
    SHAPE: ClassVar[str]
    value: str

    def __post_init__(self) -> None:
        if not self.PATTERN.fullmatch(self.value):
            raise ValueError(f"{self.SHAPE}, not {self.value!r}")

    @classmethod
    def parse(cls, text: str) -> Result[Self, IdFault]:
        """The ID the text holds, or a fault for text not of its kind's form."""
        return Ok(cls(text)) if cls.PATTERN.fullmatch(text) else Err(IdFault(cls.KIND, text))


@dataclass(frozen=True, slots=True)
class AccountId(_TextIdBase):
    """An account, such as ACC-001."""

    PATTERN: ClassVar[re.Pattern[str]] = _ACCOUNT
    KIND: ClassVar[str] = "account ID"
    SHAPE: ClassVar[str] = "an account ID is ACC- and three digits"

    @property
    def number(self) -> str:
        """The three digits a generated ID carries."""
        return self.value.removeprefix("ACC-")


@dataclass(frozen=True, slots=True)
class AuthorizationId(_TextIdBase):
    """A hold, such as Auth-A."""

    PATTERN: ClassVar[re.Pattern[str]] = _AUTHORIZATION
    KIND: ClassVar[str] = "authorization ID"
    SHAPE: ClassVar[str] = "an authorization ID is Auth- and letters or digits"


@dataclass(frozen=True, slots=True)
class IncomingId(_TextIdBase):
    """An incoming event, such as E1."""

    PATTERN: ClassVar[re.Pattern[str]] = _INCOMING
    KIND: ClassVar[str] = "event ID"
    SHAPE: ClassVar[str] = "an incoming event ID is E and digits"

    def format(self) -> str:
        """The ID as the report prints it, such as E1."""
        return self.value


@dataclass(frozen=True, slots=True)
class InstalmentId:
    """An instalment a credit generated, such as E10-1."""

    parent: IncomingId
    number: int

    def __post_init__(self) -> None:
        if self.number < 1:
            raise ValueError(f"an instalment is numbered from 1, not {self.number}")

    def format(self) -> str:
        """The ID as the report prints it, such as E10-1."""
        return f"{self.parent.value}-{self.number}"


@dataclass(frozen=True, slots=True)
class _DayEventIdBase:
    """An ID the ledger generates for an account's event about one day, at the close of another, printed as its
    PREFIX, the account's digits, and the two days, such as FEE-001-D2@D5; built from its parts, never stored as a
    string."""

    PREFIX: ClassVar[str]
    account: AccountId
    for_day: Day
    generated_day: Day

    def format(self) -> str:
        """The ID as the report prints it."""
        return f"{self.PREFIX}-{self.account.number}-D{self.for_day.number}@D{self.generated_day.number}"


@dataclass(frozen=True, slots=True)
class FeeId(_DayEventIdBase):
    """FEE-001-D2@D5: an account's fee for a day, generated at the close of another."""

    PREFIX: ClassVar[str] = "FEE"


@dataclass(frozen=True, slots=True)
class RefundId(_DayEventIdBase):
    """REFUND-001-D2@D6: the refund of an account's fee for a day."""

    PREFIX: ClassVar[str] = "REFUND"


@dataclass(frozen=True, slots=True)
class InterestId(_DayEventIdBase):
    """INT-001-D2@D5: an account's interest event for a day."""

    PREFIX: ClassVar[str] = "INT"


@dataclass(frozen=True, slots=True)
class CapitalizationId:
    """CAP-001@D6: an account's capitalization at the close of a day."""

    account: AccountId
    generated_day: Day

    def format(self) -> str:
        """The ID as the report prints it; built from its parts, never stored as a string."""
        return f"CAP-{self.account.number}@D{self.generated_day.number}"


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
