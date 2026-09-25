"""Processing one incoming event: exactly one log entry for it, plus the instalments a credit fires."""

from typing import assert_never

from account_ledger.domain.authorizations import (
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
from account_ledger.domain.balances import available_of
from account_ledger.domain.model.config import LedgerConfig
from account_ledger.domain.model.event_log import (
    Accepted,
    AuthorizationDecided,
    Captured,
    Duplicate,
    ForcePosted,
    IdReused,
    Log,
    Rejected,
    SettlementAccepted,
    append,
    first,
)
from account_ledger.domain.model.events import (
    Authorization,
    Credit,
    Debit,
    IncomingEvent,
    Instalment,
    Instalments,
    Reversal,
    Settlement,
)
from account_ledger.domain.model.ids import Day, InstalmentCount, InstalmentId
from account_ledger.domain.model.money import TooManyInstalments, split_of
from account_ledger.domain.reversals import refusal


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
    refused = refusal(log, reversal.reverses)
    return Accepted(reversal, today) if refused is None else Rejected(reversal, today, refused)
