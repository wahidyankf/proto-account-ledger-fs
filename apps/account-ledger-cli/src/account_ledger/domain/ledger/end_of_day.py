"""Closing a day: fees, interest, then capitalization, in that order (AMB-002, AMB-004, AMB-005, AMB-023)."""

from collections.abc import Callable

from account_ledger.common.result import Err, Ok, Result
from account_ledger.domain.account.domain_events import (
    LogEntry,
)
from account_ledger.domain.account.fees import (
    assess_fees_of,
)
from account_ledger.domain.account.history import (
    AnyHistory,
)
from account_ledger.domain.account.interest import (
    accrue_interest_of,
    capitalize_interest_of,
)
from account_ledger.domain.ledger.event_log import (
    Log,
    find_history_of,
)
from account_ledger.domain.model.config import LedgerConfig
from account_ledger.domain.model.ids import Day
from account_ledger.domain.model.money import CurrencyMismatch

type _Step = Callable[[AnyHistory], Result[tuple[LogEntry, ...], CurrencyMismatch]]


def close_day(log: Log, today: Day, config: LedgerConfig) -> Result[Log, CurrencyMismatch]:
    """The log with every event the close of ``today`` generates: each step runs on every account's history before the
    next step, so the log holds each step's events together, in account order."""
    steps: list[_Step] = [
        lambda history: assess_fees_of(history, today, config.first_day),
        lambda history: accrue_interest_of(history, today, config.first_day),
    ]
    if today in config.capitalization_days:
        steps.append(lambda history: capitalize_interest_of(history, today))
    for step in steps:
        for account in config.accounts:
            if isinstance(entries := step(find_history_of(log, account)), Err):
                return entries
            log = (*log, *entries.value)
    return Ok(log)
