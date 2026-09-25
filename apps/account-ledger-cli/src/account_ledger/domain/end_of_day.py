"""Closing a day: fees, interest, then capitalization, in that order (AMB-002, AMB-004, AMB-005, AMB-023)."""

from collections.abc import Iterator

from account_ledger.domain.balances import accrued, interest_base, interest_fired
from account_ledger.domain.fees import assess_fees
from account_ledger.domain.model.config import Account, AnyAccount, LedgerConfig, is_aed
from account_ledger.domain.model.event_log import Accepted, Log, append
from account_ledger.domain.model.events import Capitalization, InterestAccrual, InterestAdjustment
from account_ledger.domain.model.ids import AccountId, CapitalizationId, Day, InterestId
from account_ledger.domain.model.money import Aed, Bhd, Direction, Money, NotPositive, amount_of, daily_interest


def close_day(log: Log, today: Day, config: LedgerConfig) -> Log:
    """The log with every event the close of ``today`` fires."""
    for account in config.accounts:
        log = assess_fees(log, account, today, config.first_day)
    for account in config.accounts:
        log = _interest_step(log, account, today, config.first_day)
    if today in config.capitalization_days:
        for account in config.accounts:
            log = _capitalization_step(log, account, today)
    return log


def _capitalization_step(log: Log, account: AnyAccount, today: Day) -> Log:
    """The account's accrued interest, credited value-dated today when it is above zero (AMB-007, AMB-023)."""
    amount = amount_of(_accrued(log, account))
    if isinstance(amount, NotPositive):
        return log
    capitalization = Capitalization(CapitalizationId(account.id, today), account.id, today, amount)
    return append(log, Accepted(capitalization, today))


def _accrued(log: Log, account: AnyAccount) -> Money:
    # Both branches read alike; each narrows the account to one currency for the generic call.
    if is_aed(account):
        return accrued(log, account)
    return accrued(log, account)


def _interest_step(log: Log, account: AnyAccount, today: Day, first: Day) -> Log:
    """For each day so far whose interest differs from what was fired for it, the difference: today's accrual, or an
    adjustment of an earlier day, value-dated today (AMB-005)."""
    for day, change in _changes(log, account, today, first):
        log = append(log, Accepted(_interest_event(account.id, day, today, change), today))
    return log


def _changes(log: Log, account: AnyAccount, today: Day, first: Day) -> list[tuple[Day, Money]]:
    # Both branches read alike; each narrows the account to one currency for the generic call.
    if is_aed(account):
        return list(_changed(log, account, today, first))
    return list(_changed(log, account, today, first))


def _changed[M: (Aed, Bhd)](log: Log, account: Account[M], today: Day, first: Day) -> Iterator[tuple[Day, M]]:
    for day in first.through(today):
        change = daily_interest(interest_base(log, account, day)) - interest_fired(log, account, day)
        if change.value != 0:
            yield day, change


def _interest_event(account: AccountId, day: Day, today: Day, change: Money) -> InterestAccrual | InterestAdjustment:
    direction = Direction.UP if change.value > 0 else Direction.DOWN
    amount = amount_of(change if direction is Direction.UP else -change)
    assert not isinstance(amount, NotPositive)  # a change is never zero
    marker = InterestId(account, day, today)
    if day == today:  # nothing is fired for today before its close, so today's change is its first, positive accrual
        return InterestAccrual(marker, account, today, amount)
    return InterestAdjustment(marker, account, today, direction, amount)
