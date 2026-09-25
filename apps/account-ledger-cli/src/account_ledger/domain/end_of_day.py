"""Closing a day: fees, interest, then capitalization, in that order (AMB-002, AMB-004, AMB-005, AMB-023)."""

from collections.abc import Iterator

from account_ledger.domain.balances import accrued, closing, interest_base, interest_fired
from account_ledger.domain.model.config import Account, AnyAccount, LedgerConfig, is_aed
from account_ledger.domain.model.event_log import Accepted, Log, append
from account_ledger.domain.model.events import (
    Capitalization,
    Fee,
    FeeRefund,
    InterestAccrual,
    InterestAdjustment,
    Reversal,
)
from account_ledger.domain.model.ids import AccountId, CapitalizationId, Day, FeeId, InterestId, RefundId
from account_ledger.domain.model.money import (
    Aed,
    Bhd,
    Direction,
    Money,
    NotPositive,
    amount_of,
    daily_interest,
    overdraft_fee_of,
)


def close_day(log: Log, today: Day, config: LedgerConfig) -> Log:
    """The log with every event the close of ``today`` fires."""
    for account in config.accounts:
        log = _fee_step(log, account, today, config.first_day)
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
    for day in _days(first, today):
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


def _fee_step(log: Log, account: AnyAccount, today: Day, first: Day) -> Log:
    """For each day so far, in order: a fee, value-dated today, for a day that closes negative with no fee in force,
    and a refund of the fee in force for a day that closes at or above zero (AMB-002, AMB-004). Each closing is read
    from the log as it grows, so a fee fired for an earlier day counts in the days after it (AMB-011)."""
    amount = overdraft_fee_of(account.opening)
    for day in _days(first, today):
        fee = _in_force(log, account.id).get(day)
        if _negative(log, account, day):
            if fee is None:
                log = append(log, Accepted(Fee(FeeId(account.id, day, today), account.id, today, amount), today))
        elif fee is not None:
            refund = FeeRefund(RefundId(account.id, day, today), account.id, today, fee.id, fee.amount)
            log = append(log, Accepted(refund, today))
    return log


def _in_force(log: Log, account_id: AccountId) -> dict[Day, Fee]:
    """The account's fee in force for each day: one per day per account, until a refund names it or a reversal
    undoes it, and again once a reversal undoes that refund (AMB-002, AMB-004, AMB-035)."""
    fees: dict[Day, Fee] = {}
    refunded: dict[RefundId, Fee] = {}
    for entry in log:
        match entry:
            case Accepted(event=Fee() as fee) if fee.account == account_id:
                fees[fee.id.for_day] = fee
            case Accepted(event=FeeRefund() as refund) if refund.account == account_id:
                refunded_fee = fees.pop(refund.fee.for_day, None)
                if refunded_fee is not None:
                    refunded[refund.id] = refunded_fee
            case Accepted(event=Reversal(reverses=RefundId() as reversed_refund)) if reversed_refund in refunded:
                restored = refunded.pop(reversed_refund)  # a reversed refund puts its fee back in force
                fees[restored.id.for_day] = restored
            case Accepted(event=Reversal(reverses=FeeId() as reversed_fee)) if reversed_fee.account == account_id:
                in_force = fees.get(reversed_fee.for_day)
                if in_force is not None and in_force.id == reversed_fee:
                    del fees[reversed_fee.for_day]  # a reversed fee is out of force, so its day is judged again
            case _:
                pass
    return fees


def _negative(log: Log, account: AnyAccount, day: Day) -> bool:
    # Both branches read alike; each narrows the account to one currency for the generic call.
    if is_aed(account):
        return _below_zero(log, account, day)
    return _below_zero(log, account, day)


def _below_zero[M: (Aed, Bhd)](log: Log, account: Account[M], day: Day) -> bool:
    return closing(log, account, day) < type(account.opening).zero()


def _days(first: Day, last: Day) -> Iterator[Day]:
    day = first
    while day <= last:
        yield day
        day = day.next()
