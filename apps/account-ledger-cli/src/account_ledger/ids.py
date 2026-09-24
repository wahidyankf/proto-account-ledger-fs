"""Identifiers, days, and counts: value objects whose constructors refuse a malformed value."""

import re
from dataclasses import dataclass
from typing import assert_never

_ACCOUNT = re.compile(r"ACC-[0-9]{3}")
_HOLD = re.compile(r"Auth-[A-Za-z0-9]+")
_INCOMING = re.compile(r"E[0-9]+")


@dataclass(frozen=True, slots=True)
class InstalmentCount:
    """How many instalments a credit is posted in."""

    n: int

    def __post_init__(self) -> None:
        if self.n < 2:
            raise ValueError(f"an instalment count is at least 2, not {self.n}")

    @staticmethod
    def parse(text: str) -> InstalmentCount | IdFault:
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
        return Day(int(text)) if re.fullmatch(r"[0-9]+", text) else IdFault("day", text)

    def next(self) -> Day:
        return Day(self.number + 1)


@dataclass(frozen=True, slots=True)
class AccountId:
    """An account, such as ACC-001."""

    value: str

    def __post_init__(self) -> None:
        if not _ACCOUNT.fullmatch(self.value):
            raise ValueError(f"an account ID is ACC- and three digits, not {self.value!r}")

    @staticmethod
    def parse(text: str) -> AccountId | IdFault:
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
        return IncomingId(text) if _INCOMING.fullmatch(text) else IdFault("event ID", text)


@dataclass(frozen=True, slots=True)
class InstalmentId:
    """An instalment a credit fired, such as E10-1."""

    parent: IncomingId
    n: int

    def __post_init__(self) -> None:
        if self.n < 1:
            raise ValueError(f"an instalment is numbered from 1, not {self.n}")


@dataclass(frozen=True, slots=True)
class FeeId:
    """FEE-001-D2@D5: an account's fee for a day, fired at the close of another."""

    account: AccountId
    for_day: Day
    fired_day: Day


@dataclass(frozen=True, slots=True)
class RefundId:
    """REFUND-001-D2@D6: the refund of an account's fee for a day."""

    account: AccountId
    for_day: Day
    fired_day: Day


@dataclass(frozen=True, slots=True)
class InterestId:
    """INT-001-D2@D5: an account's interest event for a day."""

    account: AccountId
    for_day: Day
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
    found = _EVENT.fullmatch(text)
    if found is None:
        return IdFault("event ID", text)
    group = found.group
    if group("incoming"):
        incoming = IncomingId(group("incoming"))
        return InstalmentId(incoming, int(group("part"))) if group("part") else incoming
    if group("kind"):
        account, for_day, fired = (
            AccountId(f"ACC-{group('account')}"),
            Day(int(group("for_day"))),
            Day(int(group("fired"))),
        )
        match group("kind"):
            case "FEE":
                return FeeId(account, for_day, fired)
            case "REFUND":
                return RefundId(account, for_day, fired)
            case _:
                return InterestId(account, for_day, fired)
    return CapitalizationId(AccountId(f"ACC-{group('cap_account')}"), Day(int(group("cap_fired"))))


def text(event_id: EventId) -> str:
    """The ID as the report prints it; a marker is built from its parts, never stored as a string."""
    match event_id:
        case IncomingId(value):
            return value
        case InstalmentId(parent, n):
            return f"{parent.value}-{n}"
        case FeeId(account, for_day, fired):
            return f"FEE-{account.number}-D{for_day.number}@D{fired.number}"
        case RefundId(account, for_day, fired):
            return f"REFUND-{account.number}-D{for_day.number}@D{fired.number}"
        case InterestId(account, for_day, fired):
            return f"INT-{account.number}-D{for_day.number}@D{fired.number}"
        case CapitalizationId(account, fired):
            return f"CAP-{account.number}@D{fired.number}"
        case _:
            assert_never(event_id)
