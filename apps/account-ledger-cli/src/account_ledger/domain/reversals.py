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
    counted,
    first,
    instalments_of,
)
from account_ledger.domain.model.events import Credit, Fee, FeeRefund, Instalment, Instalments, Reversal
from account_ledger.domain.model.ids import AccountId, Day, EventId, FeeId, IncomingId, RefundId


def refusal(log: Log, target_id: EventId) -> Rejection | None:
    """Why a reversal of the target is refused, checked in tech-docs 002's order (AMB-028, AMB-035), or None."""
    target = first(log, target_id)
    if target is None:
        return UnknownTarget(target_id)
    if isinstance(target.event, Reversal):
        return ReversesAReversal(target_id)
    if isinstance(target, AuthorizationDecided | Rejected):
        return MovedNoMoney(target_id)
    by = reversed_by(log, target_id)
    if by is not None:
        return AlreadyReversed(target_id, by)
    return _undone_by(log, target.event)


def reversed_by(log: Log, target_id: EventId) -> IncomingId | None:
    """The accepted reversal of the target, if there is one."""
    for entry in log:
        match entry:
            case Accepted(event=Reversal(id=by, reverses=reverses)) if reverses == target_id:
                return by
            case _:
                pass
    return None


def reversed_targets(log: Log, account_id: AccountId, by: Day | None = None) -> frozenset[EventId]:
    """The events an accepted reversal on the account undid (AMB-035); with ``by``, only those value-dated by then."""
    return frozenset(
        event.reverses
        for event in counted(log, account_id)
        if isinstance(event, Reversal) and (by is None or event.value_day <= by)
    )


def _undone_by(log: Log, target: LoggedEvent) -> AlreadyUndone | None:
    """The part of the target's money already undone another way: a fee refunded, or a credit or one of its
    instalments reversed."""
    match target:
        case Instalment(id=part):
            by = reversed_by(log, part.parent)
            return None if by is None else AlreadyUndone(part, by)
        case Fee(id=fee):
            refund = _refund_of(log, fee)
            return None if refund is None else AlreadyUndone(fee, refund)
        case Credit(posting=Instalments()):
            parts = instalments_of(log, target.id)
            return next(
                (AlreadyUndone(part.id, by) for part in parts if (by := reversed_by(log, part.id)) is not None), None
            )
        case _:
            return None


def _refund_of(log: Log, fee: FeeId) -> RefundId | None:
    """The refund in effect for the fee: one that names it and is not itself reversed (AMB-004, AMB-035)."""
    for entry in log:
        match entry:
            case Accepted(event=FeeRefund(id=refund, fee=refunded)) if refunded == fee:
                if reversed_by(log, refund) is None:
                    return refund
            case _:
                pass
    return None
