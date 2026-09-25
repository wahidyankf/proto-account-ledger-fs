"""Reversals: when one is refused, and which events the accepted ones undid (AMB-028, AMB-035)."""

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
    UnknownTarget,
    find_first_entry,
    list_counted_events,
    list_instalments,
)
from account_ledger.domain.model.events import Credit, Fee, FeeRefund, Instalment, Instalments, Reversal
from account_ledger.domain.model.ids import AccountId, Day, EventId, FeeId, IncomingId, RefundId
from account_ledger.domain.model.result import Err, Ok, Result


def check_reversal(log: Log, target_id: EventId) -> Result[None, Rejection]:
    """Nothing when a reversal of the target may proceed, or why it is refused, checked in tech-docs 002's order
    (AMB-028, AMB-035)."""
    target = find_first_entry(log, target_id)
    if target is None:
        return Err(UnknownTarget(target_id))
    if isinstance(target.event, Reversal):
        return Err(ReversesAReversal(target_id))
    if isinstance(target, AuthorizationDecided | Rejected):
        return Err(MovedNoMoney(target_id))
    reverser_id = find_reverser(log, target_id)
    if reverser_id is not None:
        return Err(AlreadyReversed(target_id, reverser_id))
    undoing = _find_undoing(log, target.event)
    return Ok(None) if undoing is None else Err(undoing)


def find_reverser(log: Log, target_id: EventId) -> IncomingId | None:
    """The accepted reversal of the target, if there is one."""
    for entry in log:
        match entry:
            case Accepted(event=Reversal(id=reversal_id, target=target)) if target == target_id:
                return reversal_id
            case _:
                pass
    return None


def list_reversed_targets(log: Log, account_id: AccountId, cutoff_day: Day | None = None) -> frozenset[EventId]:
    """The events an accepted reversal on the account undid (AMB-035); with ``by``, only those value-dated by then."""
    return frozenset(
        event.target
        for event in list_counted_events(log, account_id)
        if isinstance(event, Reversal) and (cutoff_day is None or event.value_day <= cutoff_day)
    )


def _find_undoing(log: Log, target: LoggedEvent) -> AlreadyUndone | None:
    """The part of the target's money already undone another way: a fee refunded, or a credit or one of its
    instalments reversed."""
    match target:
        case Instalment(id=part):
            undoing_id = find_reverser(log, part.parent)
            return None if undoing_id is None else AlreadyUndone(part, undoing_id)
        case Fee(id=fee):
            refund = _find_refund(log, fee)
            return None if refund is None else AlreadyUndone(fee, refund)
        case Credit(posting=Instalments()):
            for part in list_instalments(log, target.id):
                undoing_id = find_reverser(log, part.id)
                if undoing_id is not None:
                    return AlreadyUndone(part.id, undoing_id)
            return None
        case _:
            return None


def _find_refund(log: Log, fee: FeeId) -> RefundId | None:
    """The refund in effect for the fee: one that names it and is not itself reversed (AMB-004, AMB-035)."""
    for entry in log:
        match entry:
            case Accepted(event=FeeRefund(id=refund, fee=refunded_fee)) if refunded_fee == fee:
                if find_reverser(log, refund) is None:
                    return refund
            case _:
                pass
    return None
