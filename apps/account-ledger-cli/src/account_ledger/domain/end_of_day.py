"""Closing a day: fees, interest, then capitalization, in that order (AMB-002, AMB-004, AMB-005, AMB-023)."""

from account_ledger.domain.fees import assess_fees
from account_ledger.domain.interest import accrue_interest, capitalize_interest
from account_ledger.domain.model.config import LedgerConfig
from account_ledger.domain.model.event_log import Log
from account_ledger.domain.model.ids import Day


def close_day(log: Log, today: Day, config: LedgerConfig) -> Log:
    """The log with every event the close of ``today`` fires."""
    for account in config.accounts:
        log = assess_fees(log, account, today, config.first_day)
    for account in config.accounts:
        log = accrue_interest(log, account, today, config.first_day)
    if today in config.capitalization_days:
        for account in config.accounts:
            log = capitalize_interest(log, account, today)
    return log
