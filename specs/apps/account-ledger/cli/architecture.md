# Account Ledger CLI — Architecture

The current, as-built system, as a C4 model in four levels and one dynamic view. A change that alters an actor, a
container, a component responsibility, a relationship, or a boundary updates this document in the same commit.

## Scope

`account-ledger-cli` is the in-memory ledger: it reads a CSV stream of account events, replays it day by day into an
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
adapters and the domain, from the adapters to the domain's types, and, inside the domain, from the driver down to the
types. Each layer is a place in the package: the shell is `cli.py` at its root, the adapters are `adapters/`, and the
domain is `domain/`, whose own `ruff.toml` refuses any import of `account_ledger.adapters` or `account_ledger.cli`
(TID251).

```text
  shell      +--------------------------------------------------------------------------------+
  cli.py     | cli: run(argv, read_text, out, err) -> exit code; main binds the real effects   |
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
                              | replay (driver)          |
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
                           |      |           |                  |
            decides and    |      v           v                  v
            settles        |   +---------------------------------------+
                           |   | balances: closing, holds, available,  |
                           |   | accrued, accrued days, interest base  |
                           |   +---------------------------------------+
                           v                  |
                   +----------------+  reads  |
                   | authorizations | <-------+
                   | the states and |
                   | transition     |
                   +----------------+
                           |                  every component above reads the log;
                           v                  only processing and end_of_day append
                   +----------------+
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
```

| Component        | Responsibility                                                                                  |
| ---------------- | ----------------------------------------------------------------------------------------------- |
| `cli`            | `run` checks the arguments, reads, parses, replays, renders, and maps every failure to a status |
| `stream_csv`     | parsing the stream file into incoming events, or the first fault with its line                  |
| `render`         | the report as text: banners, box tables, amounts with `−` and separators, and every Detail text |
| `replay`         | the stream in listed order, closing each day on time, with the log and report of every day      |
| `processing`     | one entry per incoming event: idempotency first, then by kind, with reversal checks in order    |
| `end_of_day`     | a day's close: fee re-evaluation, interest accruals and adjustments, then capitalization        |
| `report`         | a day's processed events, end-of-day rows, closings, restated closings, holds, and errors       |
| `balances`       | closing, holds, available, accrued interest and its days, and interest base, each over the log  |
| `authorizations` | the authorization states, `decide`, `transition`, and the records replayed from the log         |
| `event_log`      | the append-only tuple of entries, each kind holding only its outcome, and every `Rejection`     |
| `events`         | the incoming event kinds, joined in `IncomingEvent`, and the fired kinds, in `FiredEvent`       |
| `config`         | the accounts, each typed by its currency, the window of days, and the capitalization days       |
| `money`          | `Aed` and `Bhd`, one type per currency; `Amount` above zero; the split, fee, and daily interest |
| `ids`            | days, account and hold IDs, incoming IDs, fired-event markers, and instalment counts            |

`event_log` imports `AuthorizationState` for annotations only, so the log and the state machine do not import each other
at run time.

## L4 — Code

The types each component exposes and how they refer to one another. Every type is a frozen dataclass, a union of them,
or an enum, and each constructor refuses an illegal value, so none can be built.

```text
money     Aed | Bhd = Money             Amount[M: (Aed, Bhd)], above zero      Direction: UP | DOWN
ids       Day   AccountId   AuthorizationId   IncomingId   InstalmentCount
          EventId = IncomingId | InstalmentId | FeeId | RefundId | InterestId | CapitalizationId
events    IncomingEvent = Credit | Debit | Authorization | Settlement | Reversal     each holds an Amount
          FiredEvent = Instalment | Fee | FeeRefund | InterestAccrual | InterestAdjustment | Capitalization
config    Account[M] = id + opening M     LedgerConfig = accounts, first_day, last_day, capitalization_days
event_log LogEntry = Accepted | AuthorizationDecided | SettlementAccepted | Rejected | Duplicate
          SettlementAccepted.effect = Captured(before, after) | ForcePosted
          Rejected.reason: Rejection = IdReused | AlreadyReversed | ReversesAReversal | UnknownTarget
                                       | MovedNoMoney | AlreadyUndone
          Log = tuple[LogEntry, ...]
auth      AuthorizationState = Approved(hold) | PartiallySettled(captured, hold) | Declined(requested)
                                 | Settled(captured)
          transition(state, SettleFinal | SettlePartial) -> AuthorizationState | NoTransition
          AuthorizationRecord = the Authorization + its state now
report    DayReport = day, processed: Processed..., closing, available, restated: Restatement...,
                      authorizations: AuthorizationRecord..., errors, end_of_day: (Fired | Capitalized
                      | NothingFired)...
replay    Replay = reports: DayReport..., logs: Log...     report(day), log_at(day)
stream    parse_stream(text, config) -> tuple[IncomingEvent, ...] | StreamError(line, message)
```

`authorizations` is a hand-written state machine: `transition` is one `match` over the state and its trigger, ending in
`assert_never`. A settlement whose `final` cell is `no` fires `SettlePartial`; any other fires `SettleFinal`. As built:

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
replay, day D
  1. for each event listed next whose booked day <= D:
       processing.process(log, event, D) ---> log + one entry (+ the instalments a credit fires)
         idempotency first; then by kind; a reversal checked against its target in order
  2. end_of_day.close_day(log, D)
       step 1  fees:     each day first..D: negative with no fee in force -> Fee; non-negative with one -> FeeRefund
       step 2  interest: each day first..D: daily interest of its base, less what was fired for it
                         -> InterestAccrual for D, InterestAdjustment for an earlier day
       step 3  capitalization, on a capitalization day: accrued interest above zero -> Capitalization
  3. report.report(log, D, reported) ---> DayReport: what D processed and fired, its closings, and each earlier
       closing that changed since last reported
cli, after the last day
  4. render.render(reports) ---> the whole text, then one write and one flush to standard output
```

Every balance is recomputed from the log whenever it is asked for (D7), so a late event value-dated in the past changes
every later closing without any stored balance being updated.

## Reading the Code

To read the code for the first time, follow one day through it, in this order:

1. `cli.py`, `run`: where the program starts, and how every failure becomes an exit status.
2. `domain/replay.py`: the loop over days, which the dynamic view above draws.
3. `domain/processing.py`, `process`: what one incoming event adds to the log, duplicates caught first.
4. `domain/end_of_day.py`, `close_day`: fees, then interest, then capitalization.
5. `domain/event_log.py`: every kind of entry those two add, and every reason an event is rejected.
6. `domain/authorizations.py`, then `domain/balances.py`: how an authorization moves from state to state, and how each
   balance is worked out from the log.
7. `domain/report.py`, then `adapters/render.py`: a day as data, then as the text OUTPUT_TARGET shows.

`adapters/stream_csv.py` turns the file into events and holds no ledger rule. `domain/events.py`, `config.py`,
`money.py`, and `ids.py` define the values the rest pass around; look them up when a name is unfamiliar rather than
reading them first.

## Constraints

- No web layer, persistence, UI, or database.
- Every effect sits in the shell; the domain stays pure and deterministic.
- Balances are recomputed from the append-only log, never stored (D7); nothing in the log is changed or removed.
- Holds never expire (AMB-018), the ledger's known weakness.
- Every diagram is plain-text ASCII.
