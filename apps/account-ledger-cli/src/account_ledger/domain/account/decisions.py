"""What one account records for an incoming event, decided from its history alone."""

from typing import assert_never

from account_ledger.common.result import Err, Ok, Result
from account_ledger.domain.account.authorizations import (
    CannotSettle,
    apply_settlement,
    decide_authorization,
    derive_settlement_input,
    find_record,
)
from account_ledger.domain.account.balances import (
    compute_available,
)
from account_ledger.domain.account.domain_events import (
    AuthorizationApproved,
    AuthorizationDeclined,
    CreditPosted,
    DebitPosted,
    EventRejected,
    InstalmentPosted,
    LogEntry,
    ReversalPosted,
    SettlementApplied,
    SettlementForcePosted,
)
from account_ledger.domain.account.history import (
    AccountHistoryIn,
)
from account_ledger.domain.account.reversals import (
    check_reversal,
)
from account_ledger.domain.account.states import (
    AuthorizationState,
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


def decide_event[M: (Aed, Bhd)](
    history: AccountHistoryIn[M], event: IncomingEvent, today: Day
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
    history: AccountHistoryIn[M], authorization: Authorization, today: Day
) -> Result[AuthorizationApproved | AuthorizationDeclined, CurrencyMismatch]:
    """The authorization's decision, from the account's available balance when it arrives (AMB-008, AMB-009)."""
    return compute_available(history, today).flat_map(
        lambda available_balance: decide_authorization(available_balance, authorization, today)
    )


def _decide_settlement_entry[M: (Aed, Bhd)](
    history: AccountHistoryIn[M], settlement: Settlement, today: Day
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
    history: AccountHistoryIn[M], reversal: Reversal, today: Day
) -> ReversalPosted | EventRejected:
    """A reversal, posted unless a check refuses it."""
    match check_reversal(history, reversal.target):
        case Ok():
            return ReversalPosted(reversal, today)
        case Err(rejection):
            return EventRejected(reversal, today, rejection)
