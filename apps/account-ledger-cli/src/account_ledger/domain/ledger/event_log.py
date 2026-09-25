"""The log: the append-only tuple of every account's entries, the only state the ledger keeps (AMB-004, D7)."""

from account_ledger.domain.account.account import Account, AccountIn
from account_ledger.domain.account.domain_events import LogEntry
from account_ledger.domain.account.event_log import EventLog
from account_ledger.domain.model.config import AccountOpening, AccountOpeningIn, is_aed
from account_ledger.domain.model.money import Aed, Bhd

type Log = tuple[LogEntry, ...]


def append_entry(log: Log, entry: LogEntry) -> Log:
    """A new log with the entry at the end; nothing is ever changed or removed."""
    return (*log, entry)


def find_history[M: (Aed, Bhd)](log: Log, opening: AccountOpeningIn[M]) -> AccountIn[M]:
    """The Account aggregate: the account as opened, with its own entries in the log, in log order."""
    return AccountIn(opening.id, opening.balance, EventLog(log).select(opening.id))


def find_history_of(log: Log, opening: AccountOpening) -> Account:
    """``find_history`` for an account whose currency is known only at run time."""
    # Both branches read alike; each gives the generic call an account of one known currency.
    if is_aed(opening):
        return find_history(log, opening)
    return find_history(log, opening)
