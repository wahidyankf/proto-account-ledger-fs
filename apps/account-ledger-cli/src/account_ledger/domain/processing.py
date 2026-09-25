"""Processing one incoming event: exactly one log entry for it, plus the instalments a credit fires."""

from typing import assert_never

from account_ledger.domain.authorizations import (
    Approved,
    AuthorizationState,
    Declined,
    NoTransition,
    PartiallySettled,
    Settled,
    apply_trigger,
    decide_authorization,
    derive_trigger,
    find_record,
)
from account_ledger.domain.balances import compute_available_of
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
    append_entry,
    find_first_entry,
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
from account_ledger.domain.model.money import TooManyInstalments, split_amount_of
from account_ledger.domain.reversals import find_refusal


def process_event(log: Log, event: IncomingEvent, today: Day, config: LedgerConfig) -> Log:
    """The log with the event's entry appended; ``today`` is the day it is processed on (AMB-015)."""
    known_entry = find_first_entry(log, event.id)  # the event ID is the idempotency key (AMB-034)
    if known_entry is not None:
        if known_entry.event == event:
            return append_entry(log, Duplicate(event, today))
        return append_entry(log, Rejected(event, today, IdReused()))
    match event:
        case Credit(posting=Instalments(count=count)):
            return append_entry(log, Accepted(event, today)) + _fire_instalments(event, count, today)
        case Credit() | Debit():
            return append_entry(log, Accepted(event, today))
        case Reversal():
            return append_entry(log, _decide_reversal(log, event, today))
        case Authorization():
            account = config.find_account(event.account)
            assert account is not None  # the stream reader refuses an account the ledger does not hold
            decision = decide_authorization(compute_available_of(log, account, today), event.amount)
            return append_entry(log, AuthorizationDecided(event, today, decision))
        case Settlement():
            record = find_record(log, event)
            if record is None:  # an unknown authorization has no transition either (AMB-012)
                return append_entry(log, SettlementAccepted(event, today, ForcePosted()))
            return append_entry(log, SettlementAccepted(event, today, _decide_effect(record.state, event)))
        case _:
            assert_never(event)


def _decide_effect(state_before: AuthorizationState, settlement: Settlement) -> Captured | ForcePosted:
    """The capture a settlement completes, or a force-post when the table has no transition for it (AMB-029)."""
    state_after = apply_trigger(state_before, derive_trigger(settlement))
    match state_after:
        case NoTransition():
            return ForcePosted()
        case Approved() | PartiallySettled() | Declined() | Settled():
            return Captured(state_before, state_after)
        case _:
            assert_never(state_after)


def _fire_instalments(credit: Credit, count: InstalmentCount, today: Day) -> tuple[Accepted, ...]:
    """The instalments a credit fires, in order, each accepted with the credit's value day (AMB-017, AMB-020)."""
    parts = split_amount_of(credit.amount, count)
    assert not isinstance(parts, TooManyInstalments)  # the stream reader refuses a credit it cannot split
    return tuple(
        Accepted(Instalment(InstalmentId(credit.id, number), credit.account, credit.value_day, part), today)
        for number, part in enumerate(parts, start=1)
    )


def _decide_reversal(log: Log, reversal: Reversal, today: Day) -> Accepted | Rejected:
    """A reversal, accepted unless a check refuses it."""
    refusal = find_refusal(log, reversal.target)
    return Accepted(reversal, today) if refusal is None else Rejected(reversal, today, refusal)
