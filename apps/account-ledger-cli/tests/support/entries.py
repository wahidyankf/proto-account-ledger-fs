"""Readers that turn a log's entries, or an account's authorization states, into plain values for the tests."""

from account_ledger.challenge import CHALLENGE
from account_ledger.domain.account.authorizations import AuthorizationState
from account_ledger.domain.account.domain_events import (
    FeeCharged,
    FeeRefunded,
    InterestAccrued,
    InterestAdjusted,
    InterestCapitalized,
    LogEntry,
    SettlementApplied,
    SettlementForcePosted,
)
from account_ledger.domain.account.event_log import EventLog
from account_ledger.domain.ledger.ledger import Ledger
from account_ledger.domain.model.config import AccountOpening
from account_ledger.domain.model.events import InterestAccrual, InterestAdjustment
from account_ledger.domain.model.ids import AuthorizationId, IncomingId
from account_ledger.domain.model.money import Direction, Money
from support.streams import ACC_001_OPENING


def list_fee_ids(log: EventLog) -> list[str]:
    """The generated ID of every fee in the log, in the order generated."""
    return [entry.event.id.format() for entry in log.entries if isinstance(entry, FeeCharged)]


def list_refund_ids(log: EventLog) -> list[str]:
    """The generated ID of every fee refund in the log, in the order generated."""
    return [entry.event.id.format() for entry in log.entries if isinstance(entry, FeeRefunded)]


def list_interest_amounts(log: EventLog) -> list[tuple[str, Money]]:
    """The generated ID and signed amount of every interest event in the log, in the order generated."""
    amounts: list[tuple[str, Money]] = []
    for entry in log.entries:
        match entry:
            case InterestAccrued(event=InterestAccrual(id=interest_id, amount=amount)):
                amounts.append((interest_id.format(), amount.money))
            case InterestAdjusted(event=InterestAdjustment(id=interest_id, direction=direction, amount=amount)):
                amounts.append((interest_id.format(), amount.money if direction is Direction.UP else -amount.money))
            case _:
                pass
    return amounts


def list_capitalization_amounts(log: EventLog) -> list[tuple[str, Money]]:
    """The generated ID and amount of every capitalization in the log, in the order generated."""
    return [
        (entry.event.id.format(), entry.event.amount.money)
        for entry in log.entries
        if isinstance(entry, InterestCapitalized)
    ]


def list_states(log: EventLog, hold: str, opening: AccountOpening = ACC_001_OPENING) -> list[AuthorizationState]:
    """The state of every authorization with this authorization ID on the account, ACC-001 unless named, in the order
    first seen."""
    account = Ledger(CHALLENGE, log).find_account(opening)
    return [
        record.state for record in account.list_records() if record.authorization.authorization == AuthorizationId(hold)
    ]


def list_settlements(log: EventLog, event: str) -> list[SettlementApplied | SettlementForcePosted]:
    """Every settlement entry for this event ID, in log order."""
    return [
        entry
        for entry in log.entries
        if isinstance(entry, SettlementApplied | SettlementForcePosted) and entry.event.id == IncomingId(event)
    ]


def list_entries(log: EventLog, event: str) -> list[LogEntry]:
    """Every entry for this incoming event ID, in log order."""
    return [entry for entry in log.entries if entry.event.id == IncomingId(event)]
