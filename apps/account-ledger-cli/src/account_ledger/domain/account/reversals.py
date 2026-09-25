"""Reversals: when one is refused, and which events the posted ones undid (AMB-028, AMB-035)."""

from account_ledger.common.result import Err, Ok, Result
from account_ledger.domain.account.domain_events import (
    AlreadyReversed,
    AlreadyUndone,
    AuthorizationApproved,
    AuthorizationDeclined,
    EventRejected,
    FeeRefunded,
    LoggedEvent,
    MovedNoMoney,
    Rejection,
    ReversalPosted,
    ReversesAReversal,
    UnknownTarget,
)
from account_ledger.domain.account.history import (
    AccountHistoryIn,
)
from account_ledger.domain.model.events import Credit, Fee, FeeRefund, Instalment, Instalments, Reversal
from account_ledger.domain.model.ids import Day, EventId, FeeId, IncomingId, RefundId
from account_ledger.domain.model.money import Aed, Bhd


def check_reversal[M: (Aed, Bhd)](history: AccountHistoryIn[M], target_id: EventId) -> Result[None, Rejection]:
    """Nothing when a reversal of the target on the account may proceed, or why it is refused, checked in tech-docs
    002's order (AMB-028, AMB-035); a target on another account is refused before the account sees it (AMB-036)."""
    target = history.find_entry(target_id)
    if target is None:
        return Err(UnknownTarget(target_id))
    if isinstance(target.event, Reversal):
        return Err(ReversesAReversal(target_id))
    if isinstance(target, AuthorizationApproved | AuthorizationDeclined | EventRejected):
        return Err(MovedNoMoney(target_id))
    reversal_id = _find_reversal_id(history, target_id)
    if reversal_id is not None:
        return Err(AlreadyReversed(target_id, reversal_id))
    return _check_undoing(history, target.event)


def _find_reversal_id[M: (Aed, Bhd)](history: AccountHistoryIn[M], target_id: EventId) -> IncomingId | None:
    """The posted reversal of the target, if there is one."""
    for entry in history.entries:
        match entry:
            case ReversalPosted(event=Reversal(id=reversal_id, target=target)) if target == target_id:
                return reversal_id
            case _:
                pass
    return None


def list_reversed_targets[M: (Aed, Bhd)](
    history: AccountHistoryIn[M], cutoff_day: Day | None = None
) -> frozenset[EventId]:
    """The events a posted reversal on the account undid (AMB-035); with ``cutoff_day``, only reversals
    value-dated by then."""
    return frozenset(
        event.target
        for event in history.list_counted_events()
        if isinstance(event, Reversal) and (cutoff_day is None or event.value_date <= cutoff_day)
    )


def _check_undoing[M: (Aed, Bhd)](history: AccountHistoryIn[M], target: LoggedEvent) -> Result[None, AlreadyUndone]:
    """Nothing when none of the target's money is undone another way, or the part that is: a fee refunded, or a credit
    or one of its instalments reversed."""
    match target:
        case Instalment(id=part):
            undoing_id = _find_reversal_id(history, part.parent)
            return Ok(None) if undoing_id is None else Err(AlreadyUndone(part, undoing_id))
        case Fee(id=fee):
            refund = _find_refund(history, fee)
            return Ok(None) if refund is None else Err(AlreadyUndone(fee, refund))
        case Credit(posting=Instalments()):
            for part in history.list_instalments(target.id):
                undoing_id = _find_reversal_id(history, part.id)
                if undoing_id is not None:
                    return Err(AlreadyUndone(part.id, undoing_id))
            return Ok(None)
        case _:
            return Ok(None)


def _find_refund[M: (Aed, Bhd)](history: AccountHistoryIn[M], fee: FeeId) -> RefundId | None:
    """The refund in effect for the fee: one that names it and is not itself reversed (AMB-004, AMB-035)."""
    for entry in history.entries:
        match entry:
            case FeeRefunded(event=FeeRefund(id=refund, fee=refunded_fee)) if refunded_fee == fee:
                if _find_reversal_id(history, refund) is None:
                    return refund
            case _:
                pass
    return None
