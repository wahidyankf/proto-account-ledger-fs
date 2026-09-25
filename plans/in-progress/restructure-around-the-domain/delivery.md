# Delivery

The executable part of this plan. Every item names its paths, its command where one exists, its executor, its proof, and
the acceptance criteria it serves from [prd](prd.md). Why each item exists is in the other five documents; read them
first, above all [the target layout](tech-docs/001-target-layout.md) and
[behaviour preservation](tech-docs/004-behaviour-preservation-and-tests.md).

## Execution Record

- **2026-09-25 19:05, the quality gate.** The Plan Quality Gate ran on 9979926: FAIL, 1 blocking and 22 non-blocking.
  Repair cycle 1 closed them; its re-verification found N1 blocking and 19 non-blocking. Repair cycle 2 closed N2 to
  N20; its re-verification found N1's wording not yet carried into AC-03 and 004 (F1) and five smaller findings. At the
  ceiling the repaired draft, with F1 to F6 carried, was chosen over 9979926, on the criterion declared before cycle 1;
  R22 was added at the owner's request for a consistent, natural layout. Verdict file:
  `generated-reports/restructure-around-the-domain-2026-09-25-plan-quality-gate.md`, which is gitignored. Last gate
  passed: none yet. Next item: Phase 0, the first. No budget partly spent.
- **2026-09-25 19:18, Phase 0.** The baseline is recorded in `evidence/`: the gates (147 passed, 1 xfailed, 95.12%; 3
  integration; 6 end-to-end), the manifest of 31 source and 26 test modules, the corpus of 56 inputs, 157 cases under
  115 names with their literals, the timings, and the audits (68 broken, as expected). `gate.sh` passes on the baseline
  tree. One surprise: the directory-map gate wanted `evidence/README.md`, now added. Last gate passed: Phase 0. Next
  item: Phase 1, the first. No budget partly spent.

- **2026-09-25 19:37, Phase 1.** The values own their operations: `Aed` and `Bhd` without a base, `take` and
  `make_directed_amount` test-first, the ID kinds and events flat, `Instalments(count, parts)` with its guard, the
  configured account renamed `AccountOpeningIn`, and `CHALLENGE` in `challenge.py`. The gate passed: 159 passed and 1
  xfailed, the corpus and literals equal, three names added. Last gate passed: Phase 1. Next item: Phase 2, the first.
  No budget partly spent.

- **2026-09-25 19:58, Phase 2.** Phase 1 is f4d325d, pushed as 0569ea2..f4d325d. The Account aggregate is one class,
  `AccountIn` in `account.py`, every rule a method grouped by topic; the six topic modules, `history.py`,
  `aggregate.py`, and `states.py` are gone, each with its mutation proof; the D8 table matches the state, the kind, and
  what `take` leaves, and narrows to `Never`. The gate passed: 159 passed and 1 xfailed, the corpus and literals equal.
  Open until Phase 5: `003-operations.md` still gives `sum_money` as its example. Last gate passed: Phase 2. Next item:
  Phase 3, the first. No budget partly spent.

- **2026-09-25 20:11, Phase 3.** Phase 2 is 5a36329, pushed as f4d325d..5a36329. `Ledger(config, log)` in
  `ledger/ledger.py` replaces `processing.py`, `end_of_day.py`, `ledger/event_log.py`, and `Log`, each deletion with its
  mutation proof; a private `_append(*entries)` builds each new ledger. An event on an unconfigured account is
  `Err(UnknownAccount)`, and the CLI prints it as an internal fault through one `match`; the last `assert` in the source
  is gone. Earlier than planned, because the log now lives in the ledger: `_ProcessingState` holds the `Ledger`, and
  `build_report` and its private builders take it, so Phase 4 moves them without changing what they read. The gate
  passed: 161 passed and 1 xfailed, the corpus and literals equal. Open until Phase 5: `003-operations.md`'s `sum_money`
  example. Last gate passed: Phase 3. Next item: Phase 4, the first. No budget partly spent.
- **2026-09-25 20:33, Phase 4.** Phase 3 is 0cbeb9a, pushed as 5a36329..0cbeb9a. `application/` holds the use case,
  `LedgerRun`, its ports, `IncomingStream`, and the report read model with `DayReport.build` and `ReportedClosings`;
  `adapters/csv_file.py` and `adapters/text_report.py` implement the driven ports; `run_cli` takes a `RunLedger`, so no
  CLI test patches a module, and `ClosedPipe` is a plain `TextOutput`. Seven `ruff.toml` bans, each proved by a
  mutation. `publish` joined the verb lists with the ports, before `flush`. The gate passed: 161 passed and 1 xfailed,
  the corpus and literals equal. Open until Phase 5: `003-operations.md`'s `sum_money` and `001-naming.md`'s
  `parse_stream`, both example names the code no longer has. Last gate passed: Phase 4. Next item: Phase 5, the first.
  No budget partly spent.
- **2026-09-25 20:44, Phase 5.** Phase 4 is 553041a, pushed as 0cbeb9a..553041a. pylint's `too-many-ancestors` runs with
  `max-parents = 0` and six ignored parents, `builtins.NoneType` among them because astroid counts it an `Enum`'s
  ancestor; its RED run, over the Phase 0 baseline and a probe, found 39 derived classes, and its GREEN run over the
  tree none. Through rules-propagation, `003-operations.md` keeps four function cases and replaces Shared Bases with No
  Inheritance; the entrypoint, the module map, the naming module's example, and the architecture follow, and the
  old-wording search prints nothing. The gate passed: 161 passed and 1 xfailed, the corpus and literals equal. Last gate
  passed: Phase 5. Next item: Phase 6, the first. No budget partly spent.
- **2026-09-25 20:54, Phase 6.** Phase 5 is 62ced26 and 4bb46c9, pushed as 553041a..4bb46c9. Every source and test
  module read once: stale docstrings now name the event source, the report sink, `LedgerRun`, and the Ledger's own
  refusals; nine imports wrapped only by a leftover comma fit one line; `_record_interest_change`'s `if` and
  `_CommonFields` read plainly; `text_report.py`'s constants sit at the top and `_build_applied_row` builds one row
  shape through `_build_generated_row`. The test support is builders in `streams.py` and readers in `entries.py`, and
  the openings are `ACC_001_OPENING` and `ACC_002_OPENING`. The gate passed: 161 passed and 1 xfailed, the corpus and
  literals equal. Last gate passed: Phase 6. Next item: Phase 7, the first. No budget partly spent.
- **2026-09-25 21:03, Phase 7.** Phase 6 is d592e56, pushed as 4bb46c9..d592e56. The architecture names `__main__.py` in
  the shell, so every source module is in L3, and its prose, dynamic view, and Constraints name the event source, each
  account's own currency, and effects performed in the adapters; the app README maps `__main__.py` and the event source;
  the root README says the layers in one sentence. Measured again, no timing moved by a fifth, so the trade-offs table
  stands and its prose says the account's entries, not its history. The removed-name sweep over every tracked Markdown
  file finds only a past WORKLOG entry; the assessment docs are unchanged since 83dfd58. The gate passed. Last gate
  passed: Phase 7. Next item: Phase 8, the first. No budget partly spent.

## Execution Checkout

- **Working copy.** The main checkout at the repository root, on `main`, with no worktree and no task branch, per the
  [integration path](../../../repo-governance/development/workflow/integration-path.md). Git is invoked as
  `/usr/bin/git`, which the local rtk guard lets through.
- **Delivery mode.** Direct commits to local `main`, pushed to `origin/main` at each phase gate. The owner's goal of
  2026-09-25 authorizes the commits and pushes the gates name and those RC3 and RC4 prescribe, and no other.
- **Commands.** Every command runs from the repository root after these exports, which `gate.sh` sets as well:

  ```bash
  export APP=apps/account-ledger-cli
  export SRC=apps/account-ledger-cli/src/account_ledger
  export EV=plans/in-progress/restructure-around-the-domain/evidence
  export BASE=local-tmp/restructure/baseline/apps/account-ledger-cli
  ```

  `pytest ARGS` below means `(cd $APP && uv run --no-sync pytest ARGS)`. Every other `cd` runs inside parentheses, a
  subshell, so the next command starts from the root again.

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
- **Deletion items.** Each first records, under itself, `grep -nE '^(def|class|type) '` of the module it deletes, and a
  module is deleted only after the six steps of
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

- [x] [AI] Confirm the checkout: on `main`, level with `origin/main`, nothing uncommitted but ignored scratch. Command:
      `/usr/bin/git fetch origin && /usr/bin/git status -sb`. Proof: the output. Acceptance: AC-16. - Result:
      `## main...origin/main` at cbee806, level with `origin/main`; the one untracked file,
      `scripts/build-architecture-pdf.py`, is the Part 2 PDF work outside this plan.
- [x] [AI] Install the toolchain. Command: `npm install && (cd $APP && uv sync --locked)`. Proof: exit 0. Acceptance:
      AC-16. - Result: `npm install` and `uv sync --locked` exit 0; nothing to change.
- [x] [AI] Write `local-tmp/run.sh`, which deletes every `__pycache__` under `$APP/src` and `$APP/tests` and then runs
      its arguments, and `local-tmp/check-md.sh`, which runs Prettier on every changed or untracked Markdown file and
      fails on a line past 120 outside `repo-governance/` and the harness directories. Command:
      `sh local-tmp/check-md.sh`. Proof: exit 0 on the clean checkout. Acceptance: AC-16. - Result: both written;
      `sh local-tmp/check-md.sh` exit 0.
- [x] [AI] Record the baseline gates with `--skip-nx-cache`: `test:quick`, `test:integration`, `test:e2e`, and
      `npm run -s check:hygiene`, with the unit counts and the coverage figure, into `$EV/phase-0-baseline.txt`, headed
      by the commands, the commit, and the time. Proof: every exit 0; a failure is fixed at its cause here and recorded
      as pre-existing. Acceptance: AC-16. - Result: in `$EV/phase-0-baseline.txt`. test:quick exit 0, pyright 0 errors,
      ruff clean, 147 passed and 1 xfailed, coverage 95.12%; test:integration 3 passed; test:e2e 6 passed. - Surprise:
      the first `check:hygiene` failed on directory-map, which wants `evidence/README.md` mapping every file; added,
      then exit 0 ([learnings](learnings.md)).
- [x] [AI] Extract the baseline copy: `mkdir -p local-tmp/restructure/baseline` and
      `/usr/bin/git archive 83dfd58 apps/account-ledger-cli | tar -x -C local-tmp/restructure/baseline`; append the
      manifest, the commit and the command, and `find ... -name '*.py' | wc -l` of the copy, to
      `$EV/phase-0-baseline.txt`. Proof: 31 source and 26 test modules in the copy. Acceptance: AC-02. - Result: 31
      source and 26 test modules; the manifest, a SHA-256 per file, appended to `$EV/phase-0-baseline.txt`.
- [x] [AI] Write `local-tmp/restructure/corpus.py` with every input group
      [behaviour preservation](tech-docs/004-behaviour-preservation-and-tests.md#the-behaviour-corpus) lists. It takes
      the application directory, writes each input into a fresh temporary directory, runs the working tree's
      interpreter, `$APP/.venv/bin/python -m account_ledger <relative path>`, there with `PYTHONPATH=<app>/src`, so the
      baseline copy, which has no `.venv`, runs its own code on the same interpreter, and prints one block per input:
      name, exit code, standard error, standard output's SHA-256 and line count. Command:
      `python3 local-tmp/restructure/corpus.py $BASE`. Proof: every group present; the brief's block shows exit 0 and
      the golden fence's hash. Acceptance: AC-02. - Result: 56 inputs, every group present; `== brief` shows exit 0 and
      `ffa6f573…`, the golden fence's SHA-256, 228 lines.
- [x] [AI] Record the corpus on the baseline into `$EV/phase-0-corpus.txt`, then run it on the working tree and compare,
      proving the script deterministic. Command: the two commands in
      [the corpus section](tech-docs/004-behaviour-preservation-and-tests.md#the-behaviour-corpus). Proof:
      `diff -I '^#'` prints nothing. Acceptance: AC-02. - Result: `$EV/phase-0-corpus.txt`; the working tree's run
      compared with `diff -I '^#'` prints nothing.
- [x] [AI] Write `local-tmp/restructure/inventory.py`, which runs `pytest --collect-only -q` over `$APP/tests` and
      prints each test function's name and case count, sorted, and a `--compare BASELINE` mode that fails if a baseline
      name is missing or has another count, and lists every added name. Record `$EV/phase-0-tests.txt`. Proof: 157
      cases, 115 names. Acceptance: AC-03. - Result: `# 157 cases, 115 names` in `$EV/phase-0-tests.txt`; `--compare` on
      the tree: every name kept, 0 added.
- [x] [AI] Write `local-tmp/restructure/test_literals.py`, which walks every `test_…` function under a tests directory
      with `ast` and prints, per name, the sorted literal constants of its decorators, its body, and any upper-case
      module-level case table a decorator names, leaving out every docstring inside it, the attribute name a
      `monkeypatch.setattr` patches, and the argument names a `pytest.mark.parametrize` declares; `--compare FILE` exits
      1 when a name in `FILE` is missing or its literals differ. Record `$EV/phase-0-literals.txt` from `$BASE/tests`.
      Command: `python3 local-tmp/restructure/test_literals.py $BASE/tests`. Proof: 115 names; the same run on
      `$APP/tests` compares equal. Acceptance: AC-03. - Result: `# 115 names` in `$EV/phase-0-literals.txt`; the tree
      compares equal.
- [x] [AI] Write `local-tmp/restructure/cited_names.py`, which collects every `test_…` name in the five assessment docs
      AC-04 lists and every `def test_…` under `$APP/tests`, prints `cited N defined N missing N` and each missing name,
      and exits 1 when one is missing. Command: `python3 local-tmp/restructure/cited_names.py`. Proof:
      `cited 60 defined 115 missing 0`. Acceptance: AC-04. - Result: `cited 60 defined 115 missing 0`.
- [x] [AI] Write `local-tmp/restructure/scale.py`. For each day count given, it builds ten alternating credits of AED
      100.00 and debits of AED 90.00 a day on ACC-001, each value-dated on its booking day, over a window of that many
      days with interest capitalized every thirtieth day, and times the processing alone, printing
      `days events seconds`. With `--volume` it times the brief's events a hundred times under new IDs inside the
      brief's six days, printing `volume events seconds`. `PYTHONPATH` chooses the application. Command:
      `PYTHONPATH=$BASE/src $APP/.venv/bin/python local-tmp/restructure/scale.py 6 30 60 120`, then the same with
      `--volume`; append both to `$EV/phase-0-baseline.txt`. Proof: four window lines and one volume line. Acceptance:
      AC-14. - Result: 6 d, 60 events, 0.01 s; 30 d, 300, 0.50 s; 60 d, 600, 3.62 s; 120 d, 1,200, 28.08 s; volume,
      1,000 events, 0.72 s. Each is within a fifth of the trade-offs document's figures.
- [x] [AI] Write `local-tmp/restructure/doc_sweep.py`, which reads the documents that describe the application, the root
      and application READMEs, `docs/`, `specs/`, and the five assessment docs AC-04 lists, and lists every backticked
      identifier and path in them that no tracked code file or path holds, and every relative link that does not
      resolve; it exits 1 on any hit, save the generic references it names as allowed, today `behaviours/` and
      `architecture.md` in `specs/README.md`, each recorded. Command: `python3 local-tmp/restructure/doc_sweep.py`.
      Proof: its output appended to `$EV/phase-0-baseline.txt`, each hit today named as pre-existing. Acceptance:
      AC-14. - Result: 18 documents, no hit, exit 0; the two allowed references recorded.
- [x] [AI] Write `local-tmp/restructure/audit.py`, the structural audits: every public module-level function under
      `$SRC` (AC-08); every class under `$SRC`, and whether it is `@dataclass(frozen=True, slots=True)`, an `Enum`, a
      `Protocol`, `Ok`, or `Err` (AC-12); every module-level binding under `$SRC` to a `dict`, `list`, or `set`, literal
      or call (AC-12). It prints the three lists; `--check` exits 1 when an entry breaks its criterion. Command:
      `python3 local-tmp/restructure/audit.py`. Proof: today's lists appended to `$EV/phase-0-baseline.txt`; `--check`
      fails on the baseline, naming the functions AC-08 does not allow. Acceptance: AC-08, AC-12. - Result: 33 public
      functions, 91 classes, 3 module-level containers; `--check` exits 1 with 68 broken, as the baseline should.
- [x] [AI] Write `local-tmp/restructure/gate.sh`, the bundle every phase gate runs, which sets the four exports and
      runs, in this order, stopping at the first failure:
      `sh local-tmp/run.sh npx nx run account-ledger-cli:test:quick --skip-nx-cache`, the same for `test:integration`
      and `test:e2e`, the corpus compared with `$EV/phase-0-corpus.txt`, `inventory.py --compare $EV/phase-0-tests.txt`,
      `test_literals.py $APP/tests --compare $EV/phase-0-literals.txt`, `cited_names.py`, `sh local-tmp/check-md.sh`,
      and `npm run -s check:hygiene`. Command: `sh local-tmp/restructure/gate.sh`. Proof: exit 0 on the baseline tree.
      Acceptance: AC-16. - Result: `GATE PASSED`, every step exit 0.

### Phase 0 Gate

- [x] [AI] Run `sh local-tmp/restructure/gate.sh`, `./rhino md internal-link validate`,
      `./rhino md heading-hierarchy validate`, and `./rhino md naming validate`. Proof: each exit 0. Acceptance:
      AC-16. - Result: `GATE PASSED`; internal-link, heading-hierarchy, and naming each exit 0.
- [x] [AI] Add the `WORKLOG.md` entry, record this phase's Execution Record line, and commit `$EV/phase-0-*.txt`, this
      file, and `WORKLOG.md` as `docs(plan): record the restructure's baseline`; push. Command:
      `/usr/bin/git push origin main`. Proof: the hash and the pushed range. Acceptance: AC-16. - Result: the entry and
      the line added; committed as `docs(plan): record the restructure's baseline` with `evidence/`, and pushed; the
      hash is in the Phase 1 line.

Pause safety: the baseline is on `origin/main`. Re-verify with `sh local-tmp/restructure/gate.sh`.

## Phase 1 — The Values Own Their Operations

Reshapes `domain/model/` as [the domain model](tech-docs/002-domain-model.md) states, moves `CHALLENGE` to the shell,
and moves the value tests (R3, R4, R8, R14, R15).

- [x] [AI] Reorder `money.py`: constants, faults, private functions, then the types. Paths:
      `$SRC/domain/model/money.py`. Command: `pytest tests`. Proof: 156 passed, 1 xfailed, and
      `grep -n "^class\|^[A-Z_]* = " $SRC/domain/model/money.py` in the new order. Acceptance: AC-06. - Result: 156
      passed, 1 xfailed; the grep shows the four constants, the seven faults, the private functions, then `_MoneyBase`,
      `Aed`, `Bhd`, `Money`, `AmountIn`, `Amount`, and `Direction`, with the three public functions after them until the
      next item deletes them.
- [x] [AI] Give `Aed` and `Bhd` their own fields, `ClassVar`s, and methods, delete `_MoneyBase`, and add `require_same`,
      `add_all`, and `compute_daily_interest` as methods over private functions; switch every caller of
      `require_same_currency`, `sum_money`, and `compute_daily_interest` in `$SRC` and `$APP/tests` to the methods, and
      delete the three functions. Paths: `$SRC/domain/model/money.py`,
      `$SRC/domain/account/{authorizations,balances,fees,interest}.py`, `$APP/tests/unit/test_money.py`. Command:
      `pytest tests && (cd $APP && uv run --no-sync pyright)`. Proof: both pass;
      `grep -rn --include='*.py' "sum_money\|require_same_currency\|_MoneyBase" $SRC $APP/tests` prints nothing.
      Acceptance: AC-06, AC-08. - Result: both pass, pyright 0 errors; the grep prints nothing. The daily-interest rule
      is one private `_compute_daily_interest`, which both methods call, so the rule still exists once; the table's
      `_round_money` is the function it calls.
- [x] [AI] RED: `test_taking_all_of_a_hold_or_more_leaves_nothing` in `$APP/tests/unit/test_money.py`: `take` of an
      amount equal to the hold and of one above it gives `Ok(None)`, and of one below gives the rest. The RED adds a
      stub `AmountIn.take` returning `Ok(self)`. Command: `pytest tests/unit/test_money.py`. Proof: fails on its
      assertion. Acceptance: AC-03, AC-06. - Result: fails on its first assertion,
      `Ok(AmountIn(money=Aed(value=Decimal('100.00')))) == Ok(None)`; 9 others pass.
- [x] [AI] GREEN: `take` as [the domain model](tech-docs/002-domain-model.md#domainmodelmoneypy) states. Command:
      `pytest tests`. Proof: passes. Acceptance: AC-06. - Result: 157 passed, 1 xfailed; pyright 0 errors. `take` builds
      the rest only when `_is_positive` holds, which is today's guard, the amount below the hold.
- [x] [AI] REFACTOR: docstring and definition order; `compute_rest` stays until Phase 2 replaces its one caller.
      Command: `pytest tests`. Proof: passes. Acceptance: AC-06. - Result: `take` sits after `add` and before
      `compute_rest`, its docstring as the domain model words it; nothing else to change; 157 passed.
- [x] [AI] RED: `test_a_zero_change_has_no_direction`: `make_directed_amount` gives `(UP, 0.40)` for AED 0.40,
      `(DOWN, 0.40)` for AED −0.40, and `None` for zero. The RED adds a stub returning `None`. Command:
      `pytest tests/unit/test_money.py`. Proof: fails on its assertion. Acceptance: AC-03, AC-06. - Result: fails on its
      first assertion, `None == (<Direction.UP: 'up'>, AmountIn(money=Aed(value=Decimal('0.40'))))`.
- [x] [AI] GREEN: `make_directed_amount` on both currencies. Command: `pytest tests`. Proof: passes. Acceptance:
      AC-06. - Result: 158 passed, 1 xfailed; both methods call one private `_make_directed_amount`, which builds the
      amount through `AmountIn.make`, the function `make_amount` calls.
- [x] [AI] REFACTOR: `interest._record_interest_change` takes the direction and amount `make_directed_amount` gives, and
      `accrue_interest` skips `None`; its `assert` goes. Command: `pytest tests` and the corpus compare. Proof: passes;
      equal. Acceptance: AC-02, AC-06. - Result: 158 passed, 1 xfailed; the corpus compare prints nothing;
      `grep -n "assert " interest.py` prints nothing.
- [x] [AI] Reshape `ids.py`: `IdFault` first; `_TextIdBase` and `_DayEventIdBase` deleted, each kind with its own fields
      and `ClassVar`s over `_check_text`, `_parse_text`, and `_format_day_event_id`; `make` and `parse` classmethods on
      `Day` and `InstalmentCount`. Paths: `$SRC/domain/model/ids.py`. Command: `pytest tests`. Proof: passes;
      `grep -n "Base" $SRC/domain/model/ids.py` prints nothing. Acceptance: AC-06, AC-07. - Result: 158 passed, 1
      xfailed; the grep prints nothing; pyright, ruff, pylint, and vulture clean. The module now reads constants,
      `IdFault`, the private functions, the types, then `EventId` and its parser, the order `money.py` follows.
- [x] [AI] Flatten `events.py`: every kind declares its own fields in today's order; `_IncomingEventBase` and
      `_GeneratedEventBase` deleted; `compute_signed_money` on the two interest kinds replaces
      `interest._sign_interest`, deleted. Paths: `$SRC/domain/model/events.py`, `$SRC/domain/account/interest.py`.
      Command: `pytest tests`. Proof: passes. Acceptance: AC-06, AC-07, AC-08. - Result: 158 passed, 1 xfailed; pyright
      0 errors; the corpus compare prints nothing; `interest._sign_interest` and its three calls replaced by
      `event.compute_signed_money()`.
- [x] [AI] `Instalments(count, parts)` with `Instalments.make`, and `Credit.make_instalments`; the stream reader and
      `tests/support/brief_stream.py` and `streams.py` build postings through `make`; `decisions._generate_instalments`
      wraps `make_instalments` and loses its `assert`. Paths: `$SRC/domain/model/events.py`,
      `$SRC/adapters/stream_csv.py`, `$SRC/domain/account/decisions.py`, `$APP/tests/support/{brief_stream,streams}.py`.
      Command: `pytest tests` and the corpus compare. Proof: passes; equal, the `TooManyInstalments` input included.
      Acceptance: AC-02, AC-06. - Result: 158 passed, 1 xfailed; pyright 0 errors; the corpus compare prints nothing,
      its one `cannot be split` input included; the literals compare equal. The reader's `_parse_posting` now takes the
      amount and builds through `Instalments.make`; `decide_event's` two credit cases merge, since a whole credit makes
      no instalments; the tests build an instalment credit through the new `support.streams.make_instalment_credit`,
      which passes the amount once, so no test gains a literal.
- [x] [AI] RED: `test_instalments_refuse_parts_whose_number_is_not_the_count` in the new
      `$APP/tests/unit/domain/model/test_events.py`: `Instalments(InstalmentCount(2), three parts)` raises `ValueError`.
      Command: `pytest tests/unit/domain/model/test_events.py`. Proof: fails with `DID NOT RAISE`. Acceptance: AC-03. -
      Result: fails with `DID NOT RAISE <class 'ValueError'>`.
- [x] [AI] GREEN: the guard in `Instalments.__post_init__`. Command: `pytest tests`. Proof: passes. Acceptance: AC-03. -
      Result: 159 passed, 1 xfailed; the guard names the count and the parts, `2 instalments hold 2 parts, not 3`.
- [x] [AI] REFACTOR: none beyond the docstring; recorded as such. Command: `pytest tests`. Proof: passes. Acceptance:
      AC-03. - Result: the class docstring names the guard; nothing else changed; 159 passed.
- [x] [AI] Rename `AccountIn` and `Account` in `config.py` to `AccountOpeningIn` and `AccountOpening`, field `opening`
      to `balance`, and every user under `$SRC` and `$APP/tests`; move `CHALLENGE` to the new `$SRC/challenge.py`, and
      every importer to it. Paths: `$SRC/domain/model/config.py`, `$SRC/challenge.py`, and each user. Command:
      `pytest tests && grep -rn --include='*.py' "config import.*CHALLENGE" $SRC $APP/tests`. Proof: passes; the grep
      prints nothing. Acceptance: AC-08, AC-13. - Result: 159 passed, 1 xfailed; the grep prints nothing; pyright, ruff,
      pylint, and vulture clean. `challenge.py` imports only the model; the CLI and fifteen test modules import
      `CHALLENGE` from it.
- [x] [AI] Remove `sign` from both verb lists in `$APP/pyproject.toml` once nothing uses it. Command:
      `(cd $APP && uv run --no-sync pylint src tests)`. Proof: exit 0. Acceptance: AC-15. - Result: exit 0;
      `grep -c "|sign|" pyproject.toml` is 0.
- [x] [AI] Move the value tests with `/usr/bin/git mv`: `test_money.py`, `test_ids.py`, `test_config.py` from
      `$APP/tests/unit/` to `$APP/tests/unit/domain/model/`, and `test_result.py` to `$APP/tests/unit/common/`. Command:
      `pytest tests`. Proof: passes with the same count. Acceptance: AC-03, AC-13. - Result: 159 passed, 1 xfailed, the
      count before the move; the inventory keeps every baseline name with its count.
- [x] [AI] Update the architecture as built: L3's `model/` rows and `challenge`, L4's money, ids, events, and config
      blocks. Paths: `specs/apps/account-ledger/cli/architecture.md`. Proof: every name in those blocks exists (`grep`
      each). Acceptance: AC-14. - Result: every type and function the L3 and L4 blocks name exists under `$SRC`; the
      Domain Model table and naming sentence name `AccountOpeningIn` too, so no section names a removed type; the doc
      sweep reports nothing.

### Phase 1 Gate

- [x] [AI] Run `sh local-tmp/restructure/gate.sh`. Proof: exit 0; the inventory lists exactly three added names.
      Acceptance: AC-02, AC-03, AC-04, AC-06. - Result: every code step exit 0 (test:quick with coverage 95%,
      integration, e2e, the corpus equal, 115 names with their literals, 60 cited names found); the inventory adds
      exactly the three new tests. The first run stopped at the Markdown check, on Prettier for this file and one
      123-column line in the architecture; both fixed, then `check-md.sh` and `check:hygiene` exit 0. - Surprise:
      `width.py` had checked only directories, so a file argument was silently skipped; it now takes files too
      ([learnings](learnings.md)).
- [x] [AI] Commit as `refactor(cli): give each value its own operations, without a base` (and the new tests with it),
      add the `WORKLOG.md` entry and the Execution Record line, and push. Proof: the hash and range. Acceptance:
      AC-16. - Result: committed with the WORKLOG entry and this Execution Record line, and pushed; the hash is in the
      Phase 2 line.

Pause safety: the values are reshaped on `origin/main`. Re-verify with `sh local-tmp/restructure/gate.sh`.

## Phase 2 — The Account Aggregate Is One Class

Builds `AccountIn` in `domain/account/account.py` and moves every rule about one account into it, topic by topic (R1,
R6, R7, R8, R17).

- [x] [AI] Move the seven rejection reasons and `Rejection` from `domain_events.py` to the new `rejections.py`, and
      every importer. Paths: `$SRC/domain/account/{domain_events,rejections}.py`, `$APP/tests/support/refusals.py`, and
      every module under `$SRC` and `$APP/tests` that imports a reason. Command: `pytest tests`. Proof: passes.
      Acceptance: AC-13. - Result: 159 passed, 1 xfailed; pyright 0 errors; eight modules import the reasons from
      `rejections.py` now, `IdReused` first, as the union lists it.
- [x] [AI] Flatten the domain events: each declares `event` and `processed_day`; `_DomainEventBase` deleted. Paths:
      `$SRC/domain/account/domain_events.py`. Command: `pytest tests`. Proof: passes. Acceptance: AC-07. - Result: 159
      passed, 1 xfailed; pyright 0 errors; the fifteen kinds each declare `event`, typed by the event it records, and
      `processed_day`.
- [x] [AI] Write `EventLog` in the new `$SRC/domain/account/event_log.py` with `append`, `find_first_entry`, and
      `select`; `list_processed_on` arrives in Phase 4 with its first caller, so vulture finds nothing unused. The
      ledger's `Log` alias stays until Phase 3. Command: `pytest tests`. Proof: passes. Acceptance: AC-10. - Result: 159
      passed, 1 xfailed; pyright 0 errors. Nothing calls the three methods until the next item, so vulture reports them
      in between; the Phase 2 gate runs it.
- [x] [AI] Replace `AccountHistoryIn` and `AccountAggregateIn` with `AccountIn(id, opening, log)` in the new
      `$SRC/domain/account/account.py`, its public methods forwarding to the topic modules as `AccountAggregateIn`'s do
      today, and the entry queries (`list_instalments`, `_find_entry`, `_list_counted_events`, `_append_entry`,
      `_make_zero`) as methods. Each topic module takes an `AccountIn`, imported under `if TYPE_CHECKING:` only until
      its own item folds it, as [the transition](tech-docs/006-migration-inventory.md#transition) states, so
      `account.py` and the topics never import each other at load. `find_history` builds
      `AccountIn(opening.id, opening.balance, EventLog(log).select(opening.id))`. Until Phase 3,
      `$SRC/domain/ledger/processing.py` asks the whole log through `EventLog(log).find_first_entry(…)` both for a
      repeated ID and for a reversal's target. Between this item and the last topic's, a topic module still calls an
      entry query, now private, from outside the class, so pyright may report `reportPrivateUsage`; each item runs
      `pytest tests`, and pyright must report 0 at the Phase 2 gate. Paths:
      `$SRC/domain/account/{history,aggregate,account,balances,authorizations,decisions,fees,interest,reversals}.py`,
      `$SRC/domain/ledger/{processing,event_log,end_of_day}.py`, `$SRC/domain/report.py`, and
      `$APP/tests/support/states.py`. Delete `history.py` and `aggregate.py` with proof: break `_find_entry` to return
      `None`, see a reversal test fail, restore. Command: `pytest tests`. Proof: passes; the mutation's failing test
      named. Acceptance: AC-09, AC-13. - Result: 159 passed, 1 xfailed; pyright reports 14 `reportPrivateUsage` errors
      and no other, the transition's expected state. `history.py` and `aggregate.py` deleted with `/usr/bin/git rm`. -
      Mutation: `_find_entry` returning `None` fails `test_amb_035_a_reversal_undoes_what_its_target_moved`,
      `test_amb_028_a_second_reversal_of_the_same_event_is_refused`, and 34 others, 36 in all; restored, 159 passed.
- [x] [AI] Move `$SRC/domain/account/balances.py` into `AccountIn` as `compute_closing`, `compute_available`, and the
      three private methods; delete the module with proof (break `_list_undone_amounts`, see an AMB-028 test fail,
      restore). Command: `pytest tests`, the corpus compare. Proof: passes; equal; mutation recorded. Acceptance: AC-02,
      AC-09. - Result: 159 passed, 1 xfailed; the corpus compare prints nothing; pyright reports 12
      `reportPrivateUsage`, the transition's, and no other. The module deleted; its three callers ask
      `history.compute_closing` or `.compute_available`. Folded by `local-tmp/restructure/fold.py`, which moves each
      body unchanged but for `history` read as `self`. - Mutation: `_list_undone_amounts` returning `()` fails
      `test_amb_028_a_second_reversal_of_the_same_event_is_refused`, `test_amb_028_a_reversal_of_a_reversal_is_refused`,
      and 17 others, 19 in all; restored, 159 passed.
- [x] [AI] Move the history rules of `$SRC/domain/account/authorizations.py` (`list_records`, `find_record`,
      `sum_holds`, and `decide_authorization` folded into `_decide_authorization_entry`) into `AccountIn`;
      `_is_referenced_by` becomes `AuthorizationRecord.is_referenced_by`. Command: `pytest tests`, the corpus compare.
      Proof: passes; equal. Acceptance: AC-02, AC-08, AC-09. - Result: 159 passed, 1 xfailed; the corpus compare prints
      nothing; pyright reports only the transition's `reportPrivateUsage`. `decide_authorization` is folded into
      `_decide_authorization_entry`, which reads the available balance, returns a mismatch first as before, and decides
      on `is_below`.
- [x] [AI] Rewrite the D8 table as `apply_settlement(state, kind, amount)` over `take`, as
      [the domain model](tech-docs/002-domain-model.md#authorizationspy) shows; delete `FinalSettlement`,
      `PartialSettlement`, `_SettlementInputBase`, `SettlementInput`, `derive_settlement_input`,
      `_is_settlement_below_hold`, `_make_partial_settlement`, `_compute_rest` and its `assert`, and
      `AmountIn.compute_rest`, whose test assertion moves to `take`; the two table tests build their cases from kinds.
      The probe `local-tmp/restructure/probe_cycle/probe_table.py` showed pyright narrowing this triple to `Never`, and
      failing when a row goes; if the real types do not narrow, the fallback is a nested `match` on the state, then on
      the kind and the rest, recorded under this item. Paths: `$SRC/domain/account/authorizations.py`,
      `$SRC/domain/model/money.py`, `$APP/tests/unit/test_authorizations.py`,
      `$APP/tests/unit/domain/model/test_money.py`. Proof of the deletion: make `take` return the rest at zero, see a
      table case fail, restore. Command: `pytest tests`, the corpus compare. Proof: passes; equal, every settlement
      input included. Acceptance: AC-02, AC-03, AC-06. - Result: 159 passed, 1 xfailed; the corpus compare prints
      nothing, its seven settlement inputs included (below, reaching, and past the hold, final over it, against a
      declined and an unknown hold, and in BHD). The real types narrow the triple to `Never`, as the probe did, so no
      fallback was needed: with the `Approved, PARTIAL, None` row removed, pyright reports
      `tuple[Approved, Literal[SettlementKind.PARTIAL], None]` cannot be assigned to `Never`. The table test builds each
      case from a kind and an amount; its literals are unchanged. - Mutation: `take` giving the rest at zero fails two
      table cases, `[state2-…]` and `[state5-…]`, and 7 other tests, 9 in all; restored, 159 passed.
- [x] [AI] Move `$SRC/domain/account/reversals.py` into `AccountIn` as private methods; delete with proof (skip
      `_check_undoing`, see an AMB-035 test fail, restore). Command: `pytest tests`. Proof: passes; mutation recorded.
      Acceptance: AC-09. - Result: 159 passed, 1 xfailed; pyright reports only the transition's `reportPrivateUsage`.
      `check_reversal` and `list_reversed_targets` lose their public names, as the domain model states; one docstring
      rewrapped to 120 columns at its new indent, its words unchanged. - Mutation: `_check_reversal` returning
      `Ok(None)` instead of calling `_check_undoing` fails the three
      `test_amb_035_money_already_undone_cannot_be_undone_again` cases and two AMB-014 `AlreadyUndone` cases, 5 in all;
      restored, 159 passed.
- [x] [AI] Move `$SRC/domain/account/decisions.py` into `AccountIn` as `decide_event` and private methods;
      `_decide_effect` and `_record_interest_change`-style steps stay module functions of `account.py`; delete with
      proof (force-post every settlement, see an AMB-012 test fail, restore). Command: `pytest tests`. Proof: passes.
      Acceptance: AC-09. - Result: 159 passed, 1 xfailed; pyright reports only the transition's `reportPrivateUsage`.
      `_decide_effect` and `_generate_instalments`, which read nothing of the account, are module functions of
      `account.py`. - Mutation: force-posting every settlement fails `test_c4_e6_is_force_posted_for_180` (AMB-012,
      AMB-029), `test_c3_auth_a_settlement_is_accepted_and_releases_the_hold`, the AMB-013 tests, and others, 16 in all;
      restored, 159 passed.
- [x] [AI] Move `$SRC/domain/account/fees.py` into `AccountIn`; delete with proof (charge on a zero closing, see an
      AMB-002 test fail, restore). Command: `pytest tests`. Proof: passes. Acceptance: AC-09. - Result: 159 passed, 1
      xfailed; pyright reports only the transition's `reportPrivateUsage`. The fold read
      `history = history.append(entry)` as a reassignment of `self`; `assess_fees` now grows a local `account` instead,
      and the docstrings the fold touched read "the account" again. - Mutation: charging on a zero closing
      (`closing <= zero`) fails `test_c2_e7_causes_three_fees_all_value_dated_day_5` (AMB-002), the AMB-011 and AMB-027
      fee tests, and others, 17 in all; restored, 159 passed.
- [x] [AI] Move `$SRC/domain/account/interest.py` into `AccountIn`; delete with proof (drop the adjustment for an
      earlier day, see an AMB-005 test fail, restore). Command: `pytest tests`, the corpus compare. Proof: passes;
      equal. Acceptance: AC-02, AC-09. - Result: 159 passed, 1 xfailed; the corpus compare prints nothing; pyright
      reports 0 errors, the transition over: no `TYPE_CHECKING` guard remains. `_record_interest_change` is a module
      function of `account.py`. - Mutation: dropping every earlier day's adjustment fails
      `test_amb_005_a_changed_closing_adjusts_its_interest`, `test_c6_day_6_closes_at_285_76_not_285_79`,
      `test_c8_capitalization_equals_the_sum_of_interest_events`, the golden end-to-end run, and others, 8 in all;
      restored, 159 passed.
- [x] [AI] Move the four states from `$SRC/domain/account/states.py` into `$SRC/domain/account/authorizations.py`, which
      now imports no domain event; delete `states.py`, and every importer under `$SRC` and `$APP/tests` follows. It
      holds four frozen types and no rule, so no mutation can make a test miss it; pyright proves every importer moved.
      Command: `pytest tests && (cd $APP && uv run --no-sync ruff check . && uv run --no-sync pyright)`. Proof: all
      pass. Acceptance: AC-13. - Result: ruff, pyright, and 159 tests pass; `authorizations.py` imports only `common`
      and the model, so `domain_events.py` imports it without a cycle; eight importers follow.
- [x] [AI] Remove `derive` from both verb lists in `$APP/pyproject.toml`. Command:
      `(cd $APP && uv run --no-sync pylint src tests)`. Proof: exit 0. Acceptance: AC-15. - Result: pylint exit 0;
      vulture exit 0; `derive` appears nowhere in `pyproject.toml`.
- [x] [AI] Merge `test_fees.py`, `test_interest.py`, `test_reversals.py`, and `test_authorizations.py` from
      `$APP/tests/unit/` into `$APP/tests/unit/domain/account/test_account.py`, grouped by topic in the source's order,
      and move the two table tests to `$APP/tests/unit/domain/account/test_authorizations.py`; the AMB-036 test waits in
      `test_account.py` for Phase 3. Command: `pytest tests` and `inventory.py --compare`. Proof: passes; no name lost.
      Acceptance: AC-03, AC-13. - Result: 159 passed, 1 xfailed; the inventory keeps every baseline name with its count
      and the literals compare equal. `test_account.py` holds 29 tests in the class's topic order, authorizations,
      reversals, fees, then interest, the AMB-036 test among the reversals; `test_authorizations.py` the two table tests
      with the table.
- [x] [AI] Update the architecture as built: L3's `account/` rows, the L3 diagram's aggregate box, L4's account blocks
      and state-machine paragraph and diagram, the Domain Model's aggregate paragraph; and the docstring of
      `$SRC/domain/account/__init__.py`, which says "one account's history". Paths:
      `specs/apps/account-ledger/cli/architecture.md`, `$SRC/domain/account/__init__.py`. Proof: every name there
      exists. Acceptance: AC-14. - Result: every name those sections give exists under `$SRC`, and the doc sweep reports
      nothing. Reading the Code and the app README's domain paragraph named deleted files, so they follow in this phase
      too, not Phase 7; the account package's `ruff.toml` comment says "entries" as well. - Open until Phase 5:
      `003-operations.md` still gives `sum_money` as its example of a generic function, which Phase 1 made a method; its
      rewrite is Phase 5's, through rules-propagation.

### Phase 2 Gate

- [x] [AI] Run `sh local-tmp/restructure/gate.sh`; `grep -rn --include='*.py' "assert " $SRC | grep -v assert_never`
      lists only the ledger's; `grep -rn --include='*.py' TYPE_CHECKING $SRC` prints nothing. Proof: exit 0; one
      `assert` left; no guard survives. Acceptance: AC-02, AC-03, AC-04, AC-06. - Result: every step exit 0: test:quick,
      integration, e2e, the corpus equal, every baseline name with its count and literals, 60 cited names found,
      Markdown, and hygiene; the first run stopped at Prettier on this file, fixed, then `check-md.sh` and
      `check:hygiene` exit 0. One `assert` is left, in `ledger/processing.py`; no `TYPE_CHECKING` guard.
- [x] [AI] Commit as `refactor(cli): gather every account rule into the Account aggregate`, with the WORKLOG entry and
      the Execution Record line, and push. Proof: the hash and range. Acceptance: AC-16. - Result: committed with the
      WORKLOG entry and this Execution Record line, and pushed; the hash is in the Phase 3 line.

Pause safety: the aggregate is one class on `origin/main`. Re-verify with `sh local-tmp/restructure/gate.sh`.

## Phase 3 — The Ledger

Replaces the ledger service's functions with the `Ledger` class and returns an unconfigured account as a fault (R6, R8).

- [x] [AI] Write `Ledger(config, log)` in `$SRC/domain/ledger/ledger.py`, moved from `processing.py` with
      `/usr/bin/git mv`, with `open`, `find_account`, `list_accounts`, `process_event`, `close_day`, and the private
      steps; delete `$SRC/domain/ledger/end_of_day.py` and `$SRC/domain/ledger/event_log.py` and the `Log` alias;
      `$SRC/domain/stream_processing.py`, `$SRC/domain/report.py`, `$APP/tests/support/*.py`, and the tests call the
      class. Add `open` to both verb lists in `$APP/pyproject.toml`. Proof of each deletion, each broken, run, and
      restored: for `processing.py`, skip the repeated-ID check and see an AMB-034 test fail; for `end_of_day.py`, skip
      the capitalization step of `close_day` and see `test_c8_capitalization_equals_the_sum_of_interest_events` fail;
      for `ledger/event_log.py`, make `find_account` build every account from ACC-001's opening and see a test fail.
      Command: `pytest tests`, the corpus compare, `(cd $APP && uv run --no-sync pylint src tests)`. Proof: all pass;
      equal. Acceptance: AC-02, AC-10. - Done: `ledger/ledger.py` (git mv from `processing.py`) holds `Ledger` with
      `open`, `find_account`, `list_accounts`, `process_event`, `close_day`, `_check_target_account`, and `_append`;
      `end_of_day.py`, `ledger/event_log.py`, and `Log` are gone. `_ProcessingState` and `build_report` take the ledger,
      `ProcessedStream.logs` holds `EventLog`s, and the tests read `.entries` where they iterated the tuple. - Proof:
      pytest 159 passed, 1 xfailed; corpus equal; pylint and vulture exit 0; `open` in both verb lists. Mutations:
      repeated-ID check skipped, 8 failed, the five AMB-034 tests among them; capitalization skipped, 7 failed,
      `test_c8_capitalization_equals_the_sum_of_interest_events` among them; `find_account` building from ACC-001's
      opening, 44 failed; each restored.
- [x] [AI] RED: `test_an_event_on_an_unconfigured_account_is_an_internal_fault` in `$APP/tests/unit/test_processing.py`.
      The RED adds `UnknownAccount` and `InternalFault`, and replaces the `assert` with a stub returning the ledger
      unchanged. Command: `pytest tests/unit/test_processing.py`. Proof: fails on its assertion. Acceptance: AC-03,
      AC-06. - Done: the test in `test_processing.py`; `UnknownAccount` and `InternalFault` in `ledger.py`; the `assert`
      replaced by a stub returning the ledger unchanged. - Proof: fails on its assertion,
      `Ok(Ledger(...)) == Err(UnknownAccount(account=AccountId(value='ACC-003')))`.
- [x] [AI] GREEN: `_find_opening` returns `Err(UnknownAccount)`, and `process_event` returns it. Command:
      `pytest tests`. Proof: passes. Acceptance: AC-06. - Done:
      `Ledger._find_opening(account_id) -> Result[AccountOpening, UnknownAccount]`; `process_event` returns
      `Result[Ledger, InternalFault]`. - Proof: pytest 160 passed, 1 xfailed; pyright's one error, in
      `stream_processing.py`, is the widening the next RED makes.
- [x] [AI] RED: `test_an_unknown_account_exits_2_naming_it` in `$APP/tests/unit/test_cli.py`, patching the processing as
      its neighbours do today, until Phase 4 gives it a fake port. The RED widens the processing's fault to
      `InternalFault` with a stub line in `run_cli`. Command: `pytest tests/unit/test_cli.py`. Proof: fails on its
      assertion. Acceptance: AC-03. - Done: the test in `test_cli.py`, patching `process_stream` as its neighbours do;
      `process_stream` and `_ProcessingState`'s event steps return `InternalFault`; `run_cli` holds a stub returning 2
      for `UnknownAccount` with no line. - Proof: fails on its assertion,
      `('', '', 2) == ('', 'error: internal: ACC-003 is not a configured account\\n', 2)`; pyright 0 errors.
- [x] [AI] GREEN: `run_cli` prints `error: internal: ACC-003 is not a configured account` and exits 2 through one
      `match` over `InternalFault` ending in `assert_never`. Command: `pytest tests`. Proof: passes. Acceptance:
      AC-06. - Done: `run_cli` writes `error: internal: ` and `_describe_internal_fault(fault)`, one `match` over
      `InternalFault` ending in `assert_never`; the currency mismatch's line is unchanged. - Proof: pytest 161 passed, 1
      xfailed; pyright 0 errors.
- [x] [AI] REFACTOR: both cycles' docstrings; in `$APP/README.md`, the exit table's internal row reads "an internal
      fault" for "a currency mismatch", and the sentence after the table names the new line and says no input reaches
      it. Command: `pytest tests`. Proof: passes. Acceptance: AC-14. - Done: `process_stream`'s and `_process_file`'s
      docstrings name the internal fault; the app README's exit row reads "an internal fault, which only a bug brings",
      and the sentence after the table gives the unknown account's line and says no input reaches it. - Proof: pytest
      161 passed, 1 xfailed; Prettier clean.
- [x] [AI] Move `$APP/tests/unit/test_processing.py` to `$APP/tests/unit/domain/ledger/test_ledger.py` and the AMB-036
      test into it. Command: `pytest tests`, `inventory.py --compare`. Proof: passes; no name lost. Acceptance: AC-03,
      AC-13. - Done: `tests/unit/domain/ledger/test_ledger.py` (git mv), holding the four AMB-034 tests, the AMB-036
      test moved from `test_account.py`, and the unconfigured-account test; its docstring names all three. - Proof:
      pytest 161 passed, 1 xfailed; `inventory.py --compare`: every baseline name kept with its count, 5 added; literals
      kept (115 names); cited 60, missing 0.
- [x] [AI] Update the architecture as built: L3's `ledger/` rows and diagram box, L4's ledger line, the Dynamic View's
      calls, and the Domain Model's Ledger paragraph; and the docstring of `$SRC/domain/ledger/__init__.py`, which says
      "the log of every account". Proof: every name exists. Acceptance: AC-14. - Done: L3's prose, the `ledger` box, and
      one `ledger/ledger` row for the three; L4's `ledger/ledger` block and `stream_processing`'s `EventLog` logs and
      `InternalFault`; the Dynamic View's `Ledger.process_event`, `Ledger.close_day`, `build_report(ledger, ...)`, and
      the unknown account's line; the Domain Model's `Ledger` row and paragraph; Reading the Code steps 3 and 5;
      `ledger/__init__.py` and `ledger/ruff.toml`'s comment. Beyond the item, the stale "ledger service" in
      `/README.md`'s domain paragraph and `specs/apps/account-ledger/README.md` names the `Ledger`. - Proof:
      `doc_sweep.py` reports no missing identifier, path, or link; every line within 120; Prettier clean.

### Phase 3 Gate

- [x] [AI] Run `sh local-tmp/restructure/gate.sh`; `grep -rn --include='*.py' "assert " $SRC | grep -v assert_never`
      prints nothing. Proof: exit 0. Acceptance: AC-02, AC-03, AC-04, AC-06. - Done 20:11: `gate.sh` exit 0 (GATE
      PASSED): test:quick, test:integration, and test:e2e pass, 161 passed and 1 xfailed across the layers, coverage
      95%; corpus equal; every baseline name kept, 5 added; literals kept; cited 60, missing 0; Markdown and hygiene
      clean. - Proof: the `assert` grep prints nothing.
- [x] [AI] Commit as `refactor(cli): run every account through the Ledger`, with the WORKLOG entry and the Execution
      Record line, and push. Proof: the hash and range. Acceptance: AC-16. - Done 20:13: 0cbeb9a, pushed as
      5a36329..0cbeb9a; the push hooks passed.

Pause safety: the Ledger is on `origin/main`. Re-verify with `sh local-tmp/restructure/gate.sh`.

## Phase 4 — The Application, Its Ports, and the Adapters

Builds `application/`, the two adapters, and the shell as
[the application, ports, and adapters](tech-docs/003-application-ports-and-adapters.md) state (R2, R5, R12, R20).

- [x] [AI] Create `$SRC/application/__init__.py`, and move `$SRC/domain/report.py` to `$SRC/application/report.py` with
      `/usr/bin/git mv`; `DayReport.build` replaces `build_report`, `EventLog.list_processed_on` replaces the report's
      `entry.processed_day == day` filters, the `ReportedClosings` class replaces the alias and `update_reported`, and
      `_compute_closing` and `_compute_available`, forwarding wrappers of the module being moved, go with the move
      (R19). Command: `pytest tests`, the corpus compare. Proof: passes; equal. Acceptance: AC-02, AC-08. - Done:
      `application/report.py` (git mv); `DayReport.build(ledger, day, reported)`, the `ReportedClosings` class with
      `make_empty`, `update`, `list_days_before`, and `find_closings`; `EventLog.list_processed_on(day)` replaces the
      three `processed_day == day` filters; `_map_balances` takes lambdas where `_compute_closing` and
      `_compute_available` stood; the builders name each `Account` `account` where they named it `history`. - Proof:
      pytest 161 passed, 1 xfailed; corpus equal; pyright 0; pylint and vulture exit 0.
- [x] [AI] Move `$SRC/domain/stream_processing.py` to `$SRC/application/stream.py` with `/usr/bin/git mv`;
      `IncomingStream.process` replaces `process_stream`, and `_ProcessingState` holds the `Ledger`. Command:
      `pytest tests`, the corpus compare. Proof: passes; equal. Acceptance: AC-02, AC-08. - Done:
      `application/stream.py` (git mv); `IncomingStream(events).process(config)` replaces `process_stream`, its
      docstring unchanged; `_ProcessingState` has held the `Ledger` since Phase 3, and its `reported` field is the
      class. Every caller and test builds an `IncomingStream`; until the CLI item, the CLI tests patch
      `IncomingStream.process` where they patched `cli.process_stream`. - Proof: pytest 161 passed, 1 xfailed; corpus
      equal; literals kept.
- [x] [AI] Create `$SRC/application/ports.py` with `SourceFault`, `EventSource`, `ReportSink`, `RunLedger`, and
      `RunFault`, now that `IncomingStream` and `DayReport`, which its signatures name, exist. Command:
      `(cd $APP && uv run --no-sync pyright)`. Proof: 0 errors. Acceptance: AC-11. - Done: `SourceFault(message)`, the
      `Protocol`s `EventSource.read_events(config)`, `ReportSink.publish(reports)`, and `RunLedger.run(source, sink)`,
      and `type RunFault = SourceFault | InternalFault`; each protocol method is a docstring and `...`, since pyright
      refuses a docstring-only body that returns a value. `publish` joined both verb lists here, where `ReportSink`
      declares it, rather than with `flush`. - Proof: pyright 0 errors; pylint exit 0.
- [x] [AI] Move `$SRC/adapters/stream_csv.py` to `$SRC/adapters/csv_file.py` with `/usr/bin/git mv`: `CsvFileSource`
      with `read_events` and the static `parse`, `Reader`, `read_file`, and `_describe_fault` moved from `$SRC/cli.py`,
      `REQUIRED` and `OPTIONAL` frozen, and `RowKind`. Command: `pytest tests`. Proof: passes. Acceptance: AC-11,
      AC-12. - Done: `adapters/csv_file.py` (git mv); `CsvFileSource(path, read_text)` with `read_events(config)`, which
      gives `cannot read PATH: REASON` or the `StreamError`'s message as a `SourceFault`, and the static
      `parse(text, config) -> Result[IncomingStream, StreamError]`; `Reader`, `read_file`, and `_describe_fault` moved
      from `cli.py`, which reads through the source; `REQUIRED` and `OPTIONAL` are `MappingProxyType`s keyed by
      `RowKind`, and `_find_kind` narrows the type cell to one. The CSV tests call `CsvFileSource.parse` and compare
      with an `IncomingStream`. - Proof: pytest 161 passed, 1 xfailed; corpus equal, every file fault included; pyright
      0; pylint exit 0.
- [x] [AI] Move `$SRC/adapters/render.py` to `$SRC/adapters/text_report.py` with `/usr/bin/git mv`: `TextOutput`,
      `TextReportSink` with `publish` and the static `render`, `NUMBER_WORDS` frozen. Add `publish` and `flush`, which
      `TextOutput` declares and the test double implements, to both verb lists in `$APP/pyproject.toml`, and run
      `(cd $APP && uv run --no-sync pylint src tests)`. Command: `pytest tests`. Proof: passes. Acceptance: AC-11,
      AC-12. - Done: `adapters/text_report.py` (git mv); `TextOutput`, a `Protocol` of `write(text, /)` and `flush()`;
      `TextReportSink(out)` with `publish(reports)`, one write then a flush, and the static `render(reports)`;
      `NUMBER_WORDS` a `MappingProxyType`; `run_cli` publishes through the sink. `flush` joined both verb lists
      (`publish` did with the ports). Where the longer call made ruff split a line, the test names the report in a
      local, so every literal stays in its test. The `_build_applied_row` fold waits for Phase 6, as R19 settles. -
      Proof: pytest 161 passed, 1 xfailed; pylint exit 0; corpus equal; literals kept.
- [x] [AI] Write `$SRC/application/run.py`, `LedgerRun`. Command: `(cd $APP && uv run --no-sync pyright)`. Proof: 0
      errors. Acceptance: AC-11. - Done: `LedgerRun(config)` with `run(source, sink) -> Result[None, RunFault]`: read,
      process, publish; the first `Err` ends it before anything is published. - Proof: pyright 0 errors.
- [x] [AI] Rewrite `$SRC/cli.py`: `run_cli(argv, read_text, out, err, run_ledger)` builds the two adapters and maps each
      fault; `main` binds `read_file`, the streams, and `LedgerRun(CHALLENGE)`. The CLI tests in
      `$APP/tests/unit/test_cli.py` pass a fake `RunLedger` where they patched `process_stream`, each fake built inside
      its test with the literals the replaced helper held, such as `ZeroDivisionError("a bug in the domain")`, and
      `ClosedPipe` becomes a plain class. Command: `pytest tests`, the corpus compare. Proof: passes; equal, every file
      fault and argument error included. Acceptance: AC-02, AC-11. - Done:
      `run_cli(argv, read_text, out, err, run_ledger)` keeps its three handlers and the argument check, builds
      `CsvFileSource` and `TextReportSink`, and maps each `RunFault` through one `match` ending in `assert_never`;
      `main` binds `read_file`, the streams, and `LedgerRun(CHALLENGE)`. The CLI tests pass `LedgerRun(CHALLENGE)`, or a
      `FailingRun` or `RaisingRun` built in the test with the literals the patched helper held; no test patches a
      module; `ClosedPipe` is a plain class with `write` and `flush`. - Proof: pytest 161 passed, 1 xfailed; corpus
      equal, every file fault and argument error included; literals kept; pylint and vulture exit 0.
- [x] [AI] Write `$SRC/application/ruff.toml` and `$SRC/adapters/ruff.toml`, and rewrite the five existing bans, as
      [the import bans](tech-docs/003-application-ports-and-adapters.md#the-import-bans) state. Prove each ban: add a
      forbidden import to one module of each package, see `ruff check` fail with TID251, restore. Command:
      `(cd $APP && uv run --no-sync ruff check .)`. Proof: passes; seven failures recorded under mutation. Acceptance:
      AC-11. - Done: `application/ruff.toml` and `adapters/ruff.toml` are new; the four domain files refuse
      `application`, `adapters`, `cli`, and `challenge` in place of `domain.report` and `domain.stream_processing`,
      `domain/model/` still refusing `domain.account` and `domain.ledger` and `domain/account/` `domain.ledger`;
      `common/` adds `application` and `challenge`. - Proof: `ruff check .` passes. Seven failures recorded under
      mutation, one forbidden import each, restored after: `common/result.py` challenge; `domain/__init__.py`
      application; `domain/model/money.py` `domain.ledger`; `domain/account/event_log.py` application;
      `domain/ledger/ledger.py` challenge; `application/run.py` adapters; `adapters/csv_file.py` challenge; each
      reported as `banned-api`, TID251's name.
- [x] [AI] Move the tests, from `$APP/tests/unit/` unless named: `test_stream_processing.py`, `test_criteria.py`, and
      `test_known_weakness.py` into `$APP/tests/unit/application/test_stream.py`; `test_report.py` to
      `$APP/tests/unit/application/`; `test_stream_csv.py` and `test_render.py` to
      `$APP/tests/unit/adapters/test_csv_file.py` and `test_text_report.py`;
      `$APP/tests/integration/test_stream_file.py` to `$APP/tests/integration/adapters/test_csv_file.py`, and
      `$APP/tests/integration/test_main.py` to `$APP/tests/integration/test_cli.py`, whose imports of `render_reports`
      and `process_stream` follow the new API. Command: `pytest tests`, `inventory.py --compare`. Proof: passes; no name
      lost; `1 xfailed`. Acceptance: AC-03, AC-13. - Done: `test_stream_processing.py` (git mv), `test_criteria.py`, and
      `test_known_weakness.py` merged into `tests/unit/application/test_stream.py` in that order, the known weakness
      keeping `xfail(strict=True)`, its reason, and its annotations; `test_report.py` to `tests/unit/application/`;
      `test_stream_csv.py` and `test_render.py` to `tests/unit/adapters/test_csv_file.py` and `test_text_report.py`;
      `tests/integration/test_stream_file.py` to `tests/integration/adapters/test_csv_file.py`, one directory deeper, so
      its path to the shipped stream climbs one more level; `tests/integration/test_main.py` to
      `tests/integration/test_cli.py`; each module docstring names what it now tests. - Proof: pytest 161 passed, 1
      xfailed; `inventory.py --compare`: every baseline name kept with its count; literals kept.
- [x] [AI] Update the architecture as built: the L3 prose, diagram, and table; L4's report, stream, and adapter lines;
      the Dynamic View; the Domain Model's report paragraph; Reading the Code. Update `$APP/README.md`'s layout table,
      the `domain/` row and the new `application/` and `challenge.py` rows included, its DDD paragraph, and the known
      weakness's path; and the docstrings of `$SRC/domain/__init__.py` and `$SRC/adapters/__init__.py`, which name the
      report and the renderer. Proof: every name exists. Acceptance: AC-14. - Done: L3 rewritten for four layers, its
      diagram adding the application and the adapters as ports, its table the `csv_file`, `text_report`, `ports`, `run`,
      and `stream` rows; L4's report, stream, ports, run, `csv_file`, and `text_report` lines,
      `EventLog.list_processed_on`, and the Protocols beside the values; the Dynamic View from `run_cli` through
      `LedgerRun` to `TextReportSink.publish`; the Domain Model's report paragraph; Reading the Code steps 2 and 12 and
      its closing note. `/README.md`: the layout table's shell, `challenge.py`, adapters, `application/`, domain, and
      unit-test rows, its DDD paragraph, and the known weakness's path. The docstrings of `domain/__init__.py`,
      `adapters/__init__.py`, and `cli.py`, which no longer holds the file reader. - Proof: `doc_sweep.py` reports no
      missing identifier, path, or link; every line within 120; Prettier clean. Open until Phase 5: `001-naming.md`
      still gives `parse_stream` as an example name, beside `003-operations.md`'s `sum_money`.

### Phase 4 Gate

- [x] [AI] Run `sh local-tmp/restructure/gate.sh`. Proof: exit 0; the inventory lists the five new names. Acceptance:
      AC-02, AC-03, AC-04, AC-11. - Done 20:33: `gate.sh` exit 0 (GATE PASSED): test:quick, test:integration, and
      test:e2e pass, coverage 95%; corpus equal; every baseline name kept, and the inventory lists the five new names;
      literals kept; cited 60, missing 0; Markdown and hygiene clean.
- [x] [AI] Commit as `refactor(cli): put the use case behind ports and adapters`, with the WORKLOG entry and the
      Execution Record line, and push. Proof: the hash and range. Acceptance: AC-16. - Done 20:35: 553041a, pushed as
      0cbeb9a..553041a; the push hooks passed.

Pause safety: the layers are on `origin/main`. Re-verify with `sh local-tmp/restructure/gate.sh`.

## Phase 5 — No Inheritance, Gated and Written Down

Enables the gate and changes the rule through rules-propagation, now that the code follows it (R3, R9, R21).

- [x] [AI] RED: run pylint with `--enable=too-many-ancestors --max-parents=0` and the six ignored parents on the
      baseline copy's `$BASE/src` and `$BASE/tests`, and on a scratch probe holding one dataclass subclass. Record in
      `$EV/phase-5-no-inheritance.txt`. Proof: the baseline and the probe fail, naming the derived classes. Acceptance:
      AC-07. - Done 20:34: recorded in `$EV/phase-5-no-inheritance.txt`, mapped in the evidence README. - Proof: exit 8,
      39 findings: 38 derived classes on the baseline copy, `ClosedPipe(io.StringIO)` among them, and the probe's
      `Derived(Base)`. Without `builtins.NoneType` the tree's four Enums fail too, so the six ignored parents stay.
- [x] [AI] GREEN: enable `too-many-ancestors` and add `[tool.pylint.design]` in `$APP/pyproject.toml`, as
      [the rule changes](tech-docs/005-specification-rule-and-doc-changes.md#e-appsaccount-ledger-clipyprojecttoml)
      show. Command: `(cd $APP && uv run --no-sync pylint src tests)`. Proof: exit 0, appended to the evidence file.
      Acceptance: AC-07. - Done 20:35: `too-many-ancestors` enabled; `[tool.pylint.design]` sets `max-parents = 0` and
      the six ignored parents, with a comment on why `NoneType` is among them; the comment above the enable list names
      the check. - Proof: pylint exit 0 on `src` and `tests`, appended to the evidence file; the probe copied into `src`
      fails with R0901, then is removed.
- [x] [AI] Open the rules-propagation record `local-tmp/rules-propagation-no-inheritance.md`, naming each file below and
      the placement: development level, the Python standards' Operations module. Proof: the record. Acceptance: AC-15. -
      Done 20:37: the record freezes the three rules with reason, strength, scope, and enforcement; the conflict scan
      finds Simplicity Over Complexity agreeing and no same-level contradiction; placement is the Operations module,
      with the entrypoint, the module map, the naming module, and the architecture carried. - Proof: the record,
      `local-tmp/rules-propagation-no-inheritance.md`.
- [x] [AI] Rewrite `repo-governance/development/quality/stacks/python-standards/003-operations.md`: its frontmatter, the
      example, four cases, the aggregate sentence, and No Inheritance, as 005's diff shows. Command:
      `./rhino governance word-budget validate`. Proof: exit 0. Acceptance: AC-15. - Done: the frontmatter; the example
      `account.list_instalments(credit)`; four cases, the type-alias clause, the service, and the type-variable case
      gone with their code; the aggregate sentence; No Inheritance in place of Shared Bases, tracing to Simplicity Over
      Complexity and naming its gate. The opening, the criterion, cases 1, 2, and 5 (now 4), and the followed and
      violated sentences stay. - Proof: `./rhino governance word-budget validate` exit 0;
      `./rhino md internal-link validate` exit 0.
- [x] [AI] Rewrite the summary and Enforcement sentence of
      `repo-governance/development/quality/stacks/python-standards.md`, the file within 750 words, and the module row of
      `python-standards/README.md`; change `001-naming.md`'s example and drop its library-override exemption, as 005's
      diffs show. Command: `./rhino governance word-budget validate && ./rhino governance directory-map validate`.
      Proof: both 0. Acceptance: AC-15. - Done: the Operations summary now names four cases and no inheritance but
      `Protocol`, `Generic`, `Enum`, or exception; Enforcement names inheritance among the gates; the file is 746 words
      (wc). The README row ends "no inheritance"; `001-naming.md` gives `parse_event_id` and drops the library-override
      exemption. The architecture's Domain Model pointer and a Constraints bullet carry the rule. - Proof:
      `./rhino governance word-budget validate` exit 0 (233 files, no findings);
      `./rhino governance directory-map validate` exit 0 (60 directories, no findings).
- [x] [AI] Search the live corpus for the old wording:
      `grep -rnE --include='*.md' "$OLD" .agents repo-governance AGENTS.md specs docs apps`, where `OLD` is
      `six named|Shared Bases|share a base|shared base|sum_money|AccountHistoryIn|AccountAggregateIn`. Proof: it prints
      nothing. Acceptance: AC-15. - Done: run under bash as written. - Proof: no output, grep exit 1. Outside the
      searched set, only WORKLOG row 16:05, a past entry never reworded, says "shared bases".
- [x] [AI] Close the record: every file carried, the check commands and their exits. Proof: the record. Acceptance:
      AC-15. - Done: `local-tmp/rules-propagation-no-inheritance.md` closed at 20:40: the five rule and doc files and
      `pyproject.toml` carried; word-budget, directory-map, and internal-link exit 0; the grep prints nothing; the
      bindings are unchanged. - Proof: the record, every box ticked.

### Phase 5 Gate

- [x] [AI] Run `sh local-tmp/restructure/gate.sh` and `./rhino md internal-link validate`. Proof: both 0. Acceptance:
      AC-07, AC-15. - Done 20:43: `GATE PASSED`, exit 0 (test:quick, integration, e2e, corpus equal, every baseline name
      kept with 5 added, 115 names' literals equal, `cited 60 defined 120 missing 0`, Markdown, hygiene); internal-link
      exit 0, 1490 links, no findings.
- [x] [AI] Commit the gate as `build(cli): refuse class inheritance in lint` and the rule as
      `docs(governance): keep operations on their type, without inheritance`, with the WORKLOG entry and the Execution
      Record line, and push. Proof: the hashes and range. Acceptance: AC-16. - Done 20:46: 62ced26 (the gate and its
      evidence) and 4bb46c9 (the rule, its docs, the WORKLOG entry, and the Phase 5 line), pushed as 553041a..4bb46c9;
      every hook passed.

Pause safety: the gate and the rule are on `origin/main`. Re-verify with `sh local-tmp/restructure/gate.sh`.

## Phase 6 — Polish, File by File

Reads every source and test file once, top to bottom, and fixes what the comb finds without changing behaviour (R19).

- [x] [AI] Comb the values: `$SRC/domain/model/{money,ids,events,config}.py`, `$SRC/challenge.py`,
      `$SRC/common/result.py`. Look for: stale docstrings naming a removed type or module, parenthesized single imports,
      definition order, a comment that restates the code. Command: `pytest tests`. Proof: passes; each fix listed.
      Acceptance: AC-14. - Done: `challenge.py`'s docstring named the CLI passing the configuration to the stream
      reader; it now says `main` gives it to `LedgerRun`, which passes it to the event source and the ledger, and no
      layer below the shell imports it. `money.py`, `ids.py`, `events.py`, `config.py`, and `result.py` needed nothing:
      no stale name, no single import wrapped, top-down order, no comment restating code. - Proof: `pytest tests` 161
      passed, 1 xfailed.
- [x] [AI] Comb the aggregate package, `$SRC/domain/account/`: `account.py`, `authorizations.py`, `domain_events.py`,
      `event_log.py`, `rejections.py`; `_record_interest_change`'s wrapped `if (day == today):` becomes
      `if day == today:`, its comment moved to the line above. Command: `pytest tests`. Proof: passes; each fix listed.
      Acceptance: AC-14. - Done: `_record_interest_change`'s wrapped `if (day == today):` is `if day == today:`, its
      comment on the line above; `rejections.py`'s docstring now says the Ledger refuses a reused ID or another
      account's target and the aggregate the rest; the money imports of `account.py` and `authorizations.py`, wrapped
      only by a leftover trailing comma, fit one line (with five more such imports across the tree). - Proof:
      `pytest tests` 161 passed, 1 xfailed.
- [x] [AI] Comb `$SRC/domain/ledger/ledger.py`, every module of `$SRC/application/` and `$SRC/adapters/`, `$SRC/cli.py`,
      and `$SRC/__main__.py`; in the adapters, `_CommonFields`'s layout is tidied and `_build_applied_row`'s repeated
      tuples fold into one. Command: `pytest tests`, the corpus compare. Proof: passes; equal. Acceptance: AC-02,
      AC-14. - Done: `UnknownAccount` names the event source, not the stream reader; `ports.py` marks the printed
      `error: ` with single backticks, as every docstring marks printed text; `report.py`'s domain-events import fits
      one line. In the adapters `_CommonFields` is one line with its comment above; `text_report.py`'s `MINUS` and
      `NUMBER_WORDS` join the constants at the top, `_build_event_rows` follows the two block helpers,
      `_build_processed_rows` reads the event once, and `_build_applied_row`'s two six-cell tuples fold into
      `_build_generated_row`. `run.py`, `stream.py`, `cli.py`, and `__main__.py` needed nothing. - Proof: `pytest tests`
      161 passed, 1 xfailed; the corpus compares equal.
- [x] [AI] Split the test support into builders and readers (R22): move `list_fee_ids`, `list_refund_ids`,
      `list_interest_amounts`, and `list_capitalization_amounts` from `$APP/tests/support/streams.py`, and every
      function of `$APP/tests/support/states.py`, into the new `$APP/tests/support/entries.py`; delete `states.py`, and
      every importer follows. Command: `pytest tests`, `inventory.py --compare`, `test_literals.py --compare`. Proof:
      passes; no name or literal lost; `streams.py` holds only builders. Acceptance: AC-03, AC-13. - Done:
      `tests/support/entries.py` holds the seven readers, `list_fee_ids`, `list_refund_ids`, `list_interest_amounts`,
      and `list_capitalization_amounts` from `streams.py` and `list_states`, `list_settlements`, and `list_entries` from
      `states.py`; `states.py` is deleted; `test_stream.py`, `test_account.py`, and `test_ledger.py` import the readers
      from `support.entries`. `list_states` takes an `opening` and names what `find_account` gives `account`, not
      `history`; no caller passed it by keyword. - Proof: `pytest tests` 161 passed, 1 xfailed; `inventory.py --compare`
      every baseline name kept with its count; `test_literals.py --compare` 115 names' literals equal; `streams.py`
      holds only builders, `HEADER`, and the two openings.
- [x] [AI] Comb every module under `$APP/tests`: `support/streams.py`'s `ACC_001` and `ACC_002` openings become
      `ACC_001_OPENING` and `ACC_002_OPENING`; docstrings name the new API; no helper duplicates another. Command:
      `pytest tests`, `inventory.py --compare`. Proof: passes; no name lost. Acceptance: AC-03, AC-14. - Done: the
      openings in `support/streams.py` are `ACC_001_OPENING` and `ACC_002_OPENING`, as is `test_config.py`'s local one,
      while the `AccountId` constants of `brief_stream.py` and `test_csv_file.py` keep `ACC_001`; five docstrings named
      the stream reader or the renderer and now name the event source or the report sink (`values.py`,
      `test_csv_file.py`, `test_stream.py`, `test_ledger.py`, `test_report.py`), as do three in `src`; `test_money.py`
      and `money.py` say the account keeps each effect in its currency, not the reader; `test_account.py` no longer
      claims AMB-036, whose test is in `test_ledger.py`; `streams.py` names `Instalments.make` as the split. The three
      nested `list_details` helpers of `test_text_report.py` each select other rows, and their literals belong to their
      tests, so they stay. - Proof: `pytest tests` 161 passed, 1 xfailed; `inventory.py --compare` every baseline name
      kept with its count.
- [x] [AI] Search for stale names across the application: `grep -rnwE --include='*.py'` over `$SRC` and `$APP/tests` for
      `history`, `aggregate`, `stream_processing`, `process_stream`, `render_reports`, `parse_stream`, `Log`, and any
      name ending in `_of`. Proof: each hit is either the domain word used correctly or fixed. Acceptance: AC-14. -
      Done: run under bash as written. Every hit is the domain word `aggregate` in a docstring, used as the architecture
      defines it: the Account aggregate (8 hits in `src`, 1 in `tests`); no `history`, `stream_processing`,
      `process_stream`, `render_reports`, `parse_stream`, or `Log`; no name ends in `_of` (exit 1). - Proof: the two
      searches.

### Phase 6 Gate

- [x] [AI] Run `sh local-tmp/restructure/gate.sh`. Proof: exit 0. Acceptance: AC-02, AC-03, AC-04. - Done 20:53:
      `GATE PASSED`, exit 0: every step exit 0, the corpus equal, every baseline name kept with 5 added, 115 names'
      literals equal, `cited 60 defined 120 missing 0`.
- [x] [AI] Commit as `style(cli): comb every module after the restructure`, with the WORKLOG entry and the Execution
      Record line, and push. Proof: the hash and range. Acceptance: AC-16. - Done 20:55: d592e56, with the WORKLOG
      entry, the Phase 6 line, and the app README's `tests/support/` row naming the log readers; pushed as
      4bb46c9..d592e56; every hook passed.

Pause safety: the polish is on `origin/main`. Re-verify with `sh local-tmp/restructure/gate.sh`.

## Phase 7 — The Documents as Built

Reads each document against the tree and carries every change the restructure made stale (AC-14).

- [x] [AI] Read `architecture.md` against the tree from top to bottom; Scope, L1, and L2 unchanged; add the Constraints
      bullet. Proof: every module, type, and function it names exists (`grep`), and every source module appears in L3.
      Acceptance: AC-14. - Done: Scope, L1, and L2 unchanged; the Constraints bullet on inheritance landed in Phase 5.
      Carried now: `__main__.py` joins the shell in L3's prose, its box, and the table, so every source module appears;
      the ban sentence names `account_ledger.cli` and `account_ledger.challenge` rather than "the shell's two modules";
      the dynamic view's closing paragraph says each account keeps its effects in its currency and the event source
      refuses an unknown account, not "the reader"; the effects Constraint says they are bound in the shell and
      performed in the adapters, as L3 does. - Proof: a script over every backticked and diagram name finds each code
      name in `src` (the misses are English words only), every path exists, and each of the 19 source modules but the
      `__init__.py` files appears in L3.
- [x] [AI] Read `$APP/README.md` against the tree: layout, DDD paragraph, exit table, known weakness. Proof: every path
      exists. Acceptance: AC-14. - Done: the layout table gains `__main__.py`; the `tests/support/` row names the log
      readers (carried in d592e56); the exit paragraph says the event source refuses an unconfigured account, not the
      stream reader; the `lint` line names pylint's class-base check. The DDD paragraph, the exit table, and the known
      weakness's `tests/unit/application/test_stream.py` match the tree. - Proof: every path in the README exists (a
      loop over each backticked `src/`, `tests/`, and `streams/` path and the three project files printed nothing
      missing).
- [x] [AI] Add the layers to the root `README.md` in one sentence under its opening paragraph, pointing at the
      architecture. Proof: the sentence and a resolving link. Acceptance: AC-14. - Done: under the opening paragraph:
      "The program is layered around its domain: the shell binds every effect, the adapters read the CSV stream and
      write the text report, the application runs the one use case through its ports, and the domain holds every rule,
      as the architecture draws it." - Proof: the sentence; its link resolves (internal-link in the Phase 7 gate).
- [x] [AI] Rewrite `local-tmp/restructure/scale.py` against the new API, measure 6, 30, 60, and 120 days and the
      1,000-event volume run on the result into `local-tmp/restructure/timings-result.txt`, and update
      `docs/explanation/architecture-trade-offs.md`'s table and figures if any moves by more than a fifth from the
      recorded ones; replace "history" with "entries" where it names the code. Proof: the measurements and the diff.
      Acceptance: AC-14. - Done: `scale.py` parses through `CsvFileSource.parse` and processes through
      `IncomingStream.process`, with `CHALLENGE` from `challenge`. On the result: 6 days 0.01 s, 30 days 0.47 s, 60 days
      3.56 s, 120 days 27.21 s, and the 1,000-event volume 0.71 s, in `local-tmp/restructure/timings-result.txt`.
      Against the recorded 0.01, 0.46, 3.50, 26.89, and 0.71 none moves by a fifth, so the table stands; the prose now
      says the figures were measured again after the restructure. Its five uses of "history" for the code now say the
      account's entries, and a figure is worked out by a method of the Account aggregate, not a function. - Proof: the
      measurements above; `git diff docs/explanation/architecture-trade-offs.md` changes prose only, the table
      untouched.
- [x] [AI] Extend `local-tmp/restructure/doc_sweep.py` with the names the restructure removed, and run the removed-name
      check over every tracked Markdown file and the Phase 0 checks over the Phase 0 scope. Command:
      `python3 local-tmp/restructure/doc_sweep.py`. Proof: no hit outside `plans/done/` and this plan. Acceptance:
      AC-14. - Done: 29 removed names (the old modules `history.py`, `aggregate.py`, `stream_csv`, `render.py`,
      `processing.py`, `end_of_day.py`, `domain/report.py`, `states.py`; the old functions and types, `process_stream`,
      `parse_stream`, `render_reports`, `build_report`, `update_reported`, `find_history`, `AccountHistory`,
      `AccountAggregate`, `format_id`, `sum_money`, `is_aed_history`, every `_of(`, and `` `Log` ``; and the superseded
      rule's wording) checked over every tracked Markdown file, besides the Phase 0 checks over their 18 files. - Proof:
      exit 0: no removed name, missing identifier, missing path, or bad link. One hit outside the plans is WORKLOG's
      16:05 entry, "shared bases", which the script reports as history: a WORKLOG entry is never reworded.
- [x] [AI] Check the assessment docs:
      `/usr/bin/git diff 83dfd58 -- AMBIGUITIES.md NUMBERS.md REJECTED.md MOVEMENT.md OUTPUT_TARGET.md challenge-raw.md`
      is empty; `WORKLOG.md` only gained entries, newest first. Proof: the empty diff and the WORKLOG diff showing only
      additions. Acceptance: AC-05. - Done: the diff of the six files against 83dfd58 is empty (0 lines); `WORKLOG.md`'s
      diff against 83dfd58 removes no line and adds only entries, newest first. - Proof: `wc -l` 0 on the six-file diff;
      0 removed lines in the WORKLOG diff.

### Phase 7 Gate

- [x] [AI] Run `sh local-tmp/restructure/gate.sh`, `./rhino md internal-link validate`,
      `./rhino md heading-hierarchy validate`, and `./rhino md naming validate`. Proof: each 0. Acceptance: AC-14. -
      Done 21:03: `GATE PASSED`, exit 0; internal-link exit 0 (1491 links, no findings); heading-hierarchy exit 0;
      naming exit 0.
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
- [ ] [AI] Record `$EV/phase-8-tests.txt` and `$EV/phase-8-literals.txt`, and compare each with Phase 0's. Proof: every
      baseline name with its count and its literals, five added, one xfail, nothing skipped. Acceptance: AC-03.
- [ ] [AI] Run `cited_names.py`. Proof: `missing 0`. Acceptance: AC-04.
- [ ] [AI] Audit the types: `pyright` 0 errors;
      `grep -rnE --include='*.py' "\bassert |\bAny\b|cast\(|type: ignore|noqa" $SRC` prints nothing but `assert_never`.
      Proof: both. Acceptance: AC-06.
- [ ] [AI] Audit the operations: `python3 local-tmp/restructure/audit.py --check`, its first list. Proof: exactly the
      six AC-08 names. Acceptance: AC-08.
- [ ] [AI] Audit the aggregate and the ledger: `grep -rn --include='*.py' "AccountIn\[" $SRC` shows it as a subject only
      in `account.py`; `grep -rnE --include='*.py' "^def (process_event|close_day|find_history)|^type Log " $SRC` prints
      nothing. Proof: both. Acceptance: AC-09, AC-10.
- [ ] [AI] Audit immutability: `python3 local-tmp/restructure/audit.py --check`, its second and third lists. Proof:
      every class frozen and slotted or one of AC-12's exceptions; no module-level `dict`, `list`, or `set` under
      `$SRC`. Acceptance: AC-12.
- [ ] [AI] Compare the layout: the sorted `.py` paths under `$SRC` and `$APP/tests` equal the trees in
      [the target layout](tech-docs/001-target-layout.md). Proof: the diff is empty. Acceptance: AC-13.
- [ ] [AI] Run the six mutation spot-checks
      [behaviour preservation](tech-docs/004-behaviour-preservation-and-tests.md#every-other-proof) lists, each broken,
      run, and restored, into `$EV/phase-8-mutations.txt`. Proof: each names the test that failed. Acceptance: AC-02.
- [ ] [AI] Write `$EV/phase-8-timings.txt` with Phase 0's timings and `local-tmp/restructure/timings-result.txt` side by
      side. Proof: the file. Acceptance: AC-14.
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
      0 record. Proof: the compare equal again, recorded under the item. Acceptance: AC-02.
- [ ] [AI] RC2 — a cited or baseline test cannot keep its name or cases. Trigger: `inventory.py --compare` or
      `cited_names.py` fails and the test cannot be carried as it is. Owner: the owner, since an assessment doc cites
      it. Procedure: keep the test as it is in a file of its own beside its target, amend the test tree in
      [the target layout](tech-docs/001-target-layout.md) to list that file, log the change in the Execution Record, and
      record why in learnings; never rename it and never edit an assessment doc. Proof: both scripts pass, and AC-13's
      compare with the amended tree. Acceptance: AC-03, AC-04, AC-13.
- [ ] [AI] RC3 — a pushed phase proves wrong. Trigger: a later phase finds a defect a pushed phase made that a forward
      fix cannot reach before submission. Owner: the executor. Procedure: `/usr/bin/git revert` of that phase's commits,
      newest first, as new commits, pushed; the phase then reruns. Proof: the gate passes on the reverted tree.
      Acceptance: AC-16.
- [ ] [AI] RC4 — a hook fails a commit or a push. Trigger: the pre-commit or pre-push hook exits non-zero. Owner: the
      executor. Procedure: read its output, fix the cause, and commit again; never `--no-verify`. Proof: the hook
      passes. Acceptance: AC-16.

## Archival

After every substantive phase is terminal. The completion gate is the execution check alone.

- [ ] [AI] Give each dormant recovery item its dated disposition. Proof: every item carries one. Acceptance: AC-16.
- [ ] [AI] Triage `learnings.md`: route each entry to one owner or discard it with a reason, or record that the log is
      empty. Proof: no entry unresolved. Acceptance: AC-16.
- [ ] [AI] Run [Execution Check](../../../repo-governance/workflows/plan/plan-execution-check.md) and record its
      terminal verdict; archival needs a permitting one. Proof: the verdict. Acceptance: AC-16.
- [ ] [AI] Run [Dev Artifact Clean-Up](../../../repo-governance/workflows/maintenance/dev-artifact-clean-up.md) over
      this task's scratch in `local-tmp/`, including `local-tmp/restructure/baseline/`. Proof: the record of what it
      removed. Acceptance: AC-16.
- [ ] [AI] Move the plan to `plans/done/YYYY-MM-DD__restructure-around-the-domain/` with `/usr/bin/git mv`; update
      `plans/in-progress/README.md`, `plans/done/README.md`, and every live link to the old path; run the full
      validation from the archived state; add the WORKLOG entry; commit as `docs(plan): archive the restructure plan`
      and push. Proof: the pushed range, and
      `grep -rln "plans/in-progress/restructure-around-the-domain" --exclude-dir=.git --exclude-dir=local-tmp .` finding
      only history. Acceptance: AC-16.

[cycle]: ../../../repo-governance/development/quality/testing/test-driven-development/001-cycle-and-evidence.md
