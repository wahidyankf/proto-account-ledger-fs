"""The Account aggregate: one account and its own entries, answering every rule about the account as a method."""

from collections.abc import Iterator
from dataclasses import dataclass
from typing import assert_never

from account_ledger.common.result import Err, Ok, Result
from account_ledger.domain.account.authorizations import (
    Approved,
    AuthorizationRecord,
    AuthorizationState,
    CannotSettle,
    Declined,
    PartiallySettled,
    Settled,
    apply_settlement,
)
from account_ledger.domain.account.domain_events import (
    AuthorizationApproved,
    AuthorizationDeclined,
    CreditPosted,
    DebitPosted,
    DuplicateIgnored,
    EventRejected,
    FeeCharged,
    FeeRefunded,
    InstalmentPosted,
    InterestAccrued,
    InterestAdjusted,
    InterestCapitalized,
    LogEntry,
    LoggedEvent,
    ReversalPosted,
    SettlementApplied,
    SettlementForcePosted,
)
from account_ledger.domain.account.event_log import EventLog
from account_ledger.domain.account.rejections import (
    AlreadyReversed,
    AlreadyUndone,
    MovedNoMoney,
    Rejection,
    ReversesAReversal,
    UnknownTarget,
)
from account_ledger.domain.model.events import (
    Authorization,
    Capitalization,
    Credit,
    Debit,
    Fee,
    FeeRefund,
    IncomingEvent,
    Instalment,
    Instalments,
    InterestAccrual,
    InterestAdjustment,
    Reversal,
    Settlement,
    Whole,
)
from account_ledger.domain.model.ids import (
    AccountId,
    CapitalizationId,
    Day,
    EventId,
    FeeId,
    IncomingId,
    InterestId,
    RefundId,
)
from account_ledger.domain.model.money import Aed, Amount, Bhd, CurrencyMismatch, Direction, Money


@dataclass(frozen=True, slots=True)
class AccountIn[M: (Aed, Bhd)]:
    """The Account aggregate: one account, its opening balance, and its own entries in log order. Every rule about one
    account is one of its methods and reads only these entries, so no rule can see another account's; a caller asks the
    account, and never needs to know its currency."""

    id: AccountId
    opening: M
    log: EventLog

    def list_instalments(self, credit: IncomingId) -> tuple[Instalment, ...]:
        """The instalments a credit generated, in order (AMB-017)."""
        return tuple(
            entry.event
            for entry in self.log.entries
            if isinstance(entry, InstalmentPosted) and entry.event.id.parent == credit
        )

    def _find_entry(self, event_id: EventId) -> LogEntry | None:
        """The account's first entry for an event ID, the one a reversal targets (AMB-028, AMB-035)."""
        return self.log.find_first_entry(event_id)

    def _list_counted_events(self) -> Iterator[LoggedEvent]:
        """The events of the account's postings; a hold is read by ``sum_holds``, and a refusal or a retry moves
        nothing."""
        for entry in self.log.entries:
            match entry:
                case AuthorizationApproved() | AuthorizationDeclined() | EventRejected() | DuplicateIgnored():
                    pass
                case _:
                    yield entry.event

    def _append_entry(self, entry: LogEntry) -> AccountIn[M]:
        """This account with an entry it built, from its own ID, at the end; nothing is ever changed or removed."""
        return AccountIn(self.id, self.opening, self.log.append(entry))

    def _make_zero(self) -> M:
        """Zero in the account's currency."""
        return type(self.opening).make_zero()

    def compute_closing(self, day: Day) -> Result[M, CurrencyMismatch]:
        """The opening plus the effect of every counted entry with value date <= day."""
        effects = [effect for value_date, effect in self._list_effects() if value_date <= day]
        return self.opening.add_all(effects)

    def compute_available(self, day: Day) -> Result[M, CurrencyMismatch]:
        """The closing less the holds."""
        if isinstance(closing := self.compute_closing(day), Err):
            return closing
        return self.sum_holds(day).map(lambda holds: closing.value - holds)

    def _list_effects(self) -> list[tuple[Day, Money]]:
        """Each counted entry's value date and signed effect on the account's ledger balance."""
        effects: list[tuple[Day, Money]] = []
        for event in self._list_counted_events():
            effects.extend((event.value_date, amount) for amount in self._list_moved_amounts(event))
        return effects

    def _list_moved_amounts(self, event: LoggedEvent) -> tuple[Money, ...]:
        """The signed amounts an event moves on the ledger balance; none for an event that moves nothing."""
        match event:
            case Credit():
                match event.posting:
                    case Whole():
                        return (event.amount.money,)
                    case Instalments():
                        return ()  # a credit in instalments posts nothing itself; its instalments post the parts
                    case _:
                        assert_never(event.posting)
            case Instalment() | FeeRefund() | Capitalization():
                return (event.amount.money,)
            case Debit() | Settlement() | Fee():
                return (-event.amount.money,)
            case Authorization():
                return ()  # a hold moves the available balance only, never the ledger balance
            case InterestAccrual() | InterestAdjustment():
                return ()  # interest moves accrued interest, never the ledger balance, until capitalized (AMB-007)
            case Reversal(target=reverses):
                target = self._find_entry(reverses)
                undone_amounts = () if target is None else self._list_undone_amounts(target.event)
                return tuple(-amount for amount in undone_amounts)  # counted from the reversal's own value date
            case _:
                assert_never(event)

    def _list_undone_amounts(self, target: LoggedEvent) -> tuple[Money, ...]:
        """What reversing the target takes out: what it moved, and for a credit in instalments, every instalment."""
        match target:
            case Credit(posting=Instalments()):
                amounts: list[Money] = []
                for part in self.list_instalments(target.id):
                    amounts.extend(self._list_moved_amounts(part))
                return tuple(amounts)
            case _:
                return self._list_moved_amounts(target)

    def list_records(self) -> tuple[AuthorizationRecord, ...]:
        """Every authorization the account knows, in the order first seen, with its state."""
        records: list[AuthorizationRecord] = []
        for entry in self.log.entries:
            match entry:
                case AuthorizationApproved(event=event):
                    records.append(AuthorizationRecord(event, Approved(event.amount)))
                case AuthorizationDeclined(event=event):
                    records.append(AuthorizationRecord(event, Declined(event.amount)))
                case SettlementApplied(event=event, state_after=state_after):
                    records = [
                        AuthorizationRecord(record.authorization, state_after)
                        if record.is_referenced_by(event)
                        else record
                        for record in records
                    ]
                case (
                    CreditPosted()
                    | DebitPosted()
                    | ReversalPosted()
                    | InstalmentPosted()
                    | FeeCharged()
                    | FeeRefunded()
                    | InterestAccrued()
                    | InterestAdjusted()
                    | InterestCapitalized()
                    | SettlementForcePosted()
                    | EventRejected()
                    | DuplicateIgnored()
                ):
                    pass  # a posting, a force-post, a refusal, or a retry moves no authorization
                case _:
                    assert_never(entry)
        return tuple(records)

    def sum_holds(self, day: Day) -> Result[M, CurrencyMismatch]:
        """The hold of every approved or partially settled authorization on the account whose value date is <= day
        (AMB-010, AMB-013)."""
        holds: list[Money] = []
        for record in self.list_records():
            authorization, state = record.authorization, record.state
            if authorization.value_date > day:
                continue
            match state:
                case Approved(hold=hold) | PartiallySettled(hold=hold):
                    holds.append(hold.money)
                case Declined() | Settled():
                    pass  # a declined authorization holds nothing, and a final settlement released the hold
                case _:
                    assert_never(state)
        return self._make_zero().add_all(holds)

    def _find_record(self, settlement: Settlement) -> AuthorizationRecord | None:
        """The authorization a settlement names, if the account knows it."""
        return next((record for record in self.list_records() if record.is_referenced_by(settlement)), None)

    def decide_event(self, event: IncomingEvent, today: Day) -> Result[tuple[LogEntry, ...], CurrencyMismatch]:
        """The entries the event's account records for it, plus the instalments a credit generates."""
        match event:
            case Credit():
                return Ok((CreditPosted(event, today), *_generate_instalments(event, today)))
            case Debit():
                return Ok((DebitPosted(event, today),))
            case Reversal():
                return Ok((self._decide_reversal(event, today),))
            case Authorization():
                return self._decide_authorization_entry(event, today).map(lambda entry: (entry,))
            case Settlement():
                return self._decide_settlement_entry(event, today).map(lambda entry: (entry,))
            case _:
                assert_never(event)

    def _decide_authorization_entry(
        self, authorization: Authorization, today: Day
    ) -> Result[AuthorizationApproved | AuthorizationDeclined, CurrencyMismatch]:
        """The decision on arrival, from the account's available balance before the hold (AMB-008, AMB-009)."""
        if isinstance(available_balance := self.compute_available(today), Err):
            return available_balance
        return available_balance.value.is_below(authorization.amount).map(
            lambda is_short: (
                AuthorizationDeclined(authorization, today) if is_short else AuthorizationApproved(authorization, today)
            )
        )

    def _decide_settlement_entry(
        self, settlement: Settlement, today: Day
    ) -> Result[SettlementApplied | SettlementForcePosted, CurrencyMismatch]:
        """The settlement, settling against the authorization it names, or force-posted when there is none (AMB-012)."""
        record = self._find_record(settlement)
        if record is None:  # an unknown authorization has no transition either (AMB-012)
            return Ok(SettlementForcePosted(settlement, today))
        return _decide_effect(record.state, settlement, today)

    def _decide_reversal(self, reversal: Reversal, today: Day) -> ReversalPosted | EventRejected:
        """A reversal, posted unless a check refuses it."""
        match self._check_reversal(reversal.target):
            case Ok():
                return ReversalPosted(reversal, today)
            case Err(rejection):
                return EventRejected(reversal, today, rejection)

    def _check_reversal(self, target_id: EventId) -> Result[None, Rejection]:
        """Nothing when a reversal of the target on the account may proceed, or why it is refused, checked in tech-docs
        002's order (AMB-028, AMB-035); a target on another account is refused before the account sees it (AMB-036)."""
        target = self._find_entry(target_id)
        if target is None:
            return Err(UnknownTarget(target_id))
        if isinstance(target.event, Reversal):
            return Err(ReversesAReversal(target_id))
        if isinstance(target, AuthorizationApproved | AuthorizationDeclined | EventRejected):
            return Err(MovedNoMoney(target_id))
        reversal_id = self._find_reversal_id(target_id)
        if reversal_id is not None:
            return Err(AlreadyReversed(target_id, reversal_id))
        return self._check_undoing(target.event)

    def _find_reversal_id(self, target_id: EventId) -> IncomingId | None:
        """The posted reversal of the target, if there is one."""
        for entry in self.log.entries:
            match entry:
                case ReversalPosted(event=Reversal(id=reversal_id, target=target)) if target == target_id:
                    return reversal_id
                case _:
                    pass
        return None

    def _list_reversed_targets(self, cutoff_day: Day | None = None) -> frozenset[EventId]:
        """The events a posted reversal on the account undid (AMB-035); with ``cutoff_day``, only reversals
        value-dated by then."""
        return frozenset(
            event.target
            for event in self._list_counted_events()
            if isinstance(event, Reversal) and (cutoff_day is None or event.value_date <= cutoff_day)
        )

    def _check_undoing(self, target: LoggedEvent) -> Result[None, AlreadyUndone]:
        """Nothing when none of the target's money is undone another way, or the part that is: a fee refunded, or a
        credit or one of its instalments reversed."""
        match target:
            case Instalment(id=part):
                undoing_id = self._find_reversal_id(part.parent)
                return Ok(None) if undoing_id is None else Err(AlreadyUndone(part, undoing_id))
            case Fee(id=fee):
                refund = self._find_refund(fee)
                return Ok(None) if refund is None else Err(AlreadyUndone(fee, refund))
            case Credit(posting=Instalments()):
                for part in self.list_instalments(target.id):
                    undoing_id = self._find_reversal_id(part.id)
                    if undoing_id is not None:
                        return Err(AlreadyUndone(part.id, undoing_id))
                return Ok(None)
            case _:
                return Ok(None)

    def _find_refund(self, fee: FeeId) -> RefundId | None:
        """The refund in effect for the fee: one that names it and is not itself reversed (AMB-004, AMB-035)."""
        for entry in self.log.entries:
            match entry:
                case FeeRefunded(event=FeeRefund(id=refund, fee=refunded_fee)) if refunded_fee == fee:
                    if self._find_reversal_id(refund) is None:
                        return refund
                case _:
                    pass
        return None

    def assess_fees(self, today: Day, first_day: Day) -> Result[tuple[LogEntry, ...], CurrencyMismatch]:
        """For each day so far, in order: a fee, value-dated today, for a day that closes negative with no fee in force,
        and a refund of the fee in force for a day that closes at or above zero (AMB-002, AMB-004). Each closing is read
        from the account as it grows, so a fee generated for an earlier day counts in the days after it (AMB-011)."""
        account, account_id = self, self.id
        amount = self.opening.compute_overdraft_fee()
        entries: list[LogEntry] = []
        for day in first_day.span_to(today):
            fee = account._map_fees_in_force().get(day)
            if isinstance(negative_closing := account._is_closing_below_zero(day), Err):
                return negative_closing
            entry: LogEntry | None = None
            if negative_closing.value:
                if fee is None:
                    entry = FeeCharged(Fee(FeeId(account_id, day, today), account_id, today, amount), today)
            elif fee is not None:
                entry = FeeRefunded(
                    FeeRefund(RefundId(account_id, day, today), account_id, today, fee.id, fee.amount), today
                )
            if entry is not None:
                account = account._append_entry(entry)
                entries.append(entry)
        return Ok(tuple(entries))

    def _map_fees_in_force(self) -> dict[Day, Fee]:
        """The account's fee in force for each day: one per day per account, until a refund names it or a reversal
        undoes it, and again once a reversal undoes that refund (AMB-002, AMB-004, AMB-035)."""
        fees: dict[Day, Fee] = {}
        refunded_fees: dict[RefundId, Fee] = {}
        for entry in self.log.entries:
            match entry:
                case FeeCharged(event=fee):
                    fees[fee.id.for_day] = fee
                case FeeRefunded(event=refund):
                    refunded_fee = fees.pop(refund.fee.for_day, None)
                    if refunded_fee is not None:
                        refunded_fees[refund.id] = refunded_fee
                case ReversalPosted(event=Reversal(target=RefundId() as reversed_refund)) if (
                    reversed_refund in refunded_fees
                ):
                    restored_fee = refunded_fees.pop(reversed_refund)  # a reversed refund puts its fee back in force
                    fees[restored_fee.id.for_day] = restored_fee
                case ReversalPosted(event=Reversal(target=FeeId() as reversed_fee)):
                    fee_in_force = fees.get(reversed_fee.for_day)
                    if fee_in_force is not None and fee_in_force.id == reversed_fee:
                        del fees[reversed_fee.for_day]  # a reversed fee is out of force, so its day is judged again
                case _:
                    pass
        return fees

    def _is_closing_below_zero(self, day: Day) -> Result[bool, CurrencyMismatch]:
        """Whether the account's closing on the day is below zero, in its own currency."""
        zero = self._make_zero()
        return self.compute_closing(day).map(lambda closing: closing < zero)

    def accrue_interest(self, today: Day, first_day: Day) -> Result[tuple[LogEntry, ...], CurrencyMismatch]:
        """For each day so far whose interest differs from what was generated for it, the difference: today's accrual,
        or an adjustment of an earlier day, value-dated today (AMB-005)."""
        if isinstance(changes := self._find_interest_changes(today, first_day), Err):
            return changes
        return Ok(
            tuple(
                _record_interest_change(self.id, day, today, *directed)
                for day, change in changes.value
                if (directed := change.make_directed_amount()) is not None
            )
        )

    def capitalize_interest(self, today: Day) -> Result[tuple[LogEntry, ...], CurrencyMismatch]:
        """The account's accrued interest, credited value-dated today when it is above zero (AMB-007, AMB-023)."""
        if isinstance(accrued := self._compute_accrued(), Err):
            return accrued
        account_id = self.id
        match accrued.value.make_amount():
            case Ok(amount):
                capitalization = Capitalization(CapitalizationId(account_id, today), account_id, today, amount)
                return Ok((InterestCapitalized(capitalization, today),))
            case Err():
                return Ok(())

    def list_accrued_days(self, capitalization: CapitalizationId) -> Result[tuple[Day, ...], CurrencyMismatch]:
        """The days whose interest a capitalization pays: each day whose interest events, generated since the account's
        previous capitalization, do not net to zero (tech-docs 003)."""
        zero = self._make_zero()
        accrued_days: list[Day] = []
        for day, changes in sorted(self._map_interest_since_capitalization(capitalization).items()):
            if isinstance(net_interest := zero.add_all(changes), Err):
                return net_interest
            if net_interest.value != zero:
                accrued_days.append(day)
        return Ok(tuple(accrued_days))

    def _find_interest_changes(self, today: Day, first_day: Day) -> Result[tuple[tuple[Day, M], ...], CurrencyMismatch]:
        """Each day from ``first_day`` to ``today`` whose interest differs from what was generated, in its currency."""
        changes: list[tuple[Day, M]] = []
        for day in first_day.span_to(today):
            if isinstance(change := self._compute_interest_change(day), Err):
                return change
            if change.value.value != 0:
                changes.append((day, change.value))
        return Ok(tuple(changes))

    def _compute_interest_change(self, day: Day) -> Result[M, CurrencyMismatch]:
        """The day's interest on its base, less what was generated for it."""
        if isinstance(base := self._compute_interest_base(day), Err):
            return base
        return self._sum_interest_generated(day).map(lambda generated: base.value.compute_daily_interest() - generated)

    def _compute_accrued(self) -> Result[M, CurrencyMismatch]:
        """The account's interest events, net of their directions, less its capitalizations, each less its reversals
        (AMB-007, AMB-035)."""
        undone_ids = self._list_reversed_targets()
        changes: list[Money] = []
        for event in self._list_counted_events():
            match event:
                case InterestAccrual() | InterestAdjustment() if event.id not in undone_ids:
                    changes.append(event.compute_signed_money())
                case Capitalization(id=capitalization_id, amount=amount) if capitalization_id not in undone_ids:
                    changes.append(-amount.money)
                case _:
                    pass
        return self._make_zero().add_all(changes)

    def _map_interest_since_capitalization(self, capitalization: CapitalizationId) -> dict[Day, list[Money]]:
        """Each day's signed interest events generated since the capitalization before this one, up to this one."""
        undone_ids = self._list_reversed_targets()
        interest_by_day: dict[Day, list[Money]] = {}
        for event in self._list_counted_events():
            match event:
                case Capitalization(id=capitalization_id) if capitalization_id == capitalization:
                    break
                case Capitalization(id=capitalization_id) if capitalization_id not in undone_ids:
                    interest_by_day = {}
                case InterestAccrual() | InterestAdjustment() if event.id not in undone_ids:
                    interest_by_day.setdefault(event.id.for_day, []).append(event.compute_signed_money())
                case _:
                    pass
        return interest_by_day

    def _compute_interest_base(self, day: Day) -> Result[M, CurrencyMismatch]:
        """The closing less any capitalization value-dated that day, which posts after the day's interest (AMB-023); one
        whose reversal that closing already counts is out of it already (AMB-035)."""
        undone_ids = self._list_reversed_targets(cutoff_day=day)
        capitalized_values: list[Money] = []
        for event in self._list_counted_events():
            match event:
                case Capitalization(id=capitalization_id, value_date=value_date, amount=amount) if (
                    value_date == day and capitalization_id not in undone_ids
                ):
                    capitalized_values.append(-amount.money)
                case _:
                    pass
        return self.compute_closing(day).flat_map(lambda closing: closing.add_all(capitalized_values))

    def _sum_interest_generated(self, day: Day) -> Result[M, CurrencyMismatch]:
        """The account's interest events for a day, net of their directions and reversals (tech-docs 002, step 2)."""
        undone_ids = self._list_reversed_targets()
        generated_values = [
            event.compute_signed_money()
            for event in self._list_counted_events()
            if isinstance(event, InterestAccrual | InterestAdjustment)
            and event.id.for_day == day
            and event.id not in undone_ids
        ]
        return self._make_zero().add_all(generated_values)


type Account = AccountIn[Aed] | AccountIn[Bhd]


def _decide_effect(
    state_before: AuthorizationState, settlement: Settlement, today: Day
) -> Result[SettlementApplied | SettlementForcePosted, CurrencyMismatch]:
    """The settlement applied to its authorization, or force-posted when the table has no transition for it
    (AMB-029)."""
    match apply_settlement(state_before, settlement.kind, settlement.amount):
        case Ok(state_after):
            return Ok(SettlementApplied(settlement, today, state_before, state_after))
        case Err(fault):
            return Ok(SettlementForcePosted(settlement, today)) if isinstance(fault, CannotSettle) else Err(fault)


def _generate_instalments(credit: Credit, today: Day) -> tuple[InstalmentPosted, ...]:
    """The instalments a credit generates, in order, each posted today; none for a whole credit (AMB-017, AMB-020)."""
    return tuple(InstalmentPosted(instalment, today) for instalment in credit.make_instalments())


def _record_interest_change(
    account: AccountId, day: Day, today: Day, direction: Direction, amount: Amount
) -> InterestAccrued | InterestAdjusted:
    """A day's interest change as it is recorded today: an accrual for today, an adjustment for an earlier day."""
    interest_id = InterestId(account, day, today)
    # nothing is generated for today before its close, so today's change is its first, positive accrual
    if day == today:
        return InterestAccrued(InterestAccrual(interest_id, account, today, amount), today)
    return InterestAdjusted(InterestAdjustment(interest_id, account, today, direction, amount), today)
