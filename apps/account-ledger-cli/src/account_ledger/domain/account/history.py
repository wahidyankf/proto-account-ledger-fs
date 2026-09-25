"""The Account aggregate's history: one account and its own entries, the only thing a rule about the account reads."""

from collections.abc import Iterator
from dataclasses import dataclass
from typing import TypeIs

from account_ledger.domain.account.domain_events import (
    AuthorizationApproved,
    AuthorizationDeclined,
    DuplicateIgnored,
    EventRejected,
    InstalmentPosted,
    LogEntry,
    LoggedEvent,
)
from account_ledger.domain.model.config import AccountIn
from account_ledger.domain.model.events import Instalment
from account_ledger.domain.model.ids import EventId, IncomingId
from account_ledger.domain.model.money import Aed, Bhd


@dataclass(frozen=True, slots=True)
class AccountHistoryIn[M: (Aed, Bhd)]:
    """The Account aggregate's history: one account and its own entries, in log order. Every rule about one account
    reads a history, never the log, so it cannot see another account's entries."""

    account: AccountIn[M]
    entries: tuple[LogEntry, ...]

    def append(self, entry: LogEntry) -> AccountHistoryIn[M]:
        """This history with the entry at the end; nothing is ever changed or removed."""
        assert entry.event.account == self.account.id  # a history holds only its own account's entries
        return AccountHistoryIn(self.account, (*self.entries, entry))


type AccountHistory = AccountHistoryIn[Aed] | AccountHistoryIn[Bhd]


def is_aed_history(history: AccountHistory) -> TypeIs[AccountHistoryIn[Aed]]:
    """Whether the history is an AED account's; when it is not, the type checker knows it is a BHD account's."""
    return isinstance(history.account.opening, Aed)


def find_first_entry(entries: tuple[LogEntry, ...], event_id: EventId) -> LogEntry | None:
    """The first entry for an event ID, the one a reversal targets (AMB-028, AMB-035)."""
    return next((entry for entry in entries if entry.event.id == event_id), None)


def list_instalments[M: (Aed, Bhd)](history: AccountHistoryIn[M], credit: IncomingId) -> tuple[Instalment, ...]:
    """The instalments a credit generated, in order (AMB-017)."""
    return tuple(
        entry.event
        for entry in history.entries
        if isinstance(entry, InstalmentPosted) and entry.event.id.parent == credit
    )


def list_instalments_of(history: AccountHistory, credit: IncomingId) -> tuple[Instalment, ...]:
    """``list_instalments`` for an account whose currency is known only at run time."""
    if is_aed_history(history):
        return list_instalments(history, credit)
    return list_instalments(history, credit)


def list_counted_events[M: (Aed, Bhd)](history: AccountHistoryIn[M]) -> Iterator[LoggedEvent]:
    """The events of the account's postings; a hold is read by ``sum_holds``, and a refusal or a retry moves nothing."""
    for entry in history.entries:
        match entry:
            case AuthorizationApproved() | AuthorizationDeclined() | EventRejected() | DuplicateIgnored():
                pass
            case _:
                yield entry.event
