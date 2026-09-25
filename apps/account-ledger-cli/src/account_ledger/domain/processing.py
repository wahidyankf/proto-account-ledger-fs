"""Processing one incoming event: exactly one log entry for it, plus the instalments a credit generates."""

from typing import assert_never

from account_ledger.common.result import Err, Ok, Result
from account_ledger.domain.authorizations import (
    AuthorizationState,
    CannotSettle,
    apply_settlement,
    decide_authorization,
    derive_settlement_input,
    find_record,
)
from account_ledger.domain.balances import compute_available
from account_ledger.domain.model.config import LedgerConfig
from account_ledger.domain.model.event_log import (
    AccountHistory,
    AnyHistory,
    AuthorizationApproved,
    AuthorizationDeclined,
    CreditPosted,
    DebitPosted,
    DuplicateIgnored,
    EventRejected,
    IdReused,
    InstalmentPosted,
    Log,
    LogEntry,
    ReversalPosted,
    SettlementApplied,
    SettlementForcePosted,
    TargetOnAnotherAccount,
    append_entry,
    find_first_entry,
    find_history_of,
    is_aed_history,
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
from account_ledger.domain.model.money import Aed, Bhd, CurrencyMismatch, split_amount_of
from account_ledger.domain.reversals import check_reversal


def process_event(log: Log, event: IncomingEvent, today: Day, config: LedgerConfig) -> Result[Log, CurrencyMismatch]:
    """The log with the event's entries appended; ``today`` is the day it is processed on (AMB-015). What spans
    accounts is checked here, against the whole log: a repeated event ID (AMB-034) and a reversal whose target is on
    another account (AMB-036). Everything else the event's own account decides, from its history alone."""
    known_entry = find_first_entry(log, event.id)  # the event ID is the idempotency key (AMB-034)
    if known_entry is not None:
        if known_entry.event == event:
            return Ok(append_entry(log, DuplicateIgnored(event, today)))
        return Ok(append_entry(log, EventRejected(event, today, IdReused())))
    if isinstance(event, Reversal) and isinstance(target_check := _check_target_account(log, event), Err):
        return Ok(append_entry(log, EventRejected(event, today, target_check.error)))
    account = config.find_account(event.account)
    assert account is not None  # the stream reader refuses an account the ledger does not hold
    if isinstance(entries := _decide_event_of(find_history_of(log, account), event, today), Err):
        return entries
    return Ok((*log, *entries.value))


def _check_target_account(log: Log, reversal: Reversal) -> Result[None, TargetOnAnotherAccount]:
    """Nothing when the reversal's target is on its own account or nowhere, else the account that holds it."""
    target = find_first_entry(log, reversal.target)
    if target is None or target.event.account == reversal.account:
        return Ok(None)
    return Err(TargetOnAnotherAccount(reversal.target, target.event.account))


def _decide_event_of(
    history: AnyHistory, event: IncomingEvent, today: Day
) -> Result[tuple[LogEntry, ...], CurrencyMismatch]:
    """``_decide_event`` for an account whose currency is known only at run time."""
    # Both branches read alike; each gives the generic call a history of one known currency.
    if is_aed_history(history):
        return _decide_event(history, event, today)
    return _decide_event(history, event, today)


def _decide_event[M: (Aed, Bhd)](
    history: AccountHistory[M], event: IncomingEvent, today: Day
) -> Result[tuple[LogEntry, ...], CurrencyMismatch]:
    """The entries the event's account records for it, plus the instalments a credit generates."""
    match event:
        case Credit(posting=Instalments(count=count)):
            return Ok((CreditPosted(event, today), *_generate_instalments(event, count, today)))
        case Credit():
            return Ok((CreditPosted(event, today),))
        case Debit():
            return Ok((DebitPosted(event, today),))
        case Reversal():
            return Ok((_decide_reversal(history, event, today),))
        case Authorization():
            return _decide_authorization_entry(history, event, today).map(lambda entry: (entry,))
        case Settlement():
            return _decide_settlement_entry(history, event, today).map(lambda entry: (entry,))
        case _:
            assert_never(event)


def _decide_authorization_entry[M: (Aed, Bhd)](
    history: AccountHistory[M], authorization: Authorization, today: Day
) -> Result[AuthorizationApproved | AuthorizationDeclined, CurrencyMismatch]:
    """The authorization's decision, from the account's available balance when it arrives (AMB-008, AMB-009)."""
    return compute_available(history, today).flat_map(
        lambda available_balance: decide_authorization(available_balance, authorization, today)
    )


def _decide_settlement_entry[M: (Aed, Bhd)](
    history: AccountHistory[M], settlement: Settlement, today: Day
) -> Result[SettlementApplied | SettlementForcePosted, CurrencyMismatch]:
    """The settlement, settling against the authorization it names, or force-posted when there is none (AMB-012)."""
    record = find_record(history, settlement)
    if record is None:  # an unknown authorization has no transition either (AMB-012)
        return Ok(SettlementForcePosted(settlement, today))
    return _decide_effect(record.state, settlement, today)


def _decide_effect(
    state_before: AuthorizationState, settlement: Settlement, today: Day
) -> Result[SettlementApplied | SettlementForcePosted, CurrencyMismatch]:
    """The settlement applied to its authorization, or force-posted when the table has no transition for it
    (AMB-029)."""
    match apply_settlement(state_before, derive_settlement_input(settlement)):
        case Ok(state_after):
            return Ok(SettlementApplied(settlement, today, state_before, state_after))
        case Err(fault):
            return Ok(SettlementForcePosted(settlement, today)) if isinstance(fault, CannotSettle) else Err(fault)


def _generate_instalments(credit: Credit, count: InstalmentCount, today: Day) -> tuple[InstalmentPosted, ...]:
    """The instalments a credit generates, in order, each posted with the credit's value date (AMB-017, AMB-020)."""
    parts = split_amount_of(credit.amount, count)
    assert isinstance(parts, Ok)  # the stream reader refuses a credit it cannot split
    return tuple(
        InstalmentPosted(Instalment(InstalmentId(credit.id, number), credit.account, credit.value_date, part), today)
        for number, part in enumerate(parts.value, start=1)
    )


def _decide_reversal[M: (Aed, Bhd)](
    history: AccountHistory[M], reversal: Reversal, today: Day
) -> ReversalPosted | EventRejected:
    """A reversal, posted unless a check refuses it."""
    match check_reversal(history, reversal.target):
        case Ok():
            return ReversalPosted(reversal, today)
        case Err(rejection):
            return EventRejected(reversal, today, rejection)
