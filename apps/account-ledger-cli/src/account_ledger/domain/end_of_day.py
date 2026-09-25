"""Closing a day: fees, interest, then capitalization, in that order (AMB-002, AMB-004, AMB-005, AMB-023)."""

from collections.abc import Callable

from account_ledger.domain.fees import assess_fees
from account_ledger.domain.interest import accrue_interest, capitalize_interest
from account_ledger.domain.model.config import AnyAccount, LedgerConfig
from account_ledger.domain.model.event_log import Log
from account_ledger.domain.model.ids import Day
from account_ledger.domain.model.money import CurrencyMismatch
from account_ledger.domain.model.result import Err, Ok, Result

type _Step = Callable[[Log, AnyAccount], Result[Log, CurrencyMismatch]]


def close_day(log: Log, today: Day, config: LedgerConfig) -> Result[Log, CurrencyMismatch]:
    """The log with every event the close of ``today`` fires: each step runs for every account before the next."""
    steps: list[_Step] = [
        lambda step_log, account: assess_fees(step_log, account, today, config.first_day),
        lambda step_log, account: accrue_interest(step_log, account, today, config.first_day),
    ]
    if today in config.capitalization_days:
        steps.append(lambda step_log, account: capitalize_interest(step_log, account, today))
    for step in steps:
        for account in config.accounts:
            if isinstance(stepped_log := step(log, account), Err):
                return stepped_log
            log = stepped_log.value
    return Ok(log)
