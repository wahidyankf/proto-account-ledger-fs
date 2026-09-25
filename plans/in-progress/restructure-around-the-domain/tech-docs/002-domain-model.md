# Domain Model

The domain after the plan: every value, the Account aggregate, and the Ledger, with each type's fields and methods and
the current function each method replaces. No rule, figure, message, or order of evaluation changes; each method does
exactly what the function it replaces does ([behaviour preservation](004-behaviour-preservation-and-tests.md)).

## Rules the Design Follows

- **An operation is a method of its subject (R1, R6).** An operation whose subject is one type is a method of that type,
  called as `DomainName.do_something()` or `value.do_something()`. It stays a module function only when it is a private
  step of its module, when it would make a lower layer know a higher one (rendering, CSV), when it dispatches on two
  closed sets in one `match` (the D8 table), or when no class can hold it: a function that builds one of a union's kinds
  from text (`parse_event_id`) or narrows a union with `TypeIs` (`is_aed`), which cannot narrow `self`. The earlier
  exception for a generic rule that must keep its type variable is gone: a method returning `Result[Self, …]` keeps
  `Result[M, …]` when called on a value of a constrained variable (probe, R15).
- **No class inheritance (R3, R9).** A class derives from nothing but `Protocol`, `Generic`, `Enum`, or an exception
  class. Kinds of one concept declare their own fields (R4); what several kinds share in behaviour is one private
  function each kind's method calls; a contract a signature consumes is a `Protocol` whose members are read-only
  properties, since a frozen dataclass cannot satisfy a writable attribute (verified 2026-09-25). A closed union already
  states what its members share, and pyright checks that every member holds the field a caller reads through it, so a
  family gets no Protocol that no signature consumes (R18).
- **Immutable values.** Every class is `@dataclass(frozen=True, slots=True)`, except `Ok` and `Err`, which stay
  hand-written and frozen; collections are tuples, `frozenset`s, or `MappingProxyType`s. A method returns a new value
  and never changes its subject. A local accumulator inside one method stays allowed, as
  [Immutability](../../../../repo-governance/principles/immutability.md) confines it; a module-level `dict` does not.
- **No type escape (R8).** No `assert` remains in `src/`: each of today's five is replaced by a type that carries its
  proof, listed at the end. No `Any`, `cast`, `# type: ignore`, or `# noqa` is added.
- **Currency stays in the type.** `M: (Aed, Bhd)` stays on every type generic over the currency, a type generic over the
  currency ends in `In`, and its union takes the plain noun, per
  [Naming](../../../../repo-governance/development/quality/stacks/python-standards/001-naming.md). A currency mismatch
  stays a returned `CurrencyMismatch`, as the prior plan's decision records and the app README's exit table publish
  (R16).

## `domain/model/money.py`

The module's order becomes: constants (`AMOUNT_LIMIT`, `DAILY_RATE`, `AED_FEE`, `AED_TO_BHD`), the faults
(`NotADecimal`, `TooManyPlaces`, `AboveLimit`, `MoneyFault`, `NotPositive`, `CurrencyMismatch`, `TooManyInstalments`),
the private functions, `Aed`, `Bhd`, `Money`, `AmountIn`, `Amount`, and `Direction`, so no name is used above its
definition except through a lazy annotation.

`Aed` and `Bhd` are two independent frozen, slotted, ordered dataclasses, each with `value: Decimal` and the `ClassVar`s
`CURRENCY` and `PLACES`; `_MoneyBase` goes (R3). Each carries the same methods, one to three lines each, calling a
private function written once for both, so every rule still exists once:

| Method on `Aed` and `Bhd`       | Replaces                    | Calls                                 |
| ------------------------------- | --------------------------- | ------------------------------------- |
| `make(value)`, `parse(text)`    | `_MoneyBase.make`, `.parse` | `_make_scaled_value`, `_read_decimal` |
| `make_zero()`                   | `_MoneyBase.make_zero`      | `_find_minor_unit`                    |
| `__add__`, `__sub__`, `__neg__` | the base's operators        | nothing                               |
| `get_currency`, `format_digits` | the base's                  | nothing                               |
| `is_below(amount)`              | the base's                  | `_make_mismatch`                      |
| `require_same(money)`           | `require_same_currency`     | `_require_same`                       |
| `add_all(values)`               | `sum_money(start, values)`  | `_add_all`                            |
| `compute_daily_interest()`      | `compute_daily_interest(b)` | `_round_money`                        |
| `compute_overdraft_fee()`       | the same method             | `_round_money` (AED 25.00, AMB-027)   |
| `make_amount()`                 | the same method             | `AmountIn.make`                       |
| `make_directed_amount()`        | the interest change's `if`  | `make_amount`                         |

- `make`, `parse`, `require_same`, and `add_all` return `Result[Self, …]`; `make_zero`, `compute_daily_interest` return
  `Self`. Each `__post_init__` calls `_check_places`, as the base's does today.
- `make_directed_amount() -> tuple[Direction, AmountIn[…]] | None` is `(UP, amount)` above zero,
  `(DOWN, the negated amount)` below, and `None` at zero; it replaces the sign test and the `assert` in
  `_record_interest_change`.
- `AmountIn[M]` keeps `make`, `split`, and `add`, and replaces `compute_rest` with
  `take(taken: Amount) -> Result[AmountIn[M] | None, CurrencyMismatch]`: the hold left once a settlement takes an
  amount, or `None` when the amount reaches or passes the hold. It builds the rest only once the rest is known to be
  above zero, so its `assert` goes.

## `domain/model/ids.py`

- `IdFault` moves to the top, before its first user.
- `Day` and `InstalmentCount` keep their fields and methods; `make` and `parse` become classmethods returning `Self`, as
  the money and text IDs' are.
- `AccountId`, `AuthorizationId`, and `IncomingId` each declare `value: str` and their own `PATTERN`, `KIND`, and
  `SHAPE` `ClassVar`s; `_TextIdBase` goes. Each `__post_init__` calls one private `_check_text`, and each `parse` one
  private `_parse_text`, both written once. `AccountId.number` and `IncomingId.format` stay.
- `FeeId`, `RefundId`, and `InterestId` each declare `account`, `for_day`, and `generated_day` and their own `PREFIX`;
  `_DayEventIdBase` goes. Each `format()` calls one private `_format_day_event_id`.
- `InstalmentId`, `CapitalizationId`, `EventId`, `parse_event_id`, and `_build_event_id` stay as they are.

## `domain/model/events.py`

- Every incoming kind declares `id`, `booked`, `account`, and `value_date` first, in today's order, and every generated
  kind `id`, `account`, and `value_date`; `_IncomingEventBase` and `_GeneratedEventBase` go. Positional construction,
  keyword access, and every `match` pattern stay as they are (R4).
- `Instalments` becomes `Instalments(count: InstalmentCount, parts: tuple[Amount, ...])`, built by the classmethod
  `Instalments.make(amount, count) -> Result[Instalments, TooManyInstalments]` from `amount.split(count)`. Its guard
  refuses parts whose number is not the count, as `InterestAccrual`'s guard refuses a wrong value date today; the stream
  reader builds every posting through `make`, so the guard never fires on a stream.
- `Credit.make_instalments() -> tuple[Instalment, ...]` gives the instalments its parts make, numbered from 1, each with
  the credit's account and value date, and none for a whole credit. The aggregate wraps each in `InstalmentPosted`; it
  replaces `decisions._generate_instalments` and its `assert isinstance(parts, Ok)`.
- `InterestAccrual.compute_signed_money()` and `InterestAdjustment.compute_signed_money()` give the event's amount,
  negative for an adjustment down; they replace `interest._sign_interest`.
- `SettlementKind`, `Whole`, `Posting`, `IncomingEvent`, `GeneratedEvent`, and the interest kinds' guards stay.

## `domain/model/config.py`

- `AccountIn[M]` becomes `AccountOpeningIn[M]` with the fields `id: AccountId` and `balance: M`, and `Account` becomes
  `AccountOpening` (R7): the account as it is opened, which the configuration lists. `is_aed` takes an `AccountOpening`.
- `LedgerConfig.find_account(account_id) -> AccountOpening | None` keeps its name and meaning.
- `CHALLENGE` moves to `account_ledger/challenge.py` (R14).

## `domain/account/`

### `rejections.py`

`IdReused`, `AlreadyReversed`, `ReversesAReversal`, `UnknownTarget`, `TargetOnAnotherAccount`, `MovedNoMoney`,
`AlreadyUndone`, and `Rejection`, moved unchanged out of `domain_events.py`, which then holds only domain events.

### `authorizations.py`

- The four states, `Approved`, `PartiallySettled`, `Declined`, and `Settled`, and `AuthorizationState`, moved from
  `states.py`, which goes. Nothing cycles: this module no longer reads a history, so it imports only the model.
- `AuthorizationRecord(authorization, state)` gains `is_referenced_by(settlement) -> bool`, today's `_is_referenced_by`.
- `CannotSettle`, and `apply_settlement`, the D8 table, one `match` over the state, the settlement's kind, and what the
  settlement leaves of the hold (R17):

  ```python
  def apply_settlement(
      state: AuthorizationState, kind: SettlementKind, amount: Amount
  ) -> Result[AuthorizationState, CannotSettle | CurrencyMismatch]:
      if isinstance(taken := _take_from_hold(state, amount), Err):
          return taken
      triple = (state, kind, taken.value)
      match triple:
          case Approved(), SettlementKind.FINAL, _:
              return Ok(Settled(amount))
          case Approved(), SettlementKind.PARTIAL, AmountIn() as kept:
              return Ok(PartiallySettled(amount, kept))
          case Approved(), SettlementKind.PARTIAL, None:  # it reaches the hold
              return Ok(Settled(amount))
          case PartiallySettled(settled_amount=settled), SettlementKind.FINAL, _:
              return settled.add(amount).map(Settled)
          case PartiallySettled(settled_amount=settled), SettlementKind.PARTIAL, AmountIn() as kept:
              return settled.add(amount).map(lambda total: PartiallySettled(total, kept))
          case PartiallySettled(settled_amount=settled), SettlementKind.PARTIAL, None:
              return settled.add(amount).map(Settled)
          case Settled() | Declined(), _, _:
              return Err(CannotSettle())
          case _:
              assert_never(triple)
  ```

  `_take_from_hold(state, amount)` is `hold.take(amount)` for a state that keeps a hold and `Ok(None)` for one that does
  not, so the mismatch a bug would bring is still returned before the table is read, as today. `take` gives a rest
  exactly when today's guard, the amount below the hold, holds, so every row gives today's outcome. `FinalSettlement`,
  `PartialSettlement`, `_SettlementInputBase`, `SettlementInput`, `derive_settlement_input`,
  `_is_settlement_below_hold`, `_make_partial_settlement`, and `_compute_rest` go (R17).

### `domain_events.py`

The fifteen domain events each declare `event` and `processed_day`; `_DomainEventBase` goes. `SettlementApplied` keeps
`state_before` and `state_after`, and `EventRejected` keeps `reason`. `LogEntry` and `LoggedEvent` stay.

### `event_log.py`

`EventLog(entries: tuple[LogEntry, ...])`, the append-only entries of the whole ledger or of one account, replacing the
alias `Log`. It lives in `account/` because an account's own entries are an `EventLog` too, and the account package may
not import the ledger's.

| Method                       | Replaces                                          |
| ---------------------------- | ------------------------------------------------- |
| `append(*entries)`           | `append_entry`, and each `(*log, *entries)`       |
| `find_first_entry(event_id)` | `history.find_first_entry`, on either kind of log |
| `select(account_id)`         | the filter inside `find_history`                  |
| `list_processed_on(day)`     | the report's `entry.processed_day == day` filters |

### `account.py`: the Account aggregate

`AccountIn[M: (Aed, Bhd)]` with the fields `id: AccountId`, `opening: M`, and `log: EventLog`, the account's own entries
in log order, and `type Account = AccountIn[Aed] | AccountIn[Bhd]` (R1, R7). It replaces `AccountHistoryIn`,
`AccountAggregateIn`, and every function that took a history. Every rule about one account is one of its methods, in one
module, grouped by topic in this order; `history` in today's code reads as `self`.

| Topic          | Public methods                       | Private methods, each today's function of the same name    |
| -------------- | ------------------------------------ | ---------------------------------------------------------- |
| entries        | `list_instalments(credit)`           | `_find_entry`, `_list_counted_events`, `_with_entry`,      |
|                |                                      | `_make_zero`                                               |
| balances       | `compute_closing(day)`,              | `_list_effects`, `_list_moved_amounts`,                    |
|                | `compute_available(day)`             | `_list_undone_amounts`                                     |
| authorizations | `list_records()`, `sum_holds(day)`   | `_find_record`                                             |
| decisions      | `decide_event(event, today)`         | `_decide_authorization_entry`, `_decide_settlement_entry`, |
|                |                                      | `_decide_reversal`                                         |
| reversals      |                                      | `_check_reversal`, `_find_reversal_id`,                    |
|                |                                      | `_list_reversed_targets`, `_check_undoing`, `_find_refund` |
| fees           | `assess_fees(today, first_day)`      | `_map_fees_in_force`, `_is_closing_below_zero`             |
| interest       | `accrue_interest(today, first_day)`, | `_find_interest_changes`, `_compute_interest_change`,      |
|                | `capitalize_interest(today)`,        | `_compute_accrued`, `_map_interest_since_capitalization`,  |
|                | `list_accrued_days(capitalization)`  | `_compute_interest_base`, `_sum_interest_generated`        |

- The public methods are the ones code outside the account modules or a test calls today; every function only the
  account modules call becomes private, so `find_entry`, `list_counted_events`, `check_reversal`,
  `list_reversed_targets`, and `find_record` lose their public names.
- `decide_authorization`, today public in `authorizations.py` and called only by `_decide_authorization_entry`, folds
  into it.
- Two private steps read nothing of the account and stay module functions in `account.py`:
  `_decide_effect(state, settlement, today)`, which now calls
  `apply_settlement(state, settlement.kind, settlement.amount)`, and
  `_record_interest_change(account_id, day, today, direction, amount)`, which takes what `make_directed_amount` gives.
- `sum_money(type(history.account.opening).make_zero(), …)` becomes `self._make_zero().add_all(…)`, and
  `compute_daily_interest(base)` becomes `base.compute_daily_interest()`.
- `_with_entry(entry)` replaces `AccountHistoryIn.append` inside `assess_fees`, its one caller; it is private, and every
  entry the aggregate builds carries `self.id`, so the entry-on-its-own-account `assert` goes.

The module is long, about 650 lines, by the owner's choice of one class in one file (R1); it passes the complexity gates
because each method stays the size of the function it replaces.

## `domain/ledger/ledger.py`

`UnknownAccount(account: AccountId)` is a fault only a bug brings, and
`type InternalFault = CurrencyMismatch | UnknownAccount` (R8). `Ledger(config: LedgerConfig, log: EventLog)` is the one
object that sees every account (R6), and `Ledger.open(config)` starts it with an empty log.

| Method                            | Replaces                                           |
| --------------------------------- | -------------------------------------------------- |
| `find_account(opening)`           | `find_history_of`, the one currency dispatch       |
| `list_accounts()`                 | each `find_history_of` loop over `config.accounts` |
| `process_event(event, today)`     | `processing.process_event`                         |
| `close_day(today)`                | `end_of_day.close_day`                             |
| `_check_target_account(reversal)` | `processing._check_target_account`                 |
| `_find_opening(account_id)`       | `config.find_account` and the `assert` beside it   |

- `find_account(opening: AccountOpening) -> Account` narrows with `is_aed` and builds
  `AccountIn(opening.id, opening.balance, self.log.select(opening.id))` in each branch, since a generic class cannot be
  built from a union.
- `process_event` returns `Result[Ledger, InternalFault]` and `close_day` `Result[Ledger, CurrencyMismatch]`, each a new
  `Ledger`. `process_event` checks in today's order: the repeated ID (AMB-034), the cross-account reversal (AMB-036),
  the account, then the account's decision.
- `_find_opening(account_id) -> Result[AccountOpening, UnknownAccount]`.

## Where Each `assert` Goes (R8)

| Today                                         | After                                                         |
| --------------------------------------------- | ------------------------------------------------------------- |
| `_generate_instalments`: the split is `Ok`    | `Credit.make_instalments` reads the parts `Instalments` holds |
| `_compute_rest`: the rest is above zero       | `AmountIn.take` gives the rest or `None`; the table matches   |
| `_record_interest_change`: change is not zero | `make_directed_amount` gives `None` at zero                   |
| `process_event`: the account is configured    | `Ledger._find_opening` returns `Err(UnknownAccount)`          |
| `AccountHistoryIn.append`: the entry is its   | `_with_entry` is private, and every entry is built from       |
| own account's                                 | `self.id`                                                     |

`_find_interest_changes` already skips a zero change, so `make_directed_amount` never gives `None` there; the `None` is
matched and skipped, and no user-visible line changes. A user cannot reach `UnknownAccount` either: the stream reader
refuses an unconfigured account first, with today's message. The CLI prints it as an internal fault,
`error: internal: ACC-NNN is not a configured account`, exit 2, beside the currency mismatch's line, and a new unit test
proves the ledger returns it ([behaviour preservation](004-behaviour-preservation-and-tests.md)).
