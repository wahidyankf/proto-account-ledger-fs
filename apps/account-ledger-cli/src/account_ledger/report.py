"""The day report: what one day's close shows, as data."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from account_ledger.balances import available_of, closing_of
from account_ledger.config import LedgerConfig
from account_ledger.ids import AccountId, Day
from account_ledger.log import Log
from account_ledger.money import Money


@dataclass(frozen=True, slots=True)
class DayReport:
    """One day's close; each per-account field maps an account ID to its money."""

    day: Day
    closing: Mapping[AccountId, Money]
    available: Mapping[AccountId, Money]


def report(log: Log, day: Day, config: LedgerConfig) -> DayReport:
    """The report for ``day`` from the log as it stands at that day's close."""
    closings: dict[AccountId, Money] = {account.id: closing_of(log, account, day) for account in config.accounts}
    availables: dict[AccountId, Money] = {account.id: available_of(log, account, day) for account in config.accounts}
    return DayReport(day, MappingProxyType(closings), MappingProxyType(availables))
