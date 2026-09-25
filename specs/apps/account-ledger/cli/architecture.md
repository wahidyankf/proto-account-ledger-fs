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

The shell holds every raw value and binds every real effect; the adapters translate between text and the application's
ports; the application runs the one use case over the domain; the domain holds every business rule. The domain and the
application are pure: the program reads and writes only in the adapters, through the reader and the streams the shell
passes in. Every dependency points inward: from the shell to what it composes, from the adapters to the application's
ports and the domain's types, from the application to the domain, and, inside the domain, from the Ledger to the Account
aggregate and from the aggregate to the values. Each layer is a place in the package: the shell is `cli.py` and
`challenge.py` at its root, the adapters are `adapters/`, the application is `application/`, and the domain is
`domain/`, with the Ledger in `domain/ledger/`, the aggregate in `domain/account/`, and the values in `domain/model/`.
Each package has its own `ruff.toml` that refuses any import of the layers around it (TID251): every domain package
refuses `account_ledger.application`, `account_ledger.adapters`, and the shell's two modules, the application refuses
the adapters and the shell, and the adapters refuse the shell. The values decide nothing. Below them sits `common/`, the
tools with no ledger meaning: every layer may import it, and its own `ruff.toml` refuses any import of the others.

```text
  shell        +------------------------------------------------------------------------------------+
  cli.py       | cli: run_cli(argv, read_text, out, err, run_ledger) -> exit code; builds the two   |
  challenge.py |   adapters, calls the use case, and codes each fault; main binds the real effects  |
               | challenge: CHALLENGE, the brief's configuration main gives LedgerRun               |
               +------------------------------------------------------------------------------------+
                    | builds                      | builds                      | RunLedger.run(source, sink)
                    v                             v                             |
  adapters     +--------------------------+  +--------------------------+       |
  adapters/    | csv_file: CsvFileSource  |  | text_report:             |       |
               | the file read and parsed |  | TextReportSink, the      |       |
               | into events, or a        |  | reports as OUTPUT_TARGET |       |
               | SourceFault              |  | prints them              |       |
               +--------------------------+  +--------------------------+       |
                    | is an EventSource           | is a ReportSink             |
  -------------------------------------------------------------------------------------------------------
  application       v                             v                             v
  application/ +------------------------------------------------------------------------------------+
               | ports: EventSource, ReportSink, and RunLedger, the ports the use case declares     |
               | run: LedgerRun, the use case: read the events, process them, publish the reports   |
               | stream: IncomingStream, processed in listed order, each day closed on time         |
               | report: DayReport, the read model: a day as data, read from the Ledger             |
               +------------------------------------------------------------------------------------+
                                  | each event, each close, each day's report
  -------------------------------------------------------------------------------------------------------
  ledger                          v
  domain/ledger/   +--------------------------------------------------------------------------------+
                   | ledger: Ledger, the config and the one log; IDs and the cross-account check;   |
                   |   each close step on every account, in account order                           |
                   +--------------------------------------------------------------------------------+
                                  | one account at a time
  -------------------------------------------------------------------------------------------------------
  aggregate                       v
  domain/account/  +--------------------------------------------------------------------------------+
                   | the Account aggregate: every rule about one account, in one class              |
                   |   account         AccountIn, asked by method, topic by topic: entries,         |
                   |                   balances, authorizations, decisions, reversals, fees,        |
                   |                   and interest                                                 |
                   |   authorizations  the states, the D8 table over take, and each record          |
                   |   event_log       EventLog: an account's entries, or the whole log's           |
                   |   domain_events, rejections: what the rules record, and why one refuses        |
                   +--------------------------------------------------------------------------------+
  -------------------------------------------------------------------------------------------------------
  model                           v
  domain/model/   +----------+  +----------+  +----------+  +----------+
                  | events   |  | config   |  | money    |  | ids      |
                  | incoming,|  | accounts,|  | Aed, Bhd,|  | days,    |
                  | generated|  | window   |  | Amount   |  | IDs      |
                  +----------+  +----------+  +----------+  +----------+
  -------------------------------------------------------------------------------------------------------
  common                                          every layer above may import it; it imports none
  common/                          +----------------+
                                   | result         |
                                   | Ok, Err        |
                                   +----------------+
```

| Component                | Responsibility                                                                            |
| ------------------------ | ----------------------------------------------------------------------------------------- |
| `cli`                    | `run_cli` checks arguments, builds the adapters, runs the use case, and codes each fault  |
| `challenge`              | `CHALLENGE`: ACC-001 in AED and ACC-002 in BHD, Days 1 to 6, capitalized on Day 6         |
| `csv_file`               | `CsvFileSource`: the stream file read and parsed into events, or the first fault          |
| `text_report`            | `TextReportSink`: the report as text: banners, box tables, amounts with `−`, and errors   |
| `ports`                  | `EventSource`, `ReportSink`, and `RunLedger`, each a `Protocol` a signature consumes      |
| `run`                    | `LedgerRun`: read the events, process them, publish the reports; the first fault ends it  |
| `stream`                 | the stream in listed order, each day closed on time, with each day's log and report       |
| `report`                 | the read model: a day's events, end-of-day rows, closings, restatements, holds, errors    |
| `ledger/ledger`          | `Ledger`: the one log; IDs and the cross-account check, then the account; a day's close   |
| `account/account`        | `AccountIn[M]`: the Account aggregate, one account's entries and every rule about them    |
| `account/authorizations` | the four states, `apply_settlement` as the D8 table, and each authorization's record      |
| `account/event_log`      | `EventLog`: entries in log order, appended to, searched, and selected by account          |
| `account/domain_events`  | the domain events, one kind per fact the ledger records                                   |
| `account/rejections`     | every `Rejection`: why the account, or the ledger, refuses an event                       |
| `model/events`           | incoming kinds, in `IncomingEvent`, generated kinds, in `GeneratedEvent`; instalments     |
| `model/config`           | the accounts as opened, each typed by its currency, the window, and the capitalization    |
| `model/money`            | `Aed` and `Bhd`, one type per currency; `AmountIn` above zero; split, take, fee, interest |
| `model/ids`              | days, account and authorization IDs, incoming and generated IDs, instalment counts        |
| `result`                 | `Ok` and `Err`, so every failure a caller can meet is a value; it knows no ledger         |

## L4 — Code

The types each component exposes and how they refer to one another. Every value is a frozen dataclass, a union of them,
or an enum, none derives from another, and each constructor refuses an illegal value, so none can be built. The ports
and `TextOutput` are `Protocol`s, which an adapter or a test's stand-in satisfies by its shape, not by deriving.

```text
result    Result[T, E] = Ok[T] | Err[E]      every parse, make, check, or sum that can fail returns one
money     Aed | Bhd = Money             AmountIn[M: (Aed, Bhd)], above zero    Direction: UP | DOWN
          Aed, Bhd each a value at its CURRENCY's PLACES, with the same methods over one private function each:
            make, parse, make_zero, require_same, add_all, compute_daily_interest, make_directed_amount, ...
          Amount = AmountIn[Aed] | AmountIn[Bhd]    split(count), add(amount), take(amount) -> the rest or None
ids       Day   AccountId   AuthorizationId   IncomingId   InstalmentCount
          EventId = IncomingId | InstalmentId | FeeId | RefundId | InterestId | CapitalizationId
          AccountId, AuthorizationId, IncomingId each hold PATTERN, KIND, SHAPE; FeeId, RefundId, InterestId
          each hold PREFIX; every event ID kind has format()
events    IncomingEvent = Credit | Debit | Authorization | Settlement | Reversal     each holds an Amount
          GeneratedEvent = Instalment | Fee | FeeRefund | InterestAccrual | InterestAdjustment | Capitalization
          each incoming kind declares id, booked, account, value_date first; each generated kind id: its own
          ID kind, account, value_date     Instalments(count, parts), made by Instalments.make(amount, count)
          Credit.make_instalments()   InterestAccrual, InterestAdjustment: compute_signed_money()
config    AccountOpeningIn[M] = id + balance M, the account as opened; AccountOpening, the union of both
          LedgerConfig = accounts, first_day, last_day, capitalization_days
account/domain_events
          LogEntry = the domain events, one kind per fact, each event: its own kind + processed_day:
            CreditPosted | DebitPosted | ReversalPosted | InstalmentPosted | FeeCharged | FeeRefunded
            | InterestAccrued | InterestAdjusted | InterestCapitalized
            | AuthorizationApproved | AuthorizationDeclined
            | SettlementApplied(+ state_before, state_after) | SettlementForcePosted
            | EventRejected(+ reason) | DuplicateIgnored
account/rejections
          EventRejected.reason: Rejection = IdReused | AlreadyReversed | ReversesAReversal | UnknownTarget
                                            | TargetOnAnotherAccount | MovedNoMoney | AlreadyUndone
account/event_log
          EventLog = entries: LogEntry...   append(*entries), find_first_entry(event_id), select(account_id),
            list_processed_on(day)
account/account
          AccountIn[M: (Aed, Bhd)] = id + opening M + log: EventLog, its own entries; every rule a method
          type Account = AccountIn[Aed] | AccountIn[Bhd]; a method works on either
ledger/ledger
          Ledger = config: LedgerConfig + log: EventLog     Ledger.open(config), an empty log
          find_account(opening) -> Account     list_accounts() -> Account..., in the configured order
          process_event(event, today) -> Result[Ledger, InternalFault]
          close_day(today) -> Result[Ledger, CurrencyMismatch]
          InternalFault = CurrencyMismatch | UnknownAccount(account)
account/authorizations
          AuthorizationState = Approved(hold) | PartiallySettled(settled_amount, hold)
                                 | Declined(requested_amount) | Settled(settled_amount)
          apply_settlement(state, kind: SettlementKind, amount)   the rest the hold keeps comes from take
            -> Result[AuthorizationState, CannotSettle | CurrencyMismatch]
          AuthorizationRecord = the Authorization + its state now; is_referenced_by(settlement)
report    DayReport = day, processed_events: Processed..., closing_balances, available_balances,
                      restatements: Restatement..., authorizations: AuthorizationRecord..., errors,
                      end_of_day: (Generated | Capitalized | NothingGenerated)...
          DayReport.build(ledger, day, reported: ReportedClosings) -> Result[DayReport, CurrencyMismatch]
          ReportedClosings = closings by day and account     make_empty(), update(report), list_days_before(day),
            find_closings(day)
stream    IncomingStream = events: IncomingEvent...     process(config) -> Result[ProcessedStream, InternalFault]
          ProcessedStream = reports: DayReport..., logs: EventLog...     find_report(day), find_log(day)
ports     SourceFault = message     RunFault = SourceFault | InternalFault
          EventSource: read_events(config) -> Result[IncomingStream, SourceFault]
          ReportSink: publish(reports)     RunLedger: run(source, sink) -> Result[None, RunFault]
run       LedgerRun = config     run(source, sink): read, process, then publish; the first Err ends it
csv_file  CsvFileSource = path + read_text: Reader     read_events(config), an EventSource
          CsvFileSource.parse(text, config) -> Result[IncomingStream, StreamError(line, message)]
text_report
          TextOutput: write(text), flush()     TextReportSink = out: TextOutput     publish(reports), a ReportSink
          TextReportSink.render(reports) -> str
```

`authorizations` is a hand-written state machine: `apply_settlement` is one `match` over the state, the settlement's
kind, and what the settlement leaves of the hold, which `AmountIn.take` gives, ending in `assert_never`. A settlement
whose `final` cell is `no` is `SettlementKind.PARTIAL`; any other is `SettlementKind.FINAL`. As built:

```text
             available >= 0 after the hold              FINAL, or PARTIAL reaching the hold (take: None)
  (arrives) ------------------------------> Approved -------------------------------------------> Settled
      |                                        |                                                     ^
      | available < 0 after the hold           | PARTIAL below the hold (take: the rest)             |
      v                                        v                                                     |
   Declined                             PartiallySettled --------------------------------------------+
                                          |          ^     FINAL, or PARTIAL reaching the hold (take: None)
                                          +----------+
                                   PARTIAL below the hold (take: the rest)
```

A final settlement releases the whole remaining hold and settles for the settlements' sum; a partial one below the hold
keeps the rest. `Settled` and `Declined` have no transition for any settlement, so a settlement against either, or
against an authorization the log does not know, is force-posted: it debits its amount and releases no hold.

## Dynamic View — One Day

```text
run_cli -> LedgerRun.run(CsvFileSource(path, read_text), TextReportSink(out))
  CsvFileSource.read_events(config): read the file, parse it ---> IncomingStream, or a SourceFault
IncomingStream.process, for each event in listed order, D the current day
  1. the event is booked after D: close D (a and b), open D + 1, and look again; a day with no events closes too;
     no day closes after the window's last, so an event booked after the window reaches no day's log or report
  2. otherwise: Ledger.process_event(event, D) ---> the ledger + one entry, and a credit's instalments
       idempotency first, across every account; then a reversal whose target is on another account;
       then the account decides from its own entries, by kind; a reversal checked against its target in order
       an event booked before D is late and is processed on D (AMB-015)
IncomingStream.process, once every event is processed: close every day left in the window

closing day D
  a. Ledger.close_day(D): each step on every account in turn; step 1 AccountIn.assess_fees,
     steps 2 and 3 AccountIn.accrue_interest and .capitalize_interest, each reading one account's entries
       step 1  fees:     each day first..D: negative with no fee in force -> Fee; non-negative with one -> FeeRefund
       step 2  interest: each day first..D: daily interest of its base, less what was generated for it
                         -> InterestAccrual for D, InterestAdjustment for an earlier day
       step 3  capitalization, on a capitalization day: accrued interest above zero -> Capitalization
  b. DayReport.build(ledger, D, reported) ---> DayReport: what D processed and generated, its closings,
       and each earlier closing that changed since last reported
LedgerRun, after the last day
  TextReportSink.publish(reports): render(reports), the whole text, then one write and one flush to standard output
```

Every balance is recomputed from the log whenever it is asked for (D7), so a late event value-dated in the past changes
every later closing without any stored balance being updated. Each sum of money returns a `CurrencyMismatch` rather than
a wrong total when it meets two currencies. The reader keeps every effect in its account's currency, so only a bug
brings one; it ends the processing, and `run_cli` prints `error: internal: ` and exits 2. An event on an account the
ledger does not hold is the other internal fault, `UnknownAccount`, and ends it the same way; the reader refuses such an
event first, so no input reaches it.

## Domain Model

The domain is one bounded context, the Ledger: the brief's accounts, their events, and the days that close them. Every
type in `domain/` belongs to it, and none outside `domain/` holds a ledger rule.

| The brief says                     | The code has                                                                  |
| ---------------------------------- | ----------------------------------------------------------------------------- |
| an account, in its currency        | `AccountIn[M]`, the Account aggregate, with `M` either `Aed` or `Bhd`         |
| an account as the brief opens it   | `AccountOpeningIn[M]`: its `AccountId` and opening balance, in the config     |
| an event in the stream             | `IncomingEvent`: `Credit`, `Debit`, `Authorization`, `Settlement`, `Reversal` |
| the ledger, append-only            | `Ledger`: the configured accounts and one `EventLog` of every domain event    |
| a hold                             | the `hold` of an `Approved` or a `PartiallySettled` authorization             |
| the closing and available balances | `compute_closing` and `compute_available`, methods of `AccountIn`             |
| an overdraft fee, and its refund   | `Fee` and `FeeRefund`, recorded as `FeeCharged` and `FeeRefunded`             |
| interest, and its capitalization   | `InterestAccrual`, `InterestAdjustment`, and `Capitalization`                 |
| a credit paid in instalments       | `Instalment`, one per `InstalmentCount`, recorded as `InstalmentPosted`       |

A type generic over the currency ends in `In`, and the union over its currencies takes the plain noun, per the Python
[naming](../../../../repo-governance/development/quality/stacks/python-standards/001-naming.md) rule: `AccountIn[Aed]`
is an account in AED, and `Account` is either; `AccountOpeningIn[Aed]` is one as the configuration opens it. A caller
outside the aggregate asks it by method, such as `account.compute_closing(day)`; a method call works on the `Account`
union, so no caller needs to know the currency. Every rule about one account is a method of `AccountIn`, in
`account.py`, grouped by topic; one only the class itself calls is private. Where an operation lives, and when kinds of
one concept share a base, follows the Python
[operations](../../../../repo-governance/development/quality/stacks/python-standards/003-operations.md) rule.

**The Account aggregate** is one account and its own entries in the log, `AccountIn[M]`: its ID, its opening balance,
and its `EventLog`, with every rule about the account as one of its methods. A rule reads only the account's own entries
and never the whole log, so no rule can read another account. The aggregate guards the invariants that concern one
account:

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

**The Ledger**, `Ledger` in `domain/ledger/ledger.py`, is the only object that sees every account at once. It holds the
configuration and the one log (AMB-014, AMB-024), refuses what spans accounts before any account decides, an event ID
seen before (AMB-034) and a reversal whose target is on another account (AMB-036), and runs a day's close as each step
on every account in turn. `find_account` builds an account's aggregate from its opening and its own entries, and an
event on an account it does not hold is returned as `UnknownAccount`. Each method returns a new `Ledger`.

**The report** is a read model, outside the domain because it serves the output, not a rule: `application/report.py`
reads the Ledger's log and each account and writes nothing back. `IncomingStream.process` drives the Ledger and the
report over the stream, day by day, and `LedgerRun` is the use case around them, reached through its ports.

## Reading the Code

To read the code for the first time, follow one day through it, in this order:

1. `cli.py`, `run_cli`: where the program starts, and how every failure becomes an exit status.
2. `application/run.py`, `LedgerRun.run`, then `application/stream.py`, `IncomingStream.process`: the use case, and the
   loop over events, where a later day's event closes the current day first, as the dynamic view above draws.
3. `domain/ledger/ledger.py`, `Ledger.process_event`: duplicates and cross-account reversals caught on the whole log.
4. `domain/account/account.py`, `AccountIn.decide_event`: what one incoming event adds to its account.
5. `Ledger.close_day`: the three steps of a day's close, each run on every account.
6. `AccountIn.assess_fees`: when a day is charged an overdraft fee, and when that fee is refunded.
7. `AccountIn.accrue_interest` and `.capitalize_interest`: each day's interest, its adjustment when a closing changes,
   and its capitalization.
8. `AccountIn.compute_closing` and `.compute_available`: the balances, worked out from one account's entries.
9. `domain/account/authorizations.py`: the states and the table a settlement moves them by; then the aggregate's
   authorizations topic, where one is decided and holds money.
10. The aggregate's reversals topic: when a reversal is refused, and which events the posted ones undid.
11. `domain/account/domain_events.py`, `rejections.py`, and `event_log.py`: every domain event the rules record, every
    reason an event is rejected, and the entries each account reads.
12. `application/report.py`, then `adapters/text_report.py`: a day as data, then as the text OUTPUT_TARGET shows.

`adapters/csv_file.py` turns the file into events and holds no ledger rule. `domain/model/`, `events.py`, `config.py`,
`money.py`, and `ids.py`, defines the values the rules pass around; look them up when a name is unfamiliar rather than
reading them first.

## Constraints

- No web layer, persistence, UI, or database.
- Every effect sits in the shell; the domain stays pure and deterministic.
- Balances are recomputed from the append-only log, one account's entries at a time, never stored (D7); nothing in the
  log is changed or removed.
- Holds never expire (AMB-018), the ledger's known weakness.
- Every diagram is plain-text ASCII.
