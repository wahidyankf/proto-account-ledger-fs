# Domain Model

The types the ledger core is made of, and what each one means. Everything here is pure data, frozen dataclasses, enums,
unions, and tuples, per the
[Python standards](../../../../repo-governance/development/quality/stacks/python-standards.md), and every type is built
so that no value of it can be illegal (D16): a constructor that meets an illegal value refuses it, so the rest of the
code never checks again. One contract holds for every such type: its `__post_init__` raises `ValueError` on an illegal
value, which only a bug can reach, and its `parse` or `of` is the expected-failure path, returning a typed fault. Raw
text and integers exist only at the two edges, the parser and the renderer, and `Decimal` only inside `money.py` (D14,
D15); tests build values through the same `parse` functions. Terms are defined where they first appear.

## Terms

- **Event.** Anything that happens to the ledger. An _incoming_ event comes from the stream (E1 to E10); a _fired_ event
  is one the ledger creates itself, at the end of a day (fees, refunds, interest, capitalization) or when it posts an
  instalment. Both kinds go into the same log (AMB-024).
- **Log.** The append-only tuple of every entry, in the order it was appended. It is the only state the ledger keeps;
  every balance is computed from it (AMB-004, D7).
- **Booked day.** The day an event was recorded at its source, as the stream states it.
- **Processed day.** The day the ledger actually handles an event: its booked day, or the current day if that day has
  already closed (AMB-015). E10 is booked Day 5 and processed Day 6.
- **Value day.** The day an event counts from in balances. A closing for day `d` sums every counted event whose value
  day is at most `d`.
- **Amount.** What an event carries: always above zero, in one currency. The kind of event says which way it moves the
  balance (D18).
- **Balance.** What a sum of effects gives: signed, in one currency, such as −370.00.
- **Marker.** The ID of a fired event, naming its kind, account number, the day it is for, and the day it fired:
  `FEE-001-D2@D5` is ACC-001's fee for Day 2, fired at the close of Day 5.

## Money

```text
money.py
  Aed               value: a Decimal with exactly 2 places        Aed.parse(text) -> Aed | MoneyFault
  Bhd               value: a Decimal with exactly 3 places        Bhd.parse(text) -> Bhd | MoneyFault
  Money             Aed | Bhd
  Amount[M]         money: an M above zero                         Amount.of(money) -> Amount[M] | NotPositive
  Direction         Enum: UP, DOWN
  operators         Aed + Aed, Aed - Aed, -Aed, and Aed < Aed give Aed or bool; the same for Bhd; never across
  same_as(like, m)  M, Money -> M | CurrencyMismatch               narrows a union value to a known currency
  split(amount, n)  Amount[M], InstalmentCount -> tuple[Amount[M], ...] | TooManyInstalments
  overdraft_fee(z)  M -> Amount[M]                                 AED 25.00; BHD 2.560
  daily_interest(b) M -> M                                         b × 0.0004, half-even; zero unless b is above zero
  digits(m)         Money -> str                                   the value's text, for the renderer
```

- **One type per currency (D14).** `Aed` and `Bhd` are separate frozen dataclasses joined in the union `Money`. Their
  operators accept only their own type, so adding an `Aed` to a `Bhd` is a pyright error, not a runtime surprise.
  Generic code uses a constrained type variable, `M: (Aed, Bhd)`. A value whose currency is only known as `Money` is
  narrowed with `same_as` or a `match`, and a mismatch is the typed `CurrencyMismatch`, never a silent sum.
- **Places are checked on construction (D14b).** An `Aed` built from a `Decimal` with three places raises, so none can
  exist. `Aed.parse("12.345")` is the expected-failure path, returning `MoneyFault`, and `Aed.parse("12.5")` is the
  `Aed` of 12.50, since no digit is lost. Tests build every value through `parse`, since no `Decimal` leaves `money.py`.
  Only a computed value is rounded, half-even, inside `money.py` (AMB-006).
- **An amount is above zero (D18).** `Amount.of` of the `Aed` 0.00 is `NotPositive`, so a credit of zero or minus 400
  cannot be built. A balance is a plain `Aed` or `Bhd` and may be negative. The one event that can move interest either
  way, an interest adjustment, carries a `Direction` beside its `Amount`.
- **No `Decimal` leaves `money.py`.** The split, the fee, and the interest are computed here: `split` divides, rounds
  each part down, and puts the remainder on the last, so BHD 10.000 in `InstalmentCount(3)` is 3.333, 3.333, 3.334
  (AMB-020); a split whose parts would fall below one minor unit returns `TooManyInstalments`, which the parser reports
  as the row's fault; `overdraft_fee` gives the brief's AED 25.00 and, for BHD, 25.00 × 0.10238257 rounded half-even to
  2.560 (AMB-027); `daily_interest` applies the brief's 0.04%. The renderer reads text through `digits` only. The
  constants are in [NUMBERS](../../../../NUMBERS.md), and a unit test pins each.

## Identifiers and Days

```text
ids.py
  Day               number: an int of at least 0                   Day.parse(text) -> Day | IdFault
  AccountId         "ACC-" and three digits                        AccountId.parse(text)
  AuthorizationId   "Auth-" and one or more letters or digits      AuthorizationId.parse(text)
  IncomingId        "E" and digits, such as E1                     IncomingId.parse(text)
  InstalmentId      parent IncomingId and n, such as E10-1
  FeeId             account, for_day, fired_day: FEE-001-D2@D5
  RefundId          account, for_day, fired_day: REFUND-001-D2@D6
  InterestId        account, for_day, fired_day: INT-001-D2@D5
  CapitalizationId  account, fired_day: CAP-001@D6
  EventId           the union of the six ID types                  EventId.parse(text), for a reversal's target
  InstalmentCount   n: an int of at least 2
  text(event_id)    EventId -> str                                 the marker, for the renderer
```

Each is a frozen dataclass whose constructor refuses an illegal value (D15): `Day(-1)`, `AccountId("ACC-1")`, and
`InstalmentCount(1)` raise, and each `parse` is the expected-failure path the stream reader uses. `EventId.parse`
accepts a fired marker as well as an incoming ID, since any accepted event may be reversed (AMB-035). Days compare and
count (`day.next()`, `day_1 <= day_2`), and a marker is built from its parts, never from a string.

## Accounts and Configuration

```text
config.py
  Account[M]        id: AccountId, opening: M                      its currency is M; there is no currency field
  LedgerConfig      accounts, first_day, last_day, capitalization_days
                    LedgerConfig.of(...) -> LedgerConfig | ConfigFault
  CHALLENGE         ACC-001 opening Aed 0.00, ACC-002 opening Bhd 0.000, Days 1 to 6, capitalization on Day 6
```

An account's currency is the type of its opening balance, so an AED account with a BHD opening cannot be written.
`LedgerConfig` refuses a first day after the last, two accounts with one ID, and a capitalization day outside the
window, in `__post_init__`, so `dataclasses.replace` checks a changed copy too. The window is configuration, not a
constant, so the known-weakness test can replay through Day 32 while the program always uses `CHALLENGE` (D6).

## Incoming Events

One frozen dataclass per kind, joined in the union `IncomingEvent`. Every kind carries `id: IncomingId`, `booked: Day`,
`account: AccountId`, and `value_day: Day`; `Amount` below means `Amount[Aed] | Amount[Bhd]`, built by the parser in the
account's currency.

| Kind            | Also carries                                             | Brief events |
| --------------- | -------------------------------------------------------- | ------------ |
| `Credit`        | `amount: Amount`, `posting: Whole \| Instalments(count)` | E1, E4, E10  |
| `Debit`         | `amount: Amount`                                         | E2, E7       |
| `Authorization` | `authorization: AuthorizationId`, `amount: Amount`       | E3, E8       |
| `Settlement`    | `authorization`, `amount: Amount`, `capture: Capture`    | E5, E6       |
| `Reversal`      | `reverses: EventId`                                      | E9           |

- **`Capture`** is the enum `FINAL` or `PARTIAL`, never a boolean; a settlement the stream does not mark is `FINAL`
  (AMB-013).
- **`posting`** is `Whole()` or `Instalments(InstalmentCount)`, so a count of one or zero cannot be written. A credit in
  instalments posts nothing itself: processing fires one `Instalment` per part, `E10-1` to `E10-3`, each carrying its
  part and the credit's value day (AMB-017, AMB-020).

## Fired Events

Joined in the union `FiredEvent`; each is created only by the ledger, and its ID type fixes its marker.

| Kind                 | Carries                          | ID                 | Effect                        |
| -------------------- | -------------------------------- | ------------------ | ----------------------------- |
| `Instalment`         | its part, the credit's value day | `E10-1`            | credits the part              |
| `Fee`                | the fee                          | `FEE-001-D2@D5`    | debits the fee                |
| `FeeRefund`          | the fee it refunds               | `REFUND-001-D2@D6` | credits the fee               |
| `InterestAccrual`    | an `Amount`                      | `INT-001-D1@D1`    | raises accrued interest       |
| `InterestAdjustment` | a `Direction` and an `Amount`    | `INT-001-D2@D5`    | moves accrued interest either |
| `Capitalization`     | an `Amount`                      | `CAP-001@D6`       | credits the accrued interest  |

An accrual's ID is for the day it fires and an adjustment's for an earlier day, and each constructor refuses the other
shape. Both are _interest events_: they add up to the accrued interest capitalization pays (AMB-005, AMB-007, C8).
Sources: instalments AMB-017 and AMB-020; fees AMB-002, AMB-003, and AMB-027; refunds AMB-004; capitalization AMB-023.

## The Log

```text
log.py
  Accepted             event: Credit | Debit | Reversal | FiredEvent, processed_day
  AuthorizationDecided event: Authorization, processed_day, decision: Decision (APPROVED or DECLINED)
  SettlementAccepted   event: Settlement, processed_day, effect: Captured(before, after) | ForcePosted
  Rejected             event: IncomingEvent, processed_day, reason: Rejection
  Duplicate            event: IncomingEvent, processed_day
  LogEntry             the union of the five
  Log                  tuple[LogEntry, ...]
  append(log, entry) -> Log                         a new tuple; nothing is ever changed or removed
```

Each kind of entry holds only the events that can have that outcome, so a credit cannot be approved and an authorization
cannot be force-posted. Every incoming event is appended with its outcome, and the five entry types are AMB-014's
outcomes: accepted (`Accepted`, `SettlementAccepted`), approved and declined (`AuthorizationDecided`), rejected
(`Rejected`), and duplicate (`Duplicate`, AMB-034). Only accepted entries and approved decisions count in any
aggregation. A fired event is always `Accepted`.

`Rejection` is a union, each member carrying what its text names:

| Rejection           | Report text                                          | Source  |
| ------------------- | ---------------------------------------------------- | ------- |
| `IdReused`          | `E1 refused: ID already used with different content` | AMB-034 |
| `AlreadyReversed`   | `E12 refused: E7 is already reversed by E9`          | AMB-028 |
| `ReversesAReversal` | `E12 refused: E9 is a reversal`                      | AMB-028 |
| `UnknownTarget`     | `E12 refused: E99 is not in the log`                 | AMB-035 |
| `MovedNoMoney`      | `E12 refused: E8 moved no money`                     | AMB-035 |
| `AlreadyUndone`     | `E12 refused: E10-1 is already undone by E11`        | AMB-035 |

The texts are chosen here (D22), since the brief states none.

## Balances

Pure functions over a log (D7). Each scans the whole log, and each returns the account's own currency type.

```text
balances.py
  closing(log, account: Account[M], day) -> M
      the opening plus the effect of every counted entry for the account with value day <= day
  holds(log, account, day) -> M
      the hold of every authorization in Approved or PartiallySettled whose value day is <= day
  available(log, account, day) -> M
      closing(log, account, day) - holds(log, account, day)
  accrued(log, account) -> M
      the account's interest events, net of their directions, less its capitalizations, each less its reversals
  interest_base(log, account, day) -> M
      closing(log, account, day) less any capitalization value-dated that day
```

An entry's effect on the ledger balance is plus its amount for a credit, an instalment, a refund, and a capitalization;
minus for a debit, a settlement, and a fee; and minus the effect of its target for a reversal, counted from the
reversal's own value day. An authorization and an interest event have no effect on the ledger balance. The same log
answers every question: a closing "as known at the end of Day 5" is `closing` over the log as it stood then, which
`Replay.log_at` returns (tech-docs 002).

`interest_base` exists because capitalization runs after interest on the same day (AMB-023): a day's interest is
computed before its capitalization posts, so a later re-evaluation of that day must not count it either, or accrued
interest would earn interest (AMB-007).

## The Authorization State Machine

A hand-written machine (D8), as the
[finite-state machine standard](../../../../repo-governance/development/quality/architecture/finite-state-machines.md)
requires for a lifecycle of three or more states. Each state is its own frozen dataclass carrying only its own data
(D17), so a declined authorization with a hold, or a settled one with a hold left, cannot be written.

```text
authorizations.py
  Approved(hold)                       hold: Amount
  PartiallySettled(captured, hold)     both Amount
  Settled(captured)                    captured: Amount
  Declined(requested)                  requested: Amount
  AuthorizationState                   the union of the four
  SettleFinal(amount) | SettlePartial(amount)          the trigger, from a settlement's capture and amount
  transition(state, trigger) -> AuthorizationState | NoTransition     the table, one match
  decide(log, event, today) -> Decision                               AMB-008, AMB-009, AMB-010
  AuthorizationRecord                  id, account, state, last_event
  records(log) -> tuple[AuthorizationRecord, ...]                     the machine replayed over the log
```

`transition` is the declared table: one `match` over the pair, each case a source, a trigger, a guard, and a target,
ending in `assert_never`. Guards compare the settlement's amount `a` with the hold `h`:

| From                     | Trigger            | Guard  | To                             |
| ------------------------ | ------------------ | ------ | ------------------------------ |
| `Approved(h)`            | `SettleFinal(a)`   | none   | `Settled(a)`                   |
| `Approved(h)`            | `SettlePartial(a)` | a < h  | `PartiallySettled(a, h − a)`   |
| `Approved(h)`            | `SettlePartial(a)` | a >= h | `Settled(a)`                   |
| `PartiallySettled(c, h)` | `SettleFinal(a)`   | none   | `Settled(c + a)`               |
| `PartiallySettled(c, h)` | `SettlePartial(a)` | a < h  | `PartiallySettled(c + a, h−a)` |
| `PartiallySettled(c, h)` | `SettlePartial(a)` | a >= h | `Settled(c + a)`               |
| `Settled`, `Declined`    | either             | none   | `NoTransition`                 |

```text
             available >= 0 after the hold              SettleFinal, or SettlePartial reaching the hold
  (arrives) ------------------------------> Approved -------------------------------------------> Settled
      |                                        |                                                     ^
      | available < 0 after the hold           | SettlePartial below the hold                        |
      v                                        v                                                     |
   Declined                             PartiallySettled --------------------------------------------+
                                          |          ^     SettleFinal, or SettlePartial reaching the hold
                                          +----------+
                                   SettlePartial below the hold
```

- **Deciding.** `decide` returns a `Decision`, which the `AuthorizationDecided` entry carries; `records` builds the
  state from it, `Approved(hold)` or `Declined(requested)`, both of the authorization's amount. An authorization is
  decided when it is processed, against the ledger balance value-dated up to today minus the holds already active, minus
  its own amount; approved at or above zero (AMB-008, AMB-009). Its hold counts from its own value day (AMB-010).
- **Settling.** A final settlement releases the whole remaining hold, whatever its amount; a partial one reduces the
  hold by its amount (AMB-013, AMB-030). A partial settlement that reaches the hold leaves nothing to keep, and a
  `PartiallySettled` hold must be above zero, so it settles.
- **No transition.** A settlement whose authorization is unknown, declined, or settled has no configured transition, so
  the state is unchanged and the ledger posts the settlement as a force-post (AMB-012, AMB-029).
- **Evidence.** A settlement's log entry records the transition it completed, `Captured(before, after)`, or
  `ForcePosted`, with its processed day and the settlement that caused it: the past-tense transition event and audit
  record the standard asks for. States are named in Python's class style, `PartiallySettled`, which the standard allows
  where the stack's idiom differs.

Every `match` over these unions ends in `case _: assert_never(value)`.
