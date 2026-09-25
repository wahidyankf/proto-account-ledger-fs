# Delivery

The executable part of this plan. Every item names its paths, its command where one exists, its executor, its proof, and
the acceptance criteria it serves from [prd](prd.md). Why each item exists is in the other five documents; read them
first, above all [the target layout](tech-docs/001-target-layout.md) and
[behaviour preservation](tech-docs/004-behaviour-preservation-and-tests.md).

## Execution Record

## Execution Checkout

- **Working copy.** The main checkout at the repository root, on `main`, with no worktree and no task branch, per the
  [integration path](../../../repo-governance/development/workflow/integration-path.md). Git is invoked as
  `/usr/bin/git`, which the local rtk guard lets through.
- **Delivery mode.** Direct commits to local `main`, pushed to `origin/main` at each phase gate. The owner's goal of
  2026-09-25 authorizes the commits and pushes the gates name, and no other.
- **Commands.** `pytest` below means `uv run --no-sync pytest`, run from `apps/account-ledger-cli`; every other command
  runs from the repository root. `APP` is `apps/account-ledger-cli`, `SRC` is `$APP/src/account_ledger`, and `EV` is
  `plans/in-progress/restructure-around-the-domain/evidence`.

## Delivery Units

Each phase is one delivery unit: one theme, one outcome its gate proves, and one rollback.

- **Owner.** This repository; no other repository is touched.
- **Outcome.** The phase gate's commands exit 0 on the phase's combined state, and the behaviour corpus equals Phase
  0's.
- **Rollback.** `/usr/bin/git revert` of the unit's commits, as new commits, pushed; never a reset, amend, or force-push
  (RC3).
- **Commits.** One or more thematic Conventional Commits, each build-valid, so no commit holds a failing test or a
  half-moved module; red evidence lives in this file, not in history.

## Pause Safety

At any pause the Execution Record carries the last gate passed, the next unticked item, and any bounded budget partly
spent. A resumed session rebuilds its task list from the unticked items here, first confirming that each ticked item's
change is present, and continues. The working tree between a phase's items may hold a half-moved module; its state is
the unticked items, and `sh local-tmp/restructure/gate.sh` tells whether it is coherent.

## How an Item Is Worked

- **Refactor items.** A move, merge, or reshape changes no behaviour, so it is not a test-first cycle: it starts from a
  green run, moves in small steps, and runs `pytest tests` after each, per [cycle and evidence][cycle]. A test that goes
  red during a refactor marks a defect the refactor made, fixed before the item is ticked.
- **Deletion items.** A module is deleted only after the six steps of
  [the migration inventory](tech-docs/006-migration-inventory.md#deletion-with-proof): the item records the rule it
  broke in the successor, the test that failed, and the restore.
- **New behaviour.** Each of the five new tests is a cycle of three items, RED, GREEN, and REFACTOR. A RED counts only
  when the new test fails on its assertion; where the code it calls does not exist yet, the RED adds a stub whose wrong
  answer the assertion catches, and says so.
- **Mutation hygiene.** Every confirming run after a mutation's restore goes through `sh local-tmp/run.sh`, which
  deletes each `__pycache__` under `src` and `tests` first, as the Python standards' Mutation Proofs require.
- **Results, not ticks.** Each ticked item carries, indented under it, what it produced: the command, its output or its
  head, and anything that surprised. Discoveries go to [learnings](learnings.md) when they happen.
- **Architecture as built.** A phase that changes a component updates `specs/apps/account-ledger/cli/architecture.md`
  and the application README in the same unit, never later.

## Parallelization Model

Every node is serial, and the concurrency limit is one executor in one checkout, the repository's only mode.

- Phase 0 records the state everything else is compared with.
- Phases 1 to 4 each import what the phase before reshaped: the aggregate reads the values, the Ledger the aggregate,
  the application the Ledger. They share `architecture.md` and the test support modules.
- Phase 5's gate reads every class Phases 1 to 4 wrote, and its rule describes their result.
- Phase 6 reads every file after the moves; Phase 7 describes the polished result; Phase 8 verifies it.
- Cleanup is the terminal node, after every unit has landed and before the archival move.

## Phase 0 — Baseline

Records the state every later gate is compared with, and writes the scratch tools the gates run. No application file
changes.

- [ ] [AI] Confirm the checkout: on `main`, level with `origin/main`, nothing uncommitted but ignored scratch. Command:
      `/usr/bin/git fetch origin && /usr/bin/git status -sb`. Proof: the output. Acceptance: AC-16.
- [ ] [AI] Install the toolchain. Command: `npm install && (cd $APP && uv sync --locked)`. Proof: exit 0. Acceptance:
      AC-16.
- [ ] [AI] Write `local-tmp/run.sh`, which deletes every `__pycache__` under `$APP/src` and `$APP/tests` and then runs
      its arguments, and `local-tmp/check-md.sh`, which runs Prettier on every changed or untracked Markdown file and
      fails on a line past 120 outside `repo-governance/` and the harness directories. Command:
      `sh local-tmp/check-md.sh`. Proof: exit 0 on the clean checkout. Acceptance: AC-16.
- [ ] [AI] Record the baseline gates with `--skip-nx-cache`: `test:quick`, `test:integration`, `test:e2e`, and
      `npm run -s check:hygiene`, with the unit counts and the coverage figure, into `$EV/phase-0-baseline.txt`, headed
      by the commands, the commit, and the time. Proof: every exit 0; a failure is fixed at its cause here and recorded
      as pre-existing. Acceptance: AC-16.
- [ ] [AI] Extract the baseline copy: `mkdir -p local-tmp/restructure/baseline` and
      `/usr/bin/git archive 83dfd58 apps/account-ledger-cli | tar -x -C local-tmp/restructure/baseline`; append the
      manifest, the commit and the command, and `find ... -name '*.py' | wc -l` of the copy, to
      `$EV/phase-0-baseline.txt`. Proof: 31 source and 26 test modules in the copy. Acceptance: AC-02.
- [ ] [AI] Write `local-tmp/restructure/corpus.py` with every input group
      [behaviour preservation](tech-docs/004-behaviour-preservation-and-tests.md#the-behaviour-corpus) lists. It takes
      the application directory, writes each input into a fresh temporary directory, runs
      `uv run --no-sync --project <app> python -m account_ledger <relative path>` there with `PYTHONPATH=<app>/src`, and
      prints one block per input: name, exit code, standard error, standard output's SHA-256 and line count. Command:
      `python3 local-tmp/restructure/corpus.py local-tmp/restructure/baseline/apps/account-ledger-cli`. Proof: every
      group present; the brief's block shows exit 0 and the golden fence's hash. Acceptance: AC-02.
- [ ] [AI] Record the corpus on the baseline into `$EV/phase-0-corpus.txt`, then run it on the working tree and compare,
      proving the script deterministic. Command: the two commands in
      [the corpus section](tech-docs/004-behaviour-preservation-and-tests.md#the-behaviour-corpus). Proof:
      `diff -I '^#'` prints nothing. Acceptance: AC-02.
- [ ] [AI] Write `local-tmp/restructure/inventory.py`, which runs `pytest --collect-only -q` over `tests` and prints
      each test function's name and case count, sorted, and a `--compare BASELINE` mode that fails if a baseline name is
      missing or has another count, and lists every added name. Record `$EV/phase-0-tests.txt`. Proof: 157 cases, 115
      names. Acceptance: AC-03.
- [ ] [AI] Run `python3 local-tmp/restructure/cited_names.py`. Proof: `cited 60 defined 115 missing 0`. Acceptance:
      AC-04.
- [ ] [AI] Measure the baseline timings with `local-tmp/restructure/scale.py 6 30 60 120` against the baseline copy, and
      the 1,000-event volume run, and append them to `$EV/phase-0-baseline.txt`. Proof: four window lines and one volume
      line. Acceptance: AC-14.
- [ ] [AI] Write `local-tmp/restructure/gate.sh`, the bundle every phase gate runs, in this order, stopping at the first
      failure: `sh local-tmp/run.sh npx nx run account-ledger-cli:test:quick --skip-nx-cache`, the same for
      `test:integration` and `test:e2e`, the corpus compared with `$EV/phase-0-corpus.txt`,
      `inventory.py --compare     $EV/phase-0-tests.txt`, `cited_names.py`, `sh local-tmp/check-md.sh`, and
      `npm run -s check:hygiene`. Command: `sh local-tmp/restructure/gate.sh`. Proof: exit 0 on the baseline tree.
      Acceptance: AC-16.

### Phase 0 Gate

- [ ] [AI] Run `sh local-tmp/restructure/gate.sh`, `./rhino md internal-link validate`,
      `./rhino md heading-hierarchy validate`, and `./rhino md naming validate`. Proof: each exit 0. Acceptance: AC-16.
- [ ] [AI] Add the `WORKLOG.md` entry, record this phase's Execution Record line, and commit `$EV/phase-0-*.txt`, this
      file, and `WORKLOG.md` as `docs(plan): record the restructure's baseline`; push. Command:
      `/usr/bin/git push origin main`. Proof: the hash and the pushed range. Acceptance: AC-16.

Pause safety: the baseline is on `origin/main`. Re-verify with `sh local-tmp/restructure/gate.sh`.

## Phase 1 — The Values Own Their Operations

Reshapes `domain/model/` as [the domain model](tech-docs/002-domain-model.md) states, moves `CHALLENGE` to the shell,
and moves the value tests (R3, R4, R8, R14, R15).

- [ ] [AI] Reorder `money.py`: constants, faults, private functions, then the types. Paths:
      `$SRC/domain/model/money.py`. Command: `pytest tests`. Proof: 147 passed, 1 xfailed, and
      `grep -n "^class\|^[A-Z_]* = " money.py` in the new order. Acceptance: AC-06.
- [ ] [AI] Give `Aed` and `Bhd` their own fields, `ClassVar`s, and methods, delete `_MoneyBase`, and add `require_same`,
      `add_all`, and `compute_daily_interest` as methods over private functions; switch every caller of
      `require_same_currency`, `sum_money`, and `compute_daily_interest` in `src` and `tests` to the methods, and delete
      the three functions. Paths: `money.py`, `$SRC/domain/account/{authorizations,balances,fees,interest}.py`,
      `$APP/tests/unit/test_money.py`. Command: `pytest tests && cd $APP && uv run --no-sync pyright`. Proof: both pass;
      `grep -rn "sum_money\|require_same_currency\|_MoneyBase" $APP` prints nothing. Acceptance: AC-06, AC-08.
- [ ] [AI] RED: `test_taking_all_of_a_hold_or_more_leaves_nothing` in `tests/unit/test_money.py`: `take` of an amount
      equal to the hold and of one above it gives `Ok(None)`, and of one below gives the rest. The RED adds a stub
      `AmountIn.take` returning `Ok(self)`. Command: `pytest tests/unit/test_money.py`. Proof: fails on its assertion.
      Acceptance: AC-03, AC-06.
- [ ] [AI] GREEN: `take` as [the domain model](tech-docs/002-domain-model.md#domainmodelmoneypy) states. Command:
      `pytest tests`. Proof: passes. Acceptance: AC-06.
- [ ] [AI] REFACTOR: docstring and definition order; `compute_rest` stays until Phase 2 replaces its one caller.
      Command: `pytest tests`. Proof: passes. Acceptance: AC-06.
- [ ] [AI] RED: `test_a_zero_change_has_no_direction`: `make_directed_amount` gives `(UP, 0.40)` for AED 0.40,
      `(DOWN, 0.40)` for AED −0.40, and `None` for zero. The RED adds a stub returning `None`. Command:
      `pytest tests/unit/test_money.py`. Proof: fails on its assertion. Acceptance: AC-03, AC-06.
- [ ] [AI] GREEN: `make_directed_amount` on both currencies. Command: `pytest tests`. Proof: passes. Acceptance: AC-06.
- [ ] [AI] REFACTOR: `interest._record_interest_change` takes the direction and amount `make_directed_amount` gives, and
      `accrue_interest` skips `None`; its `assert` goes. Command: `pytest tests` and the corpus compare. Proof: passes;
      equal. Acceptance: AC-02, AC-06.
- [ ] [AI] Reshape `ids.py`: `IdFault` first; `_TextIdBase` and `_DayEventIdBase` deleted, each kind with its own fields
      and `ClassVar`s over `_check_text`, `_parse_text`, and `_format_day_event_id`; `make` and `parse` classmethods on
      `Day` and `InstalmentCount`. Paths: `$SRC/domain/model/ids.py`. Command: `pytest tests`. Proof: passes;
      `grep -n "Base" ids.py` prints nothing. Acceptance: AC-06, AC-07.
- [ ] [AI] Flatten `events.py`: every kind declares its own fields in today's order; `_IncomingEventBase` and
      `_GeneratedEventBase` deleted; `compute_signed_money` on the two interest kinds replaces
      `interest._sign_interest`, deleted. Paths: `$SRC/domain/model/events.py`, `$SRC/domain/account/interest.py`.
      Command: `pytest tests`. Proof: passes. Acceptance: AC-06, AC-07, AC-08.
- [ ] [AI] `Instalments(count, parts)` with `Instalments.make`, and `Credit.make_instalments`; the stream reader and
      `tests/support/brief_stream.py` and `streams.py` build postings through `make`; `decisions._generate_instalments`
      wraps `make_instalments` and loses its `assert`. Paths: `events.py`, `$SRC/adapters/stream_csv.py`,
      `$SRC/domain/account/decisions.py`, the two support modules. Command: `pytest tests` and the corpus compare.
      Proof: passes; equal, the `TooManyInstalments` input included. Acceptance: AC-02, AC-06.
- [ ] [AI] RED: `test_instalments_refuse_parts_whose_number_is_not_the_count` in the new
      `tests/unit/domain/model/test_events.py`: `Instalments(InstalmentCount(2), three parts)` raises `ValueError`.
      Command: `pytest tests/unit/domain/model/test_events.py`. Proof: fails with `DID NOT RAISE`. Acceptance: AC-03.
- [ ] [AI] GREEN: the guard in `Instalments.__post_init__`. Command: `pytest tests`. Proof: passes. Acceptance: AC-03.
- [ ] [AI] REFACTOR: none beyond the docstring; recorded as such. Command: `pytest tests`. Proof: passes. Acceptance:
      AC-03.
- [ ] [AI] Rename `AccountIn` and `Account` in `config.py` to `AccountOpeningIn` and `AccountOpening`, field `opening`
      to `balance`, and every user; move `CHALLENGE` to the new `$SRC/challenge.py`, and every importer to it. Command:
      `pytest tests && grep -rn "config import.*CHALLENGE" $APP`. Proof: passes; the grep prints nothing. Acceptance:
      AC-08, AC-13.
- [ ] [AI] Remove `sign` from both verb lists in `pyproject.toml` once nothing uses it. Command:
      `cd $APP && uv run --no-sync pylint src tests`. Proof: exit 0. Acceptance: AC-15.
- [ ] [AI] Move the value tests with `/usr/bin/git mv`: `test_money.py`, `test_ids.py`, `test_config.py` to
      `tests/unit/domain/model/`, and `test_result.py` to `tests/unit/common/`. Command: `pytest tests`. Proof: passes
      with the same count. Acceptance: AC-03, AC-13.
- [ ] [AI] Update the architecture as built: L3's `model/` rows and `challenge`, L4's money, ids, events, and config
      blocks. Paths: `specs/apps/account-ledger/cli/architecture.md`. Proof: every name in those blocks exists (`grep`
      each). Acceptance: AC-14.

### Phase 1 Gate

- [ ] [AI] Run `sh local-tmp/restructure/gate.sh`. Proof: exit 0; the inventory lists exactly three added names.
      Acceptance: AC-02, AC-03, AC-04, AC-06.
- [ ] [AI] Commit as `refactor(cli): give each value its own operations, without a base` (and the new tests with it),
      add the `WORKLOG.md` entry and the Execution Record line, and push. Proof: the hash and range. Acceptance: AC-16.

Pause safety: the values are reshaped on `origin/main`. Re-verify with `sh local-tmp/restructure/gate.sh`.

## Phase 2 — The Account Aggregate Is One Class

Builds `AccountIn` in `domain/account/account.py` and moves every rule about one account into it, topic by topic (R1,
R6, R7, R8, R17).

- [ ] [AI] Move the seven rejection reasons and `Rejection` from `domain_events.py` to the new `rejections.py`, and
      every importer. Paths: `$SRC/domain/account/{domain_events,rejections}.py`, `tests/support/refusals.py`, tests.
      Command: `pytest tests`. Proof: passes. Acceptance: AC-13.
- [ ] [AI] Flatten the domain events: each declares `event` and `processed_day`; `_DomainEventBase` deleted. Command:
      `pytest tests`. Proof: passes. Acceptance: AC-07.
- [ ] [AI] Write `EventLog` in the new `$SRC/domain/account/event_log.py` with `append`, `find_first_entry`, `select`,
      and `list_processed_on`. The ledger's `Log` alias stays until Phase 3; `find_history` wraps the account's entries
      in an `EventLog`. Command: `pytest tests`. Proof: passes. Acceptance: AC-10.
- [ ] [AI] Replace `AccountHistoryIn` and `AccountAggregateIn` with `AccountIn(id, opening, log)` in the new
      `account.py`, its public methods forwarding to the topic modules as `AccountAggregateIn`'s do today, and the entry
      queries (`list_instalments`, `_find_entry`, `_list_counted_events`, `_with_entry`, `_make_zero`) as methods; every
      topic module takes an `AccountIn`. Delete `history.py` and `aggregate.py` with proof: break `_find_entry` to
      return `None`, see a reversal test fail, restore. Command: `pytest tests`. Proof: passes; the mutation's failing
      test named. Acceptance: AC-09, AC-13.
- [ ] [AI] Move `balances.py` into `AccountIn` as `compute_closing`, `compute_available`, and the three private methods;
      delete the module with proof (break `_list_undone_amounts`, see an AMB-028 test fail, restore). Command:
      `pytest tests`, the corpus compare. Proof: passes; equal; mutation recorded. Acceptance: AC-02, AC-09.
- [ ] [AI] Move the history rules of `authorizations.py` (`list_records`, `find_record`, `sum_holds`, and
      `decide_authorization` folded into `_decide_authorization_entry`) into `AccountIn`; `_is_referenced_by` becomes
      `AuthorizationRecord.is_referenced_by`. Command: `pytest tests`, the corpus compare. Proof: passes; equal.
      Acceptance: AC-02, AC-08, AC-09.
- [ ] [AI] Rewrite the D8 table as `apply_settlement(state, kind, amount)` over `take`, as
      [the domain model](tech-docs/002-domain-model.md#authorizationspy) shows; delete `FinalSettlement`,
      `PartialSettlement`, `_SettlementInputBase`, `SettlementInput`, `derive_settlement_input`,
      `_is_settlement_below_hold`, `_make_partial_settlement`, `_compute_rest` and its `assert`, and
      `AmountIn.compute_rest`, whose test assertion moves to `take`; the two table tests build their cases from kinds.
      Proof of the deletion: make `take` return the rest at zero, see a table case fail, restore. Command:
      `pytest tests`, the corpus compare. Proof: passes; equal, every settlement input included. Acceptance: AC-02,
      AC-03, AC-06.
- [ ] [AI] Move `reversals.py` into `AccountIn` as private methods; delete with proof (skip `_check_undoing`, see an
      AMB-035 test fail, restore). Command: `pytest tests`. Proof: passes; mutation recorded. Acceptance: AC-09.
- [ ] [AI] Move `decisions.py` into `AccountIn` as `decide_event` and private methods; `_decide_effect` and
      `_record_interest_change`-style steps stay module functions of `account.py`; delete with proof (force-post every
      settlement, see an AMB-012 test fail, restore). Command: `pytest tests`. Proof: passes. Acceptance: AC-09.
- [ ] [AI] Move `fees.py` into `AccountIn`; delete with proof (charge on a zero closing, see an AMB-002 test fail,
      restore). Command: `pytest tests`. Proof: passes. Acceptance: AC-09.
- [ ] [AI] Move `interest.py` into `AccountIn`; delete with proof (drop the adjustment for an earlier day, see an
      AMB-005 test fail, restore). Command: `pytest tests`, the corpus compare. Proof: passes; equal. Acceptance: AC-02,
      AC-09.
- [ ] [AI] Move the four states from `states.py` into `authorizations.py`, which now imports no domain event; delete
      `states.py`, and every importer follows. Command: `pytest tests && cd $APP && uv run --no-sync ruff check .`.
      Proof: both pass. Acceptance: AC-13.
- [ ] [AI] Remove `derive` from both verb lists. Command: `uv run --no-sync pylint src tests`. Proof: exit 0.
      Acceptance: AC-15.
- [ ] [AI] Merge `test_fees.py`, `test_interest.py`, `test_reversals.py`, and `test_authorizations.py` into
      `tests/unit/domain/account/test_account.py`, grouped by topic in the source's order, and move the two table tests
      to `tests/unit/domain/account/test_authorizations.py`; the AMB-036 test waits in `test_account.py` for Phase 3.
      Command: `pytest tests` and `inventory.py --compare`. Proof: passes; no name lost. Acceptance: AC-03, AC-13.
- [ ] [AI] Update the architecture as built: L3's `account/` rows, the L3 diagram's aggregate box, L4's account blocks
      and state-machine paragraph and diagram, the Domain Model's aggregate paragraph. Proof: every name there exists.
      Acceptance: AC-14.

### Phase 2 Gate

- [ ] [AI] Run `sh local-tmp/restructure/gate.sh`; `grep -rn "assert " $SRC | grep -v assert_never` lists only the
      ledger's. Proof: exit 0; one `assert` left. Acceptance: AC-02, AC-03, AC-04, AC-06.
- [ ] [AI] Commit as `refactor(cli): gather every account rule into the Account aggregate`, with the WORKLOG entry and
      the Execution Record line, and push. Proof: the hash and range. Acceptance: AC-16.

Pause safety: the aggregate is one class on `origin/main`. Re-verify with `sh local-tmp/restructure/gate.sh`.

## Phase 3 — The Ledger

Replaces the ledger service's functions with the `Ledger` class and returns an unconfigured account as a fault (R6, R8).

- [ ] [AI] Write `Ledger(config, log)` in `$SRC/domain/ledger/ledger.py`, moved from `processing.py` with
      `/usr/bin/git mv`, with `open`, `find_account`, `list_accounts`, `process_event`, `close_day`, and the private
      steps; delete `end_of_day.py` and `ledger/event_log.py` and the `Log` alias; `stream_processing`, `report`, the
      support modules, and the tests call the class. Add `open` to both verb lists. Proof of the deletion: skip the
      repeated-ID check, see an AMB-034 test fail, restore. Command: `pytest tests`, the corpus compare,
      `uv run --no-sync pylint src tests`. Proof: all pass; equal. Acceptance: AC-02, AC-10.
- [ ] [AI] RED: `test_an_event_on_an_unconfigured_account_is_an_internal_fault` in `tests/unit/test_processing.py`. The
      RED adds `UnknownAccount` and `InternalFault`, and replaces the `assert` with a stub returning the ledger
      unchanged. Command: `pytest tests/unit/test_processing.py`. Proof: fails on its assertion. Acceptance: AC-03,
      AC-06.
- [ ] [AI] GREEN: `_find_opening` returns `Err(UnknownAccount)`, and `process_event` returns it. Command:
      `pytest tests`. Proof: passes. Acceptance: AC-06.
- [ ] [AI] RED: `test_an_unknown_account_exits_2_naming_it` in `tests/unit/test_cli.py`, patching the processing as its
      neighbours do today, until Phase 4 gives it a fake port. The RED widens the processing's fault to `InternalFault`
      with a stub line in `run_cli`. Command: `pytest tests/unit/test_cli.py`. Proof: fails on its assertion.
      Acceptance: AC-03.
- [ ] [AI] GREEN: `run_cli` prints `error: internal: ACC-003 is not a configured account` and exits 2 through one
      `match` over `InternalFault` ending in `assert_never`. Command: `pytest tests`. Proof: passes. Acceptance: AC-06.
- [ ] [AI] REFACTOR: both cycles' docstrings; the application README's sentence after the exit table names the new line
      and says no input reaches it. Command: `pytest tests`. Proof: passes. Acceptance: AC-14.
- [ ] [AI] Move `tests/unit/test_processing.py` to `tests/unit/domain/ledger/test_ledger.py` and the AMB-036 test into
      it. Command: `pytest tests`, `inventory.py --compare`. Proof: passes; no name lost. Acceptance: AC-03, AC-13.
- [ ] [AI] Update the architecture as built: L3's `ledger/` rows and diagram box, L4's ledger line, the Dynamic View's
      calls, and the Domain Model's Ledger paragraph. Proof: every name exists. Acceptance: AC-14.

### Phase 3 Gate

- [ ] [AI] Run `sh local-tmp/restructure/gate.sh`; `grep -rn "assert " $SRC | grep -v assert_never` prints nothing.
      Proof: exit 0. Acceptance: AC-02, AC-03, AC-04, AC-06.
- [ ] [AI] Commit as `refactor(cli): run every account through the Ledger`, with the WORKLOG entry and the Execution
      Record line, and push. Proof: the hash and range. Acceptance: AC-16.

Pause safety: the Ledger is on `origin/main`. Re-verify with `sh local-tmp/restructure/gate.sh`.

## Phase 4 — The Application, Its Ports, and the Adapters

Builds `application/`, the two adapters, and the shell as
[the application, ports, and adapters](tech-docs/003-application-ports-and-adapters.md) state (R2, R5, R12, R20).

- [ ] [AI] Create `$SRC/application/__init__.py` and `ports.py` with `SourceFault`, `EventSource`, `ReportSink`,
      `RunLedger`, and `RunFault`. Command: `uv run --no-sync pyright`. Proof: 0 errors. Acceptance: AC-11.
- [ ] [AI] Move `domain/report.py` to `application/report.py` with `/usr/bin/git mv`; `DayReport.build` replaces
      `build_report`, the `ReportedClosings` class replaces the alias and `update_reported`, and `_compute_closing` and
      `_compute_available` go. Command: `pytest tests`, the corpus compare. Proof: passes; equal. Acceptance: AC-02,
      AC-08.
- [ ] [AI] Move `domain/stream_processing.py` to `application/stream.py`; `IncomingStream.process` replaces
      `process_stream`, and `_ProcessingState` holds the `Ledger`. Command: `pytest tests`, the corpus compare. Proof:
      passes; equal. Acceptance: AC-02, AC-08.
- [ ] [AI] Move `adapters/stream_csv.py` to `adapters/csv_file.py`: `CsvFileSource` with `read_events` and the static
      `parse`, `Reader`, `read_file`, and `_describe_fault` moved from `cli.py`, `REQUIRED` and `OPTIONAL` frozen, and
      `RowKind`. Command: `pytest tests`. Proof: passes. Acceptance: AC-11, AC-12.
- [ ] [AI] Move `adapters/render.py` to `adapters/text_report.py`: `TextOutput`, `TextReportSink` with `publish` and the
      static `render`, `NUMBER_WORDS` frozen. Add `publish` to both verb lists. Command: `pytest tests`. Proof: passes.
      Acceptance: AC-11, AC-12.
- [ ] [AI] Write `application/run.py`, `LedgerRun`. Command: `pyright`. Proof: 0 errors. Acceptance: AC-11.
- [ ] [AI] Rewrite `cli.py`: `run_cli(argv, read_text, out, err, run_ledger)` builds the two adapters and maps each
      fault; `main` binds `read_file`, the streams, and `LedgerRun(CHALLENGE)`. The CLI tests pass a fake `RunLedger`
      where they patched `process_stream`, and `ClosedPipe` becomes a plain class. Command: `pytest tests`, the corpus
      compare. Proof: passes; equal, every file fault and argument error included. Acceptance: AC-02, AC-11.
- [ ] [AI] Write `application/ruff.toml` and `adapters/ruff.toml`, and rewrite the five existing bans, as
      [the import bans](tech-docs/003-application-ports-and-adapters.md#the-import-bans) state. Prove each ban: add a
      forbidden import to one module of each package, see `ruff check` fail with TID251, restore. Command:
      `cd $APP && uv run --no-sync ruff check .`. Proof: passes; seven failures recorded under mutation. Acceptance:
      AC-11.
- [ ] [AI] Move the tests: `test_stream_processing.py`, `test_criteria.py`, and `test_known_weakness.py` into
      `tests/unit/application/test_stream.py`; `test_report.py` to `tests/unit/application/`; `test_stream_csv.py` and
      `test_render.py` to `tests/unit/adapters/test_csv_file.py` and `test_text_report.py`;
      `tests/integration/test_stream_file.py` to `tests/integration/adapters/test_csv_file.py`, and `test_main.py` to
      `tests/integration/test_cli.py`. Command: `pytest tests`, `inventory.py --compare`. Proof: passes; no name lost;
      `1 xfailed`. Acceptance: AC-03, AC-13.
- [ ] [AI] Update the architecture as built: the L3 prose, diagram, and table; L4's report, stream, and adapter lines;
      the Dynamic View; the Domain Model's report paragraph; Reading the Code. Update the application README's layout
      table, its DDD paragraph, and the known weakness's path. Proof: every name exists. Acceptance: AC-14.

### Phase 4 Gate

- [ ] [AI] Run `sh local-tmp/restructure/gate.sh`. Proof: exit 0; the inventory lists the five new names. Acceptance:
      AC-02, AC-03, AC-04, AC-11.
- [ ] [AI] Commit as `refactor(cli): put the use case behind ports and adapters`, with the WORKLOG entry and the
      Execution Record line, and push. Proof: the hash and range. Acceptance: AC-16.

Pause safety: the layers are on `origin/main`. Re-verify with `sh local-tmp/restructure/gate.sh`.

## Phase 5 — No Inheritance, Gated and Written Down

Enables the gate and changes the rule through rules-propagation, now that the code follows it (R3, R9, R21).

- [ ] [AI] RED: run pylint with `--enable=too-many-ancestors --max-parents=0` and the six ignored parents on the
      baseline copy's `src` and `tests`, and on a scratch probe holding one dataclass subclass. Record in
      `$EV/phase-5-no-inheritance.txt`. Proof: the baseline and the probe fail, naming the derived classes. Acceptance:
      AC-07.
- [ ] [AI] GREEN: enable `too-many-ancestors` and add `[tool.pylint.design]` in `pyproject.toml`, as
      [the rule changes](tech-docs/005-specification-rule-and-doc-changes.md#e-appsaccount-ledger-clipyprojecttoml)
      show. Command: `cd $APP && uv run --no-sync pylint src tests`. Proof: exit 0, appended to the evidence file.
      Acceptance: AC-07.
- [ ] [AI] Open the rules-propagation record `local-tmp/rules-propagation-no-inheritance.md`, naming each file below and
      the placement: development level, the Python standards' Operations module. Proof: the record. Acceptance: AC-15.
- [ ] [AI] Rewrite `003-operations.md`: four cases, the aggregate sentence, and No Inheritance, as 005's diff shows.
      Command: `./rhino governance word-budget validate`. Proof: exit 0. Acceptance: AC-15.
- [ ] [AI] Rewrite the summary and Enforcement sentence of `python-standards.md`, within 750 words, and the module row
      of `python-standards/README.md`; change `001-naming.md`'s example. Command:
      `./rhino governance word-budget validate && ./rhino governance directory-map validate`. Proof: both 0. Acceptance:
      AC-15.
- [ ] [AI] Search the live corpus for the old wording: `grep -rnE "six named|Shared Bases|share a base|sum_money"` over
      `.agents`, `repo-governance`, `AGENTS.md`, `specs`, `docs`, and `apps`, Markdown only. Proof: nothing outside
      `plans/`. Acceptance: AC-15.
- [ ] [AI] Close the record: every file carried, the check commands and their exits. Proof: the record. Acceptance:
      AC-15.

### Phase 5 Gate

- [ ] [AI] Run `sh local-tmp/restructure/gate.sh` and `./rhino md internal-link validate`. Proof: both 0. Acceptance:
      AC-07, AC-15.
- [ ] [AI] Commit the gate as `build(cli): refuse class inheritance in lint` and the rule as
      `docs(governance): keep operations on their type, without inheritance`, with the WORKLOG entry and the Execution
      Record line, and push. Proof: the hashes and range. Acceptance: AC-16.

Pause safety: the gate and the rule are on `origin/main`. Re-verify with `sh local-tmp/restructure/gate.sh`.

## Phase 6 — Polish, File by File

Reads every source and test file once, top to bottom, and fixes what the comb finds without changing behaviour (R19).

- [ ] [AI] Comb the values: `money.py`, `ids.py`, `events.py`, `config.py`, `challenge.py`, `common/result.py`. Look
      for: stale docstrings naming a removed type or module, parenthesized single imports, definition order, a comment
      that restates the code. Command: `pytest tests`. Proof: passes; each fix listed. Acceptance: AC-14.
- [ ] [AI] Comb the aggregate package: `account.py`, `authorizations.py`, `domain_events.py`, `event_log.py`,
      `rejections.py`; `_record_interest_change`'s wrapped `if (day == today):` becomes one line. Command:
      `pytest     tests`. Proof: passes; each fix listed. Acceptance: AC-14.
- [ ] [AI] Comb `ledger.py`, the application modules, the adapters (`_CommonFields`'s layout, `_build_applied_row`'s
      repeated tuples folded), `cli.py`, and `__main__.py`. Command: `pytest tests`, the corpus compare. Proof: passes;
      equal. Acceptance: AC-02, AC-14.
- [ ] [AI] Comb every test and support module: `streams.py`'s `ACC_001` opening becomes `ACC_001_OPENING`; docstrings
      name the new API; no helper duplicates another. Command: `pytest tests`, `inventory.py --compare`. Proof: passes;
      no name lost. Acceptance: AC-03, AC-14.
- [ ] [AI] Search for stale names across the application: `grep -rnwE` over `$APP` for `history`, `aggregate`,
      `stream_processing`, `process_stream`, `render_reports`, `parse_stream`, `Log`, and any name ending in `_of`.
      Proof: each hit is either the domain word used correctly or fixed. Acceptance: AC-14.

### Phase 6 Gate

- [ ] [AI] Run `sh local-tmp/restructure/gate.sh`. Proof: exit 0. Acceptance: AC-02, AC-03, AC-04.
- [ ] [AI] Commit as `style(cli): comb every module after the restructure`, with the WORKLOG entry and the Execution
      Record line, and push. Proof: the hash and range. Acceptance: AC-16.

Pause safety: the polish is on `origin/main`. Re-verify with `sh local-tmp/restructure/gate.sh`.

## Phase 7 — The Documents as Built

Reads each document against the tree and carries every change the restructure made stale (AC-14).

- [ ] [AI] Read `architecture.md` against the tree from top to bottom; Scope, L1, and L2 unchanged; add the Constraints
      bullet. Proof: every module, type, and function it names exists (`grep`), and every source module appears in L3.
      Acceptance: AC-14.
- [ ] [AI] Read the application README against the tree: layout, DDD paragraph, exit table, known weakness. Proof: every
      path exists. Acceptance: AC-14.
- [ ] [AI] Add the layers to the root README in one sentence under its opening paragraph, pointing at the architecture.
      Proof: the sentence and a resolving link. Acceptance: AC-14.
- [ ] [AI] Rewrite `local-tmp/restructure/scale.py` against the new API, measure 6, 30, 60, and 120 days and the
      1,000-event volume run on the result into `$EV/phase-8-timings.txt`'s draft, and update the trade-offs document's
      table and figures if any moves by more than a fifth from the recorded ones; replace "history" with "entries" where
      it names the code. Proof: the measurements and the diff. Acceptance: AC-14.
- [ ] [AI] Adapt `local-tmp/restructure/doc_sweep.py` to the names the restructure removed and run it over every
      Markdown file. Proof: no hit outside `plans/done/` and this plan. Acceptance: AC-14.
- [ ] [AI] Check the assessment docs:
      `git diff 83dfd58 -- AMBIGUITIES.md NUMBERS.md REJECTED.md MOVEMENT.md     OUTPUT_TARGET.md challenge-raw.md` is
      empty; `WORKLOG.md` only gained entries, newest first. Proof: the empty diff and the WORKLOG diff showing only
      additions. Acceptance: AC-05.

### Phase 7 Gate

- [ ] [AI] Run `sh local-tmp/restructure/gate.sh`, `./rhino md internal-link validate`,
      `./rhino md heading-hierarchy validate`, and `./rhino md naming validate`. Proof: each 0. Acceptance: AC-14.
- [ ] [AI] Commit as `docs(specs): describe the restructured ledger as built` (and `docs: …` for the READMEs and the
      trade-offs document), with the WORKLOG entry and the Execution Record line, and push. Proof: the hashes and range.
      Acceptance: AC-16.

Pause safety: the documents are on `origin/main`. Re-verify with the Phase 7 gate.

## Phase 8 — Final Verification

Proves every acceptance criterion against the result and files the evidence.

- [ ] [AI] Run the corpus on the result into `$EV/phase-8-corpus.txt` and compare with Phase 0's. Proof: `diff -I '^#'`
      empty. Acceptance: AC-02.
- [ ] [AI] Compare the golden fence: `/usr/bin/git diff 83dfd58 -- OUTPUT_TARGET.md` empty and `test:e2e` passing.
      Proof: both. Acceptance: AC-01.
- [ ] [AI] Record `$EV/phase-8-tests.txt` and compare. Proof: every baseline name with its count, five added, one xfail,
      nothing skipped. Acceptance: AC-03.
- [ ] [AI] Run `cited_names.py`. Proof: `missing 0`. Acceptance: AC-04.
- [ ] [AI] Audit the types: `pyright` 0 errors; `grep -rnE "\bassert |\bAny\b|cast\(|type: ignore|noqa" $SRC` prints
      nothing but `assert_never`. Proof: both. Acceptance: AC-06.
- [ ] [AI] Audit the operations: list every public module-level `def` under `$SRC`. Proof: exactly the six AC-08 names.
      Acceptance: AC-08.
- [ ] [AI] Audit the aggregate and the ledger: `grep -rn "AccountIn\[" $SRC` shows it as a subject only in `account.py`;
      `grep -rnE "^def (process_event|close_day|find_history)|^type Log " $SRC` prints nothing. Proof: both. Acceptance:
      AC-09, AC-10.
- [ ] [AI] Audit immutability: every `@dataclass` under `$SRC` is `frozen=True, slots=True`; no module-level `dict`,
      `list`, or `set` literal. Proof: the two greps. Acceptance: AC-12.
- [ ] [AI] Compare the layout: the sorted `.py` paths under `$SRC` and `$APP/tests` equal the trees in
      [the target layout](tech-docs/001-target-layout.md). Proof: the diff is empty. Acceptance: AC-13.
- [ ] [AI] Run the six mutation spot-checks
      [behaviour preservation](tech-docs/004-behaviour-preservation-and-tests.md#every-other-proof) lists, each broken,
      run, and restored, into `$EV/phase-8-mutations.txt`. Proof: each names the test that failed. Acceptance: AC-02.
- [ ] [AI] Finish `$EV/phase-8-timings.txt` with the baseline and result timings side by side. Proof: the file.
      Acceptance: AC-14.
- [ ] [AI] Run the full gate with `--skip-nx-cache`, the Rhino Markdown checks, and `npm run -s check:hygiene`. Proof:
      every exit 0; coverage recorded. Acceptance: AC-16.

### Phase 8 Gate

- [ ] [AI] Run `sh local-tmp/restructure/gate.sh`. Proof: exit 0. Acceptance: AC-01 to AC-16.
- [ ] [AI] Commit the evidence as `docs(plan): record the restructure's verification`, with the WORKLOG entry and the
      Execution Record line, and push. Proof: the hash and range. Acceptance: AC-16.

Pause safety: every criterion is proven on `origin/main`. Re-verify with `sh local-tmp/restructure/gate.sh`.

## Recovery

Each stays dormant until its trigger fires, and closes with one terminal disposition.

- [ ] [AI] RC1 — a behaviour differs. Trigger: the corpus compare, the inventory compare, or a suite fails after a
      refactor item. Owner: the executor. Procedure: stop the phase; diff the failing block against the baseline; find
      the item whose change made it by rerunning the corpus after reverting each of the phase's uncommitted file changes
      in turn from a saved patch in `local-tmp/restructure/`; fix the cause so the corpus matches; never edit the Phase
      0 record. Proof: the compare equal again, recorded under the item.
- [ ] [AI] RC2 — a cited or baseline test cannot keep its name or cases. Trigger: `inventory.py --compare` or
      `cited_names.py` fails and the test cannot be carried as it is. Owner: the owner, since an assessment doc cites
      it. Procedure: keep the test as it is in a file of its own beside its target and record why in learnings; never
      rename it and never edit an assessment doc. Proof: both scripts pass.
- [ ] [AI] RC3 — a pushed phase proves wrong. Trigger: a later phase finds a defect a pushed phase made that a forward
      fix cannot reach before submission. Owner: the executor. Procedure: `/usr/bin/git revert` of that phase's commits,
      newest first, as new commits, pushed; the phase then reruns. Proof: the gate passes on the reverted tree.
- [ ] [AI] RC4 — a hook fails a commit or a push. Trigger: the pre-commit or pre-push hook exits non-zero. Owner: the
      executor. Procedure: read its output, fix the cause, and commit again; never `--no-verify`. Proof: the hook
      passes.

## Archival

After every substantive phase is terminal. The completion gate is the execution check alone.

- [ ] [AI] Give each dormant recovery item its dated disposition. Proof: every item carries one.
- [ ] [AI] Triage `learnings.md`: route each entry to one owner or discard it with a reason, or record that the log is
      empty. Proof: no entry unresolved.
- [ ] [AI] Run [Execution Check](../../../repo-governance/workflows/plan/plan-execution-check.md) and record its
      terminal verdict; archival needs a permitting one. Proof: the verdict. Acceptance: AC-16.
- [ ] [AI] Run [Dev Artifact Clean-Up](../../../repo-governance/workflows/maintenance/dev-artifact-clean-up.md) over
      this task's scratch in `local-tmp/`, including `local-tmp/restructure/baseline/`. Proof: the record of what it
      removed.
- [ ] [AI] Move the plan to `plans/done/YYYY-MM-DD__restructure-around-the-domain/` with `/usr/bin/git mv`; update
      `plans/in-progress/README.md`, `plans/done/README.md`, and every live link to the old path; run the full
      validation from the archived state; add the WORKLOG entry; commit as `docs(plan): archive the restructure plan`
      and push. Proof: the pushed range, and
      `grep -rln "plans/in-progress/restructure-around-the-domain" --exclude-dir=.git --exclude-dir=local-tmp .` finding
      only history.

[cycle]: ../../../repo-governance/development/quality/testing/test-driven-development/001-cycle-and-evidence.md
