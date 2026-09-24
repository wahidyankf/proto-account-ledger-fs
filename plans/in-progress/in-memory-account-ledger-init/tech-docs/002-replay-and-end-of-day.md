# Replay and End of Day

How the core turns a stream into one report a day. Every function here is pure: it takes a log and returns a new log, or
returns a value computed from one.

## The Driver

```text
replay.py
  replay(stream, config) -> Replay
  Replay          reports: tuple[DayReport, ...]       Day 0, then one per day of the window
                  logs: tuple[Log, ...]                the log as it stood at the end of each of those days
                  report(day) -> DayReport, log_at(day) -> Log
```

A test observes the replay at any day through `report` and `log_at`, and asks the balance functions of the domain model
about that log: Day 2's closing as known at the end of Day 5 is `closing(result.log_at(Day(5)), account, Day(2))`. To
stop after a given event, a test replays the stream up to it, which the support builder `through(stream, "E5")` gives.

The stream is replayed in the order it is listed (AMB-015). The driver keeps a current day, starting at the window's
first day, and a log, starting empty:

```text
for each event in the stream, in listed order:
    while event.booked > current day:
        close the current day; current day = current day.next()
    process the event on the current day             late events land here, on the day that is open
close every remaining day through the window's last day
```

A day closes on time and never waits for an event that might still come, so E10, listed after E9 and booked Day 5,
arrives once Day 5 has closed and is processed on Day 6 as a late event value-dated Day 5. In production the "close the
current day" call is a scheduler's; here the stream's booked days drive it.

## Processing an Incoming Event

`process(log, event, today) -> Log` appends exactly one entry for the event, plus the instalments a credit fires.

1. **Idempotency first (AMB-034).** If an entry for the event's ID is already in the log, an event equal to the first in
   every field, the booked day included, is appended as `Duplicate`; any other is appended as `Rejected(IdReused)`.
   Neither moves a balance. The event ID is the idempotency key for every event, incoming or fired.
2. **By kind:**
   - `Credit`, `Debit`: appended as `Accepted`. A credit posted in `Instalments` also fires its `Instalment` events, in
     order, each `Accepted`, and posts nothing itself.
   - `Authorization`: appended as `AuthorizationDecided`, approved or declined by `decide` (AMB-009).
   - `Settlement`: appended as `SettlementAccepted`, always. If its authorization is known and `transition` returns a
     state, the effect is `Captured(before, after)`; otherwise it is `ForcePosted` (AMB-012, AMB-029, AMB-030).
   - `Reversal`: the target is the first entry with the reversed ID (AMB-028, AMB-035). Checked in this order, it is
     appended as `Rejected(UnknownTarget)` when there is none; `Rejected(ReversesAReversal)` when the target is a
     reversal; `Rejected(MovedNoMoney)` when the target is an authorization or a rejected entry;
     `Rejected(AlreadyReversed)` when an accepted reversal of the same target exists; `Rejected(AlreadyUndone)` when the
     target's money is already undone another way, naming the part and what undid it: an instalment of a reversed
     credit, the reversed instalment of a credit, or a fee's refund; otherwise `Accepted`.

A reversal takes out only what its target moved: a settlement's debit but not its transition, and for a credit in
instalments, every instalment. A row the ledger cannot represent never reaches `process`: the stream reader refuses it
first (AMB-014, D21).

## Closing a Day

`close_day(log, day, config) -> Log` runs three steps in this order (AMB-023) and returns the log with every event they
fire. A step that moves nothing fires nothing. The ledger never fires a marker already in the log, which is AMB-034's
rule applied to its own events.

### Step 1 — Fee Re-Evaluation

For each account, for each day `d` from the window's first day through today, in order (AMB-002, AMB-016):

- if `closing(log, account, d)` is below zero and `d` has no fee in force, fire `Fee` for `d`, value-dated today, of
  `overdraft_fee` in the account's currency (AMB-003, AMB-027);
- if it is at or above zero and `d` has a fee in force, fire `FeeRefund` for that fee, value-dated today (AMB-004).

A fee is in force until a refund names it or a reversal undoes it, and again once a reversal undoes that refund; a fee
reversed while its day is still negative is therefore charged again, under a marker for today (AMB-035). Because the
loop reads the log as it grows, a fee fired for an earlier day, value-dated today, is counted when `d` reaches today
(AMB-011). One fee per day per account is in force at a time.

### Step 2 — Interest

For each account, for each day `d` from the first day through today:

```text
target = daily_interest(interest_base(log, account, d))       zero unless that base is above zero
fired  = the account's interest events for d, net of their directions and reversals
if target != fired:
    if d is today: fire an InterestAccrual of target − fired
    else:          fire an InterestAdjustment, UP or DOWN, of the difference's size
```

The base already counts fees, so interest accrues on the balance the fee rule leaves (AMB-023), and it leaves out the
capitalization dated `d`, which posts after `d`'s interest. Interest events do not move the ledger balance, so nothing
compounds before capitalization (AMB-007). A day's first accrual is never negative, since nothing is fired for today
before its close; every later correction of it is an adjustment. A reversed interest event drops out of `fired`, so the
next close fires it again as an adjustment (AMB-035).

### Step 3 — Capitalization

On a day in `config.capitalization_days` only, for each account whose `accrued(log, account)` is above zero, fire
`Capitalization` for that amount, value-dated today. It is the sum of the interest events, so the rounded accruals sum
exactly to the capitalized total, and no remainder can exist (C8). A reversed capitalization returns its interest to
`accrued`, to be paid on the next capitalization day (AMB-035).

## Checking the Algorithm Against MOVEMENT

A walk of ACC-001 through the three moments that decide most figures. Every value is MOVEMENT's.

- **End of Day 4.** The log holds E1 to E6. Closings by value day: Day 1 250.00, Day 2 250.00, Day 3 650.00, Day 4
  285.00. Step 2 fires `INT-001-D4@D4`, 0.11.
- **End of Day 5.** E7, value-dated Day 2, and E8, declined, join the log. Day 2 closes at −370.00, Day 3 at 30.00, and
  Day 4 at −335.00, so step 1 fires `FEE-001-D2@D5`, `FEE-001-D4@D5`, and `FEE-001-D5@D5`, and Day 5 closes at −410.00
  once they count. Step 2 fires adjustments DOWN of 0.10, 0.25 (Day 3 now earns 0.01), and 0.11, and no accrual.
- **End of Day 6.** E9, value-dated Day 2, and E10-1 to E10-3 join the log. Days 2 to 4 close at 250.00, 650.00, and
  285.00 again, and Day 5 at 210.00. Step 1 fires the three refunds; step 2 fires adjustments UP of 0.10, 0.25, 0.11,
  and 0.08 for Days 2 to 5 and accrues 0.11 for Day 6 on 285.00; step 3 fires `CAP-001@D6`, 0.76, and Day 6 closes at
  285.76.

Day 5 closes at 210.00 on Day 6, not 285.00, because the three fees are value-dated Day 5 and their refunds Day 6 (C6).
Its interest is 210.00 × 0.0004 = 0.084 → 0.08.

## The Day Report

```text
report.py
  DayReport       day, events processed, end-of-day rows, restated closings, per-account closing, available,
                  authorizations, and errors; each per-account field a frozen mapping from AccountId to its money
  report(log_before, log_after, day, config, earlier) -> DayReport
```

- **Events processed.** Every incoming entry processed that day, in log order, whatever its outcome, with the
  instalments it fired.
- **End-of-day rows.** Each step's fired events in the order fired, plus a row for a step that fired nothing: "no fee
  assessed or refunded" when step 1 fired nothing, "no new fee assessed" when it fired only refunds, "no interest
  accrued" for an account whose step 2 fired no accrual for today, and "no interest capitalized" for an account step 3
  paid nothing on a capitalization day. Step 3 has no row on any other day.
- **Restated closings (AMB-022).** For each earlier day whose closing now differs from the closing last reported for it,
  originally or as a restatement, one row; an account whose closing for that day did not change shows `-`.
- **Authorizations (AMB-019, AMB-025).** Every authorization known by the end of the day, with its state then, in the
  order first seen.
- **Errors.** Each `Rejected` entry processed that day, by account, in log order; `none` when there are none. A
  duplicate is not an error.

Day 0 is the opening state: no events, no end-of-day rows, and the opening balances (AMB-001).
