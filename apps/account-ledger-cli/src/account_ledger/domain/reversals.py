"""Reversals: when one is refused, and which events the accepted ones undid (AMB-028, AMB-035)."""

from account_ledger.common.result import Err, Ok, Result
from account_ledger.domain.model.event_log import (
    Accepted,
    AlreadyReversed,
    AlreadyUndone,
    AuthorizationDecided,
    Log,
    LoggedEvent,
    MovedNoMoney,
    Rejected,
    Rejection,
    ReversesAReversal,
    TargetOnAnotherAccount,
    UnknownTarget,
    find_first_entry,
    list_counted_events,
    list_instalments,
)
from account_ledger.domain.model.events import Credit, Fee, FeeRefund, Instalment, Instalments, Reversal
from account_ledger.domain.model.ids import AccountId, Day, EventId, FeeId, IncomingId, RefundId


def check_reversal(log: Log, target_id: EventId, account: AccountId) -> Result[None, Rejection]:
    """Nothing when a reversal on the account of the target may proceed, or why it is refused, checked in tech-docs
    002's order, a target on another account refused once it is found (AMB-028, AMB-035, AMB-036)."""
    target = find_first_entry(log, target_id)
    if target is None:
        return Err(UnknownTarget(target_id))
    if target.event.account != account:
        return Err(TargetOnAnotherAccount(target_id, target.event.account))
    if isinstance(target.event, Reversal):
        return Err(ReversesAReversal(target_id))
    if isinstance(target, AuthorizationDecided | Rejected):
        return Err(MovedNoMoney(target_id))
    reversal_id = find_reversal_id(log, target_id)
    if reversal_id is not None:
        return Err(AlreadyReversed(target_id, reversal_id))
    return _check_undoing(log, target.event)


def find_reversal_id(log: Log, target_id: EventId) -> IncomingId | None:
    """The accepted reversal of the target, if there is one."""
    for entry in log:
        match entry:
            case Accepted(event=Reversal(id=reversal_id, target=target)) if target == target_id:
                return reversal_id
            case _:
                pass
    return None


def list_reversed_targets(log: Log, account_id: AccountId, cutoff_day: Day | None = None) -> frozenset[EventId]:
    """The events an accepted reversal on the account undid (AMB-035); with ``cutoff_day``, only reversals
    value-dated by then."""
    return frozenset(
        event.target
        for event in list_counted_events(log, account_id)
        if isinstance(event, Reversal) and (cutoff_day is None or event.value_date <= cutoff_day)
    )


def _check_undoing(log: Log, target: LoggedEvent) -> Result[None, AlreadyUndone]:
    """Nothing when none of the target's money is undone another way, or the part that is: a fee refunded, or a credit
    or one of its instalments reversed."""
    match target:
        case Instalment(id=part):
            undoing_id = find_reversal_id(log, part.parent)
            return Ok(None) if undoing_id is None else Err(AlreadyUndone(part, undoing_id))
        case Fee(id=fee):
            refund = _find_refund(log, fee)
            return Ok(None) if refund is None else Err(AlreadyUndone(fee, refund))
        case Credit(posting=Instalments()):
            for part in list_instalments(log, target.id):
                undoing_id = find_reversal_id(log, part.id)
                if undoing_id is not None:
                    return Err(AlreadyUndone(part.id, undoing_id))
            return Ok(None)
        case _:
            return Ok(None)


def _find_refund(log: Log, fee: FeeId) -> RefundId | None:
    """The refund in effect for the fee: one that names it and is not itself reversed (AMB-004, AMB-035)."""
    for entry in log:
        match entry:
            case Accepted(event=FeeRefund(id=refund, fee=refunded_fee)) if refunded_fee == fee:
                if find_reversal_id(log, refund) is None:
                    return refund
            case _:
                pass
    return None
