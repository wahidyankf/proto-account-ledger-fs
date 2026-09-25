"""Identifiers, days, and counts: value objects whose constructors refuse a malformed value."""

import re
from collections.abc import Iterator
from dataclasses import dataclass
from typing import assert_never

_ACCOUNT = re.compile(r"ACC-[0-9]{3}")
_HOLD = re.compile(r"Auth-[A-Za-z0-9]+")
_INCOMING = re.compile(r"E[0-9]+")


@dataclass(frozen=True, slots=True)
class InstalmentCount:
    """How many instalments a credit is posted in."""

    number: int

    def __post_init__(self) -> None:
        if self.number < 2:
            raise ValueError(f"an instalment count is at least 2, not {self.number}")

    @staticmethod
    def parse(text: str) -> InstalmentCount | IdFault:
        """The count the text holds, or a fault for one below 2 or not a whole number."""
        if re.fullmatch(r"[0-9]+", text) and int(text) >= 2:
            return InstalmentCount(int(text))
        return IdFault("instalment count", text)


@dataclass(frozen=True, slots=True)
class IdFault:
    """A text that is not a valid value of its kind."""

    kind: str
    text: str


@dataclass(frozen=True, slots=True, order=True)
class Day:
    """A day of the replay, counted from 0, the opening."""

    number: int

    def __post_init__(self) -> None:
        if self.number < 0:
            raise ValueError(f"a day is at least 0, not {self.number}")

    @staticmethod
    def parse(text: str) -> Day | IdFault:
        """The day the text holds, or a fault for one that is not a whole number."""
        return Day(int(text)) if re.fullmatch(r"[0-9]+", text) else IdFault("day", text)

    def advance(self) -> Day:
        """The day after this one."""
        return Day(self.number + 1)

    def span_to(self, last_day: Day) -> Iterator[Day]:
        """Each day from this one to ``last``, both included, in order."""
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
    def parse(text: str) -> AccountId | IdFault:
        """The account ID the text holds, or a fault for one not of the form `ACC-001`."""
        return AccountId(text) if _ACCOUNT.fullmatch(text) else IdFault("account ID", text)

    @property
    def number(self) -> str:
        """The three digits a marker carries."""
        return self.value.removeprefix("ACC-")


@dataclass(frozen=True, slots=True)
class AuthorizationId:
    """A hold, such as Auth-A."""

    value: str

    def __post_init__(self) -> None:
        if not _HOLD.fullmatch(self.value):
            raise ValueError(f"a hold ID is Auth- and letters or digits, not {self.value!r}")

    @staticmethod
    def parse(text: str) -> AuthorizationId | IdFault:
        """The hold ID the text holds, or a fault for one not of the form `Auth-A`."""
        return AuthorizationId(text) if _HOLD.fullmatch(text) else IdFault("hold ID", text)


@dataclass(frozen=True, slots=True)
class IncomingId:
    """An incoming event, such as E1."""

    value: str

    def __post_init__(self) -> None:
        if not _INCOMING.fullmatch(self.value):
            raise ValueError(f"an incoming event ID is E and digits, not {self.value!r}")

    @staticmethod
    def parse(text: str) -> IncomingId | IdFault:
        """The event ID the text holds, or a fault for one not of the form `E1`."""
        return IncomingId(text) if _INCOMING.fullmatch(text) else IdFault("event ID", text)


@dataclass(frozen=True, slots=True)
class InstalmentId:
    """An instalment a credit fired, such as E10-1."""

    parent: IncomingId
    number: int

    def __post_init__(self) -> None:
        if self.number < 1:
            raise ValueError(f"an instalment is numbered from 1, not {self.number}")


@dataclass(frozen=True, slots=True)
class FeeId:
    """FEE-001-D2@D5: an account's fee for a day, fired at the close of another."""

    account: AccountId
    covered_day: Day
    fired_day: Day


@dataclass(frozen=True, slots=True)
class RefundId:
    """REFUND-001-D2@D6: the refund of an account's fee for a day."""

    account: AccountId
    covered_day: Day
    fired_day: Day


@dataclass(frozen=True, slots=True)
class InterestId:
    """INT-001-D2@D5: an account's interest event for a day."""

    account: AccountId
    covered_day: Day
    fired_day: Day


@dataclass(frozen=True, slots=True)
class CapitalizationId:
    """CAP-001@D6: an account's capitalization at the close of a day."""

    account: AccountId
    fired_day: Day


type EventId = IncomingId | InstalmentId | FeeId | RefundId | InterestId | CapitalizationId


_EVENT = re.compile(
    r"(?P<incoming>E[0-9]+)(?:-(?P<part>[1-9][0-9]*))?"
    r"|(?P<kind>FEE|REFUND|INT)-(?P<account>[0-9]{3})-D(?P<for_day>[0-9]+)@D(?P<fired>[0-9]+)"
    r"|CAP-(?P<cap_account>[0-9]{3})@D(?P<cap_fired>[0-9]+)"
)


def parse_event_id(text: str) -> EventId | IdFault:
    """An incoming ID, an instalment, or a fired marker, as a reversal names its target (AMB-035)."""
    event_match = _EVENT.fullmatch(text)
    if event_match is None:
        return IdFault("event ID", text)
    group = event_match.group
    if group("incoming"):
        incoming_id = IncomingId(group("incoming"))
        return InstalmentId(incoming_id, int(group("part"))) if group("part") else incoming_id
    if group("kind"):
        account, covered_day, fired_day = (
            AccountId(f"ACC-{group('account')}"),
            Day(int(group("for_day"))),
            Day(int(group("fired"))),
        )
        match group("kind"):
            case "FEE":
                return FeeId(account, covered_day, fired_day)
            case "REFUND":
                return RefundId(account, covered_day, fired_day)
            case _:
                return InterestId(account, covered_day, fired_day)
    return CapitalizationId(AccountId(f"ACC-{group('cap_account')}"), Day(int(group("cap_fired"))))


def format_id(event_id: EventId) -> str:
    """The ID as the report prints it; a marker is built from its parts, never stored as a string."""
    match event_id:
        case IncomingId(value):
            return value
        case InstalmentId(parent, number):
            return f"{parent.value}-{number}"
        case FeeId(account, covered_day, fired_day):
            return f"FEE-{account.number}-D{covered_day.number}@D{fired_day.number}"
        case RefundId(account, covered_day, fired_day):
            return f"REFUND-{account.number}-D{covered_day.number}@D{fired_day.number}"
        case InterestId(account, covered_day, fired_day):
            return f"INT-{account.number}-D{covered_day.number}@D{fired_day.number}"
        case CapitalizationId(account, fired_day):
            return f"CAP-{account.number}@D{fired_day.number}"
        case _:
            assert_never(event_id)
