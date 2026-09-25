# Account Ledger CLI — Architecture

The current, as-built system, as a C4 model in four levels and one dynamic view, then its domain model in DDD terms. A
change that alters an actor, a container, a component responsibility, a relationship, or a boundary updates this
document in the same commit.

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
holds every business rule. The adapters and the domain are pure. Every dependency points inward: from the shell to the
adapters and the domain, from the adapters to the domain's types, and, inside the domain, from stream processing to the
ledger service and the report, from those to the Account aggregate, and from the aggregate to the values. Each layer is
a place in the package: the shell is `cli.py` at its root, the adapters are `adapters/`, and the domain is `domain/`,
with `stream_processing.py` and `report.py` at its root, the ledger service in `domain/ledger/`, the aggregate in
`domain/account/`, and the values in `domain/model/`. Each domain package has its own `ruff.toml` that refuses any
import of the layers above it, and every one refuses `account_ledger.adapters` and `account_ledger.cli` (TID251). The
values decide nothing. Below them sits `common/`, the tools with no ledger meaning: every layer may import it, and its
own `ruff.toml` refuses any import of the other three.

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
                  | builds the values      |        | reads the report, the domain events, and the values
  ---------------------------------------------------------------------------------------------------
  domain                                   v
  domain/                     +--------------------------+
                              | stream_processing        |
                              | the stream in listed     |
                              | order, each day closed   |
                              | on time                  |
                              +--------------------------+
                                | each event, each close       | each day
                                v                              v
  ledger service   +----------------------------------+   +----------------------------+
  domain/ledger/   | processing: IDs across accounts, |   | report, the read model:    |
                   |   the cross-account check        |   | a day as data, read from   |
                   | end_of_day: each step on every   |   | the log and each account's |
                   |   account, in account order      |   | history                    |
                   | event_log: the log               |   | domain/report.py           |
                   +----------------------------------+   +----------------------------+
                                | one account's history at a time      |
  ---------------------------------------------------------------------------------------------------
  aggregate                     v
  domain/account/  +-------------------------------------------------------------------------+
                   | the Account aggregate; every rule reads one AccountHistory, never the log |
                   |   decisions       one incoming event on the account -> its entries      |
                   |   interest        accruals, adjustments, capitalization, accrued days   |
                   |   fees            a fee for each day closing negative, refunded after   |
                   |   balances        closing and available                                 |
                   |   authorizations  decide, transition, holds, and records                |
                   |   reversals       which reversal is refused, and which events one undid |
                   |   history, domain_events, states: what the rules read and record        |
                   +-------------------------------------------------------------------------+
  ---------------------------------------------------------------------------------------------------
  model                                    v
  domain/model/   +----------+  +----------+  +----------+  +----------+
                  | events   |  | config   |  | money    |  | ids      |
                  | incoming,|  | accounts,|  | Aed, Bhd,|  | days,    |
                  | generated|  | window   |  | Amount   |  | IDs      |
                  +----------+  +----------+  +----------+  +----------+
  ---------------------------------------------------------------------------------------------------
  common                                          every layer above may import it; it imports none
  common/                          +----------------+
                                   | result         |
                                   | Ok, Err        |
                                   +----------------+
```

| Component                | Responsibility                                                                            |
| ------------------------ | ----------------------------------------------------------------------------------------- |
| `cli`                    | `run_cli` checks arguments, reads, parses, processes, renders, and codes each failure     |
| `stream_csv`             | the stream file parsed into incoming events, or the first fault with its line             |
| `render`                 | the report as text: banners, box tables, amounts with `−`, notes, and errors              |
| `stream_processing`      | the stream in listed order, each day closed on time, with each day's log and report       |
| `report`                 | the read model: a day's events, end-of-day rows, closings, restatements, holds, errors    |
| `ledger/processing`      | idempotency and the cross-account check on the log; then the account decides              |
| `ledger/end_of_day`      | a day's close, each step on every account: fees, interest, then capitalization            |
| `ledger/event_log`       | the append-only log of every account's domain events, and each account's history in it    |
| `account/decisions`      | one incoming event on one account, decided from its history, as the entries it records    |
| `account/fees`           | a fee for each day closing negative with none in force, refunded once the day recovers    |
| `account/interest`       | a day's interest on a positive closing, adjusted when a closing changes, capitalized      |
| `account/balances`       | closing and available, each recomputed over the account's history                         |
| `account/authorizations` | `decide_authorization`, `apply_settlement`, holds, and records rebuilt from the history   |
| `account/reversals`      | why a reversal is refused, in tech-docs 002's order, and which events one undid           |
| `account/history`        | `AccountHistoryIn[M]`: one account and its own entries, all that an account rule may read |
| `account/domain_events`  | the domain events, one kind per fact the ledger records, and every `Rejection`            |
| `account/states`         | the authorization states, one frozen dataclass each                                       |
| `model/events`           | incoming event kinds, in `IncomingEvent`, and generated kinds, in `GeneratedEvent`        |
| `model/config`           | the accounts, each typed by its currency, the window of days, and the capitalization days |
| `model/money`            | `Aed` and `Bhd`, one type per currency; `AmountIn` above zero; split, fee, daily interest |
| `model/ids`              | days, account and authorization IDs, incoming and generated IDs, instalment counts        |
| `result`                 | `Ok` and `Err`, so every failure a caller can meet is a value; it knows no ledger         |

`states` sits apart from `authorizations` so that `domain_events` can hold the states a settlement moved its
authorization between, and the state machine can read the domain events, without either importing the other.

## L4 — Code

The types each component exposes and how they refer to one another. Every type is a frozen dataclass, a union of them,
or an enum, and each constructor refuses an illegal value, so none can be built.

```text
result    Result[T, E] = Ok[T] | Err[E]      every parse, make, check, or sum that can fail returns one
money     Aed | Bhd = Money             AmountIn[M: (Aed, Bhd)], above zero    Direction: UP | DOWN
          Amount = AmountIn[Aed] | AmountIn[Bhd]
ids       Day   AccountId   AuthorizationId   IncomingId   InstalmentCount
          EventId = IncomingId | InstalmentId | FeeId | RefundId | InterestId | CapitalizationId
events    IncomingEvent = Credit | Debit | Authorization | Settlement | Reversal     each holds an Amount
          GeneratedEvent = Instalment | Fee | FeeRefund | InterestAccrual | InterestAdjustment | Capitalization
config    AccountIn[M] = id + opening M   LedgerConfig = accounts, first_day, last_day, capitalization_days
account/domain_events
          LogEntry = the domain events, one kind per fact, each holding its event and processed_day:
            CreditPosted | DebitPosted | ReversalPosted | InstalmentPosted | FeeCharged | FeeRefunded
            | InterestAccrued | InterestAdjusted | InterestCapitalized
            | AuthorizationApproved | AuthorizationDeclined
            | SettlementApplied(+ state_before, state_after) | SettlementForcePosted
            | EventRejected(+ reason) | DuplicateIgnored
          EventRejected.reason: Rejection = IdReused | AlreadyReversed | ReversesAReversal | UnknownTarget
                                            | TargetOnAnotherAccount | MovedNoMoney | AlreadyUndone
account/history
          AccountHistoryIn[M: (Aed, Bhd)] = account: AccountIn[M] + entries: LogEntry...   one account's own entries
          every account rule takes one; a rule generic over M is reached through one dispatch, AccountHistory
ledger/event_log
          Log = tuple[LogEntry, ...]     find_history(log, account) -> AccountHistoryIn[M]
account/states, account/authorizations
          AuthorizationState = Approved(hold) | PartiallySettled(settled_amount, hold)
                                 | Declined(requested_amount) | Settled(settled_amount)
          apply_settlement(state, FinalSettlement | PartialSettlement)
            -> Result[AuthorizationState, CannotSettle | CurrencyMismatch]
          AuthorizationRecord = the Authorization + its state now
report    DayReport = day, processed_events: Processed..., closing_balances, available_balances,
                      restatements: Restatement..., authorizations: AuthorizationRecord..., errors,
                      end_of_day: (Generated | Capitalized | NothingGenerated)...
stream_processing
          ProcessedStream = reports: DayReport..., logs: Log...     find_report(day), find_log(day)
          process_stream(stream, config) -> Result[ProcessedStream, CurrencyMismatch]
stream    parse_stream(text, config) -> Result[tuple[IncomingEvent, ...], StreamError(line, message)]
```

`authorizations` is a hand-written state machine: `apply_settlement` is one `match` over the state and the settlement,
ending in `assert_never`. A settlement whose `final` cell is `no` becomes `PartialSettlement`; any other becomes
`FinalSettlement`. As built:

```text
             available >= 0 after the hold              FinalSettlement, or PartialSettlement reaching the hold
  (arrives) ------------------------------> Approved -------------------------------------------> Settled
      |                                        |                                                     ^
      | available < 0 after the hold           | PartialSettlement below the hold                    |
      v                                        v                                                     |
   Declined                             PartiallySettled --------------------------------------------+
                                          |          ^     FinalSettlement, or PartialSettlement reaching the hold
                                          +----------+
                                   PartialSettlement below the hold
```

A final settlement releases the whole remaining hold and settles for the settlements' sum; a partial one below the hold
keeps the rest. `Settled` and `Declined` have no transition for any settlement, so a settlement against either, or
against an authorization the log does not know, is force-posted: it debits its amount and releases no hold.

## Dynamic View — One Day

```text
process_stream, for each event in listed order, D the current day
  1. the event is booked after D: close D (a and b), open D + 1, and look again; a day with no events closes too;
     no day closes after the window's last, so an event booked after the window reaches no day's log or report
  2. otherwise: ledger.processing.process_event(log, event, D) ---> log + one entry, and a credit's instalments
       idempotency first, across every account; then a reversal whose target is on another account;
       then the account decides from its own history, by kind; a reversal checked against its target in order
       an event booked before D is late and is processed on D (AMB-015)
process_stream, once every event is processed: close every day left in the window

closing day D
  a. ledger.end_of_day.close_day(log, D): each step on every account in turn; step 1 in account.fees,
     steps 2 and 3 in account.interest, each reading one account's history
       step 1  fees:     each day first..D: negative with no fee in force -> Fee; non-negative with one -> FeeRefund
       step 2  interest: each day first..D: daily interest of its base, less what was generated for it
                         -> InterestAccrual for D, InterestAdjustment for an earlier day
       step 3  capitalization, on a capitalization day: accrued interest above zero -> Capitalization
  b. report.build_report(log, D, reported_closings) ---> DayReport: what D processed and generated, its closings,
       and each earlier closing that changed since last reported
cli, after the last day
  render.render_reports(reports) ---> the whole text, then one write and one flush to standard output
```

Every balance is recomputed from the log whenever it is asked for (D7), so a late event value-dated in the past changes
every later closing without any stored balance being updated. Each sum of money returns a `CurrencyMismatch` rather than
a wrong total when it meets two currencies. The reader keeps every effect in its account's currency, so only a bug
brings one; it ends the processing, and `run_cli` prints `error: internal: ` and exits 2.

## Domain Model

The domain is one bounded context, the Ledger: the brief's accounts, their events, and the days that close them. Every
type in `domain/` belongs to it, and none outside `domain/` holds a ledger rule.

| The brief says                     | The code has                                                                  |
| ---------------------------------- | ----------------------------------------------------------------------------- |
| an account, in its currency        | `AccountIn[M]`, with `M` either `Aed` or `Bhd`, and its `AccountId`           |
| an event in the stream             | `IncomingEvent`: `Credit`, `Debit`, `Authorization`, `Settlement`, `Reversal` |
| the ledger, append-only            | `Log`, the one tuple of every account's domain events                         |
| a hold                             | the `hold` of an `Approved` or a `PartiallySettled` authorization             |
| the closing and available balances | `compute_closing` and `compute_available`, over one account's history         |
| an overdraft fee, and its refund   | `Fee` and `FeeRefund`, recorded as `FeeCharged` and `FeeRefunded`             |
| interest, and its capitalization   | `InterestAccrual`, `InterestAdjustment`, and `Capitalization`                 |
| a credit paid in instalments       | `Instalment`, one per `InstalmentCount`, recorded as `InstalmentPosted`       |

A type generic over the currency ends in `In`, and the union over its currencies takes the plain noun, per the Python
[naming](../../../../repo-governance/development/quality/stacks/python-standards/001-naming.md) rule: `AccountIn[Aed]`
is an account in AED, and `Account` is either. Each rule inside the aggregate is generic, and is reached from outside
through a function ending in `_of` that takes the plain noun, such as
`compute_closing_of(history: AccountHistory, day)`.

**The Account aggregate** is one account and its own entries in the log, `AccountHistoryIn[M]`. Every rule in
`domain/account/` takes one history and never the log, so pyright refuses a rule that reads another account. The
aggregate guards the invariants that concern one account:

- an authorization is decided once, on arrival, and approved only while the available balance after its hold stays at or
  above zero (AMB-008, AMB-009);
- a settlement moves its authorization only as the state machine in L4 allows (D8), and is force-posted otherwise
  (AMB-012);
- a target is reversed at most once, a reversal is never reversed, and one that undoes nothing is refused (AMB-028,
  AMB-035);
- a day closing negative carries one fee at most, refunded once that day recovers (AMB-002, AMB-004);
- a day's interest is accrued once and adjusted when its closing changes, then capitalized on a capitalization day.

It records each fact as a **domain event**, one kind per fact: `CreditPosted`, `AuthorizationApproved`,
`SettlementForcePosted`, `EventRejected`, and the rest listed in L4. The aggregate's balances are not stored; each is
recomputed from its domain events whenever it is asked for (D7).

**The Ledger service**, `domain/ledger/`, is the only code that sees every account at once. It keeps the one log
(AMB-014, AMB-024), refuses what spans accounts before any account decides, an event ID seen before (AMB-034) and a
reversal whose target is on another account (AMB-036), and runs a day's close as each step on every account in turn.

**The report** is a read model: `domain/report.py` reads the log and each account's history and writes nothing back.
`stream_processing` drives the service and the report over the stream, day by day.

## Reading the Code

To read the code for the first time, follow one day through it, in this order:

1. `cli.py`, `run_cli`: where the program starts, and how every failure becomes an exit status.
2. `domain/stream_processing.py`: the loop over events, where a later day's event closes the current day first, as the
   dynamic view above draws.
3. `domain/ledger/processing.py`, `process_event`: duplicates and cross-account reversals caught on the whole log.
4. `domain/account/decisions.py`, `decide_event_of`: what one incoming event adds to its account's history.
5. `domain/ledger/end_of_day.py`, `close_day`: the three steps of a day's close, each run on every account.
6. `domain/account/fees.py`: when a day is charged an overdraft fee, and when that fee is refunded.
7. `domain/account/interest.py`: each day's interest, its adjustment when a closing changes, and its capitalization.
8. `domain/account/balances.py`: the closing and available balances, worked out from one account's history.
9. `domain/account/authorizations.py`: how an authorization is decided, holds money, and moves from state to state.
10. `domain/account/reversals.py`: when a reversal is refused, and which events the posted ones undid.
11. `domain/account/domain_events.py` and `history.py`: every domain event the rules record, every reason an event is
    rejected, and the one account's history each rule reads.
12. `domain/report.py`, then `adapters/render.py`: a day as data, then as the text OUTPUT_TARGET shows.

`adapters/stream_csv.py` turns the file into events and holds no ledger rule. `domain/model/`, `events.py`, `config.py`,
`money.py`, and `ids.py`, defines the values the rules pass around; look them up when a name is unfamiliar rather than
reading them first.

## Constraints

- No web layer, persistence, UI, or database.
- Every effect sits in the shell; the domain stays pure and deterministic.
- Balances are recomputed from the append-only log, one account's history at a time, never stored (D7); nothing in the
  log is changed or removed.
- Holds never expire (AMB-018), the ledger's known weakness.
- Every diagram is plain-text ASCII.
