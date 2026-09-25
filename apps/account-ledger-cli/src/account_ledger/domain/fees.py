"""Fees: an overdraft fee for each day that closes negative, refunded once the day closes at or above zero (AMB-002,
AMB-004, AMB-011, AMB-027)."""

from account_ledger.domain.balances import closing
from account_ledger.domain.model.config import Account, AnyAccount, is_aed
from account_ledger.domain.model.event_log import Accepted, Log, append
from account_ledger.domain.model.events import Fee, FeeRefund, Reversal
from account_ledger.domain.model.ids import AccountId, Day, FeeId, RefundId
from account_ledger.domain.model.money import Aed, Bhd, overdraft_fee_of


def assess_fees(log: Log, account: AnyAccount, today: Day, first: Day) -> Log:
    """For each day so far, in order: a fee, value-dated today, for a day that closes negative with no fee in force,
    and a refund of the fee in force for a day that closes at or above zero (AMB-002, AMB-004). Each closing is read
    from the log as it grows, so a fee fired for an earlier day counts in the days after it (AMB-011)."""
    amount = overdraft_fee_of(account.opening)
    for day in first.through(today):
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
    """Whether the account's closing on the day is below zero."""
    # Both branches read alike; each narrows the account to one currency for the generic call.
    if is_aed(account):
        return _below_zero(log, account, day)
    return _below_zero(log, account, day)


def _below_zero[M: (Aed, Bhd)](log: Log, account: Account[M], day: Day) -> bool:
    """Whether the account's closing on the day is below zero, in its own currency."""
    return closing(log, account, day) < type(account.opening).zero()
