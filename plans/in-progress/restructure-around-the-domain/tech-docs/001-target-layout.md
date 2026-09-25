# Target Layout

What the application looks like once the plan is executed: the layers and what each may import, the final source and
test trees file by file, and where every current file goes. The types and methods inside each file are in
[the domain model](002-domain-model.md) and
[the application, ports, and adapters](003-application-ports-and-adapters.md).

## Layers

Four layers, hexagonal (R2, R5): the domain at the centre, the application around it declaring the ports it needs, the
adapters implementing those ports, and the shell composing them. Every arrow points inward.

```text
                 argv, the stream file, stdout, stderr
                                  |
+---------------------------- shell ------------------------------+
| cli.py       driving adapter: run_cli maps each fault to the    |
|              exit code and message the README tables publish    |
| challenge.py composition data: CHALLENGE, the brief's config    |
+----------------------------------+------------------------------+
        | RunLedger (driving port)  |  builds the adapters
        v                           v
+---------------- application -----------------+   +----------- adapters -----------+
| ports.py   EventSource, ReportSink, RunLedger |<--| csv_file.py    CsvFileSource    |
| run.py     LedgerRun: read, process, publish  |   |   is an EventSource             |
| stream.py  IncomingStream -> ProcessedStream  |   | text_report.py TextReportSink   |
| report.py  DayReport, the read model          |   |   is a ReportSink               |
+-----------------------+-----------------------+   +---------------+----------------+
                        |                                           |
                        v                                           v
+-------------------------------- domain ----------------------------------------+
| ledger/   Ledger: the config and the one EventLog; every account at once        |
| account/  AccountIn: one account's entries, every rule about it a method;       |
|           EventLog, the domain events, the rejections, the authorization table  |
| model/    money, ids, events, config: values that decide nothing                |
+----------------------------------------+----------------------------------------+
                                         v
                              common/result.py: Ok, Err, Result
```

| Package           | May import                           | Its `ruff.toml` refuses (TID251)                  |
| ----------------- | ------------------------------------ | ------------------------------------------------- |
| `common/`         | nothing else in the package          | `domain`, `application`, `adapters`, the shell    |
| `domain/`         | `common`                             | `application`, `adapters`, the shell              |
| `domain/model/`   | `common`                             | `domain.account`, `domain.ledger`, and above      |
| `domain/account/` | `common`, `domain.model`             | `domain.ledger`, and above                        |
| `domain/ledger/`  | `common`, `domain.model`, `.account` | `application`, `adapters`, the shell              |
| `application/`    | `common`, `domain`                   | `adapters`, the shell                             |
| `adapters/`       | `common`, `domain`, `application`    | the shell                                         |
| the shell         | everything                           | nothing: `cli.py` and `challenge.py` are the edge |

"The shell" is the two modules `account_ledger.cli` and `account_ledger.challenge`; "and above" is every layer after it
in this table. The shell's two modules sit at the package root, so no `ruff.toml` binds them; nothing may import them,
which the bans above enforce from every other side.

## Source Tree

Every `.py` file under `apps/account-ledger-cli/src/account_ledger/` once the plan is done, and nothing else.

```text
src/account_ledger/
├── __init__.py
├── __main__.py              python -m account_ledger runs cli.main
├── challenge.py             CHALLENGE: ACC-001 in AED and ACC-002 in BHD, Days 1 to 6, capitalized on Day 6
├── cli.py                   run_cli and main: the driving adapter and composition root
├── common/
│   ├── __init__.py
│   ├── result.py            Ok, Err, Result
│   └── ruff.toml
├── domain/
│   ├── __init__.py
│   ├── ruff.toml
│   ├── model/
│   │   ├── __init__.py
│   │   ├── config.py        AccountOpeningIn, AccountOpening, is_aed, ConfigFault, LedgerConfig
│   │   ├── events.py        SettlementKind, Whole, Instalments, the eleven event kinds, their unions
│   │   ├── ids.py           IdFault, Day, InstalmentCount, the eight ID kinds, EventId, parse_event_id
│   │   ├── money.py         the money faults, Aed, Bhd, Money, AmountIn, Amount, Direction
│   │   └── ruff.toml
│   ├── account/
│   │   ├── __init__.py
│   │   ├── account.py       AccountIn, Account: the Account aggregate, every rule about one account a method
│   │   ├── authorizations.py the four states, CannotSettle, apply_settlement (the D8 table), AuthorizationRecord
│   │   ├── domain_events.py the fifteen domain events, LogEntry, LoggedEvent
│   │   ├── event_log.py     EventLog: append-only entries, the whole ledger's or one account's
│   │   ├── rejections.py    the seven reasons an event is refused, Rejection
│   │   └── ruff.toml
│   └── ledger/
│       ├── __init__.py
│       ├── ledger.py        Ledger, UnknownAccount, InternalFault
│       └── ruff.toml
├── application/
│   ├── __init__.py
│   ├── ports.py             SourceFault, EventSource, ReportSink, RunLedger, RunFault
│   ├── report.py            DayReport, its rows, Restatement, ReportedClosings, Step, Note
│   ├── run.py               LedgerRun: the one use case
│   ├── stream.py            IncomingStream, ProcessedStream
│   └── ruff.toml
└── adapters/
    ├── __init__.py
    ├── csv_file.py          Reader, read_file, StreamError, CsvFileSource
    ├── text_report.py       TextOutput, TextReportSink
    └── ruff.toml
```

Today the package holds 31 modules and 5 `ruff.toml` files; after, 28 modules and 7 `ruff.toml` files, counting each
`__init__.py` as a module.

## Test Tree

One test file per source module that has tests (R13), under a directory that mirrors the source package. A module with
no test of its own, such as `domain_events.py`, whose values the aggregate's tests read, has no file.

```text
tests/
├── e2e/
│   └── test_program.py                  the program as a process: the golden run and the error paths
├── integration/
│   ├── adapters/
│   │   └── test_csv_file.py             the shipped stream read from disk
│   └── test_cli.py                      main on the real descriptors
├── support/
│   ├── brief_stream.py                  the brief's stream in code and as CSV
│   ├── output_target.py                 OUTPUT_TARGET's fenced block
│   ├── entries.py                       readers that turn a log into what a test asserts (R22)
│   ├── refusals.py                      one stream per refusal reason
│   ├── results.py                       unwrap_ok
│   ├── streams.py                       builders of the short streams the rule tests process
│   └── values.py                        make_aed, make_bhd
└── unit/
    ├── adapters/
    │   ├── test_csv_file.py             every stream fault, and the brief's stream read
    │   └── test_text_report.py          every rendering rule
    ├── application/
    │   ├── test_report.py               restatements, authorizations, errors, empty steps
    │   └── test_stream.py               the day-by-day processing, criteria C1 to C8, the known weakness
    ├── common/
    │   └── test_result.py
    ├── domain/
    │   ├── account/
    │   │   ├── test_account.py          fees, interest, reversals, holds, settlements, decisions
    │   │   └── test_authorizations.py   the D8 table
    │   ├── ledger/
    │   │   └── test_ledger.py           idempotency, the cross-account refusal, an unknown account
    │   └── model/
    │       ├── test_config.py
    │       ├── test_events.py           the instalments' guard (new)
    │       ├── test_ids.py
    │       └── test_money.py
    └── test_cli.py                      run_cli with fake ports
```

`--import-mode=importlib`, already set in `pyproject.toml`, lets two test files share a basename in different
directories, as `test_cli.py` and `test_csv_file.py` do; a probe on 2026-09-25 collected and type-checked such a pair.

## How the Names Read

The layout follows five patterns, so a reader who knows one file can guess the name of the next (R22):

- **A module is named for its concept, and its main type for the concept made precise.** `ledger.py` holds `Ledger`,
  `account.py` `AccountIn`, `event_log.py` `EventLog`, `report.py` `DayReport`, `stream.py` `IncomingStream`, `run.py`
  `LedgerRun`, `csv_file.py` `CsvFileSource`, and `text_report.py` `TextReportSink`.
- **A module holding one concept is singular; one holding a family is plural.** `money.py`, `config.py`, `account.py`,
  `ledger.py`, and `result.py` against `ids.py`, `events.py`, `domain_events.py`, `rejections.py`, `authorizations.py`,
  and `ports.py`.
- **A type generic over the currency ends in `In`, and its union drops the suffix.** `AmountIn` and `Amount`,
  `AccountIn` and `Account`, `AccountOpeningIn` and `AccountOpening`.
- **An adapter is named for its medium and the port it fills.** `CsvFileSource` is an `EventSource`, and
  `TextReportSink` a `ReportSink`.
- **A test file mirrors its source.** `src/account_ledger/X/Y.py` is tested in `tests/<suite>/X/test_Y.py`, and
  `tests/support/` holds what several test files share, builders apart from readers: `streams.py`, `brief_stream.py`,
  `refusals.py`, and `values.py` build inputs; `entries.py` and `output_target.py` read what a test compares;
  `results.py` unwraps a `Result` a test expects to be `Ok`. The e2e suite has one file, `test_program.py`, since it
  tests the program as a whole rather than a module.

`EventLog` sits in `account/`, below the ledger, because the aggregate reads its own entries through it and the ledger
holds the same type for every account; the ledger imports downward, never the reverse.

## Where Every Current File Goes

Source, under `src/account_ledger/`:

| Now                                | After                                                                         |
| ---------------------------------- | ----------------------------------------------------------------------------- |
| `cli.py`                           | `cli.py`, composing ports; its file reader goes to `adapters/csv_file.py`     |
| `adapters/stream_csv.py`           | `adapters/csv_file.py`, as `CsvFileSource`                                    |
| `adapters/render.py`               | `adapters/text_report.py`, as `TextReportSink`                                |
| `domain/stream_processing.py`      | `application/stream.py`                                                       |
| `domain/report.py`                 | `application/report.py`                                                       |
| `domain/ledger/processing.py`      | `domain/ledger/ledger.py`, `Ledger.process_event`                             |
| `domain/ledger/end_of_day.py`      | `domain/ledger/ledger.py`, `Ledger.close_day`                                 |
| `domain/ledger/event_log.py`       | `EventLog` in `domain/account/event_log.py`; `Ledger.find_account`            |
| `domain/account/aggregate.py`      | `domain/account/account.py`                                                   |
| `domain/account/history.py`        | `account.py`; `find_first_entry` becomes `EventLog.find_first_entry`          |
| `domain/account/balances.py`       | `domain/account/account.py`                                                   |
| `domain/account/decisions.py`      | `domain/account/account.py`                                                   |
| `domain/account/fees.py`           | `domain/account/account.py`                                                   |
| `domain/account/interest.py`       | `domain/account/account.py`                                                   |
| `domain/account/reversals.py`      | `domain/account/account.py`                                                   |
| `domain/account/authorizations.py` | stays for the table, states, and record; its history rules go to `account.py` |
| `domain/account/states.py`         | `domain/account/authorizations.py`                                            |
| `domain/account/domain_events.py`  | stays for the domain events; the rejection reasons go to `rejections.py`      |
| `domain/model/config.py`           | stays; `CHALLENGE` goes to `challenge.py`                                     |
| `domain/model/*.py`, `common/`     | stay, reshaped as [the domain model](002-domain-model.md) says                |

Tests, under `tests/`:

| Now                                | After                                                                       |
| ---------------------------------- | --------------------------------------------------------------------------- |
| `unit/test_result.py`              | `unit/common/test_result.py`                                                |
| `unit/test_money.py`               | `unit/domain/model/test_money.py`                                           |
| `unit/test_ids.py`                 | `unit/domain/model/test_ids.py`                                             |
| `unit/test_config.py`              | `unit/domain/model/test_config.py`                                          |
| `unit/test_fees.py`                | `unit/domain/account/test_account.py`                                       |
| `unit/test_interest.py`            | `unit/domain/account/test_account.py`                                       |
| `unit/test_reversals.py`           | `unit/domain/account/test_account.py`; the AMB-036 test to `test_ledger.py` |
| `unit/test_authorizations.py`      | `unit/domain/account/test_account.py`; the two table tests stay by name in  |
|                                    | `unit/domain/account/test_authorizations.py`                                |
| `unit/test_processing.py`          | `unit/domain/ledger/test_ledger.py`                                         |
| `unit/test_stream_processing.py`   | `unit/application/test_stream.py`                                           |
| `unit/test_criteria.py`            | `unit/application/test_stream.py`                                           |
| `unit/test_known_weakness.py`      | `unit/application/test_stream.py`                                           |
| `unit/test_report.py`              | `unit/application/test_report.py`                                           |
| `unit/test_stream_csv.py`          | `unit/adapters/test_csv_file.py`                                            |
| `unit/test_render.py`              | `unit/adapters/test_text_report.py`                                         |
| `unit/test_cli.py`                 | `unit/test_cli.py`                                                          |
| `integration/test_stream_file.py`  | `integration/adapters/test_csv_file.py`                                     |
| `integration/test_main.py`         | `integration/test_cli.py`                                                   |
| `e2e/test_program.py`, `support/*` | stay, save `support/states.py`, whose readers join `support/entries.py`     |

The two table tests are `test_every_state_and_settlement_input_pair_follows_the_table` and
`test_an_unconfigured_transition_leaves_the_state_unchanged`. Every test keeps its name and its cases; only its file and
the calls it makes move ([behaviour preservation](004-behaviour-preservation-and-tests.md)).
