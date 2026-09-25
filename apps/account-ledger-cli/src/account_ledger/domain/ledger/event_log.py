"""The log: the append-only tuple of every account's entries, the only state the ledger keeps (AMB-004, D7)."""

from account_ledger.domain.account.aggregate import AccountAggregate, AccountAggregateIn
from account_ledger.domain.account.domain_events import LogEntry
from account_ledger.domain.model.config import AccountOpening, AccountOpeningIn, is_aed
from account_ledger.domain.model.money import Aed, Bhd

type Log = tuple[LogEntry, ...]


def append_entry(log: Log, entry: LogEntry) -> Log:
    """A new log with the entry at the end; nothing is ever changed or removed."""
    return (*log, entry)


def find_history[M: (Aed, Bhd)](log: Log, account: AccountOpeningIn[M]) -> AccountAggregateIn[M]:
    """The Account aggregate: the account with its own entries in the log, in log order."""
    return AccountAggregateIn(account, tuple(entry for entry in log if entry.event.account == account.id))


def find_history_of(log: Log, account: AccountOpening) -> AccountAggregate:
    """``find_history`` for an account whose currency is known only at run time."""
    # Both branches read alike; each gives the generic call an account of one known currency.
    if is_aed(account):
        return find_history(log, account)
    return find_history(log, account)
