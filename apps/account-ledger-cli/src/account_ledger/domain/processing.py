"""Processing one incoming event: exactly one log entry for it, plus the instalments a credit fires."""

from typing import assert_never

from account_ledger.common.result import Err, Ok, Result
from account_ledger.domain.authorizations import (
    AuthorizationState,
    NoTransition,
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
from account_ledger.domain.model.money import CurrencyMismatch, split_amount_of
from account_ledger.domain.reversals import check_reversal


def process_event(log: Log, event: IncomingEvent, today: Day, config: LedgerConfig) -> Result[Log, CurrencyMismatch]:
    """The log with the event's entry appended; ``today`` is the day it is processed on (AMB-015)."""
    known_entry = find_first_entry(log, event.id)  # the event ID is the idempotency key (AMB-034)
    if known_entry is not None:
        if known_entry.event == event:
            return Ok(append_entry(log, Duplicate(event, today)))
        return Ok(append_entry(log, Rejected(event, today, IdReused())))
    match event:
        case Credit(posting=Instalments(count=count)):
            return Ok(append_entry(log, Accepted(event, today)) + _fire_instalments(event, count, today))
        case Credit() | Debit():
            return Ok(append_entry(log, Accepted(event, today)))
        case Reversal():
            return Ok(append_entry(log, _decide_reversal(log, event, today)))
        case Authorization():
            return _decide_authorization_entry(log, event, today, config).map(lambda entry: append_entry(log, entry))
        case Settlement():
            return _decide_settlement_entry(log, event, today).map(lambda entry: append_entry(log, entry))
        case _:
            assert_never(event)


def _decide_authorization_entry(
    log: Log, authorization: Authorization, today: Day, config: LedgerConfig
) -> Result[AuthorizationDecided, CurrencyMismatch]:
    """The authorization's decision, from the account's available balance when it arrives (AMB-008, AMB-009)."""
    account = config.find_account(authorization.account)
    assert account is not None  # the stream reader refuses an account the ledger does not hold
    return (
        compute_available_of(log, account, today)
        .flat_map(lambda available_balance: decide_authorization(available_balance, authorization.amount))
        .map(lambda decision: AuthorizationDecided(authorization, today, decision))
    )


def _decide_settlement_entry(
    log: Log, settlement: Settlement, today: Day
) -> Result[SettlementAccepted, CurrencyMismatch]:
    """The settlement, capturing against the authorization it names, or force-posted when there is none (AMB-012)."""
    record = find_record(log, settlement)
    if record is None:  # an unknown authorization has no transition either (AMB-012)
        return Ok(SettlementAccepted(settlement, today, ForcePosted()))
    return _decide_effect(record.state, settlement).map(lambda effect: SettlementAccepted(settlement, today, effect))


def _decide_effect(
    state_before: AuthorizationState, settlement: Settlement
) -> Result[Captured | ForcePosted, CurrencyMismatch]:
    """The capture a settlement completes, or a force-post when the table has no transition for it (AMB-029)."""
    match apply_trigger(state_before, derive_trigger(settlement)):
        case Ok(state_after):
            return Ok(Captured(state_before, state_after))
        case Err(fault):
            return Ok(ForcePosted()) if isinstance(fault, NoTransition) else Err(fault)


def _fire_instalments(credit: Credit, count: InstalmentCount, today: Day) -> tuple[Accepted, ...]:
    """The instalments a credit fires, in order, each accepted with the credit's value day (AMB-017, AMB-020)."""
    parts = split_amount_of(credit.amount, count)
    assert isinstance(parts, Ok)  # the stream reader refuses a credit it cannot split
    return tuple(
        Accepted(Instalment(InstalmentId(credit.id, number), credit.account, credit.value_day, part), today)
        for number, part in enumerate(parts.value, start=1)
    )


def _decide_reversal(log: Log, reversal: Reversal, today: Day) -> Accepted | Rejected:
    """A reversal, accepted unless a check refuses it."""
    match check_reversal(log, reversal.target):
        case Ok():
            return Accepted(reversal, today)
        case Err(rejection):
            return Rejected(reversal, today, rejection)
