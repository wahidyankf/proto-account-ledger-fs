"""Processing one incoming event: exactly one log entry for it, plus the instalments a credit fires."""

from typing import assert_never

from account_ledger.authorizations import (
    Approved,
    AuthorizationState,
    Declined,
    NoTransition,
    PartiallySettled,
    Settled,
    decide,
    record_for,
    transition,
    trigger_of,
)
from account_ledger.balances import available_of
from account_ledger.config import LedgerConfig
from account_ledger.events import (
    Authorization,
    Credit,
    Debit,
    Fee,
    FeeRefund,
    IncomingEvent,
    Instalment,
    Instalments,
    Reversal,
    Settlement,
)
from account_ledger.ids import Day, EventId, FeeId, IncomingId, InstalmentCount, InstalmentId, RefundId
from account_ledger.log import (
    Accepted,
    AlreadyReversed,
    AlreadyUndone,
    AuthorizationDecided,
    Captured,
    Duplicate,
    ForcePosted,
    IdReused,
    Log,
    LoggedEvent,
    MovedNoMoney,
    Rejected,
    Rejection,
    ReversesAReversal,
    SettlementAccepted,
    UnknownTarget,
    append,
    first,
    instalments_of,
)
from account_ledger.money import TooManyInstalments, split_of


def process(log: Log, event: IncomingEvent, today: Day, config: LedgerConfig) -> Log:
    """The log with the event's entry appended; ``today`` is the day it is processed on (AMB-015)."""
    known = first(log, event.id)  # the event ID is the idempotency key (AMB-034)
    if known is not None:
        return append(log, Duplicate(event, today) if known.event == event else Rejected(event, today, IdReused()))
    match event:
        case Credit(posting=Instalments(count=count)):
            return (*append(log, Accepted(event, today)), *_instalments(event, count, today))
        case Credit() | Debit():
            return append(log, Accepted(event, today))
        case Reversal():
            return append(log, _reversal(log, event, today))
        case Authorization():
            account = config.account(event.account)
            assert account is not None  # the stream reader refuses an account the ledger does not hold
            decision = decide(available_of(log, account, today), event.amount)
            return append(log, AuthorizationDecided(event, today, decision))
        case Settlement():
            record = record_for(log, event)
            if record is None:  # an unknown authorization has no transition either (AMB-012)
                return append(log, SettlementAccepted(event, today, ForcePosted()))
            return append(log, SettlementAccepted(event, today, _effect(record.state, event)))
        case _:
            assert_never(event)


def _effect(before: AuthorizationState, settlement: Settlement) -> Captured | ForcePosted:
    """The capture a settlement completes, or a force-post when the table has no transition for it (AMB-029)."""
    after = transition(before, trigger_of(settlement))
    match after:
        case NoTransition():
            return ForcePosted()
        case Approved() | PartiallySettled() | Declined() | Settled():
            return Captured(before, after)
        case _:
            assert_never(after)


def _instalments(credit: Credit, count: InstalmentCount, today: Day) -> tuple[Accepted, ...]:
    """The instalments a credit fires, in order, each accepted with the credit's value day (AMB-017, AMB-020)."""
    parts = split_of(credit.amount, count)
    assert not isinstance(parts, TooManyInstalments)  # the stream reader refuses a credit it cannot split
    return tuple(
        Accepted(Instalment(InstalmentId(credit.id, n), credit.account, credit.value_day, part), today)
        for n, part in enumerate(parts, start=1)
    )


def _reversal(log: Log, reversal: Reversal, today: Day) -> Accepted | Rejected:
    """A reversal, accepted unless a check refuses it."""
    refusal = _refusal(log, reversal.reverses)
    return Accepted(reversal, today) if refusal is None else Rejected(reversal, today, refusal)


def _refusal(log: Log, target_id: EventId) -> Rejection | None:
    """Why a reversal of the target is refused, checked in tech-docs 002's order (AMB-028, AMB-035), or None."""
    target = first(log, target_id)
    if target is None:
        return UnknownTarget(target_id)
    if isinstance(target.event, Reversal):
        return ReversesAReversal(target_id)
    if isinstance(target, AuthorizationDecided | Rejected):
        return MovedNoMoney(target_id)
    by = _reversed_by(log, target_id)
    if by is not None:
        return AlreadyReversed(target_id, by)
    return _undone_by(log, target.event)


def _undone_by(log: Log, target: LoggedEvent) -> AlreadyUndone | None:
    """The part of the target's money already undone another way: a fee refunded, or a credit or one of its
    instalments reversed."""
    match target:
        case Instalment(id=part):
            by = _reversed_by(log, part.parent)
            return None if by is None else AlreadyUndone(part, by)
        case Fee(id=fee):
            refund = _refund_of(log, fee)
            return None if refund is None else AlreadyUndone(fee, refund)
        case Credit(posting=Instalments()):
            parts = instalments_of(log, target.id)
            return next(
                (AlreadyUndone(part.id, by) for part in parts if (by := _reversed_by(log, part.id)) is not None), None
            )
        case _:
            return None


def _refund_of(log: Log, fee: FeeId) -> RefundId | None:
    """The refund in effect for the fee: one that names it and is not itself reversed (AMB-004, AMB-035)."""
    for entry in log:
        match entry:
            case Accepted(event=FeeRefund(id=refund, fee=refunded)) if refunded == fee:
                if _reversed_by(log, refund) is None:
                    return refund
            case _:
                pass
    return None


def _reversed_by(log: Log, target_id: EventId) -> IncomingId | None:
    """The accepted reversal of the target, if there is one."""
    for entry in log:
        match entry:
            case Accepted(event=Reversal(id=by, reverses=reverses)) if reverses == target_id:
                return by
            case _:
                pass
    return None
