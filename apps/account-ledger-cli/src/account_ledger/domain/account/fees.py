"""Fees: an overdraft fee for each day that closes negative, refunded once the day closes at or above zero (AMB-002,
AMB-004, AMB-011, AMB-027)."""

from account_ledger.common.result import Err, Ok, Result
from account_ledger.domain.account.balances import (
    compute_closing,
)
from account_ledger.domain.account.domain_events import (
    FeeCharged,
    FeeRefunded,
    LogEntry,
    ReversalPosted,
)
from account_ledger.domain.account.history import (
    AccountHistoryIn,
)
from account_ledger.domain.model.events import Fee, FeeRefund, Reversal
from account_ledger.domain.model.ids import Day, FeeId, RefundId
from account_ledger.domain.model.money import Aed, Bhd, CurrencyMismatch, compute_overdraft_fee_of


def assess_fees[M: (Aed, Bhd)](
    history: AccountHistoryIn[M], today: Day, first_day: Day
) -> Result[tuple[LogEntry, ...], CurrencyMismatch]:
    """For each day so far, in order: a fee, value-dated today, for a day that closes negative with no fee in force,
    and a refund of the fee in force for a day that closes at or above zero (AMB-002, AMB-004). Each closing is read
    from the history as it grows, so a fee generated for an earlier day counts in the days after it (AMB-011)."""
    account = history.account
    amount = compute_overdraft_fee_of(account.opening)
    entries: list[LogEntry] = []
    for day in first_day.span_to(today):
        fee = _map_fees_in_force(history).get(day)
        if isinstance(negative_closing := _is_closing_below_zero(history, day), Err):
            return negative_closing
        entry: LogEntry | None = None
        if negative_closing.value:
            if fee is None:
                entry = FeeCharged(Fee(FeeId(account.id, day, today), account.id, today, amount), today)
        elif fee is not None:
            entry = FeeRefunded(
                FeeRefund(RefundId(account.id, day, today), account.id, today, fee.id, fee.amount), today
            )
        if entry is not None:
            history = history.append(entry)
            entries.append(entry)
    return Ok(tuple(entries))


def _map_fees_in_force[M: (Aed, Bhd)](history: AccountHistoryIn[M]) -> dict[Day, Fee]:
    """The account's fee in force for each day: one per day per account, until a refund names it or a reversal
    undoes it, and again once a reversal undoes that refund (AMB-002, AMB-004, AMB-035)."""
    fees: dict[Day, Fee] = {}
    refunded_fees: dict[RefundId, Fee] = {}
    for entry in history.entries:
        match entry:
            case FeeCharged(event=fee):
                fees[fee.id.for_day] = fee
            case FeeRefunded(event=refund):
                refunded_fee = fees.pop(refund.fee.for_day, None)
                if refunded_fee is not None:
                    refunded_fees[refund.id] = refunded_fee
            case ReversalPosted(event=Reversal(target=RefundId() as reversed_refund)) if (
                reversed_refund in refunded_fees
            ):
                restored_fee = refunded_fees.pop(reversed_refund)  # a reversed refund puts its fee back in force
                fees[restored_fee.id.for_day] = restored_fee
            case ReversalPosted(event=Reversal(target=FeeId() as reversed_fee)):
                fee_in_force = fees.get(reversed_fee.for_day)
                if fee_in_force is not None and fee_in_force.id == reversed_fee:
                    del fees[reversed_fee.for_day]  # a reversed fee is out of force, so its day is judged again
            case _:
                pass
    return fees


def _is_closing_below_zero[M: (Aed, Bhd)](history: AccountHistoryIn[M], day: Day) -> Result[bool, CurrencyMismatch]:
    """Whether the account's closing on the day is below zero, in its own currency."""
    zero = type(history.account.opening).make_zero()
    return compute_closing(history, day).map(lambda closing: closing < zero)
