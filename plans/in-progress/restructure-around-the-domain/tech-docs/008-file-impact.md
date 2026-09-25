# File Impact

Every path the plan touches, rooted at the repository root, as
[file impact](../../../../repo-governance/conventions/structure/plans/013-file-impact.md) requires. Exact paths only; no
pattern family is used. The `apps/account-ledger-cli/` prefix is written once per block.

## Source: `apps/account-ledger-cli/src/account_ledger/`

```text
apps/account-ledger-cli/src/account_ledger/
├── challenge.py                       [N] CHALLENGE, from domain/model/config.py
├── cli.py                             [E] run_cli takes TextOutput streams and a RunLedger; main composes
├── common/
│   └── ruff.toml                      [E] bans application and challenge too
├── domain/
│   ├── __init__.py                    [E] docstring: the report leaves
│   ├── ruff.toml                      [E] bans application and the shell's two modules
│   ├── report.py                      [M] to application/report.py
│   ├── stream_processing.py           [M] to application/stream.py
│   ├── model/
│   │   ├── config.py                  [E] AccountOpeningIn, AccountOpening; CHALLENGE leaves
│   │   ├── events.py                  [E] flat fields; Instalments holds parts; make_instalments; signed money
│   │   ├── ids.py                     [E] flat fields; IdFault first; classmethod make and parse
│   │   ├── money.py                   [E] Aed and Bhd without a base; add_all, require_same, take, directed amount
│   │   └── ruff.toml                  [E] bans application, adapters, and the shell
│   ├── account/
│   │   ├── __init__.py                [E] docstring: entries, not history
│   │   ├── account.py                 [N] AccountIn, every rule about one account a method
│   │   ├── aggregate.py               [D] into account.py
│   │   ├── authorizations.py          [E] the states, the record, the D8 table on kind and rest
│   │   ├── balances.py                [D] into account.py
│   │   ├── decisions.py               [D] into account.py
│   │   ├── domain_events.py           [E] flat fields; the rejection reasons leave
│   │   ├── event_log.py               [N] EventLog
│   │   ├── fees.py                    [D] into account.py
│   │   ├── history.py                 [D] into account.py and event_log.py
│   │   ├── interest.py                [D] into account.py
│   │   ├── rejections.py              [N] the seven reasons and Rejection, from domain_events.py
│   │   ├── reversals.py               [D] into account.py
│   │   ├── states.py                  [D] into authorizations.py
│   │   └── ruff.toml                  [E] bans application, adapters, and the shell
│   └── ledger/
│       ├── __init__.py                [E] docstring: the Ledger, not the log
│       ├── end_of_day.py              [D] into ledger.py
│       ├── event_log.py               [D] EventLog to account/event_log.py, the dispatch to Ledger.find_account
│       ├── ledger.py                  [M] from processing.py; Ledger, UnknownAccount, InternalFault
│       ├── processing.py              [M] to ledger.py
│       └── ruff.toml                  [E] bans application, adapters, and the shell
├── application/
│   ├── __init__.py                    [N] package docstring
│   ├── ports.py                       [N] SourceFault, EventSource, ReportSink, RunLedger, RunFault
│   ├── report.py                      [M] from domain/report.py; DayReport.build, ReportedClosings class
│   ├── run.py                         [N] LedgerRun
│   ├── stream.py                      [M] from domain/stream_processing.py; IncomingStream, ProcessedStream
│   └── ruff.toml                      [N] bans adapters and the shell
└── adapters/
    ├── __init__.py                    [E] docstring: the ports' implementations
    ├── csv_file.py                    [M] from stream_csv.py; CsvFileSource, Reader, read_file
    ├── render.py                      [M] to text_report.py
    ├── stream_csv.py                  [M] to csv_file.py
    ├── text_report.py                 [M] from render.py; TextOutput, TextReportSink
    └── ruff.toml                      [N] bans the shell
```

## Tests: `apps/account-ledger-cli/tests/`

```text
apps/account-ledger-cli/tests/
├── integration/
│   ├── test_main.py                             [M] to integration/test_cli.py
│   ├── test_cli.py                              [M] from test_main.py; imports follow the new API
│   ├── test_stream_file.py                      [M] to integration/adapters/test_csv_file.py
│   └── adapters/test_csv_file.py                [M] from test_stream_file.py
├── support/
│   ├── brief_stream.py                          [E] Instalments.make for E10
│   ├── entries.py                               [N] the log readers of states.py and streams.py (R22)
│   ├── refusals.py                              [E] the rejection reasons from rejections.py
│   ├── states.py                                [D] into entries.py
│   └── streams.py                               [E] builders only; ACC_001_OPENING, ACC_002_OPENING
└── unit/
    ├── test_authorizations.py                   [D] into domain/account/test_account.py and test_authorizations.py
    ├── test_cli.py                              [E] fake RunLedger; plain ClosedPipe; the unknown-account test
    ├── test_config.py                           [M] to domain/model/test_config.py
    ├── test_criteria.py                         [D] into application/test_stream.py
    ├── test_fees.py                             [D] into domain/account/test_account.py
    ├── test_ids.py                              [M] to domain/model/test_ids.py
    ├── test_interest.py                         [D] into domain/account/test_account.py
    ├── test_known_weakness.py                   [D] into application/test_stream.py
    ├── test_money.py                            [M] to domain/model/test_money.py; two new tests
    ├── test_processing.py                       [M] to domain/ledger/test_ledger.py
    ├── test_render.py                           [M] to adapters/test_text_report.py
    ├── test_report.py                           [M] to application/test_report.py
    ├── test_result.py                           [M] to common/test_result.py
    ├── test_reversals.py                        [D] into domain/account/test_account.py and test_ledger.py
    ├── test_stream_csv.py                       [M] to adapters/test_csv_file.py
    ├── test_stream_processing.py                [M] to application/test_stream.py
    ├── adapters/test_csv_file.py                [M] from test_stream_csv.py
    ├── adapters/test_text_report.py             [M] from test_render.py
    ├── application/test_report.py               [M] from test_report.py
    ├── application/test_stream.py               [M] from test_stream_processing.py, with two files merged in
    ├── common/test_result.py                    [M] from test_result.py
    ├── domain/account/test_account.py           [N] four files merged
    ├── domain/account/test_authorizations.py    [N] the two table tests
    ├── domain/ledger/test_ledger.py             [M] from test_processing.py; the AMB-036 and unknown-account tests
    ├── domain/model/test_config.py              [M] from test_config.py
    ├── domain/model/test_events.py              [N] the instalments' guard
    ├── domain/model/test_ids.py                 [M] from test_ids.py
    └── domain/model/test_money.py               [M] from test_money.py
```

## Configuration, Specifications, Rules, and Documents

```text
.
├── WORKLOG.md                                                        [E] one entry per session
├── README.md                                                         [E] the layers, in one sentence
├── apps/account-ledger-cli/README.md                                 [E] layout, DDD paragraph, exit row, weakness
├── apps/account-ledger-cli/pyproject.toml                            [E] too-many-ancestors; the verb lists
├── docs/explanation/architecture-trade-offs.md                       [E] entries wording; re-measured timings
├── specs/apps/account-ledger/cli/architecture.md                     [E] L3, L4, dynamic view, model, reading order
├── plans/in-progress/README.md                                       [E] directory map lists this plan
├── plans/done/README.md                                              [E] at archival, lists this plan
├── repo-governance/development/quality/stacks/python-standards.md    [E] the operations summary, enforcement
└── repo-governance/development/quality/stacks/python-standards/
    ├── 001-naming.md                                                 [E] parse_event_id as the example
    ├── 003-operations.md                                             [E] four cases; No Inheritance section
    └── README.md                                                     [E] the module table's row
```

## The Plan

```text
plans/in-progress/restructure-around-the-domain/
├── README.md                                  [N] status, scope, navigation; maps evidence/
├── brd.md                                     [N] business goal, outcomes, risks
├── prd.md                                     [N] personas, stories, acceptance criteria
├── delivery.md                                [N] execution record, phases, gates
├── learnings.md                               [N] what execution discovers
├── tech-docs/README.md                        [N] the companions in order
├── tech-docs/001-target-layout.md             [N]
├── tech-docs/002-domain-model.md              [N]
├── tech-docs/003-application-ports-and-adapters.md [N]
├── tech-docs/004-behaviour-preservation-and-tests.md [N]
├── tech-docs/005-specification-rule-and-doc-changes.md [N]
├── tech-docs/006-migration-inventory.md       [N]
├── tech-docs/007-decision-records.md          [N]
├── tech-docs/008-file-impact.md               [N]
├── evidence/README.md                        [N] the evidence folder's map, which the directory-map gate requires
├── evidence/phase-0-baseline.txt              [N] gates, counts, and the baseline manifest
├── evidence/phase-0-corpus.txt                [N] the behaviour corpus on the baseline
├── evidence/phase-0-tests.txt                 [N] the test inventory on the baseline
├── evidence/phase-0-literals.txt              [N] each test's literals on the baseline
├── evidence/phase-5-no-inheritance.txt        [N] the gate failing on the baseline, passing on the tree
├── evidence/phase-8-corpus.txt                [N] the corpus on the result
├── evidence/phase-8-tests.txt                 [N] the test inventory on the result
├── evidence/phase-8-literals.txt              [N] each test's literals on the result
├── evidence/phase-8-mutations.txt             [N] the mutation spot-checks
└── evidence/phase-8-timings.txt               [N] the re-measured timings
```

### More Detail

- Files the plan leaves as they are, such as `__main__.py`, `common/result.py`, and `tests/support/values.py`, are not
  in the tree. Phase 6 reads every file; where its comb finds a defect in an unlisted file, its item names the file and
  the Execution Record notes that the tree grew.
- `local-tmp/restructure/` holds the scratch scripts Phase 0 writes (`corpus.py`, `inventory.py`, `test_literals.py`,
  `cited_names.py`, `scale.py`, `doc_sweep.py`, `audit.py`, `gate.sh`), the probes, and the baseline copy. The folder is
  gitignored, so it is not in the tree above.
- At archival the plan folder moves to `plans/done/<completion-date>__restructure-around-the-domain/` with every file
  above; no file changes in the move.
