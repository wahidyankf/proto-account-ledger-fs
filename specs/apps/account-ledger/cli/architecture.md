# Account Ledger CLI — Architecture

The current, as-built system, as a C4 model in four levels and one dynamic view. A change that alters an actor, a
container, a component responsibility, a relationship, or a boundary updates this document in the same commit.

## Scope

`account-ledger-cli` is the in-memory ledger: it reads a CSV stream of account events, processes it day by day into an
append-only log, and prints one report per day. It runs locally, reads only the file it is given, keeps nothing after it
exits, and never reaches the network.

## L1 — System Context

```text
                  stream.csv (UTF-8 CSV)
+-------------+   argv: one path   +--------------------+   report (UTF-8)       +-----------------+
|  Operator   | -----------------> | account-ledger-cli | ---------------------> | standard output |
+-------------+                    +--------------------+                        +-----------------+
                                         |       ^         usage and errors        +-----------------+
                                         |       +-------------------------------> | standard error  |
                                         | reads                                   +-----------------+
                                         v
                                   +------------+
                                   | the stream |   the brief's is streams/challenge.csv
                                   | file       |
                                   +------------+
```

One actor runs one executable with one stream file. The report goes to standard output; a usage error, an unreadable or
malformed stream, or an internal failure goes to standard error with exit status 2. A closed pipe exits 141 and an
interrupt 130, as the application README publishes.

## L2 — Containers

```text
+--------------------------------------------------------------+
| account-ledger-cli                                           |
| one Python 3.14 process, one package                         |
| reached as python -m account_ledger PATH, or its Nx run      |
+--------------------------------------------------------------+
         | reads the path in argv          | writes UTF-8 whatever the locale
         v                                 v
+-----------------------------+   +-------------------------------------+
| the stream file             |   | standard streams                    |
| UTF-8 CSV, a header row,    |   | standard output: the report         |
| one event a row             |   | standard error: usage and errors    |
| the brief's is              |   +-------------------------------------+
| streams/challenge.csv       |
+-----------------------------+
```

The program is the one container: it reads the one stream file its argument names and writes nothing but its two
standard streams, in UTF-8 whatever the locale, since the report prints the minus sign U+2212.

## L3 — Components

The shell holds every effect and every raw value; the adapters translate between text and the domain's types; the domain
holds every business rule. The adapters and the domain are pure. Every dependency points inward, from the shell to the
adapters and the domain, from the adapters to the domain's types, and, inside the domain, from stream processing down to
the types. Each layer is a place in the package: the shell is `cli.py` at its root, the adapters are `adapters/`, and
the domain is `domain/`, its values in `domain/model/`, under its own `ruff.toml` that refuses any import of
`account_ledger.adapters` or `account_ledger.cli` (TID251). The values are everything below the model line: they decide
nothing. Below them sits `common/`, the tools with no ledger meaning: every layer may import it, and its own `ruff.toml`
refuses any import of the other three.

```text
  shell      +--------------------------------------------------------------------------------+
  cli.py     | cli: run_cli(argv, read_text, out, err) -> exit code; main binds real effects   |
             +--------------------------------------------------------------------------------+
                  | text                   | events                 | reports
                  v                        |                        v
  adapters   +--------------------------+  |  +--------------------------+
  adapters/  | stream_csv               |  |  | render                   |
             | text -> the events, or   |  |  | DayReport -> text, as    |
             | a StreamError            |  |  | OUTPUT_TARGET prints it  |
             +--------------------------+  |  +--------------------------+
                  | builds the types       |        | reads report, event_log, and the types
  ---------------------------------------------------------------------------------------------------
  domain                                   v
  domain/                     +--------------------------+
                              | stream_processing        |
                              | the stream in listed     |
                              | order, each day closed   |
                              | on time                  |
                              +--------------------------+
                              | each event     | each close       | each day
                              v                v                  v
                        +------------+   +------------+     +------------+
                        | processing |   | end_of_day |     | report     |
                        | one entry  |   | fees, then |     | a day as   |
                        | per event  |   | interest,  |     | data       |
                        |            |   | capitalize |     |            |
                        +------------+   +------------+     +------------+
                              |                |                  |
                              v                v                  v
            +-------------------------------------------------------------------------+
            | the rules; each uses only those listed below it                         |
            |   interest        accruals, adjustments, capitalization, accrued days   |
            |   fees            a fee for each day closing negative, refunded after   |
            |   balances        closing and available                                 |
            |   authorizations  the states, decide, transition, holds, and records    |
            |   reversals       which reversal is refused, and which events one undid |
            +-------------------------------------------------------------------------+
                                           |      every component above reads the log;
                                           |      only processing and end_of_day append
  ---------------------------------------------------------------------------------------------------
  model                                    v
  domain/model/                    +----------------+
                                   | event_log      |
                                   | entries and    |
                                   | rejections     |
                                   +----------------+
                                           |
                                           v
          +----------+  +----------+  +----------+  +----------+
          | events   |  | config   |  | money    |  | ids      |
          | incoming |  | accounts,|  | Aed, Bhd,|  | days,    |
          | and fired|  | window   |  | Amount   |  | IDs      |
          +----------+  +----------+  +----------+  +----------+
  ---------------------------------------------------------------------------------------------------
  common                                          every layer above may import it; it imports none
  common/                          +----------------+
                                   | result         |
                                   | Ok, Err        |
                                   +----------------+
```

| Component           | Responsibility                                                                                 |
| ------------------- | ---------------------------------------------------------------------------------------------- |
| `cli`               | `run_cli` checks arguments, reads, parses, processes, renders, and maps each failure to a code |
| `stream_csv`        | parsing the stream file into incoming events, or the first fault with its line                 |
| `render`            | the report as text: banners, box tables, amounts with `−` and separators, notes, and errors    |
| `stream_processing` | the stream in listed order, closing each day on time, with each day's log and report           |
| `processing`        | one entry per incoming event: idempotency first, then by kind; `reversals` checks a reversal   |
| `end_of_day`        | a day's close: `fees`, then `interest`'s accruals and adjustments, then its capitalization     |
| `report`            | a day as data: processed events, end-of-day rows, closings, restated ones, holds, and errors   |
| `fees`              | a fee for each day closing negative with none in force, refunded once the day recovers         |
| `interest`          | a day's interest on a positive closing, adjusted when a closing changes, and capitalized       |
| `balances`          | closing and available, each recomputed over the log                                            |
| `authorizations`    | states, `decide_authorization`, `apply_trigger`, holds, and records rebuilt from the log       |
| `reversals`         | why a reversal is refused, in tech-docs 002's order, and which events the accepted ones undid  |
| `event_log`         | the append-only tuple of entries, each kind holding only its outcome, and every `Rejection`    |
| `events`            | the incoming event kinds, joined in `IncomingEvent`, and the fired kinds, in `FiredEvent`      |
| `config`            | the accounts, each typed by its currency, the window of days, and the capitalization days      |
| `money`             | `Aed` and `Bhd`, one type per currency; `Amount` above zero; split, fee, and daily interest    |
| `ids`               | days, account and hold IDs, incoming IDs, fired-event markers, and instalment counts           |
| `result`            | `Ok` and `Err`, so every failure a caller can meet comes back as a value; it knows no ledger   |

`event_log` imports `AuthorizationState` for annotations only, so the log and the state machine do not import each other
at run time.

## L4 — Code

The types each component exposes and how they refer to one another. Every type is a frozen dataclass, a union of them,
or an enum, and each constructor refuses an illegal value, so none can be built.

```text
result    Result[T, E] = Ok[T] | Err[E]      every parse, make, check, or sum that can fail returns one
money     Aed | Bhd = Money             Amount[M: (Aed, Bhd)], above zero      Direction: UP | DOWN
ids       Day   AccountId   AuthorizationId   IncomingId   InstalmentCount
          EventId = IncomingId | InstalmentId | FeeId | RefundId | InterestId | CapitalizationId
events    IncomingEvent = Credit | Debit | Authorization | Settlement | Reversal     each holds an Amount
          FiredEvent = Instalment | Fee | FeeRefund | InterestAccrual | InterestAdjustment | Capitalization
config    Account[M] = id + opening M     LedgerConfig = accounts, first_day, last_day, capitalization_days
event_log LogEntry = Accepted | AuthorizationDecided | SettlementAccepted | Rejected | Duplicate
          SettlementAccepted.effect = Captured(state_before, state_after) | ForcePosted
          Rejected.reason: Rejection = IdReused | AlreadyReversed | ReversesAReversal | UnknownTarget
                                       | MovedNoMoney | AlreadyUndone
          Log = tuple[LogEntry, ...]
auth      AuthorizationState = Approved(hold) | PartiallySettled(captured_amount, hold)
                                 | Declined(requested_amount) | Settled(captured_amount)
          apply_trigger(state, SettleFinal | SettlePartial)
            -> Result[AuthorizationState, NoTransition | CurrencyMismatch]
          AuthorizationRecord = the Authorization + its state now
report    DayReport = day, processed_events: Processed..., closing_balances, available_balances,
                      restatements: Restatement..., authorizations: AuthorizationRecord..., errors,
                      end_of_day: (Fired | Capitalized | NothingFired)...
stream_processing
          ProcessedStream = reports: DayReport..., logs: Log...     find_report(day), find_log(day)
          process_stream(stream, config) -> Result[ProcessedStream, CurrencyMismatch]
stream    parse_stream(text, config) -> Result[tuple[IncomingEvent, ...], StreamError(line, message)]
```

`authorizations` is a hand-written state machine: `apply_trigger` is one `match` over the state and its trigger, ending
in `assert_never`. A settlement whose `final` cell is `no` fires `SettlePartial`; any other fires `SettleFinal`. As
built:

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

A final settlement releases the whole remaining hold and settles for the captures' sum; a partial one below the hold
keeps the rest. `Settled` and `Declined` have no transition for any trigger, so a settlement against either, or against
an authorization the log does not know, is accepted as a force-post: it debits its amount and releases no hold.

## Dynamic View — One Day

```text
process_stream, for each event in listed order, D the current day
  1. the event is booked after D: close D (a and b), open D + 1, and look again; a day with no events closes too;
     no day closes after the window's last, so an event booked after the window reaches no day's log or report
  2. otherwise: processing.process_event(log, event, D) ---> log + one entry (+ the instalments a credit fires)
       idempotency first; then by kind; a reversal checked against its target in order
       an event booked before D is late and is processed on D (AMB-015)
process_stream, once every event is processed: close every day left in the window

closing day D
  a. end_of_day.close_day(log, D): step 1 in fees, steps 2 and 3 in interest
       step 1  fees:     each day first..D: negative with no fee in force -> Fee; non-negative with one -> FeeRefund
       step 2  interest: each day first..D: daily interest of its base, less what was fired for it
                         -> InterestAccrual for D, InterestAdjustment for an earlier day
       step 3  capitalization, on a capitalization day: accrued interest above zero -> Capitalization
  b. report.build_report(log, D, reported_closings) ---> DayReport: what D processed and fired, its closings,
       and each earlier closing that changed since last reported
cli, after the last day
  render.render_reports(reports) ---> the whole text, then one write and one flush to standard output
```

Every balance is recomputed from the log whenever it is asked for (D7), so a late event value-dated in the past changes
every later closing without any stored balance being updated. Each sum of money returns a `CurrencyMismatch` rather than
a wrong total when it meets two currencies. The reader keeps every effect in its account's currency, so only a bug
brings one; it ends the processing, and `run_cli` prints `error: internal: ` and exits 2.

## Reading the Code

To read the code for the first time, follow one day through it, in this order:

1. `cli.py`, `run_cli`: where the program starts, and how every failure becomes an exit status.
2. `domain/stream_processing.py`: the loop over events, where a later day's event closes the current day first, as the
   dynamic view above draws.
3. `domain/processing.py`, `process_event`: what one incoming event adds to the log, duplicates caught first.
4. `domain/end_of_day.py`, `close_day`: the three steps of a day's close, each in its own module.
5. `domain/fees.py`: when a day is charged an overdraft fee, and when that fee is refunded.
6. `domain/interest.py`: each day's interest, its adjustment when a closing changes, and its capitalization.
7. `domain/balances.py`: the closing and available balances, worked out from the log.
8. `domain/authorizations.py`: how an authorization is decided, holds money, and moves from state to state.
9. `domain/reversals.py`: when a reversal is refused, and which events the accepted ones undid.
10. `domain/model/event_log.py`: every kind of entry the rules add, and every reason an event is rejected.
11. `domain/report.py`, then `adapters/render.py`: a day as data, then as the text OUTPUT_TARGET shows.

`adapters/stream_csv.py` turns the file into events and holds no ledger rule. The rest of `domain/model/`, `events.py`,
`config.py`, `money.py`, and `ids.py`, defines the values the rules pass around; look them up when a name is unfamiliar
rather than reading them first.

## Constraints

- No web layer, persistence, UI, or database.
- Every effect sits in the shell; the domain stays pure and deterministic.
- Balances are recomputed from the append-only log, never stored (D7); nothing in the log is changed or removed.
- Holds never expire (AMB-018), the ledger's known weakness.
- Every diagram is plain-text ASCII.
