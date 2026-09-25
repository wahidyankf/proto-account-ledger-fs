# Code Walkthrough

This page follows one run of the ledger through its functions, in the order they run, so you can read the code with the
page beside it. The [architecture](../../specs/apps/account-ledger/cli/architecture.md) is the canonical view of the
components and their boundaries; this page goes one level down, to the functions and the values they pass. Every rule it
meets is decided in [AMBIGUITIES](../../AMBIGUITIES.md), cited by its ID, and every figure is the brief's stream as
[OUTPUT_TARGET](../../OUTPUT_TARGET.md) prints it. The [Python crash course](python-crash-course.md) explains the
language features the code uses, and [fees and interest](fees-and-interest.md) works through the end-of-day arithmetic.

Each diagram is a sequence diagram: one column per object, time running down. A solid arrow `---->` is a call, a dotted
arrow `<....` its return, and `|--+` a call an object makes on itself. The numbers on the arrows match the list under
each diagram.

## Three Rules That Explain the Code

1. **The Ledger stores only the log.** It stores no balance, no hold, and no authorization state. It keeps one
   append-only log of entries, and every figure is worked out from that log each time it is asked for (AMB-004,
   AMB-024). No stored figure is ever edited: after a backdated event, the next closing asked for is summed again with
   the event in it, and the close generates new events, refunds and interest adjustments, for what it changed. The
   application also remembers the closings each report printed, to detect restatements; that is a record of output, not
   a second source of balances.
2. **Nothing is changed in place.** Every value is a frozen dataclass, a union of them, or an enum, as the
   [architecture](../../specs/apps/account-ledger/cli/architecture.md#l4--code) says; `Ok` and `Err` are written by hand
   to the same effect. An operation returns a new object: `Ledger._append` returns a new `Ledger` with a longer log, and
   the stream's `_ProcessingState` is copied with `dataclasses.replace`. So a value you hold never changes under you.
3. **A refused event is a success, not a failure.** When the ledger refuses an event, such as a second reversal of E7,
   it returns `Ok` with an `EventRejected` entry for the log (AMB-014), and the report prints it on that day's Errors
   row. `Err` is kept for two things only: input the ledger cannot read, a `SourceFault`, which stops the run with exit
   status 2, and a fault only a bug can cause, an `InternalFault`. A refusal is the ledger's rule working; an `Err` is
   the run failing.

Two words recur below. An **event** is what happened: an incoming `Credit`, `Debit`, `Authorization`, `Settlement`, or
`Reversal` from the stream, or a `Fee`, `FeeRefund`, `InterestAccrual`, `InterestAdjustment`, `Capitalization`, or
`Instalment` the ledger generates, all in [`events.py`][events]. An **entry** is the log's record of one event, in
[`domain_events.py`][domain-events]: `DebitPosted`, `FeeCharged`, `EventRejected`, and the rest, each holding the event
and the day it was processed, and, where it has them, a refusal's reason or a settlement's states before and after. So a
day is charged a `Fee` event, and the log records it as a `FeeCharged` entry.

## Where the Code Lives

The package is [`src/account_ledger`][pkg], laid out in hexagonal layers, each importing only the layers inside it:

| Layer       | Folder                   | Holds                                                             |
| ----------- | ------------------------ | ----------------------------------------------------------------- |
| shell       | `cli.py`, `challenge.py` | the entry point, every real effect, and the brief's configuration |
| adapters    | `adapters/`              | the CSV file read into events; the reports written as text        |
| application | `application/`           | the one use case, its ports, the stream loop, and the day report  |
| Ledger      | `domain/ledger/`         | the one log of every account, and what spans accounts             |
| aggregate   | `domain/account/`        | the Account aggregate: every rule about one account               |
| values      | `domain/model/`          | money, IDs, days, events, and configuration; no rule decides here |
| common      | `common/`                | `Result`, `Ok`, and `Err`; no ledger meaning                      |

A `ruff.toml` in each folder refuses an import that points outwards, so the domain cannot import the adapters, and a
lint run proves it. The architecture draws the layers as a diagram in its
[L3 section](../../specs/apps/account-ledger/cli/architecture.md#l3--components).

## One Run, End to End

`npx nx run account-ledger-cli:run` runs `python -m account_ledger streams/challenge.csv`, and this is what happens:

```text
       main              run_cli           LedgerRun        CsvFileSource     IncomingStream     TextReportSink
         |                  |                  |                  |                  |                  |
         | 1 run_cli        |                  |                  |                  |                  |
         |----------------->|                  |                  |                  |                  |
         |                  | 2 run            |                  |                  |                  |
         |                  |----------------->|                  |                  |                  |
         |                  |                  | 3 read_events    |                  |                  |
         |                  |                  |----------------->|                  |                  |
         |                  |                  |                  |--+ 4 read_text, parse               |
         |                  |                  |                  |<-+               |                  |
         |                  |                  | 5 Ok(stream)     |                  |                  |
         |                  |                  |<.................|                  |                  |
         |                  |                  | 6 process        |                  |                  |
         |                  |                  |------------------------------------>|                  |
         |                  |                  |                  |                  |--+ 7 events, closes
         |                  |                  |                  |                  |<-+               |
         |                  |                  | 8 Ok(processed)  |                  |                  |
         |                  |                  |<....................................|                  |
         |                  |                  | 9 publish(reports)                  |                  |
         |                  |                  |------------------------------------------------------->|
         |                  |                  |                  |                  |                  |--+ 10 render
         |                  |                  |                  |                  |                  |<-+
         |                  | 11 Ok(None)      |                  |                  |                  |
         |                  |<.................|                  |                  |                  |
         | 12 status 0      |                  |                  |                  |                  |
         |<.................|                  |                  |                  |                  |
         |                  |                  |                  |                  |                  |
```

1. [`__main__.py`][main-module] calls `main` in [`cli.py`][cli]. `main` switches standard output and error to UTF-8,
   because the report prints `−`, and calls `run_cli` with every real effect as an argument: the arguments, the file
   reader `read_file`, `sys.stdout`, `sys.stderr`, and `LedgerRun(CHALLENGE)`.
2. `run_cli`, through `_run_file`, checks there is exactly one argument, builds the two adapters,
   `CsvFileSource(path, read_text)` and `TextReportSink(out)`, and calls `LedgerRun.run` in [`run.py`][run].
3. `LedgerRun.run` asks the source for the events: `CsvFileSource.read_events(config)` in [`csv_file.py`][csv].
4. The source reads the file through the reader it was given, then `CsvFileSource.parse` checks the header and turns
   each row into an event through `_parse_row`. Every cell is built by its own type's `parse`, such as `Day.parse` or
   `Aed.parse`, so a bad cell is refused by the type that would have held it.
5. It returns `Ok(IncomingStream)`, or `Err(SourceFault)` with the line number of the first bad row.
6. `LedgerRun.run` calls `IncomingStream.process(config)` in [`stream.py`][stream].
7. The stream processes each event on the current day and closes each day as the booked days advance; the next sections
   open this step.
8. It returns `Ok(ProcessedStream)`: the Day 0 report, one report per day of the window, and the log as it stood at each
   close.
9. `LedgerRun.run` hands the reports to `TextReportSink.publish` in [`text_report.py`][text-report].
10. The sink renders every report as text and writes it in one write and one flush, so a closed pipe is caught inside
    `run_cli` rather than at exit.
11. `LedgerRun.run` returns `Ok(None)`.
12. `run_cli` returns 0, and `main` exits with it. Every other status is on the [faults](#faults-and-exit-statuses)
    diagram below.

Nothing is printed until every day is processed: the first `Err` returns before `publish`, so a run prints the whole
report or none of it.

## When a Day Closes

`IncomingStream.process` has one loop, over the events in the order the file lists them (AMB-015). Before each event,
`_ProcessingState.close_days_before(event.booked)` closes every open day earlier than the event's booked day, so an
event booked later is the signal that the current day is over. An event booked earlier than the open day is late, and is
processed on the open day. Once the events run out, `close_days_before(None)` closes every day left in the window, and
no day closes after the window's last (AMB-001).

So each day moves through three states, and a closed day can still be restated:

```text
+----------+  the previous day closes    +--------+  an event booked later arrives,  +----------+
| not open | -------------------------> |  open  | -------------------------------> |  closed  |
+----------+                            +--------+  or the events run out           +----------+
                                          |    ^                                       |    ^
                                          +----+                                       +----+
                              an event booked on or before it              a late event changes its closing:
                              is processed on it                           a later report restates it
```

A closed day is never reopened: no event is processed on it again and its report is never reprinted. A late event
value-dated on it is processed on the open day, and changes its closing only in the sums later reports make.

This is the brief's stream through that loop:

```text
open day   event   booked   closed before it is processed   processed on
--------   -----   ------   -----------------------------   ------------
   1        E1       1      -                               Day 1
   1        E2       1      -                               Day 1
   1        E3       2      Day 1                           Day 2
   2        E4       3      Day 2                           Day 3
   3        E5       4      Day 3                           Day 4
   4        E6       4      -                               Day 4
   4        E7       5      Day 4                           Day 5
   5        E8       5      -                               Day 5
   5        E9       6      Day 5                           Day 6
   6        E10      5      -   (booked Day 5, so late)     Day 6
   6        end      -      Day 6, the window's last        -
```

E10 is booked Day 5 but listed after E9, which opened Day 6, so it is processed on Day 6 as a late event value-dated Day
5: Day 5's report shows ACC-002 at 0.000, and Day 6's restates its Day 5 to 10.000 (AMB-015). Before the loop,
`DayReport.build(ledger, Day(0), …)` builds the Day 0 report, the opening balances, which no close produces.

## One Incoming Event

`_ProcessingState.process_event` hands the event to `Ledger.process_event(event, today)` in [`ledger.py`][ledger], which
checks what spans accounts on the whole log, then asks the event's own account to decide:

```text
       _ProcessingState                    Ledger                        EventLog                       AccountIn
               |                              |                              |                              |
               | 1 process_event(event, day)  |                              |                              |
               |----------------------------->|                              |                              |
               |                              | 2 find_first_entry(id)       |                              |
               |                              |----------------------------->|                              |
               |                              | entry or None                |                              |
               |                              |<.............................|                              |
               |                              |--+ 3 _check_target_account   |                              |
               |                              |<-+                           |                              |
               |                              |--+ 4 _check_authorization_id |                              |
               |                              |<-+                           |                              |
               |                              |--+ 5 _find_opening           |                              |
               |                              |<-+                           |                              |
               |                              | 6 select(account)            |                              |
               |                              |----------------------------->|                              |
               |                              | the account's entries        |                              |
               |                              |<.............................|                              |
               |                              | 7 decide_event(event, day)   |                              |
               |                              |------------------------------------------------------------>|
               |                              | Ok(entries)                  |                              |
               |                              |<............................................................|
               |                              |--+ 8 _append(*entries)       |                              |
               |                              |<-+                           |                              |
               | 9 Ok(new Ledger)             |                              |                              |
               |<.............................|                              |                              |
               |                              |                              |                              |
```

1. The stream passes the event and the open day, `today`, which becomes the entry's `processed_day`.
2. `EventLog.find_first_entry(event.id)` in [`event_log.py`][event-log] looks for the ID in the whole log. The event ID
   is the idempotency key (AMB-034): an entry with an equal event gives `DuplicateIgnored`, no effect and no error; one
   with a different event, the booked day included, gives `EventRejected(IdReused())`.
3. A reversal whose target is in the log on another account is refused as `TargetOnAnotherAccount` (AMB-036).
4. An authorization whose authorization ID an approved or declined authorization already holds, on any account, is
   refused as `AuthorizationIdReused` (AMB-038).
5. `_find_opening` looks the account up in the configuration. An account the ledger does not hold is
   `Err(UnknownAccount)`, an internal fault: the CSV reader already refuses such a row, so only a bug reaches it.
6. `find_account(opening)` builds the Account aggregate, `AccountIn(id, opening balance, log.select(id))`: the account
   with its own entries only, so no rule can read another account's.
7. `AccountIn.decide_event(event, today)` in [`account.py`][account] matches on the event's kind and returns the entries
   it records.
8. `_append` adds the entries at the end of the log.
9. The new `Ledger` goes back to the stream, which keeps it.

Steps 2 to 4 append their entry and return at once; only an event that passes them reaches its account. What each kind
records, from `decide_event`:

| Event         | Entries recorded                                           | Decided by                    |
| ------------- | ---------------------------------------------------------- | ----------------------------- |
| Credit        | `CreditPosted`, then one `InstalmentPosted` per instalment | `_generate_instalments`       |
| Debit         | `DebitPosted`                                              | -                             |
| Authorization | `AuthorizationApproved` or `AuthorizationDeclined`         | `_decide_authorization_entry` |
| Settlement    | `SettlementApplied`, with both states, or a force-post     | `_decide_settlement_entry`    |
| Reversal      | `ReversalPosted`, or `EventRejected` with its reason       | `_decide_reversal`            |

The kinds of entry, one per fact the ledger records, are in [`domain_events.py`][domain-events]; the reasons for a
refusal are in [`rejections.py`][rejections].

## How a Balance Is Worked Out

Every balance comes from two methods of `AccountIn`, and both read the account's own entries:

```text
compute_closing(day)   = opening + every effect whose value date is on or before day
compute_available(day) = compute_closing(day) - sum_holds(day)
sum_holds(day)         = the hold of each Approved or PartiallySettled authorization value-dated on or before day
```

`_list_counted_events` skips the entries that move no money: an approval, a decline, a refusal, and a duplicate. Then
`_list_moved_amounts` gives each counted event its signed effect:

| Event                                                   | Effect on the ledger balance                             |
| ------------------------------------------------------- | -------------------------------------------------------- |
| Credit posted whole, instalment, refund, capitalization | plus its amount                                          |
| Credit in instalments                                   | nothing itself; its instalments carry the money          |
| Debit, settlement, fee                                  | minus its amount                                         |
| Authorization                                           | nothing: a hold moves the available balance only         |
| Interest accrual or adjustment                          | nothing until capitalized (AMB-007)                      |
| Reversal                                                | minus whatever its target moved, from its own value date |

So a closing is a sum filtered by value date, never a stored figure. When E7 arrives on Day 5 value-dated Day 2, the
next `compute_closing(Day(2))` includes its −620.00, and Day 2 reads −370.00. When E9 reverses it, E9's effect is
+620.00 from Day 2, and Day 2 reads 250.00 again. Nothing was edited: E7 and E9 are both still in the log.

## An Authorization

E3 asks for a hold of AED 200.00 on Day 2:

```text
             Ledger                         AccountIn                      Aed or Bhd
                |                               |                               |
                | 1 decide_event(E3, Day 2)     |                               |
                |------------------------------>|                               |
                |                               |--+ 2 compute_closing(Day 2)   |
                |                               |<-+                            |
                |                               |--+ 3 sum_holds(Day 2)         |
                |                               |<-+                            |
                |                               | 4 available.is_below(200.00)  |
                |                               |------------------------------>|
                |                               | Ok(False)                     |
                |                               |<..............................|
                | 5 AuthorizationApproved       |                               |
                |<..............................|                               |
                |                               |                               |
```

1. `decide_event` matches `Authorization` and calls `_decide_authorization_entry`, which decides on arrival, against the
   balances as they stand at that moment (AMB-009).
2. `compute_available(Day 2)` first sums the closing: 250.00. The balance includes every event value-dated on or before
   the day, so on Day 5 E8 sees E7 (AMB-008).
3. It subtracts `sum_holds(Day 2)`: no hold yet, so 250.00 is available.
4. `Aed.is_below(amount)` in [`money.py`][money] asks whether 250.00 is below 200.00. The brief's rule, available at or
   above zero after the hold, is the same test as available not below the amount.
5. It is not, so the entry is `AuthorizationApproved`, and from Day 2, E3's value date, the hold of 200.00 counts in
   `sum_holds` (AMB-010): Day 2 closes at 250.00 with 50.00 available.

E8, for 90.00 on Day 5, meets a closing of −335.00, since E7 is in and the day's fees are not yet generated (AMB-016),
and no hold, since Auth-A settled. −335.00 is below 90.00, so it is `AuthorizationDeclined`: the −425.00 the brief's
rule would leave is −335.00 − 90.00. A decline is an authorization state, printed with the others, not an error
(AMB-019), and it holds nothing.

## A Settlement

E5 settles Auth-A for AED 185.00 on Day 4:

```text
           Ledger                     AccountIn               apply_settlement                AmountIn
              |                           |                           |                           |
              | 1 decide_event(E5, Day 4) |                           |                           |
              |-------------------------->|                           |                           |
              |                           |--+ 2 _find_record(E5)     |                           |
              |                           |<-+                        |                           |
              |                           | 3 (Approved, FINAL, 185.00)                           |
              |                           |-------------------------->|                           |
              |                           |                           | 4 hold.take(185.00)       |
              |                           |                           |-------------------------->|
              |                           |                           | Ok(15.00)                 |
              |                           |                           |<..........................|
              |                           |                           |--+ 5 match the triple     |
              |                           |                           |<-+                        |
              |                           | Ok(Settled(185.00))       |                           |
              |                           |<..........................|                           |
              | 6 SettlementApplied       |                           |                           |
              |<..........................|                           |                           |
              |                           |                           |                           |
```

1. `decide_event` matches `Settlement` and calls `_decide_settlement_entry`.
2. `_find_record` looks through `list_records`, which replays the account's authorization entries into an
   `AuthorizationRecord` for each: the event that opened it and its state now. Auth-A is `Approved(hold=200.00)`.
3. `_decide_effect` calls `apply_settlement` in [`authorizations.py`][authorizations] with the state, the settlement's
   kind, and its amount. A settlement whose `final` cell is blank or `yes` is final; only `no` makes it partial
   (AMB-013).
4. `_take_from_hold` asks the hold for what the settlement leaves: `AmountIn.take` returns the rest, 15.00, or `None`
   when the settlement reaches or passes the hold.
5. One `match` over the triple (state, kind, what is left) is the whole state machine.
6. `Approved` with a final settlement becomes `Settled(185.00)`: 185.00 is debited, and the whole hold is released, the
   unused 15.00 included. The entry `SettlementApplied` keeps both states, so `list_records` can replay it.

As a state machine, with the settlements that move an authorization between its four states:

```text
                         available not below the amount
  (arrives) ------------------------------------------------> Approved(hold)
      |                                                        |          |
      | available below the amount                             |          | partial, leaving a rest
      v                                                        |          v
  Declined(requested) --+                                      |    PartiallySettled(settled, hold) --+
      ^                 | any settlement:                      |          |          ^                | partial,
      +-----------------+ force-posted                         |          |          +----------------+ leaving a rest
                                                               |          |
                                   final, or reaching the hold |          | final, or reaching the hold
                                                               v          v
                                                            Settled(settled) --+
                                                               ^               | any later settlement:
                                                               +---------------+ force-posted

  A hold in Approved or PartiallySettled that no settlement reaches stays there, holding, forever (AMB-018).
```

Every case of that `match`, which the architecture's
[state diagram](../../specs/apps/account-ledger/cli/architecture.md#l4--code) draws:

| State before            | Kind    | Left of the hold | State after                     | Entry                   |
| ----------------------- | ------- | ---------------- | ------------------------------- | ----------------------- |
| `Approved`              | final   | anything         | `Settled`                       | `SettlementApplied`     |
| `Approved`              | partial | a rest           | `PartiallySettled`              | `SettlementApplied`     |
| `Approved`              | partial | nothing          | `Settled`                       | `SettlementApplied`     |
| `PartiallySettled`      | final   | anything         | `Settled`, for the sum          | `SettlementApplied`     |
| `PartiallySettled`      | partial | a rest           | `PartiallySettled`, for the sum | `SettlementApplied`     |
| `PartiallySettled`      | partial | nothing          | `Settled`, for the sum          | `SettlementApplied`     |
| `Settled` or `Declined` | any     | -                | none: `CannotSettle`            | `SettlementForcePosted` |

Three settlements are force-posted: they debit their amount and release no hold. E6, whose Auth-Z the account has never
seen, finds no record (AMB-012); one against a declined or already settled authorization meets `CannotSettle` (AMB-029).
A settlement above its hold is not force-posted: `take` returns `None`, so it settles and debits its full amount
(AMB-030).

## A Reversal

A reversal passes a ladder of checks, in this order, and the first that fails refuses it:

```text
Ledger.process_event
  |- the event ID is already in the log ...................... DuplicateIgnored or IdReused    AMB-034
  |- the target is in the log, on another account ............ TargetOnAnotherAccount          AMB-036
AccountIn._check_reversal
  |- the target is not in the account's log .................. UnknownTarget                   AMB-035
  |- the target is itself a reversal ......................... ReversesAReversal               AMB-028
  |- the target moved no money (an authorization, a refusal) . MovedNoMoney                    AMB-035
  |- a posted reversal already names the target .............. AlreadyReversed                 AMB-028
  |- the reversal is value-dated before its target ........... DatedBeforeTarget               AMB-037
  |- part of the target's money is undone another way ........ AlreadyUndone                   AMB-035
  '- none of these ........................................... ReversalPosted
```

`_decide_reversal` turns an `Err(rejection)` from `_check_reversal` into `EventRejected(reversal, today, rejection)`,
and `Ok` into `ReversalPosted`. The last check, `_check_undoing`, is what "undone at most once" means: an instalment
whose credit is reversed, a credit one of whose instalments is reversed, and a fee already refunded cannot be reversed
again.

A posted reversal edits nothing. `_list_moved_amounts` gives it the negation of what its target moved, from the
reversal's own value date; for a credit in instalments, that is every instalment. E9 targets E7, a debit of 620.00, and
is value-dated Day 2, as E7 is, so it counts +620.00 from Day 2. What follows is the next close's work: the fee step
finds Days 2, 4, and 5 no longer negative and refunds their fees (AMB-004), and the interest step adjusts the interest
of every day whose closing changed (AMB-005).

## A Day's Close

`_ProcessingState.close_current_day` closes the open day, here Day 6, the capitalization day:

```text
   _ProcessingState            Ledger                AccountIn              DayReport          ReportedClosings
           |                      |                      |                      |                      |
           | 1 close_day(Day 6)   |                      |                      |                      |
           |--------------------->|                      |                      |                      |
           |                      | 2 assess_fees        |                      |                      |
           |                      |--------------------->|                      |                      |
           |                      | fees, refunds        |                      |                      |
           |                      |<.....................|                      |                      |
           |                      | 3 accrue_interest    |                      |                      |
           |                      |--------------------->|                      |                      |
           |                      | accruals, adjustments|                      |                      |
           |                      |<.....................|                      |                      |
           |                      | 4 capitalize_interest|                      |                      |
           |                      |--------------------->|                      |                      |
           |                      | capitalization       |                      |                      |
           |                      |<.....................|                      |                      |
           | 5 Ok(ledger)         |                      |                      |                      |
           |<.....................|                      |                      |                      |
           | 6 build(ledger, day, reported)              |                      |                      |
           |------------------------------------------------------------------->|                      |
           |                      |                      |                      | 7 list_days_before   |
           |                      |                      |                      |--------------------->|
           |                      |                      |                      | Days 0 to 5          |
           |                      |                      |                      |<.....................|
           | 8 Ok(report)         |                      |                      |                      |
           |<...................................................................|                      |
           | 9 update(report)     |                      |                      |                      |
           |------------------------------------------------------------------------------------------>|
           |--+ 10 day.advance()  |                      |                      |                      |
           |<-+                   |                      |                      |                      |
           |                      |                      |                      |                      |
```

1. `Ledger.close_day(today)` builds the day's steps and runs each on every account, in the configured order, before the
   next step (AMB-023). Each step reads the ledger as the previous one left it.
2. Step 1, `AccountIn.assess_fees(today, first_day)`, walks every day from the first to today. A day that closes
   negative with no fee in force is charged a `Fee`, value-dated today and naming the day it is for (AMB-002, AMB-003);
   a day that closes at or above zero with a fee in force has it refunded by a `FeeRefund`, value-dated today (AMB-004).
3. Step 2, `AccountIn.accrue_interest(today, first_day)`, walks the same days. For each, it works out the interest the
   day's closing earns and subtracts what was already generated for it; a difference is today's `InterestAccrual`, or an
   `InterestAdjustment` for an earlier day, both value-dated today (AMB-005).
4. Step 3, `AccountIn.capitalize_interest(today)`, runs only on a capitalization day, Day 6 in this configuration. It
   credits the account's accrued interest as one `Capitalization`, value-dated today.
5. The ledger, with the day's generated entries, goes back to the stream.
6. `DayReport.build(ledger, day, reported)` in [`report.py`][report] reads the day off the ledger: the events processed
   that day, the end-of-day rows, each account's closing and available balance, every authorization with its state, and
   the day's errors. It writes nothing back.
7. For each day already reported, it asks `ReportedClosings` for the closing printed last and compares it with the
   closing now; a day that differs becomes a `Restatement` row (AMB-022).
8. The report goes back to the stream.
9. `ReportedClosings.update(report)` records what this report printed, the restatements included, so a day is restated
   again only if it changes again.
10. The next day opens.

The walk over every day in steps 1 and 2, with the figures each produces, is in
[fees and interest](fees-and-interest.md).

## The Report as Text

`DayReport` is data; [`text_report.py`][text-report] turns it into text. `TextReportSink.render` joins each day's
`_format_day`: a banner between two rules of 120 `=`, then three blocks, Events processed, EOD applied, and Closing
summary, each a box drawn by `_format_table` with every column as wide as its widest cell. A negative amount prints `−`,
U+2212. Each `Rejection` has its own sentence in `_format_reason`, such as `E7 is already reversed by E9`, and
`_format_refusal` puts the event's ID in front: `E12 refused: E7 is already reversed by E9`.

The end-to-end test `test_the_brief_stream_prints_output_target`, in [`tests/e2e/test_program.py`][e2e], runs the
program as a separate process and compares its standard output with the fenced text in OUTPUT_TARGET, line by line. Any
change to a figure or to the layout fails it.

## Faults and Exit Statuses

Every way a run can end, where it starts, and what the process exits with; the
[application README](../../apps/account-ledger-cli/README.md#exit-statuses) publishes the same statuses:

```text
where it starts                          what carries it            run_cli prints to stderr           exit
---------------------------------------  -------------------------  ---------------------------------  ----
every event processed                    Ok(None)                   nothing; the report is on stdout      0
no argument, or more than one            _run_file checks argv      usage: account-ledger-cli ...         2
the file cannot be read or decoded       read_file -> SourceFault   error: cannot read PATH: REASON       2
a malformed row                          StreamError -> SourceFault error: line N: ...                    2
two currencies meet in one sum           CurrencyMismatch           error: internal: ...                  2
an event on an unconfigured account      UnknownAccount             error: internal: ...                  2
any other exception                      run_cli's last except      error: internal failure: TYPE         2
standard output closed early             BrokenPipeError            nothing                             141
an interrupt                             KeyboardInterrupt          nothing                             130
```

A refused event is on none of these lines: it is an entry in the log, and the run exits 0. The two internal faults,
`CurrencyMismatch` and `UnknownAccount`, are the `InternalFault` union in `ledger.py`; each account keeps every effect
in its own currency and the reader refuses an unconfigured account, so no input reaches either.

## Where a Change Would Go

These are the places the code would change for the changes a reviewer is likely to ask about. None of them is built.

- **Hold expiry, the known weakness** (AMB-018). A new end-of-day step in `Ledger.close_day`, before the fee step, would
  ask each account for approved or partially settled holds older than a lifetime and record a new entry kind, such as a
  hold expiry, in `domain_events.py`. `list_records` would read that entry as a new state with no hold, so `sum_holds`
  drops it, and `apply_settlement`'s table would treat a settlement after expiry as a force-post, as the
  [trade-offs](architecture-trade-offs.md#authorization-lifecycle) mandate. The strict expected failure,
  `test_known_weakness_an_unsettled_hold_never_expires`, would then pass, turn the run red as `XPASS(strict)`, and lose
  its marker. [Fix the known weakness](../how-to/fix-the-known-weakness.md) walks through this change, built and run on
  a scratch copy outside the repository's code.
- **A third currency.** A class beside `Aed` and `Bhd` in `money.py`, with its own `CURRENCY`, `PLACES`, and methods,
  and its fee rule; the constraint `(Aed, Bhd)` on each generic type in `money.py`, `config.py`, and `account.py`
  widened; the unions `Money`, `Amount`, `Account`, and `AccountOpening` widened; and the two places that branch on the
  currency, `Ledger.find_account` with `is_aed` and `_parse_amount` in `csv_file.py`, given a third branch. pyright then
  reports every `match` that misses the new type.
- **A new reason to refuse an event.** A class in `rejections.py`, added to the `Rejection` union, returned by the check
  that finds it, and given its sentence in `_format_reason`; the [how-to](../how-to/add-a-refusal-test-first.md) walks
  through one.
- **The projection that defers the cost at scale.** `compute_closing` scans every entry for every day asked; a running
  total of each account's effects by value day, kept beside its entries, would answer it as a lookup, with no rule
  changed ([trade-offs](architecture-trade-offs.md#append-only-at-scale)).

[pkg]: ../../apps/account-ledger-cli/src/account_ledger/__init__.py
[main-module]: ../../apps/account-ledger-cli/src/account_ledger/__main__.py
[cli]: ../../apps/account-ledger-cli/src/account_ledger/cli.py
[run]: ../../apps/account-ledger-cli/src/account_ledger/application/run.py
[csv]: ../../apps/account-ledger-cli/src/account_ledger/adapters/csv_file.py
[stream]: ../../apps/account-ledger-cli/src/account_ledger/application/stream.py
[text-report]: ../../apps/account-ledger-cli/src/account_ledger/adapters/text_report.py
[ledger]: ../../apps/account-ledger-cli/src/account_ledger/domain/ledger/ledger.py
[event-log]: ../../apps/account-ledger-cli/src/account_ledger/domain/account/event_log.py
[account]: ../../apps/account-ledger-cli/src/account_ledger/domain/account/account.py
[domain-events]: ../../apps/account-ledger-cli/src/account_ledger/domain/account/domain_events.py
[events]: ../../apps/account-ledger-cli/src/account_ledger/domain/model/events.py
[rejections]: ../../apps/account-ledger-cli/src/account_ledger/domain/account/rejections.py
[money]: ../../apps/account-ledger-cli/src/account_ledger/domain/model/money.py
[authorizations]: ../../apps/account-ledger-cli/src/account_ledger/domain/account/authorizations.py
[report]: ../../apps/account-ledger-cli/src/account_ledger/application/report.py
[e2e]: ../../apps/account-ledger-cli/tests/e2e/test_program.py
