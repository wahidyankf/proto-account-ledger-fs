# Delivery

The executable part of this plan. Every item names its paths, its command where one exists, its executor, its proof, and
the acceptance criteria it serves from [prd](prd.md). Why each item exists is in the other five documents; read them
first.

## Execution Record

- Phase 0 (2026-09-25 04:04–04:08): baseline green, `test:quick`, `test:integration`, `test:e2e`, and `check:hygiene`
  all exit 0, unit coverage 90.00%, at 07e72d9. The quality gate returned PASS_WITH_FINDINGS after one repair cycle,
  every finding fixed in 07e72d9.
- Phase 1 (04:07–04:17): Gherkin and pytest-bdd retired, R1 applied; the greeting proven by three plain tests. Last gate
  passed: Phase 1. Next: Phase 2.
- Phase 2 (04:17–04:22): R2 and R3 applied; python-standards records returned result values and the domain shapes, 011
  and plan-execution record the delivery options. Last gate passed: Phase 2. Next: Phase 3, Cycle 3.1.
- Cycle 3.16 passed on arrival: the reader built in 3.14 already refused malformed IDs; its mutation proof is recorded
  under its RED.
- Phase 3 (04:21–04:42): 24 cycles green, one (3.16) passing on arrival with its mutation proof; the type gate proven to
  fail on an AED plus BHD sum. Last gate passed: Phase 3. Next: Phase 4, Cycle 4.1.
- Cycle 4.3 passed on arrival, as planned; its mutation proof is recorded under its RED.
- Cycle 4.6 passed on arrival, as planned; its mutation proof is recorded under its RED.
- Cycle 4.7 passed on arrival, as planned; its mutation proof is recorded under its RED.
- Cycle 4.12 passed on arrival, as planned; its mutation proof is recorded under its RED.
- Cycle 4.13 passed on arrival, as planned; its mutation proof is recorded under its RED.
- Before the Phase 4 gate, the two matches over the authorization unions that ended in a wildcard or a capture,
  `balances.holds` and `processing._effect`, were brought to end in `assert_never`, as tech-docs 001 requires; no
  behaviour changed, and `test:quick` passed (51 passed, coverage 97%).
- Phase 4 (04:42–05:13): 23 cycles green, five of them (4.3, 4.6, 4.7, 4.12, 4.13) passing on arrival with their
  mutation proofs; every incoming kind processed, and C1, C3, C4, C5, and C7 green. Last gate passed: Phase 4. Next:
  Phase 5, Cycle 5.1.
- Phase 4 committed as `58b0cdb` and pushed, `bd5722b..58b0cdb`.
- Cycle 5.5 passed on arrival, as planned; its mutation proof is recorded under its RED.
- Cycle 5.6 passed on arrival, as planned; its mutation proof is recorded under its RED.
- Cycle 5.11 passed on arrival, as planned; its mutation proof is recorded under its RED.
- Cycle 5.16 added `test_amb_035_a_reversed_refund_puts_its_fee_back_in_force` beside its planned test, since its GREEN
  adds the reversed-refund rule, which no planned test reached; both failed on their assertions first.
- Phase 5 (05:14–05:37): 17 cycles green, three of them (5.5, 5.6, 5.11) passing on arrival with their mutation proofs;
  every criterion green, and every day report complete as data. Last gate passed: Phase 5. Next: Phase 6, Cycle 6.1.

## Execution Checkout

- **Working copy.** The main checkout at the repository root, on `main`, with no worktree and no task branch, per the
  [integration path](../../../repo-governance/development/workflow/integration-path.md). Git is invoked as
  `/usr/bin/git`, which the local rtk guard lets through.
- **Delivery mode.** Direct commits to local `main`, pushed to `origin/main` at each phase gate (D10). The owner's order
  to execute, on 2026-09-24, authorizes exactly the commits and pushes the gates name, and no other.
- **Commands.** `pytest` below means `uv run --no-sync pytest`, run from `apps/account-ledger-cli`; every other command
  runs from the repository root.

## Delivery Units

Each phase is one delivery unit: one theme, one outcome its gate proves, and one rollback.

- **Owner.** This repository; no other repository is touched.
- **Outcome.** The phase gate's commands exit 0 on the phase's combined state.
- **Rollback.** `/usr/bin/git revert` of the unit's commits, as new commits, pushed; never a reset, amend, or force-push
  (recovery item RC3).
- **Commits.** Each is build-valid, so no commit holds a failing test; red evidence lives in this file, not in history
  ([thematic commits](../../../repo-governance/development/workflow/thematic-commits.md)).

## Pause Safety

At any pause the Execution Record carries the last gate passed, the next unticked item, and any bounded budget partly
spent, such as Phase 8's repair attempts. A resumed session rebuilds its task list from the unticked items here, first
confirming that each ticked item's change is present, and continues; no fresh gate is needed to resume (D11).

## How an Item Is Worked

- **Test-first items (D9a).** Each behaviour is a cycle of three items: RED, GREEN, and REFACTOR, per [Cycle and
  Evidence][cycle]. A RED counts only when the new test fails on its assertion; an import error or a broken fixture is
  repaired first. A GREEN is the smallest change that passes, so a later cycle's test still has something to fail on.
- **A test that passes on arrival.** A cycle expected to pass says so in its RED, with the mutation that proves it; any
  test can still surprise. The RED stays unticked with the disposition "passes on arrival"; the executor breaks the code
  path the test names, watches it fail on its assertion, restores it, and records that run instead. The GREEN closes as
  "no production change", and the Execution Record gets a line ([testing strategy](tech-docs/004-testing-strategy.md)).
- **Results, not ticks.** Each ticked item carries, indented under it, what it produced: the command, its output or its
  head, and anything that surprised. Discoveries go to [learnings](learnings.md) when they happen.
- **Domain types first.** Every value a test builds goes through the domain constructors of
  [the domain model](tech-docs/001-domain-model.md), and every signature is strictly typed, so pyright in `test:quick`
  checks each GREEN as the tests do (D16).
- **Architecture as built.** A phase that adds a component updates `specs/apps/account-ledger/cli/architecture.md` in
  the same unit, never later.

## Parallelization Model

Every node is serial, and the concurrency limit is one executor in one checkout, the repository's only mode.

- Phase 0 records the state everything else is measured against.
- Phases 1 and 2 change the rules the code phases follow, so they come first; Phase 2 edits governance files Phase 1
  also reads.
- Phases 3 to 8 each import the modules the phase before wrote, and share `architecture.md`.
- Phase 9 cites test names Phases 3 to 8 create, so it waits for them.
- Phase 10 describes the built code, so it comes last among the substantive phases.
- Cleanup is the terminal node, after every unit has landed and before the archival move.

Within a phase, cycles run in the order listed, since each GREEN is sized against the tests before it.

## Phase 0 — Baseline

The plan and the quality gate's repairs are already on `origin/main`; this phase records the state the work starts from
and writes the gate helper every later gate runs.

- [x] [AI] Confirm the checkout: on `main`, level with `origin/main`, with nothing uncommitted. Command:
      `/usr/bin/git fetch origin && /usr/bin/git status -sb`. Proof: the output, recorded here. Acceptance: AC-30.
  - Result (2026-09-25 04:04): `## main...origin/main` at 07e72d9, level with the remote; only ignored scratch files
    outside version control.
- [x] [AI] Install the toolchain. Command: `npm install`. Proof: exit 0. Acceptance: AC-30.
  - Result: `npm install` exit 0.
- [x] [AI] Record the baseline: run `npx nx run account-ledger-cli:test:quick`, `test:integration`, `test:e2e`, and
      `npm run -s check:hygiene` before any change. Proof: each exit status and the unit coverage figure, as the first
      Execution Record line; a failure is fixed at its cause inside this phase, and recorded as pre-existing.
      Acceptance: AC-30.
  - Result, with `--skip-nx-cache`: `test:quick` 0 (pyright, ruff, 1 passed, coverage 90.00%), `test:integration` 0,
    `test:e2e` 0, `npm run -s check:hygiene` 0. Nothing pre-existing failed.
- [x] [AI] Write `local-tmp/check-md.sh`, the Markdown check every gate runs, as shown below. Command:
      `sh local-tmp/check-md.sh`. Proof: exit 0 on the clean checkout. Acceptance: AC-30.
  - Result: written as shown; `sh local-tmp/check-md.sh` exit 0 on the clean checkout.

The script lists every Markdown file changed since `HEAD` or new and untracked, never a deleted one, and exits non-zero
if prettier rejects one or a line outside `repo-governance/` and the harness directories passes 120 characters:

```bash
#!/bin/sh
files=$( { /usr/bin/git diff --name-only --diff-filter=d HEAD -- '*.md'
           /usr/bin/git ls-files -o --exclude-standard -- '*.md'; } | sort -u)
[ -z "$files" ] && exit 0
npx prettier --check $files || exit 1
python3 - $files <<'PY'
import sys
skip = ("repo-governance/", ".claude/", ".codex/", ".opencode/", ".agents/")
bad = [(f, n) for f in sys.argv[1:] if not f.startswith(skip)
       for n, line in enumerate(open(f, encoding="utf-8"), 1) if len(line.rstrip("\n")) > 120]
for f, n in bad:
    print(f"{f}:{n}")
sys.exit(1 if bad else 0)
PY
```

### Phase 0 Gate

- [x] [AI] Run `sh local-tmp/check-md.sh`, `./rhino md internal-link validate`, `./rhino md heading-hierarchy validate`,
      and `./rhino md naming validate`. Proof: each exit status. Acceptance: AC-30.
  - Result (04:06): check-md 0, internal-link 0, heading-hierarchy 0, naming 0.
- [x] [AI] Add the `WORKLOG.md` entry for the baseline, then commit this file's Phase 0 record and the entry as
      `docs(plan): record the ledger plan's baseline` and push. Command: `/usr/bin/git push origin main`. Proof: the
      commit hash and pushed range. Acceptance: AC-24.
  - Result: WORKLOG entry "Plan execution, Phase 0"; commit c5afbb0, pushed 07e72d9..c5afbb0.

Pause safety: the baseline is recorded on `origin/main`. Re-verify with `npx nx run account-ledger-cli:test:quick`.

## Phase 1 — Plain Pytest Replaces Gherkin

Retires pytest-bdd and the behaviour-driven rules (D12, D12c; rule change R1 in
[the rule changes](tech-docs/006-specification-and-rule-changes.md)). The greeting's behaviour is kept, proven by plain
tests first, so the suite never goes a commit without covering it.

- [x] [AI] Open the Rules Propagation run for R1, recording its record at
      `local-tmp/rules-propagation-retire-gherkin.md` with every file R1 names. Proof: the record exists. Acceptance:
      AC-28.
  - Result: `local-tmp/rules-propagation-retire-gherkin.md` opened 04:08, listing every file R1 names and the two
    catalog texts left unchanged.
- [x] [AI] Characterize the greeting at the unit layer: `test_the_greeting_prints_and_exits_0` in
      `tests/unit/test_cli.py` calls `run` with a `StringIO`. It passes on arrival, since the behaviour exists; break
      the greeting text, watch it fail, restore. Command: `pytest tests/unit/test_cli.py`. Proof: the passing run and
      the mutation's failure. Acceptance: AC-28.
  - Result: `test_the_greeting_prints_and_exits_0` passes on arrival. Mutation: greeting text changed to "Hello,
    there!", the test failed on its assertion
    (`FAILED tests/unit/test_cli.py::test_the_greeting_prints_and_exits_0 - AssertionError`), text restored,
    `git diff -- src` empty.
- [x] [AI] Characterize it at the integration layer in `tests/integration/test_main.py` (`main` with `capfd`) and end to
      end in `tests/e2e/test_program.py` (a subprocess), each with the same mutation proof. Command:
      `pytest tests/integration tests/e2e`. Proof: the runs. Acceptance: AC-28.
  - Result: `test_main_prints_the_greeting_and_exits_0` and `test_the_program_prints_the_greeting_and_exits_0` pass (3
    passed with the unit test). The same mutation failed both on their assertions (3 failed); restored.
- [x] [AI] Remove Gherkin from the application: delete `tests/conftest.py`, the three
      `tests/*/steps/test_greeting_steps.py` files, and `specs/apps/account-ledger/cli/behaviours/`; drop `pytest-bdd`,
      `bdd_features_base_dir`, and the pytest cap with its pytest-bdd comment from `pyproject.toml`; regenerate
      `uv.lock` with `uv lock` and sync with `uv sync`; drop the feature glob from every target's inputs and `*.feature`
      from the watch targets' `--patterns` in `project.json`; drop the Gherkin layout and bindings from
      `apps/account-ledger-cli/README.md`. Command: `pytest tests`. Proof: the passing run, and
      `/usr/bin/git grep -n -E "pytest_bdd|pytest-bdd|\.feature" -- apps` printing nothing. Acceptance: AC-28.
  - Result: deleted `tests/conftest.py`, the three steps files, and `specs/apps/account-ledger/cli/behaviours/` (README
    and `greeting.feature`); `pyproject.toml` drops `pytest-bdd`, the `<9.1` cap with its comment, and
    `bdd_features_base_dir`; `uv lock` removed pytest-bdd 8.1.0, parse-type, and six, keeping pytest 9.0.3;
    `project.json` drops the feature glob from four targets, `tests/conftest.py` from three, and `*.feature` from both
    watch patterns; the app README drops the step layout and the corpus sentence.
  - `pytest tests`: 3 passed, after clearing a stale bytecode cache (learnings L1).
    `/usr/bin/git grep -n -E "pytest_bdd|pytest-bdd|\.feature" -- apps` printed nothing (exit 1).
- [x] [AI] Apply R1's rule edits: `AGENTS.md`; `behaviour-driven-development.md` and its `002-layers-and-adapters.md`;
      the testing `README.md`; `specification-tree.md`; `nx-workspace-policy.md`, dropping only its feature-file
      sentence; and the root `README.md` prerequisites. Close the Rules Propagation record. Command:
      `./rhino governance word-budget validate`. Proof: exit 0 and the closed record. Acceptance: AC-28.
  - Result: AGENTS.md (specs line; Testing: plain pytest, test-first, BDD binds only its layers);
    `behaviour-driven-development.md` and `002-layers-and-adapters.md` each gain a "This Repository's Binding" section;
    the testing README index line; `specification-tree.md` binding, `behaviours/` not applicable;
    `nx-workspace-policy.md` drops only the feature-file sentence; root README prerequisites drop pytest-bdd.
    `./rhino governance word-budget validate` exit 0; record closed at 04:10 with its conflict scan.
- [x] [AI] Carry R1 into the documents it makes stale: `specs/README.md`, `specs/apps/account-ledger/cli/README.md`, and
      `docs/README.md`. Proof: the md gates below. Acceptance: AC-28.
  - Result: `specs/README.md` (as-built architecture, no `behaviours/` tree), `specs/apps/account-ledger/cli/README.md`
    (Behaviours link removed), and `docs/README.md` reworded; md gates exit 0.

### Phase 1 Gate

- [x] [AI] Run every gate command below against the phase's combined state; each exits 0. Proof: each command and its
      exit status, recorded here. Acceptance: AC-28, AC-30. Commands:
  - `npx nx run account-ledger-cli:test:quick`
  - `npx nx run account-ledger-cli:test:integration`
  - `npx nx run account-ledger-cli:test:e2e`
  - `npm run -s check:hygiene`
  - `sh local-tmp/check-md.sh`
  - `./rhino md internal-link validate && ./rhino md heading-hierarchy validate && ./rhino md naming validate`
  - `./rhino governance word-budget validate`
  - Result (04:10–04:16): `test:quick` 0 (1 passed, coverage 90%), `test:integration` 0, `test:e2e` 0; `check:hygiene`
    first failed `harness-adapters`, since the adapters record a digest of `AGENTS.md` (learnings L2), then 0 after
    `npm run generate:bindings`; `sh local-tmp/check-md.sh` 0; internal-link, heading-hierarchy, naming, and
    word-budget 0.
- [x] [AI] Add a new `WORKLOG.md` entry for the phase at the top, stamped with its real start and end `date` times.
      Path: `WORKLOG.md`. Proof: the entry. Acceptance: AC-24.
  - Result: entry "Plan execution, Phase 1".
- [x] [AI] Commit the phase as one commit,
      `test(account-ledger-cli): replace Gherkin with plain pytest and retire its rules`, then push to `origin/main`;
      the pre-push hook runs every test layer. Command: `/usr/bin/git push origin main`. Proof: the commit hash and the
      pushed range, recorded here and in the Execution Record. Acceptance: AC-28, AC-30.
  - Result: 6daf504, pushed c5afbb0..6daf504; the pre-push hook ran every test layer.

Pause safety: the phase leaves a Gherkin-free repository whose suite still proves the greeting. Re-verify with
`npx nx run account-ledger-cli:test:quick`.

## Phase 2 — Record the Repository's Choices

Rule changes R2 and R3: the Python choices (S3, D8, D14 to D18) and the delivery grammar (D9a to D9d, D11).

- [x] [AI] Open a Rules Propagation run at `local-tmp/rules-propagation-ledger-choices.md` for R2 and R3. Proof: the
      record exists. Acceptance: AC-29.
  - Result: `local-tmp/rules-propagation-ledger-choices.md` opened, listing R2 and R3 and their four files.
- [x] [AI] Apply R2 to `repo-governance/development/quality/stacks/python-standards.md`: typed result values under
      Failures; the money, positive-amount, value-object, and state rows under Domain Types; the sentences on illegal
      values and hand-written machines. Proof: the md and word-budget gates. Acceptance: AC-29.
  - Result: Domain Types: the money row now one frozen dataclass per currency in a union, same-type operators; new rows
    for a positive amount, an identifier or day, and a state carrying data; two sentences under the table, on illegal
    values (constructor raises, `parse`/`of` return typed faults) and hand-written machines. Failures records **returned
    result values**. md and word-budget gates 0.
- [x] [AI] Carry R2 into `AGENTS.md`'s Coding Conventions summary, as tech-docs 006 states it. Proof: the md gates.
      Acceptance: AC-29.
  - Result: the summary reads "frozen dataclasses and unions for the domain, one type per currency for money";
    `npm run generate:bindings` regenerated the adapters for the new `AGENTS.md` digest (learnings L2).
- [x] [AI] Apply R3's four sentences to
      `repo-governance/conventions/structure/plans/011-phase-boundaries-and-delivery-choices.md`. Proof: the gates.
      Acceptance: AC-29.
  - Result: under each table, "This repository records **phase gate**", "**Phase 0 baseline**", "**split cycle**", and
    "**reopen**, adapted as `plans/done/README.md` states"; word-budget and internal-link 0.
- [x] [AI] Apply R3's completion-gate sentence to `repo-governance/workflows/plan/plan-execution.md`, and close the
      record. Proof: the gates. Acceptance: AC-29.
  - Result: "This repository records **execution check only**" under the Completion Gate table; the record closed at
    04:18 with its conflict scan.

### Phase 2 Gate

- [x] [AI] Run every gate command below against the phase's combined state; each exits 0. Proof: each command and its
      exit status, recorded here. Acceptance: AC-29. Commands:
  - `npx nx run account-ledger-cli:test:quick`
  - `npx nx run account-ledger-cli:test:integration`
  - `npx nx run account-ledger-cli:test:e2e`
  - `npm run -s check:hygiene`
  - `sh local-tmp/check-md.sh`
  - `./rhino md internal-link validate && ./rhino md heading-hierarchy validate && ./rhino md naming validate`
  - `./rhino governance word-budget validate`
  - Result (04:20–04:21): `test:quick` 0, `test:integration` 0, `test:e2e` 0, `check:hygiene` 0;
    `sh local-tmp/check-md.sh`, internal-link, heading-hierarchy, naming, and word-budget each 0.
- [x] [AI] Add a new `WORKLOG.md` entry for the phase at the top, stamped with its real start and end `date` times.
      Path: `WORKLOG.md`. Proof: the entry. Acceptance: AC-24.
  - Result: entry "Plan execution, Phase 2".
- [x] [AI] Commit the phase as `docs(governance): record the ledger's Python and delivery choices`, then push to
      `origin/main`; the pre-push hook runs every test layer. Command: `/usr/bin/git push origin main`. Proof: the
      commit hash and the pushed range, recorded here and in the Execution Record. Acceptance: AC-29.
  - Result: ad8daaf, pushed 6daf504..ad8daaf; the pre-push hook ran every test layer.

Pause safety: the phase leaves every choice this plan made recorded where later work will read it. Re-verify with
`npx nx run account-ledger-cli:test:quick`.

## Phase 3 — Money, Identifiers, and the Stream File

The domain types and the parser, bottom-up ([domain model](tech-docs/001-domain-model.md),
[input and output](tech-docs/003-input-output-and-cli.md)). The header has eight columns; `final` arrives in Phase 8.

### Cycle 3.1 — AED and BHD keep their places

- [x] [AI] RED: write `test_aed_refuses_more_than_two_places` in `tests/unit/test_money.py`, with the smallest stub it
      imports, and run it; it fails on its assertion because the stub `Aed` accepts `12.345`. Command:
      `pytest tests/unit/test_money.py`. Proof: the failure message, recorded here. Acceptance: AC-34.
  - Result: with a stub `Aed.parse` returning `Aed(Decimal(text))`, it failed on its assertion:
    `assert Aed(value=Decimal('12.345')) == TooManyPlaces(text='12.345', places=2, currency='AED')` (2 failed, with
    `test_bhd_refuses_more_than_three_places` beside it). A first run without `Bhd` in the stub was an import error and
    did not count.
- [x] [AI] GREEN: Write `Aed`, `Bhd`, and `Money` in `src/account_ledger/money.py`, each checking its places on
      construction, with `parse` returning `MoneyFault`. Command: `pytest tests/unit/test_money.py`, then
      `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance: AC-34.
  - Result: `Aed` and `Bhd` check their places in `__post_init__` (`ValueError`); `parse` returns `NotADecimal` or
    `TooManyPlaces`, joined as `MoneyFault`. `pytest tests/unit/test_money.py` 2 passed; `pytest tests/unit` 3 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-34.
  - Result: ruff UP037 removed the quoted return annotations. `test:quick` exit 0, coverage 96%.

### Cycle 3.2 — an amount is above zero

- [x] [AI] RED: write `test_an_amount_must_be_above_zero` in `tests/unit/test_money.py`, with the smallest stub it
      imports, and run it; it fails on its assertion because the stub `Amount.of` accepts `Aed("0.00")`. Command:
      `pytest tests/unit/test_money.py`. Proof: the failure message, recorded here. Acceptance: AC-34.
  - Result: with a stub `Amount.of` returning `Amount(money)`, it failed on its assertion:
    `assert Amount(money=Aed(value=Decimal('0.00'))) == NotPositive(text='0.00')` (1 failed, 2 passed).
- [x] [AI] GREEN: Write `Amount[M]` and `Amount.of` returning `NotPositive`. Command: `pytest tests/unit/test_money.py`,
      then `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance: AC-34.
  - Result: `Amount[M: (Aed, Bhd)]` raises `ValueError` at or below zero; `Amount.of` returns `NotPositive`. 3 passed;
    `pytest tests/unit` 4 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-34.
  - Result: the test helper `aed` moved to `tests/support/values.py`, beside `bhd`. `test:quick` exit 0, coverage 97%.

### Cycle 3.3 — AED and BHD never combine

- [x] [AI] RED: write `test_aed_and_bhd_values_never_combine` in `tests/unit/test_money.py`, with the smallest stub it
      imports, and run it; it fails on its assertion because the stub `same_as` returns its second argument for a `Bhd`
      against an `Aed`. Command: `pytest tests/unit/test_money.py`. Proof: the failure message, recorded here.
      Acceptance: AC-34.
  - Result: with a stub `same_as` returning its second argument, it failed on its assertion:
    `assert Bhd(value=Decimal('1.000')) == CurrencyMismatch(expected='AED', found='BHD')` (1 failed, 3 passed).
- [x] [AI] GREEN: Write the same-type operators, the constrained type variable, and `same_as` returning
      `CurrencyMismatch`. Command: `pytest tests/unit/test_money.py`, then `pytest tests/unit`. Proof: both passing
      runs, recorded here. Acceptance: AC-34.
  - Result: `+`, `-`, and unary `-` per currency, each returning `NotImplemented` for another type; `order=True` gives
    same-type comparison; `currency` and `same_as[M: (Aed, Bhd)]` returning `CurrencyMismatch`. 4 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-34.
  - Result: the runtime mix checks carry a narrow pyright suppression stating the reason (strict pyright rejected a bare
    expression and `operator.add` alike, since the mix is a type error). `test:quick` exit 0, coverage 93%.
- [x] [AI] Prove the type gate can fail: add a line summing an `Aed` and a `Bhd` to a scratch test, run
      `npx nx run account-ledger-cli:typecheck`, watch it fail naming the line, remove it. Proof: the failing run's
      head. Acceptance: AC-34.
  - Result: a scratch `tests/unit/test_scratch_mix.py` summing `aed("1.00") + bhd("1.000")` made `typecheck` exit 1:
    `error: Operator "+" not supported for types "Aed" and "Bhd" (reportOperatorIssue)`; removed, `typecheck` exit 0.

### Cycle 3.4 — daily interest rounds half-even

- [x] [AI] RED: write `test_amb_006_daily_interest_rounds_half_even` in `tests/unit/test_money.py`, with the smallest
      stub it imports, and run it; it fails on its assertion because the stub's `daily_interest` rounds AED 312.50 ×
      0.0004 = 0.125 up to 0.13 instead of 0.12. Command: `pytest tests/unit/test_money.py`. Proof: the failure message,
      recorded here. Acceptance: AC-13.
  - Result: with a stub rounding half-up, it failed on its assertion:
    `assert Aed(value=Decimal('0.13')) == Aed(value=Decimal('0.12'))` for AED 312.50 (1 failed, 4 passed). A first run
    was a NameError from a missed import edit and did not count.
- [x] [AI] GREEN: Write `daily_interest` at 0.0004 in `money.py`, rounding half-even to the currency's places. Command:
      `pytest tests/unit/test_money.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance:
      AC-13.
  - Result: `daily_interest` multiplies by `DAILY_RATE = Decimal("0.0004")`, zero unless the balance is above zero,
    rounded half-even by `_round`. 5 passed; `pytest tests/unit` 6 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-13.
  - Result: rounding reads the minor unit from the currency type, since strict pyright rejected the exponent union.
    `test:quick` exit 0, coverage 94%.

### Cycle 3.5 — an amount splits with the remainder last

- [x] [AI] RED: write `test_amb_020_ten_bhd_splits_3_333_3_333_3_334` in `tests/unit/test_money.py`, with the smallest
      stub it imports, and run it; it fails on its assertion because `split` returns equal parts that sum to `10.002`.
      Command: `pytest tests/unit/test_money.py`. Proof: the failure message, recorded here. Acceptance: AC-12.
  - Result: with a stub rounding each part up, it failed on its assertion:
    `At index 0 diff: Amount(money=Bhd(value=Decimal('3.334'))) != Amount(money=Bhd(value=Decimal('3.333')))`, three
    parts of 3.334 summing to 10.002 (1 failed, 5 passed). `InstalmentCount` arrived in `ids.py` without its check,
    which Cycle 3.11 adds.
- [x] [AI] GREEN: Write `split`: round each part down, add the remainder to the last, and return `TooManyInstalments`
      when a part would fall below one minor unit. Command: `pytest tests/unit/test_money.py`, then `pytest tests/unit`.
      Proof: both passing runs, recorded here. Acceptance: AC-12.
  - Result: parts rounded down, the remainder on the last, `TooManyInstalments` when a part is below one minor unit (BHD
    0.002 in 3). 6 passed; `pytest tests/unit` 7 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-12.
  - Result: nothing to tidy beyond a docstring. `test:quick` exit 0, coverage 95%.

### Cycle 3.6 — the BHD fee is derived from the AED fee

- [x] [AI] RED: write `test_amb_027_the_bhd_fee_is_2_560` in `tests/unit/test_money.py`, with the smallest stub it
      imports, and run it; it fails on its assertion because the stub's BHD fee is the AED figure `25.000`. Command:
      `pytest tests/unit/test_money.py`. Proof: the failure message, recorded here. Acceptance: AC-22.
  - Result: with a stub charging 25 in each currency, it failed on its assertion:
    `assert Amount(money=...al('25.000'))) == Amount(money=...mal('2.560')))` (1 failed, 6 passed). A first stub raised
    `AttributeError` and did not count.
- [x] [AI] GREEN: Write `overdraft_fee` as AED 25.00 and, for BHD, 25.00 × 0.10238257 rounded half-even. Command:
      `pytest tests/unit/test_money.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance:
      AC-22.
  - Result: `overdraft_fee` matches the currency: AED 25.00, BHD 25.00 × 0.10238257 = 2.55956425 → 2.560 half-even. 7
    passed; `pytest tests/unit` 8 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-22.
  - Result: the constants are named `AED_FEE` and `AED_TO_BHD`. `test:quick` exit 0, coverage 95%.

### Cycle 3.7 — a day refuses a malformed value

- [x] [AI] RED: write `test_day_refuses_a_malformed_value` in `tests/unit/test_ids.py`, with the smallest stub it
      imports, and run it; it fails on its assertion because the stub accepts `Day.parse("-1")`. Command:
      `pytest tests/unit/test_ids.py`. Proof: the failure message, recorded here. Acceptance: AC-34.
  - Result: with a stub `Day.parse` returning `Day(int(text))`, it failed on its assertion:
    `assert Day(number=-1) == IdFault(kind='day', text='-1')` (1 failed).
- [x] [AI] GREEN: Write its type in `src/account_ledger/ids.py`, with the constructor check and `parse`. Command:
      `pytest tests/unit/test_ids.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance:
      AC-34.
  - Result: `Day` refuses a number below 0 in `__post_init__`; `parse` accepts only ASCII digits, else
    `IdFault("day", text)`; `next` and `order=True` give counting and comparison. 1 passed; `pytest tests/unit` 9
    passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-34.
  - Result: nothing to tidy. `test:quick` exit 0, coverage 96%.

### Cycle 3.8 — an account ID refuses a malformed value

- [x] [AI] RED: write `test_account_id_refuses_a_malformed_value` in `tests/unit/test_ids.py`, with the smallest stub it
      imports, and run it; it fails on its assertion because the stub accepts `AccountId.parse("ACC-1")`. Command:
      `pytest tests/unit/test_ids.py`. Proof: the failure message, recorded here. Acceptance: AC-34.
  - Result: with a stub accepting any text, it failed on its assertion:
    `assert AccountId(value='ACC-1') == IdFault(kind='account ID', text='ACC-1')` (1 failed, 1 passed).
- [x] [AI] GREEN: Write its type in `src/account_ledger/ids.py`, with the constructor check and `parse`. Command:
      `pytest tests/unit/test_ids.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance:
      AC-34.
  - Result: `AccountId` checks `ACC-` and three digits in `__post_init__` and `parse`, and gives `number` for markers. 2
    passed; `pytest tests/unit` 10 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-34.
  - Result: the pattern is one compiled `_ACCOUNT`. `test:quick` exit 0, coverage 96%.

### Cycle 3.9 — a hold ID refuses a malformed value

- [x] [AI] RED: write `test_authorization_id_refuses_a_malformed_value` in `tests/unit/test_ids.py`, with the smallest
      stub it imports, and run it; it fails on its assertion because the stub accepts `AuthorizationId.parse("Auth-")`.
      Command: `pytest tests/unit/test_ids.py`. Proof: the failure message, recorded here. Acceptance: AC-34.
  - Result: with a stub accepting any text, it failed on its assertion:
    `assert AuthorizationId(value='Auth-') == IdFault(kind='hold ID', text='Auth-')` (1 failed, 2 passed).
- [x] [AI] GREEN: Write its type in `src/account_ledger/ids.py`, with the constructor check and `parse`. Command:
      `pytest tests/unit/test_ids.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance:
      AC-34.
  - Result: `AuthorizationId` checks `Auth-` and one or more ASCII letters or digits. 3 passed; `pytest tests/unit` 11
    passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-34.
  - Result: nothing to tidy. `test:quick` exit 0, coverage 96%.

### Cycle 3.10 — an event ID refuses a malformed value

- [x] [AI] RED: write `test_event_id_refuses_a_malformed_value` in `tests/unit/test_ids.py`, with the smallest stub it
      imports, and run it; it fails on its assertion because the stub accepts `EventId.parse("FEE-1")`. Command:
      `pytest tests/unit/test_ids.py`. Proof: the failure message, recorded here. Acceptance: AC-34.
  - Result: with a stub `parse_event_id` returning `IncomingId(text)`, it failed on its assertion:
    `assert IncomingId(value='FEE-1') == IdFault(kind='event ID', text='FEE-1')` (1 failed, 3 passed). `EventId` is a
    union type alias, so its parse is the function `parse_event_id`, not a method.
- [x] [AI] GREEN: Write its type in `src/account_ledger/ids.py`, with the constructor check and `parse`. Command:
      `pytest tests/unit/test_ids.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance:
      AC-34.
  - Result: `IncomingId`, `InstalmentId`, `FeeId`, `RefundId`, `InterestId`, `CapitalizationId`, the `EventId` union,
    and `parse_event_id`, one anchored pattern reading an incoming ID, an instalment, or a marker. 4 passed;
    `pytest tests/unit` 12 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-34.
  - Result: ruff format only. `test:quick` exit 0, coverage 97%.

### Cycle 3.11 — an instalment count refuses a malformed value

- [x] [AI] RED: write `test_instalment_count_refuses_a_malformed_value` in `tests/unit/test_ids.py`, with the smallest
      stub it imports, and run it; it fails on its assertion because the stub accepts `InstalmentCount(1)`. Command:
      `pytest tests/unit/test_ids.py`. Proof: the failure message, recorded here. Acceptance: AC-34.
  - Result: with a stub `parse` accepting any digits, it failed on its assertion:
    `assert InstalmentCount(n=1) == IdFault(kind='instalment count', text='1')` (1 failed, 4 passed).
- [x] [AI] GREEN: Write its type in `src/account_ledger/ids.py`, with the constructor check and `parse`. Command:
      `pytest tests/unit/test_ids.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance:
      AC-34.
  - Result: `InstalmentCount` refuses below 2 in `__post_init__`; `parse` returns `IdFault("instalment count", text)`. 5
    passed; `pytest tests/unit` 13 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-34.
  - Result: nothing to tidy. `test:quick` exit 0, coverage 97%.

### Cycle 3.12 — a marker prints its kind, account, and days

- [x] [AI] RED: write `test_a_marker_prints_its_kind_account_and_days` in `tests/unit/test_ids.py`, with the smallest
      stub it imports, and run it; it fails on its assertion because the stub's `text` returns an empty string for
      `FeeId`. Command: `pytest tests/unit/test_ids.py`. Proof: the failure message, recorded here. Acceptance: AC-07.
  - Result: with a stub `text` printing only incoming IDs, it failed on its assertion: `assert '' == 'E10-3'` (1 failed,
    5 passed).
- [x] [AI] GREEN: Write `text` for the six event ID types. Command: `pytest tests/unit/test_ids.py`, then
      `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance: AC-07.
  - Result: one `match` over the `EventId` union, ending in `assert_never`, builds each marker from its parts. 6 passed;
    `pytest tests/unit` 14 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-07.
  - Result: a loop variable that shadowed `text` renamed (ruff F402). `test:quick` exit 0, coverage 96%.

### Cycle 3.13 — the configuration refuses an inverted window

- [x] [AI] RED: write `test_ledger_config_refuses_an_inverted_window` in `tests/unit/test_config.py`, with the smallest
      stub it imports, and run it; it fails on its assertion because the stub `LedgerConfig.of` accepts a first day
      after the last. Command: `pytest tests/unit/test_config.py`. Proof: the failure message, recorded here.
      Acceptance: AC-34.
  - Result: with a stub `LedgerConfig.of` accepting anything, it failed on its assertion:
    `assert LedgerConfig(... first_day=Day(number=6), last_day=Day(number=1) ...) == ConfigFault(...)`, the reason being
    `the first day 6 is after the last 1` (1 failed). A first stub lacked `CHALLENGE`, an import error that did not
    count; `Aed.zero()` and `Bhd.zero()` came with it.
- [x] [AI] GREEN: Write `config.py`: `Account[M]`, `LedgerConfig.of`, and `CHALLENGE`. Command:
      `pytest tests/unit/test_config.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance:
      AC-34.
  - Result: `Account[M]`, `AnyAccount`, `ConfigFault`, and `LedgerConfig`, whose `__post_init__` and `of` share one
    check: an inverted window, a repeated account, a capitalization day outside the window; `account(id)` looks one up;
    `CHALLENGE` holds ACC-001 AED 0.00 and ACC-002 BHD 0.000, Days 1 to 6, capitalization on Day 6. 1 passed;
    `pytest tests/unit` 15 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-34.
  - Result: ruff format only. `test:quick` exit 0, coverage 97%.

### Cycle 3.14 — a valid stream parses to its events

- [x] [AI] RED: write `test_a_valid_stream_parses_to_its_events` in `tests/unit/test_stream_csv.py`, with the smallest
      stub it imports, and run it; it fails on its assertion because the stub parser returns no events for one row of
      each kind. Command: `pytest tests/unit/test_stream_csv.py`. Proof: the failure message, recorded here. Acceptance:
      AC-05.
  - Result: with a stub `parse_stream` returning `()`, it failed on its assertion:
    `assert () == (Credit(id=In...tCount(n=3))))`, `Right contains 6 more items` (1 failed).
- [x] [AI] GREEN: Write `events.py` (the incoming kinds, `Capture`, and `posting`) and `parse_stream` in `stream_csv.py`
      for well-formed rows; the test builds its text with `csv_text(rows)` in `tests/support/streams.py`, which writes
      rows under the current header. Command: `pytest tests/unit/test_stream_csv.py`, then `pytest tests/unit`. Proof:
      both passing runs, recorded here. Acceptance: AC-05.
  - Result: `events.py` holds `Capture`, `Whole`, `Instalments`, and the five incoming kinds joined in `IncomingEvent`;
    `parse_stream` reads rows through `csv` and each value through its type's `parse` (`IncomingId.parse` added), with a
    generic fault message the later cycles refine; `csv_text(rows)` in `tests/support/streams.py` writes dict rows under
    `HEADER`. 1 passed; `pytest tests/unit` 16 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-05.
  - Result: the GREEN's private exception for early exit was replaced by returned `RowFault` values with walrus-narrowed
    early returns, as S3 and python-standards require. `test:quick` exit 0, coverage 95%.

### Cycle 3.15 — a wrong header or cell count is refused

- [x] [AI] RED: write `test_a_wrong_header_or_cell_count_is_refused` in `tests/unit/test_stream_csv.py`, with the
      smallest stub it imports, and run it; it fails on its assertion because the parser accepts the faulty row instead
      of returning a `StreamError` with its line and message. Command: `pytest tests/unit/test_stream_csv.py`. Proof:
      the failure message, recorded here. Acceptance: AC-03.
  - Result: the first run raised `KeyError: 'account'` on the short row, not an assertion, so the reader first read
    missing cells as empty, adding no behaviour; the rerun failed on its assertion:
    `assert StreamError(l...is not valid") == StreamError(l...,instalments')` (1 failed, 1 passed).
- [x] [AI] GREEN: Add the header check and the cell count, against this version's columns to `stream_csv.py`, returning
      the message tech-docs 003 fixes. Command: `pytest tests/unit/test_stream_csv.py`, then `pytest tests/unit`. Proof:
      both passing runs, recorded here. Acceptance: AC-03.
  - Result: the header must equal `COLUMNS` exactly, an empty file included, and each row must have `len(COLUMNS)`
    cells, each a returned `StreamError`. 2 passed; `pytest tests/unit` 17 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-03.
  - Result: rows now zip strictly, the count being checked first. `test:quick` exit 0, coverage 95%.

### Cycle 3.16 — an ID of the wrong form is refused

- [ ] [AI] RED: write `test_an_id_of_the_wrong_form_is_refused` in `tests/unit/test_stream_csv.py`, with the smallest
      stub it imports, and run it; it fails on its assertion because the parser accepts the faulty row instead of
      returning a `StreamError` with its line and message. Command: `pytest tests/unit/test_stream_csv.py`. Proof: the
      failure message, recorded here. Acceptance: AC-03.
  - Disposition: passes on arrival (3 passed), since Cycle 3.14 already read every ID through its type's `parse`.
    Mutation: `AccountId.parse` relabelled its fault; the test failed on its assertion
    (`assert StreamError(l...is not valid") == StreamError(l...is not valid")`, 1 failed, 2 passed); restored from a
    copy, 3 passed.
- [x] [AI] GREEN: Add the ID checks, reading each through its type's `parse` to `stream_csv.py`, returning the message
      tech-docs 003 fixes. Command: `pytest tests/unit/test_stream_csv.py`, then `pytest tests/unit`. Proof: both
      passing runs, recorded here. Acceptance: AC-03.
  - Result: no production change; passes on arrival, recorded in the Execution Record.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-03.
  - Result: nothing to tidy. `test:quick` exit 0.

### Cycle 3.17 — an unknown type or account is refused

- [x] [AI] RED: write `test_an_unknown_type_or_account_is_refused` in `tests/unit/test_stream_csv.py`, with the smallest
      stub it imports, and run it; it fails on its assertion because the parser accepts the faulty row instead of
      returning a `StreamError` with its line and message. Command: `pytest tests/unit/test_stream_csv.py`. Proof: the
      failure message, recorded here. Acceptance: AC-03.
  - Result: it failed on its assertion: the type fault read `... is not valid` instead of listing the five types (1
    failed, 3 passed).
- [x] [AI] GREEN: Add the type and account checks to `stream_csv.py`, returning the message tech-docs 003 fixes.
      Command: `pytest tests/unit/test_stream_csv.py`, then `pytest tests/unit`. Proof: both passing runs, recorded
      here. Acceptance: AC-03.
  - Result: the type is checked against `KINDS` before the account, so an unknown type is named whatever else the row
    holds; the unheld account already returned its message. 4 passed; `pytest tests/unit` 19 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-03.
  - Result: the final `match` arm now serves authorizations and settlements, so no arm is unreachable. `test:quick` exit
    0, coverage 97%.

### Cycle 3.18 — an amount that is not a valid amount is refused

- [x] [AI] RED: write `test_an_amount_that_is_not_a_valid_amount_is_refused` in `tests/unit/test_stream_csv.py`, with
      the smallest stub it imports, and run it; it fails on its assertion because the parser accepts the faulty row
      instead of returning a `StreamError` with its line and message. Command: `pytest tests/unit/test_stream_csv.py`.
      Proof: the failure message, recorded here. Acceptance: AC-03.
  - Result: it failed on its assertion: `assert StreamError(l...is not valid") == StreamError(l...cimal number")` (1
    failed, 4 passed).
- [x] [AI] GREEN: Add the amount checks: a decimal, no more places than the account's currency, above zero to
      `stream_csv.py`, returning the message tech-docs 003 fixes. Command: `pytest tests/unit/test_stream_csv.py`, then
      `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance: AC-03.
  - Result: `_amount` matches the typed fault: `NotADecimal`, `TooManyPlaces` with its places and currency, and
    `NotPositive`, each with the tech-docs 003 text. 5 passed; `pytest tests/unit` 20 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-03.
  - Result: nothing to tidy. `test:quick` exit 0, coverage 97%.

### Cycle 3.19 — a missing or inapplicable cell is refused

- [x] [AI] RED: write `test_a_missing_or_inapplicable_cell_is_refused` in `tests/unit/test_stream_csv.py`, with the
      smallest stub it imports, and run it; it fails on its assertion because the parser accepts the faulty row instead
      of returning a `StreamError` with its line and message. Command: `pytest tests/unit/test_stream_csv.py`. Proof:
      the failure message, recorded here. Acceptance: AC-03.
  - Result: it failed on its assertion: an empty event ID read `... is not valid`, not
    `column 'event' is required for CREDIT` (1 failed, 5 passed).
- [x] [AI] GREEN: Add the per-kind required and inapplicable cells to `stream_csv.py`, returning the message tech-docs
      003 fixes. Command: `pytest tests/unit/test_stream_csv.py`, then `pytest tests/unit`. Proof: both passing runs,
      recorded here. Acceptance: AC-03.
  - Result: `REQUIRED` and `OPTIONAL` per kind; after the type, each column is checked in header order for a missing
    required cell or a cell the kind does not take. 6 passed; `pytest tests/unit` 21 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-03.
  - Result: `OPTIONAL` typed in full for strict pyright. `test:quick` exit 0, coverage 97%.

### Cycle 3.20 — a day outside the window is refused

- [x] [AI] RED: write `test_a_day_outside_the_window_is_refused` in `tests/unit/test_stream_csv.py`, with the smallest
      stub it imports, and run it; it fails on its assertion because the parser accepts the faulty row instead of
      returning a `StreamError` with its line and message. Command: `pytest tests/unit/test_stream_csv.py`. Proof: the
      failure message, recorded here. Acceptance: AC-03.
  - Result: it failed on its assertion:
    `assert None == StreamError(line=2, message="line 2: day '7' is outside the window 1 to 6")`, Day 7 being accepted
    (1 failed, 6 passed).
- [x] [AI] GREEN: Add the day checks against the configuration's window to `stream_csv.py`, returning the message
      tech-docs 003 fixes. Command: `pytest tests/unit/test_stream_csv.py`, then `pytest tests/unit`. Proof: both
      passing runs, recorded here. Acceptance: AC-03.
  - Result: `_day` reads a day through `Day.parse` and refuses one outside the configured window, a non-whole number
    included, with the window in the message. 7 passed; `pytest tests/unit` 22 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-03.
  - Result: nothing to tidy. `test:quick` exit 0, coverage 98%.

### Cycle 3.21 — a reversal's reference must be an event ID

- [x] [AI] RED: write `test_a_reversal_reference_must_be_an_event_id` in `tests/unit/test_stream_csv.py`, with the
      smallest stub it imports, and run it; it fails on its assertion because the parser accepts the faulty row instead
      of returning a `StreamError` with its line and message. Command: `pytest tests/unit/test_stream_csv.py`. Proof:
      the failure message, recorded here. Acceptance: AC-03.
  - Result: it failed on its assertion: `assert StreamError(l...is not valid") == StreamError(l... an event ID")` (1
    failed, 7 passed); a marker target, `FEE-001-D2@D5`, parses to a `FeeId`.
- [x] [AI] GREEN: Add the reference check through `EventId.parse` to `stream_csv.py`, returning the message tech-docs
      003 fixes. Command: `pytest tests/unit/test_stream_csv.py`, then `pytest tests/unit`. Proof: both passing runs,
      recorded here. Acceptance: AC-03.
  - Result: a reversal's reference goes through `parse_event_id`, and its fault reads
    `reference 'X' is not an event ID`. 8 passed; `pytest tests/unit` 23 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-03.
  - Result: nothing to tidy. `test:quick` exit 0, coverage 98%.

### Cycle 3.22 — an instalment count below two is refused

- [x] [AI] RED: write `test_an_instalment_count_below_2_is_refused` in `tests/unit/test_stream_csv.py`, with the
      smallest stub it imports, and run it; it fails on its assertion because the parser accepts the faulty row instead
      of returning a `StreamError` with its line and message. Command: `pytest tests/unit/test_stream_csv.py`. Proof:
      the failure message, recorded here. Acceptance: AC-03.
  - Result: it failed on its assertion: `assert StreamError(l...is not valid") == StreamError(l...e at least 2')` (1
    failed, 8 passed).
- [x] [AI] GREEN: Add the instalment check to `stream_csv.py`, returning the message tech-docs 003 fixes. Command:
      `pytest tests/unit/test_stream_csv.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-03.
  - Result: an `InstalmentCount.parse` fault reads `instalments must be at least 2`, a non-number included. 9 passed;
    `pytest tests/unit` 24 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-03.
  - Result: nothing to tidy. `test:quick` exit 0, coverage 98%.

### Cycle 3.23 — more instalments than minor units are refused

- [x] [AI] RED: write `test_more_instalments_than_minor_units_are_refused` in `tests/unit/test_stream_csv.py`, with the
      smallest stub it imports, and run it; it fails on its assertion because the parser accepts the faulty row instead
      of returning a `StreamError` with its line and message. Command: `pytest tests/unit/test_stream_csv.py`. Proof:
      the failure message, recorded here. Acceptance: AC-03.
  - Result: it failed on its assertion:
    `assert None == StreamError(line=2, message='line 2: 0.002 cannot be split into 3 instalments')`, the credit being
    accepted (1 failed, 9 passed).
- [x] [AI] GREEN: Add the split's floor, reporting `TooManyInstalments` as the row's fault to `stream_csv.py`, returning
      the message tech-docs 003 fixes. Command: `pytest tests/unit/test_stream_csv.py`, then `pytest tests/unit`. Proof:
      both passing runs, recorded here. Acceptance: AC-03.
  - Result: a credit in instalments is refused when `split_of` returns `TooManyInstalments`; `split_of` narrows a
    run-time currency for `split`, and `digits` gives the value's text. 10 passed; `pytest tests/unit` 25 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-03.
  - Result: `split_of` returns typed `Amount` parts, not plain money, for processing to reuse. `test:quick` exit 0,
    coverage 98%.

### Cycle 3.24 — the shipped stream is the brief's

- [x] [AI] RED: write `test_the_shipped_stream_is_the_brief` in `tests/integration/test_stream_file.py`, with the
      smallest stub it imports, and run it; it fails on its assertion because `streams/challenge.csv` holds only its
      header, so it parses to no events against `brief_stream()`. Command:
      `pytest tests/integration/test_stream_file.py`. Proof: the failure message, recorded here. Acceptance: AC-05.
  - Result: with `streams/challenge.csv` holding only its header, it failed on its assertion:
    `assert () == (Credit(id=In...final'>), ...)`, `Right contains 10 more items` (1 failed).
- [x] [AI] GREEN: Write `apps/account-ledger-cli/streams/challenge.csv` with the eight columns tech-docs 003 shows, and
      `tests/support/brief_stream.py`, and list `{projectRoot}/streams/**/*.csv` among the test targets' inputs in
      `project.json`. Command: `pytest tests/integration/test_stream_file.py`, then `pytest tests/unit`. Proof: both
      passing runs, recorded here. Acceptance: AC-05.
  - Result: the file holds E1 to E10 in eight columns, as tech-docs 003 shows; `tests/support/brief_stream.py` builds
    the same events in code; `{projectRoot}/streams/**/*.csv` joined the inputs of `test:unit`, `test:integration`,
    `test:e2e`, and `test:quick`. 1 passed; `pytest tests/unit tests/integration` 27 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-05.
  - Result: nothing to tidy. `test:quick` exit 0, coverage 98%; `test:integration` exit 0.
- [x] [AI] Mark the rate literal and the working precision in place in `NUMBERS.md`, since `money.py` now uses both; no
      value changes. Proof: the md gates. Acceptance: AC-24.
  - Result: both rows of `NUMBERS.md`'s Chosen Constants read `in place`, since `money.py` defines
    `DAILY_RATE = Decimal("0.0004")` and uses the default 28-digit context; no value changed. md gates 0.
- [x] [AI] Add `money`, `ids`, `config`, `events`, and `stream_csv` to the components view of
      `specs/apps/account-ledger/cli/architecture.md`. Proof: each named module exists under `src/account_ledger/`.
      Acceptance: AC-26.
  - Result: the Components section of `architecture.md` gains a dependency diagram and five table rows; each named
    module exists under `src/account_ledger/`.

### Phase 3 Gate

- [x] [AI] Run every gate command below against the phase's combined state; each exits 0. Proof: each command and its
      exit status, recorded here. Acceptance: AC-03, AC-05, AC-12, AC-22, AC-34. Commands:
  - `npx nx run account-ledger-cli:test:quick`
  - `npx nx run account-ledger-cli:test:integration`
  - `npx nx run account-ledger-cli:test:e2e`
  - `npm run -s check:hygiene`
  - `sh local-tmp/check-md.sh`
  - `./rhino md internal-link validate && ./rhino md heading-hierarchy validate && ./rhino md naming validate`
  - Result (04:39–04:42): `test:quick` 0 (coverage 98%), `test:integration` 0, `test:e2e` 0, `check:hygiene` 0;
    `sh local-tmp/check-md.sh`, internal-link, heading-hierarchy, and naming each 0.
- [x] [AI] Add a new `WORKLOG.md` entry for the phase at the top, stamped with its real start and end `date` times.
      Path: `WORKLOG.md`. Proof: the entry. Acceptance: AC-24.
  - Result: entry "Plan execution, Phase 3".
- [x] [AI] Commit the phase as `feat(account-ledger-cli): add the domain types and the stream reader`, then push to
      `origin/main`; the pre-push hook runs every test layer. Command: `/usr/bin/git push origin main`. Proof: the
      commit hash and the pushed range, recorded here and in the Execution Record. Acceptance: AC-03, AC-05, AC-12,
      AC-22, AC-34.
  - Result: bd5722b, pushed ad8daaf..bd5722b; the pre-push hook ran every test layer.

Pause safety: the phase leaves domain types and a parser proven at the unit and integration layers. Re-verify with
`npx nx run account-ledger-cli:test:quick`.

## Phase 4 — The Log, the Driver, and Incoming Events

The log, balances, the authorization machine, processing, and a first driver
([replay and end of day](tech-docs/002-replay-and-end-of-day.md)). No day-end step exists yet. Each criterion test is
the red of the cycle that builds its behaviour.

### Cycle 4.1 — an empty stream reports the opening balances

- [x] [AI] RED: write `test_an_empty_stream_reports_the_opening_balances_for_day_0_to_6` in `tests/unit/test_replay.py`,
      with the smallest stub it imports, and run it; it fails on its assertion because the stub `replay` returns no
      reports. Command: `pytest tests/unit/test_replay.py`. Proof: the failure message, recorded here. Acceptance:
      AC-01.
  - Result: with a stub `replay` returning no reports, it failed on its assertion:
    `assert [] == [Day(number=0...umber=5), ...]` (1 failed).
- [x] [AI] GREEN: Write `log.py`, `balances.closing`, `report.py`'s `DayReport` with closings only, and `replay.py`'s
      `Replay`, with `reports`, `logs`, `report(day)`, and `log_at(day)`, over an empty stream; add `ACC_001`,
      `ACC_002`, and `through` to `tests/support/streams.py`. Command: `pytest tests/unit/test_replay.py`, then
      `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance: AC-01.
  - Result: `log.py` holds `Accepted`, `LogEntry`, `Log`, and `append`; `balances.closing` returns the opening;
    `DayReport` holds the day and a frozen mapping of closings; `Replay` has `reports`, `logs`, `report(day)`, and
    `log_at(day)`; `tests/support/streams.py` gains `ACC_001`, `ACC_002`, and `through`. 1 passed; `pytest tests/unit`
    26 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-01.
  - Result: `closing_of` dispatches an `AnyAccount` through the `is_aed` `TypeIs` guard in `config.py`, since strict
    pyright refused the union for the generic `closing`. `test:quick` exit 0, coverage 98%.

### Cycle 4.2 — C1: Day 2 closes at −370.00 at the end of Day 5

- [x] [AI] RED: write `test_c1_day_2_closes_at_minus_370_at_end_of_day_5_before_fees` in `tests/unit/test_criteria.py`,
      with the smallest stub it imports, and run it; it fails on its assertion because credits and debits are not yet
      appended, so Day 2 closes at 0.00. Command: `pytest tests/unit/test_criteria.py`. Proof: the failure message,
      recorded here. Acceptance: AC-06.
  - Result: it failed on its assertion: `assert Aed(value=Decimal('0.00')) == Aed(value=Decimal('-370.00'))`, nothing
    being appended (1 failed).
- [x] [AI] GREEN: Process credits and debits in `processing.py` as `Accepted`, count them by value day in
      `balances.closing`, and close days in `replay.py` as booked days advance. Command:
      `pytest tests/unit/test_criteria.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-06.
  - Result: `process` appends credits and debits as `Accepted` on the processed day; `closing` sums each counted effect
    by value day through `same_as`; the driver closes each day as the booked days advance, then every remaining day. 1
    passed; `pytest tests/unit` 27 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-06.
  - Result: the driver's lists typed for strict pyright; ruff allows U+2212 (`allowed-confusables`), which the brief's
    verbatim quote and OUTPUT_TARGET print. `test:quick` exit 0, coverage 98%.

### Cycle 4.3 — a late event is processed on the open day

- [ ] [AI] RED: write `test_amb_015_a_late_event_is_processed_on_the_open_day` in `tests/unit/test_replay.py`, with the
      smallest stub it imports, and run it; it is expected to pass on arrival, since 4.2's driver already processes
      every event on the day that is open; its red is the mutation proof that sorting the stream by booked day puts E10
      in Day 5's log. Command: `pytest tests/unit/test_replay.py`. Proof: the failure message, recorded here.
      Acceptance: AC-01.
  - Disposition: passes on arrival (2 passed), since Cycle 4.2's driver already processes each event on the open day.
    Mutation: sorting the stream by booked day put E10 in Day 5's log, and the test failed on its assertion
    (`assert IncomingId(value='E10') not in [... IncomingId(value='E10')]`); restored from a copy, 2 passed.
- [x] [AI] GREEN: No production change is expected; any gap the red shows is closed here. Command:
      `pytest tests/unit/test_replay.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance:
      AC-01.
  - Result: no production change; passes on arrival, recorded in the Execution Record.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-01.
  - Result: nothing to tidy. `test:quick` exit 0.

### Cycle 4.4 — C5: a hold reduces available balance only

- [x] [AI] RED: write `test_c5_a_hold_reduces_available_balance_but_not_ledger_balance` in
      `tests/unit/test_criteria.py`, with the smallest stub it imports, and run it; it fails on its assertion because
      authorizations are ignored, so Day 2's available balance is 250.00, not 50.00. Command:
      `pytest tests/unit/test_criteria.py`. Proof: the failure message, recorded here. Acceptance: AC-10.
  - Result: with `DayReport.available` stubbed as the closing, it failed on its assertion:
    `assert Aed(value=Decimal('250.00')) == Aed(value=Decimal('50.00'))` (1 failed, 1 passed).
- [x] [AI] GREEN: Write `decide` returning a `Decision`, `AuthorizationDecided` in `log.py`, `records` building
      `Approved`, `holds` and `available` in `balances.py`, and `available` in `DayReport`. Command:
      `pytest tests/unit/test_criteria.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-10.
  - Result: `Decision` and `AuthorizationDecided` in `log.py`; `authorizations.py` with `Approved`,
    `AuthorizationRecord`, `decide(available, amount)`, which approves for now, and `records`; `holds`, `available`, and
    `available_of` in `balances.py`; `available` in `DayReport`; `process` takes the configuration to find the account.
    2 passed; `pytest tests/unit` 29 passed. `decide` takes the balance, not the log, to avoid an import cycle
    (learnings L3).
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-10.
  - Result: the effect `match` names the authorization case, with no effect, for exhaustiveness. `test:quick` exit 0,
    coverage 98%.

### Cycle 4.5 — C5: Auth-B is declined

- [x] [AI] RED: write `test_c5_auth_b_is_declined` in `tests/unit/test_criteria.py`, with the smallest stub it imports,
      and run it; it fails on its assertion because every authorization is approved. Command:
      `pytest tests/unit/test_criteria.py`. Proof: the failure message, recorded here. Acceptance: AC-10.
  - Result: it failed on its assertion:
    `At index 0 diff: Approved(hold=Amount(money=Aed(value=Decimal('90.00')))) != Declined(requested=...)`, every
    authorization being approved (1 failed, 2 passed).
- [x] [AI] GREEN: Return a declined `Decision` when the available balance after the hold is below zero, and build
      `Declined(requested)` from it in `records`. Command: `pytest tests/unit/test_criteria.py`, then
      `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance: AC-10.
  - Result: `decide` declines when the available balance is below the amount, through `money.below`; `records` builds
    `Declined(requested)` from a declined decision. 3 passed; `pytest tests/unit` 30 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-10.
  - Result: nothing to tidy. `test:quick` exit 0, coverage 98%.

### Cycle 4.6 — a future-dated credit does not count for an authorization

- [ ] [AI] RED: write `test_amb_008_a_future_dated_credit_does_not_count_for_an_authorization` in
      `tests/unit/test_authorizations.py`, with the smallest stub it imports, and run it; it is expected to pass on
      arrival, since `available` already reads balances by value day; its red is the mutation proof that counting every
      accepted credit, whatever its value date, approves the authorization. Command:
      `pytest tests/unit/test_authorizations.py`. Proof: the failure message, recorded here. Acceptance: AC-37.
  - Disposition: passes on arrival (1 passed), since `available` already reads balances by value day. Mutation: counting
    every effect whatever its value day approved the authorization, and the test failed on its assertion
    (`At index 0 diff: Approved(hold=...) != Declined(requested=...)`); restored from a copy, 1 passed.
- [x] [AI] GREEN: No production change is expected; any gap the red shows is closed here. Command:
      `pytest tests/unit/test_authorizations.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-37.
  - Result: no production change; passes on arrival, recorded in the Execution Record. The support builders `credit`,
    `debit`, `authorization`, `settlement`, and `reversal` arrived with the test.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-37.
  - Result: the builders' amount typed for strict pyright. `test:quick` exit 0, coverage 98%.

### Cycle 4.7 — a later credit the same day does not rescue a decline

- [ ] [AI] RED: write `test_amb_009_a_later_credit_the_same_day_does_not_rescue_a_decline` in
      `tests/unit/test_authorizations.py`, with the smallest stub it imports, and run it; it is expected to pass on
      arrival, since `records` builds the state from the decision logged on arrival; its red is the mutation proof that
      re-deciding each authorization at the day's end approves it. Command: `pytest tests/unit/test_authorizations.py`.
      Proof: the failure message, recorded here. Acceptance: AC-37.
  - Disposition: passes on arrival (2 passed), since `records` builds the state from the decision logged on arrival.
    Mutation: re-deciding the day's authorizations after a credit appended an approval, and the test failed on its
    assertion (`Left contains one more item: Approved(...)`); restored from a copy, 2 passed.
- [x] [AI] GREEN: No production change is expected; any gap the red shows is closed here. Command:
      `pytest tests/unit/test_authorizations.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-37.
  - Result: no production change; passes on arrival, recorded in the Execution Record.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-37.
  - Result: nothing to tidy. `test:quick` exit 0.

### Cycle 4.8 — a hold counts from its value date

- [x] [AI] RED: write `test_amb_010_a_hold_counts_from_its_value_date` in `tests/unit/test_authorizations.py`, with the
      smallest stub it imports, and run it; it fails on its assertion because `holds` counts an authorization
      value-dated Day 3 against Day 2's available balance. Command: `pytest tests/unit/test_authorizations.py`. Proof:
      the failure message, recorded here. Acceptance: AC-37.
  - Result: it failed on its assertion: `assert Aed(value=Decimal('60.00')) == Aed(value=Decimal('100.00'))`, the Day 3
    hold counting on Day 2 (1 failed, 2 passed).
- [x] [AI] GREEN: Count a hold in `balances.holds` from its authorization's value date only. Command:
      `pytest tests/unit/test_authorizations.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-37.
  - Result: `holds` counts an approved hold only once its authorization's value day is at most the day asked. 3 passed;
    `pytest tests/unit` 33 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-37.
  - Result: nothing to tidy. `test:quick` exit 0, coverage 98%.

### Cycle 4.9 — C3: Auth-A's final settlement releases its hold

- [x] [AI] RED: write `test_c3_auth_a_settlement_is_accepted_and_releases_the_hold` in `tests/unit/test_criteria.py`,
      with the smallest stub it imports, and run it; it fails on its assertion because settlements are ignored, so no
      185.00 debit posts and the hold stays. Command: `pytest tests/unit/test_criteria.py`. Proof: the failure message,
      recorded here. Acceptance: AC-08.
  - Done 04:47. Stubs: `Settled` in `authorizations.py`, and `Captured` and `SettlementAccepted` in `log.py`, typed
    `object` and outside `LogEntry`.
  - `pytest tests/unit/test_criteria.py`: 1 failed, 3 passed, on its assertion: `At index 0 diff:`
    `Approved(hold=Amount(money=Aed(value=Decimal('200.00'))))` `!=`
    `Settled(captured=Amount(money=Aed(value=Decimal('185.00'))))`. The hold stays, because settlements were ignored.
- [x] [AI] GREEN: Add `Settlement` processing, `Settled`, `SettleFinal`, `transition`, and the `Captured` effect.
      Command: `pytest tests/unit/test_criteria.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-08.
  - Done 04:53. `log.py`: typed `Captured(before, after)` and
    `SettlementAccepted(event: Settlement, processed_day, effect)`, now in `LogEntry`; the states are imported under
    `TYPE_CHECKING`, since `authorizations` reads the log. `authorizations.py`: `SettleFinal`, `trigger_of`,
    `transition` (Approved + SettleFinal → Settled), and `record_for`; `records` applies each capture's `after`.
    `processing.py`: a `Settlement` case appends `SettlementAccepted` with `Captured`. `balances.py`: a settlement
    debits its amount at its value day.
  - `pytest tests/unit/test_criteria.py`: 4 passed. `pytest tests/unit`: 34 passed.
  - `test:quick` then failed typecheck on two test annotations: `state_of` typed `list[Approved | Declined]`, and
    `SettlementAccepted` built from the union-typed log event. Fixed by typing `state_of` as `list[AuthorizationState]`
    and narrowing the E5 event with `isinstance`.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-08.
  - Done 04:53. The duplicated `state_of` in `test_authorizations.py` and `test_criteria.py` moved to
    `tests/support/states.py`.
  - `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 34 passed, coverage 98%.

### Cycle 4.10 — C4: E6 is a force-post

- [x] [AI] RED: write `test_c4_e6_is_force_posted_for_180` in `tests/unit/test_criteria.py`, with the smallest stub it
      imports, and run it; it fails on its assertion because a settlement without an authorization posts nothing.
      Command: `pytest tests/unit/test_criteria.py`. Proof: the failure message, recorded here. Acceptance: AC-09.
  - Done 04:54. Stub: an empty `ForcePosted` in `log.py`.
  - `pytest tests/unit/test_criteria.py`: 1 failed, 4 passed, on its assertion:
    `assert [] == [SettlementAc...orcePosted())]`, `Right contains one more item`. A settlement with no authorization
    was dropped, posting nothing.
- [x] [AI] GREEN: Post a settlement with no transition as `ForcePosted`, releasing nothing. Command:
      `pytest tests/unit/test_criteria.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-09.
  - Done 04:54. `ForcePosted` is documented and joins `SettlementAccepted.effect` as `Captured | ForcePosted`; `process`
    appends a force-post when `record_for` finds no authorization. The settlement debit in `balances.py` already covers
    it.
  - `pytest tests/unit/test_criteria.py`: 5 passed. `pytest tests/unit`: 35 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-09.
  - Done 04:55. The wildcard case in `records` became an explicit `Accepted() | SettlementAccepted()` case, commented;
    pyright cannot prove exhaustiveness through a nested `effect=ForcePosted()` pattern, so the case matches on the
    entry type.
  - `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 35 passed, coverage 98%.

### Cycle 4.11 — an unconfigured transition leaves the state unchanged

- [x] [AI] RED: write `test_an_unconfigured_transition_leaves_the_state_unchanged` in
      `tests/unit/test_authorizations.py`, with the smallest stub it imports, and run it; it fails on its assertion
      because `transition` on `Settled` returns a new state. Command: `pytest tests/unit/test_authorizations.py`. Proof:
      the failure message, recorded here. Acceptance: AC-18, AC-19.
  - Done 04:55. Parametrized over `Settled` and `Declined`, triggered by `SettleFinal`. Stub: an empty `NoTransition` in
    `authorizations.py`.
  - `pytest tests/unit/test_authorizations.py`: 2 failed, 3 passed, on their assertion:
    `assert Settled(captured=Amount(money=Aed(value=Decimal('185.00')))) == NoTransition()`. The wildcard case handed
    back the state itself, not `NoTransition`.
- [x] [AI] GREEN: Return `NoTransition` from `transition` for `Settled` and `Declined`, ending the `match` in
      `assert_never`. Command: `pytest tests/unit/test_authorizations.py`, then `pytest tests/unit`. Proof: both passing
      runs, recorded here. Acceptance: AC-18, AC-19.
  - Done 04:56. `transition` returns `AuthorizationState | NoTransition`: `Settled() | Declined(), _` gives
    `NoTransition()`, and the `match` ends in `assert_never(pair)` over the named `(state, trigger)` pair, since pyright
    flags a capture pattern on an exhausted tuple as never matched. `process` force-posts a settlement whose transition
    is `NoTransition`.
  - `pytest tests/unit/test_authorizations.py`: 5 passed. `pytest tests/unit`: 37 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-18, AC-19.
  - Done 04:56. The nested `match` in `process` moved to `_effect(before, settlement)`, and the unknown-authorization
    branch gained its AMB-012 comment.
  - `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 37 passed, coverage 98%.

### Cycle 4.12 — a settlement against a declined authorization is a force-post

- [ ] [AI] RED: write `test_amb_029_a_settlement_against_a_declined_authorization_is_force_posted` in
      `tests/unit/test_authorizations.py`, with the smallest stub it imports, and run it; it is expected to pass on
      arrival, since 4.10 and 4.11 already route it; its red is the mutation proof that letting a declined authorization
      settle captures it. Command: `pytest tests/unit/test_authorizations.py`. Proof: the failure message, recorded
      here. Acceptance: AC-18.
  - Disposition: passes on arrival (6 passed), since 4.10 and 4.11 route a settlement whose transition is `NoTransition`
    to `ForcePosted`. Mutation: adding a `Declined(), SettleFinal(amount=a)` case that returns `Settled(a)` made the
    test fail on its assertion: at index 0 the entry's effect was `Captured(before=Declined(...), after=Settled(...))`,
    not `ForcePosted()`. Restored from a copy, 6 passed.
- [x] [AI] GREEN: No production change is expected; any gap the red shows is closed here. Command:
      `pytest tests/unit/test_authorizations.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-18.
  - Result: no production change; passes on arrival, recorded in the Execution Record.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-18.
  - Done 04:57. The test's settlement-entry filter moved to `settlements_of` in `tests/support/states.py`, and the C3
    and C4 tests use it too.
  - `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 38 passed, coverage 98%.

### Cycle 4.13 — a settlement after a final one is a force-post

- [ ] [AI] RED: write `test_amb_029_a_settlement_after_a_final_one_is_force_posted` in
      `tests/unit/test_authorizations.py`, with the smallest stub it imports, and run it; it is expected to pass on
      arrival, since 4.10 and 4.11 already route it; its red is the mutation proof that letting `Settled` accept a
      second settlement captures it. Command: `pytest tests/unit/test_authorizations.py`. Proof: the failure message,
      recorded here. Acceptance: AC-19.
  - Disposition: passes on arrival (7 passed), since `transition` gives `NoTransition` for `Settled`, which `process`
    force-posts. Mutation: adding a `Settled(), SettleFinal(amount=a)` case that returns `Settled(a)` made the test fail
    on its assertion: at index 0 the entry's effect was `Captured(before=Settled(...), after=Settled(...))`, not
    `ForcePosted()`. Restored from a copy, 7 passed.
- [x] [AI] GREEN: No production change is expected; any gap the red shows is closed here. Command:
      `pytest tests/unit/test_authorizations.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-19.
  - Result: no production change; passes on arrival, recorded in the Execution Record.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-19.
  - Result: nothing to tidy; the test reuses `settlements_of` and `state_of`.
    `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 39 passed, coverage 98%.

### Cycle 4.14 — C7: E10 posts three instalments

- [x] [AI] RED: write `test_c7_e10_posts_3_333_3_333_3_334` in `tests/unit/test_criteria.py`, with the smallest stub it
      imports, and run it; it fails on its assertion because E10 posts as one credit of 10.000. Command:
      `pytest tests/unit/test_criteria.py`. Proof: the failure message, recorded here. Acceptance: AC-12.
  - Done 04:58. Stub: `Instalment(id, account, value_day, amount)` in `events.py`.
  - `pytest tests/unit/test_criteria.py`: 1 failed, 5 passed, on its assertion:
    `assert [] == [(InstalmentI...ay(number=5))]`, `Right contains 3 more items`. E10 posted as one credit of 10.000 and
    fired nothing.
- [x] [AI] GREEN: Fire `Instalment` events E10-1 to E10-3 from a credit in `Instalments`, using `money.split`. Command:
      `pytest tests/unit/test_criteria.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-12.
  - Done 04:59. `events.py`: `Instalment` documented, and `type FiredEvent = Instalment`; `Accepted.event` now takes
    `Credit | Debit | FiredEvent`. `process` appends a credit in `Instalments` as `Accepted`, then one
    `Accepted(Instalment(...))` per part of `split_of`, numbered from 1 with the credit's value day. `balances._effects`
    counts a `Whole` credit and each instalment, and a credit in instalments posts nothing itself.
  - `pytest tests/unit/test_criteria.py`: 6 passed. `pytest tests/unit`: 40 passed.
  - Typecheck first flagged the `Credit(posting=Whole())` class pattern as not exhaustive, so `_effects` matches
    `event.posting` inside the `Credit` case.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-12.
  - Done 04:59. The instalment firing moved from the `match` in `process` to `_instalments(credit, count, today)`.
  - `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 40 passed, coverage 98%.

### Cycle 4.15 — a reversal undoes what its target moved

- [x] [AI] RED: write `test_amb_035_a_reversal_undoes_what_its_target_moved` in `tests/unit/test_processing.py`, with
      the smallest stub it imports, and run it; it fails on its assertion because reversals are ignored, so Day 2 stays
      at −370.00 after E9. Command: `pytest tests/unit/test_processing.py`. Proof: the failure message, recorded here.
      Acceptance: AC-11.
  - Done 05:00. New file `tests/unit/test_processing.py`; no stub was needed.
  - `pytest tests/unit/test_processing.py`: 1 failed, on its assertion:
    `At index 0 diff: Aed(value=Decimal('-370.00')) != Aed(value=Decimal('250.00'))`. E9 was ignored, so Day 2 stayed at
    −370.00.
- [x] [AI] GREEN: Append a reversal as `Accepted`, and give it minus its target's effect, from the reversal's value day,
      in `balances.closing`. Command: `pytest tests/unit/test_processing.py`, then `pytest tests/unit`. Proof: both
      passing runs, recorded here. Acceptance: AC-11.
  - Done 05:00. `process` appends a `Reversal` as `Accepted`, whose event type now includes `Reversal`.
    `balances._effects` reads each event's signed movement from `_moved(log, event)`; a reversal moves minus its
    target's movement, found as the first entry with the reversed ID, counted from the reversal's own value day.
    `log.py` gained `LoggedEvent`, the union of every entry's event.
  - `pytest tests/unit/test_processing.py`: 1 passed. `pytest tests/unit`: 41 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-11.
  - Done 05:01. The now-unreachable wildcard in `process` became `assert_never(event)`, so a new incoming kind fails
    typecheck until it is processed.
  - `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 41 passed, coverage 98%.

### Cycle 4.16 — a second reversal of the same event is refused

- [x] [AI] RED: write `test_amb_028_a_second_reversal_of_the_same_event_is_refused` in `tests/unit/test_processing.py`,
      with the smallest stub it imports, and run it; it fails on its assertion because E12 reverses E7 a second time.
      Command: `pytest tests/unit/test_processing.py`. Proof: the failure message, recorded here. Acceptance: AC-16.
  - Done 05:01. Stubs: `AlreadyReversed` and `Rejected` in `log.py`, typed `object` and outside `LogEntry`.
  - `pytest tests/unit/test_processing.py`: 1 failed, 1 passed, on its assertion: at index 0,
    `Accepted(event=Reversal(id=IncomingId(value='E12'), ...))` was not
    `Rejected(event=Reversal(...), ..., reason=AlreadyReversed(...))`. E12 reversed E7 a second time.
- [x] [AI] GREEN: Append it as `Rejected(AlreadyReversed)`; the test asserts the entry. Command:
      `pytest tests/unit/test_processing.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-16.
  - Done 05:02. `log.py`: typed `AlreadyReversed(target: EventId, by: IncomingId)`, `type Rejection`, and
    `Rejected(event: IncomingEvent, processed_day, reason)`, now in `LogEntry`. `process` routes a reversal through
    `_reversal`, which refuses it when an accepted reversal of the same target exists. `balances._effects` counts only
    `Accepted` and `SettlementAccepted` entries, and `records` passes over a refusal.
  - `pytest tests/unit/test_processing.py`: 2 passed. `pytest tests/unit`: 42 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-16.
  - Done 05:02. The entry filter in `_effects` moved to the generator `_counted(log, account_id)`.
  - `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 42 passed, coverage 98%.

### Cycle 4.17 — a reversal of a reversal is refused

- [x] [AI] RED: write `test_amb_028_a_reversal_of_a_reversal_is_refused` in `tests/unit/test_processing.py`, with the
      smallest stub it imports, and run it; it fails on its assertion because E12 undoes E9. Command:
      `pytest tests/unit/test_processing.py`. Proof: the failure message, recorded here. Acceptance: AC-17.
  - Done 05:02. Stub: `ReversesAReversal` in `log.py`, typed `object`.
  - `pytest tests/unit/test_processing.py`: 1 failed, 2 passed, on its assertion: at index 0,
    `Accepted(event=Reversal(id=IncomingId(value='E12'), ..., reverses=IncomingId(value='E9')))` was not
    `Rejected(..., reason=ReversesAReversal(target=IncomingId(value='E9')))`. E12 undid E9.
- [x] [AI] GREEN: Append it as `Rejected(ReversesAReversal)`; the test asserts the entry. Command:
      `pytest tests/unit/test_processing.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-17.
  - Done 05:02. `log.py`: typed `ReversesAReversal(target: EventId)`, joining `Rejection`. `_reversal` refuses a
    reversal whose target is a reversal, before the already-reversed check, in tech-docs 002's order. The first run
    failed with `NameError` on a missing import, which does not count; fixed, then:
  - `pytest tests/unit/test_processing.py`: 3 passed. `pytest tests/unit`: 43 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-17.
  - Done 05:03. The first-entry lookup in `processing._reversal` and `balances._moved` moved to
    `log.first(log, event_id)`.
  - `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 43 passed, coverage 98%.

### Cycle 4.18 — a reversal of an unknown event is refused

- [x] [AI] RED: write `test_amb_035_a_reversal_of_an_unknown_event_is_refused` in `tests/unit/test_processing.py`, with
      the smallest stub it imports, and run it; it fails on its assertion because a reversal of E99 is accepted and
      undoes nothing. Command: `pytest tests/unit/test_processing.py`. Proof: the failure message, recorded here.
      Acceptance: AC-32.
  - Done 05:03. Stub: `UnknownTarget` in `log.py`, typed `object`.
  - `pytest tests/unit/test_processing.py`: 1 failed, 3 passed, on its assertion: at index 0,
    `Accepted(event=Reversal(..., reverses=IncomingId(value='E99')))` was not
    `Rejected(..., reason=UnknownTarget(target=IncomingId(value='E99')))`. The reversal of E99 was accepted and undid
    nothing.
- [x] [AI] GREEN: Append it as `Rejected(UnknownTarget)`; the test asserts the entry. Command:
      `pytest tests/unit/test_processing.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-32.
  - Done 05:03. `log.py`: typed `UnknownTarget(target: EventId)`, joining `Rejection`. `_reversal` refuses a reversal
    with no first entry for its target, as the first check.
  - `pytest tests/unit/test_processing.py`: 4 passed. `pytest tests/unit`: 44 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-32.
  - Result: nothing to tidy; the checks in `_reversal` read in tech-docs 002's order.
    `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 44 passed, coverage 98%.

### Cycle 4.19 — a reversal of an event that moved no money is refused

- [x] [AI] RED: write `test_amb_035_a_reversal_of_an_event_that_moved_no_money_is_refused` in
      `tests/unit/test_processing.py`, with the smallest stub it imports, and run it; it fails on its assertion because
      a reversal of the declined E8 or the approved E3 is accepted. Command: `pytest tests/unit/test_processing.py`.
      Proof: the failure message, recorded here. Acceptance: AC-32.
  - Done 05:04. Parametrized over the declined E8 and the approved E3. Stub: `MovedNoMoney` in `log.py`, typed `object`.
  - `pytest tests/unit/test_processing.py`: 2 failed, 4 passed, each on its assertion: at index 0,
    `Accepted(event=Reversal(..., reverses=IncomingId(value='E8')))` was not
    `Rejected(..., reason=MovedNoMoney(target=IncomingId(value='E8')))`, and the same for E3.
- [x] [AI] GREEN: Append it as `Rejected(MovedNoMoney)` when the target is an authorization or a rejected entry.
      Command: `pytest tests/unit/test_processing.py`, then `pytest tests/unit`. Proof: both passing runs, recorded
      here. Acceptance: AC-32.
  - Done 05:04. `log.py`: typed `MovedNoMoney(target: EventId)`, joining `Rejection`. `_reversal` refuses a reversal
    whose target entry is an `AuthorizationDecided` or a `Rejected`, after the reversal check.
  - `pytest tests/unit/test_processing.py`: 6 passed. `pytest tests/unit`: 46 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-32.
  - Done 05:05. `_reversal` now wraps `_refusal(log, target_id) -> Rejection | None`, which runs the checks in order;
    the already-reversed search became `_reversed_by`, one class pattern.
  - `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 46 passed, coverage 98%.

### Cycle 4.20 — reversing a credit in instalments undoes every instalment

- [x] [AI] RED: write `test_amb_035_reversing_a_credit_in_instalments_undoes_every_instalment` in
      `tests/unit/test_processing.py`, with the smallest stub it imports, and run it; it fails on its assertion because
      reversing E10 undoes nothing, since E10 itself posted nothing. Command: `pytest tests/unit/test_processing.py`.
      Proof: the failure message, recorded here. Acceptance: AC-33.
  - Done 05:05. No stub was needed.
  - `pytest tests/unit/test_processing.py`: 1 failed, 6 passed, on its assertion:
    `assert Bhd(value=Decimal('10.000')) == Bhd(value=Decimal('0.000'))`. Reversing E10 undid nothing, since E10 itself
    posted nothing.
- [x] [AI] GREEN: Count a credit's instalments as its effect when it is reversed. Command:
      `pytest tests/unit/test_processing.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-33.
  - Done 05:05. `balances._moved` returns a tuple of signed amounts, empty for an event that moves nothing; a reversal
    takes out minus `_undone(log, target)`, which for a credit in instalments is every instalment it fired.
  - `pytest tests/unit/test_processing.py`: 7 passed. `pytest tests/unit`: 47 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-33.
  - Done 05:05. The instalment search moved to `log.instalments_of(log, credit)`, which Cycle 4.21 reuses.
  - `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 47 passed, coverage 98%.

### Cycle 4.21 — money already undone cannot be undone again

- [x] [AI] RED: write `test_amb_035_money_already_undone_cannot_be_undone_again` in `tests/unit/test_processing.py`,
      with the smallest stub it imports, and run it; it fails on its assertion because a reversal of an instalment of a
      reversed credit, or of a credit one of whose instalments was reversed, is accepted. Command:
      `pytest tests/unit/test_processing.py`. Proof: the failure message, recorded here. Acceptance: AC-35.
  - Done 05:06. Parametrized: E11 reverses E10 then E12 reverses E10-1 (`part`), and E11 reverses E10-1 then E12
    reverses E10 (`whole`). Stub: `AlreadyUndone` in `log.py`, typed `object`.
  - `pytest tests/unit/test_processing.py`: 2 failed, 7 passed, each on its assertion: at index 0,
    `Accepted(event=Reversal(id=IncomingId(value='E12'), ...))` was not `Rejected(..., reason=AlreadyUndone(...))`
    naming part `InstalmentId(parent=IncomingId(value='E10'), n=1)` and `by=IncomingId(value='E11')`.
- [x] [AI] GREEN: Append it as `Rejected(AlreadyUndone)`, naming the part and what undid it; the test asserts the entry,
      and its refunded-fee case is added in Cycle 5.16, once refunds exist. Command:
      `pytest tests/unit/test_processing.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-35.
  - Done 05:06. `log.py`: typed `AlreadyUndone(part: EventId, by: EventId)`, joining `Rejection`; `by` is an `EventId`
    so that Cycle 5.16 can name a refund. `_refusal` ends with `_undone_by`, which refuses an instalment of a reversed
    credit, or a credit one of whose instalments is reversed, naming the part and its reversal.
  - `pytest tests/unit/test_processing.py`: 9 passed. `pytest tests/unit`: 49 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-35.
  - Done 05:06. The credit branch of `_undone_by` became one `next(...)` over the instalments.
  - `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 49 passed, coverage 98%.

### Cycle 4.22 — the same event twice is logged as a duplicate

- [x] [AI] RED: write `test_amb_034_a_repeated_event_is_logged_as_a_duplicate_with_no_effect` in
      `tests/unit/test_processing.py`, with the smallest stub it imports, and run it; it fails on its assertion because
      the second E1 credits another 100.00. Command: `pytest tests/unit/test_processing.py`. Proof: the failure message,
      recorded here. Acceptance: AC-14.
  - Done 05:07. Stub: `Duplicate` in `log.py`, typed `object`. The first run failed with `NameError`, from an import the
    edit missed, and does not count; with the import fixed:
  - `pytest tests/unit/test_processing.py`: 1 failed, 9 passed, on its assertion: at index 1,
    `Accepted(event=Credit(id=IncomingId(value='E1'), ...))` was not
    `Duplicate(event=Credit(...), processed_day=Day(number=1))`. The second E1 credited another 100.00.
- [x] [AI] GREEN: Append an event equal to the first with its ID as `Duplicate`, counted by no aggregation. Command:
      `pytest tests/unit/test_processing.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-14.
  - Done 05:07. `log.py`: typed `Duplicate(event: IncomingEvent, processed_day)`, in `LogEntry`. `process` first looks
    up the first entry for the event's ID, and appends an equal event as `Duplicate`; `_counted` counts only accepted
    entries, so no balance moves, and `records` passes over it.
  - `pytest tests/unit/test_processing.py`: 10 passed. `pytest tests/unit`: 50 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-14.
  - Result: nothing to tidy; the idempotency check is three lines ahead of the `match`, reusing `log.first`.
    `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 50 passed, coverage 98%.

### Cycle 4.23 — a reused ID with other content is refused

- [x] [AI] RED: write `test_amb_034_a_reused_id_with_different_content_is_refused` in `tests/unit/test_processing.py`,
      with the smallest stub it imports, and run it; it fails on its assertion because the second E1 credits 90.00.
      Command: `pytest tests/unit/test_processing.py`. Proof: the failure message, recorded here. Acceptance: AC-15.
  - Done 05:07. Stub: `IdReused` in `log.py`, typed `object`.
  - `pytest tests/unit/test_processing.py`: 1 failed, 10 passed, on its assertion: at index 1,
    `Accepted(event=Credit(id=IncomingId(value='E1'), ..., amount=Amount(money=Aed(value=Decimal('90.00'))), ...))` was
    not `Rejected(..., reason=IdReused(...))`. The second E1 credited 90.00.
- [x] [AI] GREEN: Append it as `Rejected(IdReused)`; the test asserts the entry. Command:
      `pytest tests/unit/test_processing.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-15.
  - Done 05:08. `log.py`: `IdReused` joins `Rejection` with no field, since the refused event already carries the ID its
    text names; the test now expects `IdReused()`. The idempotency check in `process` appends an equal event as
    `Duplicate` and any other as `Rejected(IdReused())`.
  - `pytest tests/unit/test_processing.py`: 11 passed. `pytest tests/unit`: 51 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-15.
  - Done 05:08. The test module's `entries_for` moved to `tests/support/states.py`, beside `settlements_of` and
    `state_of`.
  - `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 51 passed, coverage 98%.
- [x] [AI] Add `log`, `balances`, `authorizations` with its state diagram, `processing`, `replay`, and `report` to
      `architecture.md`'s components. Proof: each named module exists. Acceptance: AC-26.
  - Done 05:10. `architecture.md`: a ledger-core component diagram (replay, processing, report, authorizations,
    balances, log), the as-built authorization state diagram (Approved, Declined, Settled; `SettleFinal`; force-post
    without a transition), six new rows in the component table, and a Scope that no longer calls the app a hello-world
    scaffold.
  - Each named module exists: `ls src/account_ledger/{log,balances,authorizations,processing,replay,report}.py` lists
    all six.

### Phase 4 Gate

- [x] [AI] Run every gate command below against the phase's combined state; each exits 0. Proof: each command and its
      exit status, recorded here. Acceptance: AC-06, AC-08 to AC-12, AC-14 to AC-19, AC-32, AC-33, AC-35, AC-37.
      Commands:
  - `npx nx run account-ledger-cli:test:quick`
  - `npx nx run account-ledger-cli:test:integration`
  - `npx nx run account-ledger-cli:test:e2e`
  - `npm run -s check:hygiene`
  - `sh local-tmp/check-md.sh`
  - `./rhino md internal-link validate && ./rhino md heading-hierarchy validate && ./rhino md naming validate`
  - Done 05:13, each exiting 0: `test:quick` 0 (51 passed, coverage 97%); `test:integration` 0 (2 passed); `test:e2e` 0
    (1 passed); `npm run -s check:hygiene` 0; `sh local-tmp/check-md.sh` 0; `./rhino md internal-link validate` 0,
    `heading-hierarchy validate` 0, `naming validate` 0.
- [x] [AI] Add a new `WORKLOG.md` entry for the phase at the top, stamped with its real start and end `date` times.
      Path: `WORKLOG.md`. Proof: the entry. Acceptance: AC-24.
  - Done 05:13: the row `2026-09-25 04:42–05:13`, "Plan execution, Phase 4: log, authorizations, settlements, reversals,
    and idempotency".
- [x] [AI] Commit the phase as `feat(account-ledger-cli): replay incoming events through an append-only log`, then push
      to `origin/main`; the pre-push hook runs every test layer. Command: `/usr/bin/git push origin main`. Proof: the
      commit hash and the pushed range, recorded here and in the Execution Record. Acceptance: AC-06, AC-08 to AC-12,
      AC-14 to AC-19, AC-32, AC-33, AC-35, AC-37.
  - Done 05:14: commit `58b0cdb`; the pre-push hook ran `test:quick`, `test:integration`, and `test:e2e`, all green;
    pushed `bd5722b..58b0cdb` to `origin/main`.

Pause safety: the phase leaves every incoming kind processed, C1, C3, C4, C5, and C7 green, and each decision rule
proven. Re-verify with `npx nx run account-ledger-cli:test:quick`.

## Phase 5 — End of Day and the Day Report

The three end-of-day steps and the full day report. Each criterion test is again the red of its cycle where the order
allows; C6's Day 6 figure follows once adjustments and capitalization both exist, so it is expected to pass on arrival
and is handled as the rule above says.

### Cycle 5.1 — C2: E7 causes three fees

- [x] [AI] RED: write `test_c2_e7_causes_three_fees_all_value_dated_day_5` in `tests/unit/test_criteria.py`, with the
      smallest stub it imports, and run it; it fails on its assertion because no day closes with a fee step. Command:
      `pytest tests/unit/test_criteria.py`. Proof: the failure message, recorded here. Acceptance: AC-07.
  - Done 05:15. Stubs: `Fee(id, account, value_day, amount)` in `events.py`, and `fee_markers` returning `[]` in
    `tests/support/streams.py`.
  - `pytest tests/unit/test_criteria.py`: 1 failed, 6 passed, on its assertion:
    `assert [] == ['FEE-001-D2@...EE-001-D5@D5']`, `Right contains 3 more items`. No day closed with a fee step.
- [x] [AI] GREEN: Write step 1 in `end_of_day.py`: a fee for each negative day, value-dated today, and call `close_day`
      from the driver; add `fee_markers` to `tests/support/streams.py`. Command: `pytest tests/unit/test_criteria.py`,
      then `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance: AC-07.
  - Done 05:17. `end_of_day.close_day` fires, per account, a `Fee` value-dated today for each day so far whose closing
    is negative, of `overdraft_fee_of(account.opening)`, new in `money.py` for a currency known only at run time, since
    pyright will not assign a generic `Amount[M]` to `AnyAmount`. `Fee` joins `FiredEvent` and debits in
    `balances._moved`; `replay` runs `close_day` before each day's report; `fee_markers` reads each fee's marker.
  - Four earlier rule tests asserted closings on days that went negative incidentally, and now drew fees: the AMB-029
    declined-settlement test and the AMB-028 and unknown-target reversal tests. Their streams now open with a credit so
    no day is negative, and their asserted figures moved with it; what each test proves is unchanged.
  - `pytest tests/unit/test_criteria.py`: 7 passed. `pytest tests/unit`: 52 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-07.
  - Done 05:17. `replay` now runs one loop over the window's days: process the events listed next whose booked day has
    come, then close. It no longer repeats close, report, and append in two loops; the order is the same as tech-docs
    002's, since the stream reader refuses a booked day outside the window.
  - `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 52 passed, coverage 97%.

### Cycle 5.2 — a day still negative is not charged again

- [x] [AI] RED: write `test_amb_011_a_day_still_negative_is_not_charged_again` in `tests/unit/test_end_of_day.py`, with
      the smallest stub it imports, and run it; it fails on its assertion because the next close charges the same day a
      second fee. Command: `pytest tests/unit/test_end_of_day.py`. Proof: the failure message, recorded here.
      Acceptance: AC-07.
  - Done 05:18. New file `tests/unit/test_end_of_day.py`; no stub was needed.
  - `pytest tests/unit/test_end_of_day.py`: 1 failed, on its assertion:
    `At index 1 diff: 'FEE-001-D1@D2' != 'FEE-001-D2@D2'`. Day 2's close charged Day 1 a second fee.
- [x] [AI] GREEN: Track fees in force, so a day is charged once until refunded. Command:
      `pytest tests/unit/test_end_of_day.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-07.
  - Done 05:18. `end_of_day._in_force` gives the days the account's fees are for, and step 1 skips a negative day that
    has one.
  - `pytest tests/unit/test_end_of_day.py`: 1 passed. `pytest tests/unit`: 53 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-07.
  - Result: nothing to tidy; `_in_force` is one set comprehension, which refunds and reversals extend in 5.4 and 5.7.
    `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 53 passed, coverage 97%.

### Cycle 5.3 — a fee counts in the closings after it

- [x] [AI] RED: write `test_amb_011_a_fee_counts_in_the_closings_after_it` in `tests/unit/test_end_of_day.py`, with the
      smallest stub it imports, and run it; it fails on its assertion because step 1 reads each day's closing before
      firing any fee, so a Day 1 fee that takes Day 2 from 10.00 to −15.00 leaves Day 2 uncharged. Command:
      `pytest tests/unit/test_end_of_day.py`. Proof: the failure message, recorded here. Acceptance: AC-07.
  - Done 05:19. E1 debits 20.00 value-dated Day 1 and E2 credits 30.00 on Day 2, so Day 1 closes at −20.00 and Day 2 at
    10.00 before any fee. No stub was needed.
  - `pytest tests/unit/test_end_of_day.py`: 1 failed, 1 passed, on its assertion:
    `assert ['FEE-001-D1@D2'] == ['FEE-001-D1@...EE-001-D2@D2']`, `Right contains one more item: 'FEE-001-D2@D2'`. Step
    1 read every closing before firing, so the Day 1 fee left Day 2 uncharged.
- [x] [AI] GREEN: Read each closing in step 1 from the log as it grows, so a fee fired for an earlier day counts in the
      days after it. Command: `pytest tests/unit/test_end_of_day.py`, then `pytest tests/unit`. Proof: both passing
      runs, recorded here. Acceptance: AC-07.
  - Done 05:19. `close_day` runs `_fee_step` per account, which walks the days in order and appends each fee before
    reading the next closing; `_negative` dispatches to the generic `_below_zero`.
  - `pytest tests/unit/test_end_of_day.py`: 2 passed. `pytest tests/unit`: 54 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-07.
  - Result: nothing to tidy; the green replaced the list-building helpers with the single walk.
    `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 54 passed, coverage 97%.

### Cycle 5.4 — C6: E9 restores Days 2 to 4 and refunds the fees

- [x] [AI] RED: write `test_c6_e9_restores_days_2_to_4_and_refunds_the_fees` in `tests/unit/test_criteria.py`, with the
      smallest stub it imports, and run it; it fails on its assertion because no refund fires once the days are
      non-negative. Command: `pytest tests/unit/test_criteria.py`. Proof: the failure message, recorded here.
      Acceptance: AC-11.
  - Done 05:19. Stubs: `FeeRefund(id, account, value_day, fee, amount)` in `events.py`; `refund_markers` in
    `tests/support/streams.py`.
  - `pytest tests/unit/test_criteria.py`: 1 failed, 7 passed, on its assertion:
    `assert [] == ['REFUND-001-...ND-001-D5@D6']`, `Right contains 3 more items`. No refund fired once the days were
    non-negative.
- [x] [AI] GREEN: Fire `FeeRefund` for a fee in force whose day closes at or above zero. Command:
      `pytest tests/unit/test_criteria.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-11.
  - Done 05:20. `_fee_step` refunds the fee in force for a day that closes at or above zero, value-dated today, naming
    the fee and its amount; `_in_force` maps each day to its fee until a refund names it. `FeeRefund` joins `FiredEvent`
    and credits in `balances._moved`. The first run failed with `NameError` on two missed imports, which does not count;
    fixed, then:
  - `pytest tests/unit/test_criteria.py`: 8 passed. `pytest tests/unit`: 55 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-11.
  - Result: nothing to tidy in the code; a `local-tmp/addimport.py` helper now adds import names, since `ruff format`
    wraps long imports and plain string edits missed them. `npx nx run account-ledger-cli:test:quick`: pyright 0 errors,
    ruff all checks passed, 55 passed, coverage 97%.

### Cycle 5.5 — a BHD account is charged BHD 2.560

- [ ] [AI] RED: write `test_amb_027_a_bhd_account_is_charged_bhd_2_560` in `tests/unit/test_end_of_day.py`, with the
      smallest stub it imports, and run it; it is expected to pass on arrival, since step 1 takes `overdraft_fee` in the
      account's own currency type; its red is the mutation proof that making `overdraft_fee` return the AED figure's
      digits for BHD charges BHD 25.000. Command: `pytest tests/unit/test_end_of_day.py`. Proof: the failure message,
      recorded here. Acceptance: AC-22.
  - Disposition: passes on arrival (3 passed), since step 1 takes `overdraft_fee_of` in the account's own currency.
    Mutation: making `overdraft_fee` return the AED figure's digits for BHD made the test fail on its assertion:
    `At index 0 diff: Amount(money=Bhd(value=Decimal('25.000'))) != Amount(money=Bhd(value=Decimal('2.560')))`. Restored
    from a copy, 3 passed.
- [x] [AI] GREEN: No production change is expected; any gap the red shows is closed here. Command:
      `pytest tests/unit/test_end_of_day.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-22.
  - Result: no production change; passes on arrival, recorded in the Execution Record.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-22.
  - Result: nothing to tidy. `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 56
    passed, coverage 97%.

### Cycle 5.6 — a settlement above its hold debits in full

- [ ] [AI] RED: write `test_amb_030_a_settlement_above_its_hold_debits_in_full` in `tests/unit/test_end_of_day.py`, with
      the smallest stub it imports, and run it; it is expected to pass on arrival, since Cycle 4.9's `Captured` effect
      debits the settlement's own amount; its red is the mutation proof that capping the debit at the hold leaves the
      day non-negative and fires no fee. Command: `pytest tests/unit/test_end_of_day.py`. Proof: the failure message,
      recorded here. Acceptance: AC-20.
  - Disposition: passes on arrival (4 passed), since a settlement debits its own amount in `balances._moved`. Mutation:
    capping the settlement debit at its authorization's amount left Day 2 at 0.00, and the test failed on its assertion:
    `assert [] == ['FEE-001-D2@D2']`. Restored from a copy, 4 passed.
- [x] [AI] GREEN: No production change is expected; any gap the red shows is closed here. Command:
      `pytest tests/unit/test_end_of_day.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-20.
  - Result: no production change; passes on arrival, recorded in the Execution Record.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-20.
  - Result: nothing to tidy. `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 57
    passed, coverage 97%.

### Cycle 5.7 — a reversed fee on a negative day is charged again

- [x] [AI] RED: write `test_amb_035_a_fee_reversed_on_a_negative_day_is_charged_again` in
      `tests/unit/test_end_of_day.py`, with the smallest stub it imports, and run it; it fails on its assertion because
      the reversed fee still counts as in force, so Day 1 is not charged again. Command:
      `pytest tests/unit/test_end_of_day.py`. Proof: the failure message, recorded here. Acceptance: AC-31.
  - Done 05:22. No stub was needed.
  - `pytest tests/unit/test_end_of_day.py`: 1 failed, 4 passed, on its assertion:
    `At index 1 diff: 'FEE-001-D2@D2' != 'FEE-001-D1@D2'`. The reversed fee still counted as in force, so Day 1 was not
    charged again.
- [x] [AI] GREEN: Take a reversed fee out of force in step 1. Command: `pytest tests/unit/test_end_of_day.py`, then
      `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance: AC-31.
  - Done 05:22. `_in_force` drops a fee that an accepted reversal names, so step 1 judges its day again and charges it
    under a marker for today.
  - `pytest tests/unit/test_end_of_day.py`: 5 passed. `pytest tests/unit`: 58 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-31.
  - Done 05:22. The set comprehension over the fees in force became a direct lookup of the reversed fee's day.
  - `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 58 passed, coverage 97%.

### Cycle 5.8 — interest accrues on a positive closing

- [x] [AI] RED: write `test_amb_005_interest_accrues_on_a_positive_closing` in `tests/unit/test_end_of_day.py`, with the
      smallest stub it imports, and run it; it fails on its assertion because no interest event fires. Command:
      `pytest tests/unit/test_end_of_day.py`. Proof: the failure message, recorded here. Acceptance: AC-13.
  - Done 05:23. Stub: `interest_amounts` returning `[]` in `tests/support/streams.py`.
  - `pytest tests/unit/test_end_of_day.py`: 1 failed, 5 passed, on its assertion:
    `assert [] == [('INT-001-D1...mal('0.40')))]`, `Right contains one more item`. No interest event fired.
- [x] [AI] GREEN: Write step 2's accrual for today, only on a base above zero, and add `interest_amounts` to
      `tests/support/streams.py`. Command: `pytest tests/unit/test_end_of_day.py`, then `pytest tests/unit`. Proof: both
      passing runs, recorded here. Acceptance: AC-13.
  - Done 05:24. `events.py`: `InterestAccrual(id, account, value_day, amount)`, whose constructor refuses an ID for
    another day, joins `FiredEvent`, and `balances._moved` gives it no ledger effect (AMB-007). `close_day` runs
    `_interest_step` after the fees: `daily_interest` of today's closing, turned into an amount by the new
    run-time-currency `money.amount_of`, fires an accrual unless it is `NotPositive`. `interest_amounts` reads each
    interest event's marker and amount.
  - `pytest tests/unit/test_end_of_day.py`: 6 passed. `pytest tests/unit`: 59 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-13.
  - Done 05:24. The new docstring was wrapped under ruff's 120 columns; nothing else to tidy.
  - `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 59 passed, coverage 97%.

### Cycle 5.9 — a changed closing adjusts its interest

- [x] [AI] RED: write `test_amb_005_a_changed_closing_adjusts_its_interest` in `tests/unit/test_end_of_day.py`, with the
      smallest stub it imports, and run it; it fails on its assertion because a backdated debit leaves Day 1's accrual
      unchanged. Command: `pytest tests/unit/test_end_of_day.py`. Proof: the failure message, recorded here. Acceptance:
      AC-11, AC-13.
  - Done 05:25. E2 debits 500.00 on Day 2 value-dated Day 1, halving Day 1's closing. No stub was needed.
  - `pytest tests/unit/test_end_of_day.py`: 1 failed, 6 passed, on its assertion:
    `At index 1 diff: ('INT-001-D2@D2', Aed(value=Decimal('0.20'))) != ('INT-001-D1@D2', Aed(value=Decimal('-0.20')))`.
    The backdated debit left Day 1's accrual unchanged.
- [x] [AI] GREEN: Fire adjustments for earlier days in step 2, `UP` or `DOWN`, as target minus what was fired. Command:
      `pytest tests/unit/test_end_of_day.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-11, AC-13.
  - Done 05:25. `money.Direction` (UP, DOWN) and `events.InterestAdjustment`, whose constructor refuses an ID for its
    own day, join the model; `balances.interest_fired` nets an account's interest events for a day. Step 2 walks every
    day so far and fires the target minus what was fired: an accrual for today, or an adjustment for an earlier day,
    `UP` or `DOWN`, value-dated today. `interest_amounts` signs an adjustment by its direction.
  - `pytest tests/unit/test_end_of_day.py`: 7 passed. `pytest tests/unit`: 60 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-11, AC-13.
  - Result: nothing to tidy; the test reader signs interest itself rather than reuse production code.
    `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 60 passed, coverage 97%.

### Cycle 5.10 — C8: capitalization is the sum of the interest events

- [x] [AI] RED: write `test_c8_capitalization_equals_the_sum_of_interest_events` in `tests/unit/test_criteria.py`, with
      the smallest stub it imports, and run it; it fails on its assertion because no capitalization fires, so no
      CAP-001@D6 of AED 0.76 or CAP-002@D6 of BHD 0.008 exists. Command: `pytest tests/unit/test_criteria.py`. Proof:
      the failure message, recorded here. Acceptance: AC-13.
  - Done 05:26. Stub: `capitalization_amounts` returning `[]` in `tests/support/streams.py`.
  - `pytest tests/unit/test_criteria.py`: 1 failed, 8 passed, on its assertion:
    `assert [] == [('CAP-001@D6...al('0.008')))]`, `Right contains 2 more items`. No capitalization fired.
- [x] [AI] GREEN: Write step 3 in `end_of_day.py` from `balances.accrued`, on the configured days. Command:
      `pytest tests/unit/test_criteria.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-13.
  - Done 05:26. `events.Capitalization` joins `FiredEvent` and credits in `balances._moved`; `balances.accrued` nets the
    account's interest events less its capitalizations. On a day in `config.capitalization_days`, step 3 credits each
    account's accrued interest when above zero, value-dated today. `capitalization_amounts` reads each marker and
    amount.
  - `pytest tests/unit/test_criteria.py`: 9 passed, CAP-001@D6 0.76 and CAP-002@D6 0.008, each equal to its interest
    events' sum. `pytest tests/unit`: 61 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-13.
  - Done 05:26. `accrued` and `interest_fired` share `_signed_interest`, which signs an adjustment by its direction.
  - `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 61 passed, coverage 97%.

### Cycle 5.11 — C6: Day 6 closes at 285.76

- [ ] [AI] RED: write `test_c6_day_6_closes_at_285_76_not_285_79` in `tests/unit/test_criteria.py`, with the smallest
      stub it imports, and run it; it is expected to pass on arrival once 5.10 is green; its red is the mutation proof
      that removing step 3 leaves Day 6 at 285.00. Command: `pytest tests/unit/test_criteria.py`. Proof: the failure
      message, recorded here. Acceptance: AC-11.
  - Disposition: passes on arrival (10 passed), since 5.10 capitalizes 0.76 on Day 6, and Day 5 closes at 210.00.
    Mutation: disabling step 3 made the test fail on its assertion:
    `assert Aed(value=Decimal('285.00')) == Aed(value=Decimal('285.76'))`. Restored from a copy, 10 passed.
- [x] [AI] GREEN: No production change is expected; any gap the red shows is closed here. Command:
      `pytest tests/unit/test_criteria.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-11.
  - Result: no production change; passes on arrival, recorded in the Execution Record.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-11.
  - Result: nothing to tidy. `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 62
    passed, coverage 97%.

### Cycle 5.12 — a day's interest never counts its own capitalization

- [x] [AI] RED: write `test_amb_023_a_days_interest_never_counts_its_own_capitalization` in
      `tests/unit/test_end_of_day.py`, with the smallest stub it imports, and run it; it fails on its assertion because
      re-evaluating a capitalization day fires an adjustment on AED 50,000.00's capitalized 20.00. Command:
      `pytest tests/unit/test_end_of_day.py`. Proof: the failure message, recorded here. Acceptance: AC-13.
  - Done 05:27. A config replaced from `CHALLENGE` with a window of Days 1–2 and capitalization on Day 1. No stub was
    needed.
  - `pytest tests/unit/test_end_of_day.py`: 1 failed, 7 passed, on its assertion:
    `At index 1 diff: ('INT-001-D1@D2', Aed(value=Decimal('0.01'))) != ('INT-001-D2@D2', Aed(value=Decimal('20.01')))`.
    Re-evaluating Day 1 read its capitalized 20.00 and adjusted up.
- [x] [AI] GREEN: Compute step 2's target from `balances.interest_base`. Command:
      `pytest tests/unit/test_end_of_day.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-13.
  - Done 05:27. `balances.interest_base` is the closing less any capitalization value-dated that day, and step 2's
    target is `daily_interest` of it.
  - `pytest tests/unit/test_end_of_day.py`: 8 passed. `pytest tests/unit`: 63 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-13.
  - Result: nothing to tidy. `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 63
    passed, coverage 97%.

### Cycle 5.13 — a day restates each earlier closing it changed

- [x] [AI] RED: write `test_amb_022_a_day_restates_each_earlier_closing_it_changed` in `tests/unit/test_report.py`, with
      the smallest stub it imports, and run it; it fails on its assertion because the report lists no restated closing.
      Command: `pytest tests/unit/test_report.py`. Proof: the failure message, recorded here. Acceptance: AC-11.
  - Done 05:28. New file `tests/unit/test_report.py`. Stubs: `Restatement(day, closing)` in `report.py`, and a
    `restated` field on `DayReport` defaulting to `()`.
  - `pytest tests/unit/test_report.py`: 1 failed, on its assertion: `assert () == (Restatement(...002'): None}))`,
    `Right contains 3 more items`. The report listed no restated closing.
- [x] [AI] GREEN: Compute restated closings against the last reported ones. Command: `pytest tests/unit/test_report.py`,
      then `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance: AC-11.
  - Done 05:28. `report` takes the closings last reported for each day and restates each earlier day whose closing now
    differs, with `None` for an unchanged account; `reported_after` folds a report's own closings and restatements into
    that record, and `replay` threads it day by day.
  - `pytest tests/unit/test_report.py`: 1 passed, including Day 6's restatement of Day 5 to 210.00 and BHD 10.000.
    `pytest tests/unit`: 64 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-11.
  - Result: nothing to tidy. `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 64
    passed, coverage 97%.

### Cycle 5.14 — every known authorization is listed with its state

- [x] [AI] RED: write `test_amb_019_every_known_authorization_is_listed_with_its_state` in `tests/unit/test_report.py`,
      with the smallest stub it imports, and run it; it fails on its assertion because the report lists no
      authorization. Command: `pytest tests/unit/test_report.py`. Proof: the failure message, recorded here. Acceptance:
      AC-10.
  - Done 05:29. Stub: an `authorizations` field on `DayReport` defaulting to `()`.
  - `pytest tests/unit/test_report.py`: 1 failed, 1 passed, on its assertion:
    `assert [] == [(Authorizati...'200.00')))))]`,
    `Right contains one more item: (AuthorizationId(value='Auth-A'), Approved(...))`. The report listed no
    authorization.
- [x] [AI] GREEN: Add authorization states to `DayReport`. Command: `pytest tests/unit/test_report.py`, then
      `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance: AC-10.
  - Done 05:29. `DayReport.authorizations` holds `records(log)` at the day's close, in the order first seen; the test's
    helper is typed `AuthorizationState`.
  - `pytest tests/unit/test_report.py`: 2 passed. `pytest tests/unit`: 65 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-10.
  - Result: nothing to tidy. `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 65
    passed, coverage 97%.

### Cycle 5.15 — a rejected event prints as that day's error

- [x] [AI] RED: write `test_amb_014_a_rejected_event_prints_as_that_days_error` in `tests/unit/test_report.py`, with the
      smallest stub it imports, and run it; it fails on its assertion because the report's errors are always none.
      Command: `pytest tests/unit/test_report.py`. Proof: the failure message, recorded here. Acceptance: AC-15 to
      AC-17, AC-32, AC-35.
  - Done 05:30. Parametrized with one case per `Rejection`: IdReused, AlreadyReversed, ReversesAReversal, UnknownTarget,
    MovedNoMoney, and AlreadyUndone. Stub: an `errors` field on `DayReport` defaulting to an empty mapping.
  - `pytest tests/unit/test_report.py`: 6 failed, 2 passed, each on its assertion:
    `assert mappingproxy({}) == {AccountId(va...ACC-002'): ()}`. The report's errors were always none.
- [x] [AI] GREEN: Add `Rejected` entries to the errors, by account, with the texts tech-docs 001 fixes; the test has one
      case per rejection. Command: `pytest tests/unit/test_report.py`, then `pytest tests/unit`. Proof: both passing
      runs, recorded here. Acceptance: AC-15 to AC-17, AC-32, AC-35.
  - Done 05:30. `DayReport.errors` maps each account to the texts of the `Rejected` entries processed that day on it, in
    log order; `report.refusal` renders each with tech-docs 001's text, one `match` over `Rejection` ending in
    `assert_never`.
  - `pytest tests/unit/test_report.py`: 8 passed. `pytest tests/unit`: 71 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-15 to AC-17,
      AC-32, AC-35.
  - Result: nothing to tidy; `refusal` stays public for the text renderer of Phase 6.
    `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 71 passed, coverage 97%.

### Cycle 5.16 — a refunded fee cannot be reversed

- [x] [AI] RED: write `test_amb_035_money_already_undone_cannot_be_undone_again` in `tests/unit/test_processing.py`,
      with the smallest stub it imports, and run it; it fails on its assertion because its new refunded-fee case, a
      reversal of FEE-001-D2@D5 after REFUND-001-D2@D6, is accepted and credits 25.00 again. Command:
      `pytest tests/unit/test_processing.py`. Proof: the failure message, recorded here. Acceptance: AC-35.
  - Done 05:31. The test's cases became a table, `part`, `whole`, and the new `refunded-fee`: the brief's stream plus
    E12 reversing FEE-001-D2@D5 on Day 7, in a week-long window. Each case now proves "moves no balance" against the
    same stream without E12. Beside it, `test_amb_035_a_reversed_refund_puts_its_fee_back_in_force` in
    `tests/unit/test_end_of_day.py` covers the GREEN's second half, which no planned test reached. No stub was needed.
  - `pytest tests/unit/test_processing.py tests/unit/test_end_of_day.py`: 2 failed, 19 passed, each on its assertion.
    `[refunded-fee]`: at index 0, `Accepted(event=Reversal(..., reverses=FeeId(...)))` was not
    `Rejected(..., reason=AlreadyUndone(...))`, so the reversal would credit 25.00 again. The reversed-refund test:
    `assert ['REFUND-001-...ND-001-D5@D6'] == ['REFUND-001-...ND-001-D2@D7']`, so no fee came back in force.
- [x] [AI] GREEN: Treat a refund as undoing its fee in the `AlreadyUndone` check, and a reversed refund as putting the
      fee back in force in step 1. Command: `pytest tests/unit/test_processing.py`, then `pytest tests/unit`. Proof:
      both passing runs, recorded here. Acceptance: AC-35.
  - Done 05:32. `processing._undone_by` refuses a reversal of a fee whose refund is in effect, naming the fee and the
    refund, through `_refund_of`, which skips a refund itself reversed. `end_of_day._in_force` remembers each refunded
    fee and puts it back in force when an accepted reversal names its refund.
  - `pytest tests/unit/test_processing.py tests/unit/test_end_of_day.py`: 21 passed. `pytest tests/unit`: 73 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-35.
  - Result: nothing to tidy. `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 73
    passed, coverage 97%.

### Cycle 5.17 — a step that fires nothing reports its row

- [x] [AI] RED: write `test_amb_033_a_step_that_fires_nothing_reports_its_row` in `tests/unit/test_report.py`, with the
      smallest stub it imports, and run it; it fails on its assertion because the end-of-day rows omit the empty steps.
      Command: `pytest tests/unit/test_report.py`. Proof: the failure message, recorded here. Acceptance: AC-01.
  - Done 05:33. Stubs in `report.py`: the `Step` and `Note` enums, `Fired(step, event)`,
    `NothingFired(step, accounts, note)`, and an `end_of_day` field on `DayReport` defaulting to `()`.
  - `pytest tests/unit/test_report.py`: 1 failed, 8 passed, on its assertion:
    `assert [] == [(1, 'no fee ...('ACC-002',))]`, `Right contains 3 more items`. The report carried no end-of-day row
    at all, the empty steps included.
- [x] [AI] GREEN: Add the rows tech-docs 002 lists for a step with no event, `no interest capitalized` included.
      Command: `pytest tests/unit/test_report.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-01.
  - Done 05:33. `DayReport.end_of_day` lists each step's fired events in log order. Step 1 adds one row for every
    account, "no fee assessed or refunded" or, after refunds only, "no new fee assessed"; step 2 adds "no interest
    accrued" for an account with no accrual today; on a capitalization day, step 3 adds "no interest capitalized" for an
    account paid nothing. Day 0, never closed, has no rows.
  - `pytest tests/unit/test_report.py`: 9 passed. `pytest tests/unit`: 74 passed.
- [x] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-01.
  - Done 05:34. `_end_of_day` split into `_fee_rows`, `_interest_rows`, and `_capitalization_rows`, which take a
    `Sequence[LoggedEvent]`, since pyright holds `list` invariant.
  - `npx nx run account-ledger-cli:test:quick`: pyright 0 errors, ruff all checks passed, 74 passed, coverage 97%.
- [x] [AI] Add `end_of_day` to `architecture.md`'s components. Proof: the module exists. Acceptance: AC-26.
  - Done 05:35. The ledger-core diagram gains `end_of_day` between `replay` and the log, closing each day with fees,
    interest, then capitalization; the component table adds its row and updates `events`, `balances`, and `report`.
  - The module exists: `ls src/account_ledger/end_of_day.py`.

### Phase 5 Gate

- [x] [AI] Run every gate command below against the phase's combined state; each exits 0. Proof: each command and its
      exit status, recorded here. Acceptance: AC-06 to AC-20, AC-22, AC-31, AC-35. Commands:
  - `npx nx run account-ledger-cli:test:quick`
  - `npx nx run account-ledger-cli:test:integration`
  - `npx nx run account-ledger-cli:test:e2e`
  - `npm run -s check:hygiene`
  - `sh local-tmp/check-md.sh`
  - `./rhino md internal-link validate && ./rhino md heading-hierarchy validate && ./rhino md naming validate`
  - Done 05:37, each exiting 0: `test:quick` 0 (74 passed, coverage 97%); `test:integration` 0 (2 passed); `test:e2e` 0
    (1 passed); `npm run -s check:hygiene` 0; `sh local-tmp/check-md.sh` 0; `./rhino md internal-link validate` 0,
    `heading-hierarchy validate` 0, `naming validate` 0.
- [x] [AI] Add a new `WORKLOG.md` entry for the phase at the top, stamped with its real start and end `date` times.
      Path: `WORKLOG.md`. Proof: the entry. Acceptance: AC-24.
  - Done 05:37: the row `2026-09-25 05:14–05:37`, "Plan execution, Phase 5: fees, refunds, interest, capitalization, and
    the day report".
- [ ] [AI] Commit the phase as `feat(account-ledger-cli): close each day with fees, interest, and capitalization`, then
      push to `origin/main`; the pre-push hook runs every test layer. Command: `/usr/bin/git push origin main`. Proof:
      the commit hash and the pushed range, recorded here and in the Execution Record. Acceptance: AC-06 to AC-20,
      AC-22, AC-31, AC-35.

Pause safety: the phase leaves every criterion green and every day report complete as data. Re-verify with
`npx nx run account-ledger-cli:test:quick`.

## Phase 6 — The Report as Text and the Command Line

The renderer, the floor-tier shell, and the golden run ([input and output](tech-docs/003-input-output-and-cli.md)).

- [ ] [AI] RED, the phase's outer tests: write `test_the_brief_replay_prints_output_target` in
      `tests/e2e/test_program.py`, with `tests/support/output_target.py`, and beside it the error paths
      `test_a_missing_stream_file_exits_2`, `test_a_malformed_amount_names_its_line`,
      `test_an_unheld_account_names_its_line`, and `test_no_argument_prints_usage_and_exits_2`. Each fails on its
      assertion, since the program still prints the greeting and exits 0. Command: `pytest tests/e2e`. Proof: each
      failure's head, recorded here. Acceptance: AC-01 to AC-04.

### Cycle 6.1 — a day opens with its banner and its blocks

- [ ] [AI] RED: write `test_a_day_opens_with_its_banner_and_its_blocks` in `tests/unit/test_render.py`, with the
      smallest stub it imports, and run it; it fails on its assertion because the stub renders nothing. Command:
      `pytest tests/unit/test_render.py`. Proof: the failure message, recorded here. Acceptance: AC-01.
- [ ] [AI] GREEN: Write `render.py`'s banner, block titles, and blank-line layout. Command:
      `pytest tests/unit/test_render.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance:
      AC-01.
- [ ] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-01.

### Cycle 6.2 — an empty block prints none

- [ ] [AI] RED: write `test_an_empty_block_prints_none` in `tests/unit/test_render.py`, with the smallest stub it
      imports, and run it; it fails on its assertion because an empty block prints an empty table. Command:
      `pytest tests/unit/test_render.py`. Proof: the failure message, recorded here. Acceptance: AC-01.
- [ ] [AI] GREEN: Print two spaces and `none` for a block with no rows. Command: `pytest tests/unit/test_render.py`,
      then `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance: AC-01.
- [ ] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-01.

### Cycle 6.3 — a table is a box as wide as its cells

- [ ] [AI] RED: write `test_a_table_is_a_box_as_wide_as_its_cells` in `tests/unit/test_render.py`, with the smallest
      stub it imports, and run it; it fails on its assertion because cells are not padded to their column. Command:
      `pytest tests/unit/test_render.py`. Proof: the failure message, recorded here. Acceptance: AC-01.
- [ ] [AI] GREEN: Draw the borders and pad every column, left-aligned, to its widest cell. Command:
      `pytest tests/unit/test_render.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance:
      AC-01.
- [ ] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-01.

### Cycle 6.4 — amounts print in their currency's format

- [ ] [AI] RED: write `test_amounts_print_in_their_currencys_format` in `tests/unit/test_render.py`, with the smallest
      stub it imports, and run it; it fails on its assertion because `-370.00` prints with a hyphen and `1200.00` with
      no comma. Command: `pytest tests/unit/test_render.py`. Proof: the failure message, recorded here. Acceptance:
      AC-01.
- [ ] [AI] GREEN: Format places, thousands, and `−` from `money.digits`, a `DOWN` adjustment taking the minus. Command:
      `pytest tests/unit/test_render.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance:
      AC-01.
- [ ] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-01.

### Cycle 6.5 — each row prints its type and detail

- [ ] [AI] RED: write `test_each_row_prints_its_type_and_detail` in `tests/unit/test_render.py`, with the smallest stub
      it imports, and run it; it fails on its assertion because rows print the class names of their events. Command:
      `pytest tests/unit/test_render.py`. Proof: the failure message, recorded here. Acceptance: AC-01.
- [ ] [AI] GREEN: Render the Type strings and Detail patterns tech-docs 003 lists. Command:
      `pytest tests/unit/test_render.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance:
      AC-01.
- [ ] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-01.

### Cycle 6.6 — instalment counts print as words

- [ ] [AI] RED: write `test_instalment_counts_print_as_words` in `tests/unit/test_render.py`, with the smallest stub it
      imports, and run it; it fails on its assertion because the count prints as `3`. Command:
      `pytest tests/unit/test_render.py`. Proof: the failure message, recorded here. Acceptance: AC-01.
- [ ] [AI] GREEN: Spell counts from two to ten. Command: `pytest tests/unit/test_render.py`, then `pytest tests/unit`.
      Proof: both passing runs, recorded here. Acceptance: AC-01.
- [ ] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-01.

### Cycle 6.7 — authorization states print as OUTPUT_TARGET shows

- [ ] [AI] RED: write `test_authorization_states_print_as_output_target_shows` in `tests/unit/test_render.py`, with the
      smallest stub it imports, and run it; it fails on its assertion because states print as class names. Command:
      `pytest tests/unit/test_render.py`. Proof: the failure message, recorded here. Acceptance: AC-01.
- [ ] [AI] GREEN: Render each state's text. Command: `pytest tests/unit/test_render.py`, then `pytest tests/unit`.
      Proof: both passing runs, recorded here. Acceptance: AC-01.
- [ ] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-01.

### Cycle 6.8 — capitalization names the days it accrued

- [ ] [AI] RED: write `test_capitalization_names_the_days_it_accrued` in `tests/unit/test_render.py`, with the smallest
      stub it imports, and run it; it fails on its assertion because the detail omits the days. Command:
      `pytest tests/unit/test_render.py`. Proof: the failure message, recorded here. Acceptance: AC-01.
- [ ] [AI] GREEN: Render the day list rules tech-docs 003 fixes. Command: `pytest tests/unit/test_render.py`, then
      `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance: AC-01.
- [ ] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-01.

### Cycle 6.9 — the texts beyond OUTPUT_TARGET follow its patterns

- [ ] [AI] RED: write `test_the_texts_beyond_output_target_follow_its_patterns` in `tests/unit/test_render.py`, with the
      smallest stub it imports, and run it; it fails on its assertion because a duplicate and a force-post against a
      known hold print no detail. Command: `pytest tests/unit/test_render.py`. Proof: the failure message, recorded
      here. Acceptance: AC-01.
- [ ] [AI] GREEN: Render the D22 texts in tech-docs 003. Command: `pytest tests/unit/test_render.py`, then
      `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance: AC-01.
- [ ] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-01.

### Cycle 6.10 — a stream file prints its report and exits 0

- [ ] [AI] RED: write `test_a_stream_file_prints_its_report_and_exits_0` in `tests/unit/test_cli.py`, with the smallest
      stub it imports, and run it; it fails on its assertion because `run` still prints the greeting. Command:
      `pytest tests/unit/test_cli.py`. Proof: the failure message, recorded here. Acceptance: AC-01.
- [ ] [AI] GREEN: Rewrite `cli.run(argv, read_text, out, err)` to read, parse, replay, and render; delete `greeting.py`
      and the greeting tests. Command: `pytest tests/unit/test_cli.py`, then `pytest tests/unit`. Proof: both passing
      runs, recorded here. Acceptance: AC-01.
- [ ] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-01.

### Cycle 6.11 — no argument is a usage error

- [ ] [AI] RED: write `test_no_argument_is_a_usage_error_exiting_2` in `tests/unit/test_cli.py`, with the smallest stub
      it imports, and run it; it fails on its assertion because `run` with no argument exits 0. Command:
      `pytest tests/unit/test_cli.py`. Proof: the failure message, recorded here. Acceptance: AC-04.
- [ ] [AI] GREEN: Print the usage line to `err` and return 2. Command: `pytest tests/unit/test_cli.py`, then
      `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance: AC-04.
- [ ] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-04.

### Cycle 6.12 — an unreadable file exits 2

- [ ] [AI] RED: write `test_an_unreadable_file_exits_2` in `tests/unit/test_cli.py`, with the smallest stub it imports,
      and run it; it fails on its assertion because the reader's error escapes `run`. Command:
      `pytest tests/unit/test_cli.py`. Proof: the failure message, recorded here. Acceptance: AC-02.
- [ ] [AI] GREEN: Catch the read failure in `run` and print `error: cannot read PATH: REASON`. Command:
      `pytest tests/unit/test_cli.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance:
      AC-02.
- [ ] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-02.

### Cycle 6.13 — a malformed stream exits 2

- [ ] [AI] RED: write `test_a_malformed_stream_exits_2_naming_the_line` in `tests/unit/test_cli.py`, with the smallest
      stub it imports, and run it; it fails on its assertion because the `StreamError` is rendered as a report. Command:
      `pytest tests/unit/test_cli.py`. Proof: the failure message, recorded here. Acceptance: AC-03.
- [ ] [AI] GREEN: Print the error and return 2. Command: `pytest tests/unit/test_cli.py`, then `pytest tests/unit`.
      Proof: both passing runs, recorded here. Acceptance: AC-03.
- [ ] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-03.

### Cycle 6.14 — an internal failure exits 2

- [ ] [AI] RED: write `test_an_internal_failure_exits_2_without_a_traceback` in `tests/unit/test_cli.py`, with the
      smallest stub it imports, and run it; it fails on its assertion because an exception from the core escapes `run`.
      Command: `pytest tests/unit/test_cli.py`. Proof: the failure message, recorded here. Acceptance: AC-36.
- [ ] [AI] GREEN: Catch it in `run`, print its type, and return 2. Command: `pytest tests/unit/test_cli.py`, then
      `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance: AC-36.
- [ ] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-36.

### Cycle 6.15 — a closed pipe exits 141

- [ ] [AI] RED: write `test_a_closed_pipe_exits_141_quietly` in `tests/unit/test_cli.py`, with the smallest stub it
      imports, and run it; it fails on its assertion because `BrokenPipeError` escapes `run`. Command:
      `pytest tests/unit/test_cli.py`. Proof: the failure message, recorded here. Acceptance: AC-36.
- [ ] [AI] GREEN: Catch it in `run` and return 141. Command: `pytest tests/unit/test_cli.py`, then `pytest tests/unit`.
      Proof: both passing runs, recorded here. Acceptance: AC-36.
- [ ] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-36.

### Cycle 6.16 — an interrupt exits 130

- [ ] [AI] RED: write `test_an_interrupt_exits_130` in `tests/unit/test_cli.py`, with the smallest stub it imports, and
      run it; it fails on its assertion because `KeyboardInterrupt` escapes `run`. Command:
      `pytest tests/unit/test_cli.py`. Proof: the failure message, recorded here. Acceptance: AC-36.
- [ ] [AI] GREEN: Catch it in `run` and return 130. Command: `pytest tests/unit/test_cli.py`, then `pytest tests/unit`.
      Proof: both passing runs, recorded here. Acceptance: AC-36.
- [ ] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-36.

### Cycle 6.17 — main reads a real file and a missing one

- [ ] [AI] RED: write `test_main_reads_a_real_file_and_reports_a_missing_one` in `tests/integration/test_main.py`, with
      the smallest stub it imports, and run it; it fails on its assertion because `main` does not yet bind a UTF-8
      reader and the real streams. Command: `pytest tests/integration/test_main.py`. Proof: the failure message,
      recorded here. Acceptance: AC-02.
- [ ] [AI] GREEN: Bind `main` to `sys.argv[1:]`, a UTF-8 reader, and UTF-8 standard streams, pointing standard output at
      the null device after a closed pipe. Command: `pytest tests/integration/test_main.py`, then `pytest tests/unit`.
      Proof: both passing runs, recorded here. Acceptance: AC-02.
- [ ] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-02.
- [ ] [AI] Prove the integration reader can fail: stub the parser to succeed, point `main` at a file missing a column,
      watch `test_main_reads_a_real_file_and_reports_a_missing_one`'s assertion on exit 2 fail, restore. Proof: the
      failing run's head. Acceptance: AC-02, AC-03.
- [ ] [AI] GREEN, the outer tests: the golden run and the four error paths pass in `tests/e2e/test_program.py`. Command:
      `pytest tests/e2e`. Proof: the passing run. Acceptance: AC-01 to AC-04.
- [ ] [AI] Prove the golden harness can fail: change one character of the expected text in the test's copy, run it,
      watch it fail with a diff naming the line, restore. Proof: the failing run's head. Acceptance: AC-01.
- [ ] [AI] Make `run` pass `streams/challenge.csv`, and list `{workspaceRoot}/OUTPUT_TARGET.md` among the test targets'
      inputs in `project.json`, beside the streams Cycle 3.24 listed. Commands: `npx nx run account-ledger-cli:run`
      prints the report, and `npx nx show projects --affected --files=OUTPUT_TARGET.md` lists `account-ledger-cli`.
      Proof: both outputs; if the second does not, recovery item RC4. Today no project is affected by
      `OUTPUT_TARGET.md`, which is what this item changes. Acceptance: AC-01.
- [ ] [AI] Add the sentence naming the stream files and `OUTPUT_TARGET.md` among the test targets' inputs to
      `repo-governance/development/workflow/nx-workspace-policy.md`, through a Rules Propagation record at
      `local-tmp/rules-propagation-nx-inputs.md`, now that the item above lists them. Proof: the record and the md
      gates. Acceptance: AC-28.
- [ ] [AI] Complete `architecture.md` as the C4 model tech-docs 006 states: context, containers, components with the
      shell, code, and the dynamic view of one day; drop the scaffold wording. Proof: every named module exists.
      Acceptance: AC-26.
- [ ] [AI] Rewrite `apps/account-ledger-cli/README.md`: layout, commands, the exit statuses, and the floor tier (D13).
      Proof: the md gates. Acceptance: AC-02 to AC-04, AC-29.

### Phase 6 Gate

- [ ] [AI] Run every gate command below against the phase's combined state; each exits 0. Proof: each command and its
      exit status, recorded here. Acceptance: AC-01 to AC-04, AC-26, AC-36. Commands:
  - `npx nx run account-ledger-cli:test:quick`
  - `npx nx run account-ledger-cli:test:integration`
  - `npx nx run account-ledger-cli:test:e2e`
  - `npm run -s check:hygiene`
  - `sh local-tmp/check-md.sh`
  - `./rhino md internal-link validate && ./rhino md heading-hierarchy validate && ./rhino md naming validate`
- [ ] [AI] Add a new `WORKLOG.md` entry for the phase at the top, stamped with its real start and end `date` times.
      Path: `WORKLOG.md`. Proof: the entry. Acceptance: AC-24.
- [ ] [AI] Commit the phase as `feat(account-ledger-cli): print the daily report from a stream file`, then push to
      `origin/main`; the pre-push hook runs every test layer. Command: `/usr/bin/git push origin main`. Proof: the
      commit hash and the pushed range, recorded here and in the Execution Record. Acceptance: AC-01 to AC-04, AC-26,
      AC-36.

Pause safety: the phase leaves a program that prints OUTPUT_TARGET exactly and honours the floor-tier contract.
Re-verify with `npx nx run account-ledger-cli:test:quick`.

## Phase 7 — The Known Weakness

The brief's one failing test (AMB-018, AMB-031, D6), as [testing strategy](tech-docs/004-testing-strategy.md) shows it.

- [ ] [AI] RED: write `test_known_weakness_an_unsettled_hold_never_lapses` in `tests/unit/test_known_weakness.py`, with
      `auth_a_never_settled()` in `tests/support/streams.py`, without its marker, and run it; it fails on its assertion,
      since Day 32 still holds AED 200.00. Command: `pytest tests/unit/test_known_weakness.py`. Proof: the failure.
      Acceptance: AC-23.
- [ ] [AI] Mark it `xfail(strict=True, reason=…)` with the inline annotation, citing Visa Business News AI13522.
      Command: `npx nx run account-ledger-cli:test:unit`. Proof: the run passes and reports `1 xfailed`. Acceptance:
      AC-23.
- [ ] [AI] Prove the marker is strict: make holds lapse after 30 days in the working tree, never committed, run the unit
      suite, watch `XPASS(strict)` fail it, restore. Command: `/usr/bin/git diff --stat -- apps/account-ledger-cli/src`
      prints nothing afterwards. Proof: the failing run's summary line. Acceptance: AC-23.
- [ ] [AI] Add two chosen constants to `NUMBERS.md`, each with its reason and why not half: the hold time frame, 30
      calendar days, cited from Visa Business News AI13522 (at 15, Visa would still honour a lodging or cruise
      authorization, so a lapse test would claim a weakness no network shows); and the replay length, Day 32, the first
      day after Auth-A's thirty (at Day 16 the hold is still legitimately active). Add a known-weakness section to the
      application README. Proof: the md gates. Acceptance: AC-23, AC-24.

### Phase 7 Gate

- [ ] [AI] Run every gate command below against the phase's combined state; each exits 0. Proof: each command and its
      exit status, recorded here. Acceptance: AC-23. Commands:
  - `npx nx run account-ledger-cli:test:quick`
  - `npx nx run account-ledger-cli:test:integration`
  - `npx nx run account-ledger-cli:test:e2e`
  - `npm run -s check:hygiene`
  - `sh local-tmp/check-md.sh`
  - `./rhino md internal-link validate && ./rhino md heading-hierarchy validate && ./rhino md naming validate`
- [ ] [AI] Add a new `WORKLOG.md` entry for the phase at the top, stamped with its real start and end `date` times.
      Path: `WORKLOG.md`. Proof: the entry. Acceptance: AC-24.
- [ ] [AI] Commit the phase as `test(account-ledger-cli): record that holds never expire as a strict expected failure`,
      then push to `origin/main`; the pre-push hook runs every test layer. Command: `/usr/bin/git push origin main`.
      Proof: the commit hash and the pushed range, recorded here and in the Execution Record. Acceptance: AC-23.

Pause safety: the phase leaves exactly one strict expected failure in a green suite. Re-verify with
`npx nx run account-ledger-cli:test:quick`.

## Phase 8 — Partial Capture, Bounded

AMB-013, built last (D3). The phase is a bounded checkpoint: each cycle gets at most two repair attempts after its first
GREEN attempt fails, and the attempts spent are recorded in the Execution Record. At the ceiling, or when the owner
calls time, recovery item RC2 fires.

### Cycle 8.1 — the stream carries a final marker

- [ ] [AI] RED: write `test_a_final_cell_other_than_yes_or_no_is_refused` in `tests/unit/test_stream_csv.py`, with the
      smallest stub it imports, and run it; it fails on its assertion because the header has eight columns and no
      `final` cell is read. Command: `pytest tests/unit/test_stream_csv.py`. Proof: the failure message, recorded here.
      Acceptance: AC-03, AC-05.
- [ ] [AI] GREEN: Add `final` to the header, read it into `Capture`, add the fault message, add a trailing empty cell to
      each row of `streams/challenge.csv`, and move `csv_text` and every fixture to nine columns. Command:
      `pytest tests/unit/test_stream_csv.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-03, AC-05.
- [ ] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-03, AC-05.

### Cycle 8.2 — a non-final settlement keeps the rest of the hold

- [ ] [AI] RED: write `test_amb_013_a_non_final_settlement_keeps_the_rest_of_the_hold` in
      `tests/unit/test_authorizations.py`, with the smallest stub it imports, and run it; it fails on its assertion
      because every settlement releases the whole hold. Command: `pytest tests/unit/test_authorizations.py`. Proof: the
      failure message, recorded here. Acceptance: AC-21.
- [ ] [AI] GREEN: Add `PartiallySettled`, `SettlePartial`, and their rows of the table, with a final settlement of the
      rest settling for the captures' sum. Command: `pytest tests/unit/test_authorizations.py`, then
      `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance: AC-21.
- [ ] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-21.

### Cycle 8.3 — a partial capture reaching the hold settles

- [ ] [AI] RED: write `test_amb_013_a_partial_capture_reaching_the_hold_settles` in `tests/unit/test_authorizations.py`,
      with the smallest stub it imports, and run it; it fails on its assertion because a partial settlement of the whole
      remaining hold builds a `PartiallySettled` with a zero hold, and `Amount.of` refuses it. Command:
      `pytest tests/unit/test_authorizations.py`. Proof: the failure message, recorded here. Acceptance: AC-21.
- [ ] [AI] GREEN: Add the guard `a >= h` rows, which go to `Settled`. Command:
      `pytest tests/unit/test_authorizations.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-21.
- [ ] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-21.

### Cycle 8.4 — every state and trigger follow the table

- [ ] [AI] RED: write `test_every_state_and_trigger_pair_follows_the_table` in `tests/unit/test_authorizations.py`, with
      the smallest stub it imports, and run it; it is expected to pass on arrival, since 4.9, 4.11, 8.2, and 8.3 built
      every row; its red is the mutation proof that swapping one row's result fails the walk. Command:
      `pytest tests/unit/test_authorizations.py`. Proof: the failure message, recorded here. Acceptance: AC-18, AC-19,
      AC-21.
- [ ] [AI] GREEN: No production change is expected; any gap the red shows is closed here. Command:
      `pytest tests/unit/test_authorizations.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here.
      Acceptance: AC-18, AC-19, AC-21.
- [ ] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-18, AC-19,
      AC-21.

### Cycle 8.5 — a partially settled authorization prints its remaining hold

- [ ] [AI] RED: write `test_a_partially_settled_authorization_prints_its_remaining_hold` in `tests/unit/test_render.py`,
      with the smallest stub it imports, and run it; it fails on its assertion because the state has no text. Command:
      `pytest tests/unit/test_render.py`. Proof: the failure message, recorded here. Acceptance: AC-21.
- [ ] [AI] GREEN: Render `Auth-A partially settled for 120.00, hold 80.00` and the partial settlement's Detail. Command:
      `pytest tests/unit/test_render.py`, then `pytest tests/unit`. Proof: both passing runs, recorded here. Acceptance:
      AC-21.
- [ ] [AI] REFACTOR: tidy the names and helpers the green added, adding no behaviour. Command:
      `npx nx run account-ledger-cli:test:quick`. Proof: the passing run, recorded here. Acceptance: AC-21.
- [ ] [AI] Update the state diagram in `architecture.md`. Proof: it matches `transition`. Acceptance: AC-26.

### Phase 8 Gate

- [ ] [AI] Run every gate command below against the phase's combined state; each exits 0. Proof: each command and its
      exit status, recorded here. Acceptance: AC-21. Commands:
  - `npx nx run account-ledger-cli:test:quick`
  - `npx nx run account-ledger-cli:test:integration`
  - `npx nx run account-ledger-cli:test:e2e`
  - `npm run -s check:hygiene`
  - `sh local-tmp/check-md.sh`
  - `./rhino md internal-link validate && ./rhino md heading-hierarchy validate && ./rhino md naming validate`
- [ ] [AI] Add a new `WORKLOG.md` entry for the phase at the top, stamped with its real start and end `date` times.
      Path: `WORKLOG.md`. Proof: the entry. Acceptance: AC-24.
- [ ] [AI] Commit the phase as `feat(account-ledger-cli): keep the rest of a hold after a partial capture`, then push to
      `origin/main`; the pre-push hook runs every test layer. Command: `/usr/bin/git push origin main`. Proof: the
      commit hash and the pushed range, recorded here and in the Execution Record. Acceptance: AC-21.

Pause safety: the phase leaves partial capture proven, or RC2 applied and recorded. Re-verify with
`npx nx run account-ledger-cli:test:quick`.

## Phase 9 — The Assessment Docs Name Their Tests

Docs Propagation of Phases 3 to 8 into the assessment docs, and rule change R4 (D12b). No figure changes.

- [ ] [AI] Give each criterion bullet in `MOVEMENT.md` its test names, and drop its sentence linking
      `ACCEPTANCE_CRITERIA.feature`. Proof: the name check below. Acceptance: AC-24.
- [ ] [AI] Name, in each refused criterion's paragraph of `REJECTED.md`, the tests that prove it: one for C2, C4, C7,
      and C8, and two each for C5 and C6. Proof: the name check. Acceptance: AC-24.
- [ ] [AI] Close the Resolution part of each `AMBIGUITIES.md` entry with a sentence naming the tests tech-docs 004's
      table maps to it, every entry but AMB-032, so each entry keeps its six parts, and replace its introduction's "the
      ledger code, which does not exist yet" with the suite that now re-derives every figure. Proof: the name check.
      Acceptance: AC-24.
- [ ] [AI] Delete `ACCEPTANCE_CRITERIA.feature`; apply R4 to `repo-governance/conventions/structure/assessment-docs.md`
      through Rules Propagation; drop its row from the root `README.md` and its line from this plan's README. Command:
      the first below. Proof: the output, each hit being `WORKLOG.md`, REJECTED's abandoned approach, or this plan's own
      documents. Acceptance: AC-24.
- [ ] [AI] Write the root `README.md`'s run-and-read section: the command that prints the report, each test layer's
      command, and how to read the three tables a day prints. Proof: the md gates. Acceptance: AC-25.
- [ ] [AI] Check every test name the docs cite exists; the second command below prints nothing. Proof: the empty output.
      Acceptance: AC-24.

```bash
grep -rln --exclude-dir=.git --exclude-dir=.nx --exclude-dir=local-tmp --exclude-dir=generated-reports \
  --exclude-dir=node_modules "ACCEPTANCE_CRITERIA" .
```

```bash
grep -ohE 'test_[a-z0-9_]+' MOVEMENT.md REJECTED.md AMBIGUITIES.md | sort -u | while read -r t; do
  grep -rq "def $t(" apps/account-ledger-cli/tests || echo "missing $t"
done
```

### Phase 9 Gate

- [ ] [AI] Run every gate command below against the phase's combined state; each exits 0. Proof: each command and its
      exit status, recorded here. Acceptance: AC-24, AC-25. Commands:
  - `npx nx run account-ledger-cli:test:quick`
  - `npx nx run account-ledger-cli:test:integration`
  - `npx nx run account-ledger-cli:test:e2e`
  - `npm run -s check:hygiene`
  - `sh local-tmp/check-md.sh`
  - `./rhino md internal-link validate && ./rhino md heading-hierarchy validate && ./rhino md naming validate`
  - `./rhino governance word-budget validate`
- [ ] [AI] Add a new `WORKLOG.md` entry for the phase at the top, stamped with its real start and end `date` times.
      Path: `WORKLOG.md`. Proof: the entry. Acceptance: AC-24.
- [ ] [AI] Commit the phase as `docs(assessment): name the test behind every criterion and rule`, then push to
      `origin/main`; the pre-push hook runs every test layer. Command: `/usr/bin/git push origin main`. Proof: the
      commit hash and the pushed range, recorded here and in the Execution Record. Acceptance: AC-24, AC-25.

Pause safety: the phase leaves assessment docs that agree with the code and cite its tests. Re-verify with
`npx nx run account-ledger-cli:test:quick`.

## Phase 10 — The Trade-Offs Document and Final Verification

- [ ] [AI] Write `docs/explanation/architecture-trade-offs.md` with the brief's four sections, drawn from the built
      code: the log scan (D7) and the projection that defers it, value-dated entries and one control, every way an
      authorization ends other than a matching settlement, and every simplification with its deferred risk, among them
      the hold lifetime, the fee waiver a reversal cannot make (D20), and a live stream's quarantine (D21). Proof: the
      section headings, and a read confirming it restates neither the stream nor Part 1's rule text. Acceptance: AC-27.
- [ ] [AI] List it in `docs/explanation/README.md`. Proof: the md gates. Acceptance: AC-27.
- [ ] [AI] Search for any live rule requiring Gherkin with the command below. Proof: each hit listed here with why it is
      not a requirement, such as catalog text conditional on a repository that uses Gherkin, the scenario clauses of
      `red-green-refactor.md` and `swe-code-maker.md` that R1 names, or a binding that records it as not applicable.
      Acceptance: AC-28.

```bash
grep -rniE 'gherkin|pytest-bdd|\.feature' AGENTS.md README.md repo-governance specs apps .agents --include='*.md'
```

- [ ] [AI] Read the governance for each choice AC-29 lists and record where each is stated. Proof: the list of paths.
      Acceptance: AC-29.

### Phase 10 Gate

- [ ] [AI] Run every gate command below against the phase's combined state; each exits 0. Proof: each command and its
      exit status, recorded here. Acceptance: AC-27 to AC-30. Commands:
  - `npx nx run account-ledger-cli:test:quick`
  - `npx nx run account-ledger-cli:test:integration`
  - `npx nx run account-ledger-cli:test:e2e`
  - `npm run -s check:hygiene`
  - `sh local-tmp/check-md.sh`
  - `./rhino md internal-link validate && ./rhino md heading-hierarchy validate && ./rhino md naming validate`
  - `./rhino governance word-budget validate`
- [ ] [AI] Record the final unit coverage figure from `test:unit`; it is at least 80%. Proof: the figure. Acceptance:
      AC-30.
- [ ] [AI] Add a new `WORKLOG.md` entry for the phase at the top, stamped with its real start and end `date` times.
      Path: `WORKLOG.md`. Proof: the entry. Acceptance: AC-24.
- [ ] [AI] Commit the phase as `docs(explanation): write the architecture trade-offs`, then push to `origin/main`; the
      pre-push hook runs every test layer. Command: `/usr/bin/git push origin main`. Proof: the commit hash and the
      pushed range, recorded here and in the Execution Record. Acceptance: AC-27 to AC-30.

Pause safety: the phase leaves every substantive item terminal. Re-verify with
`npx nx run account-ledger-cli:test:quick`.

## Recovery Items

Dormant until their trigger fires; each closes with a disposition at reconciliation.

- [ ] [AI] RC1 — Resolve a figure the code disagrees with. Trigger: a criterion test or the golden run fails, and the
      code follows the resolutions while MOVEMENT or OUTPUT_TARGET shows another figure. Decision owner: the owner.
      Procedure: stop the phase; record both figures and the trace in `learnings.md`; put the choice to the owner with
      grill-me; apply the decision to MOVEMENT, OUTPUT_TARGET, and AMBIGUITIES in its own commit, with a WORKLOG entry.
      Proof: the golden run passes against the corrected text.
- [ ] [AI] RC2 — Fall back from partial capture. Trigger: a Phase 8 cycle reaches its repair ceiling, or the owner calls
      time. Decision owner: the owner. Procedure: discard Phase 8's uncommitted work with `/usr/bin/git restore`; put
      the rewording of AMB-013 as not built to the owner and apply it; add partial capture to "What you cut and why" in
      Phase 10 and to REJECTED's abandoned approaches; record AC-21 as not applicable by the owner's dated decision.
      Proof: the gates pass with the header at eight columns.
- [ ] [AI] RC3 — Revert a pushed unit. Trigger: a later phase shows a pushed unit broke behaviour its own gate did not
      cover. Decision owner: the executor. Procedure: `/usr/bin/git revert <commit>` for the unit's commits, push, and
      redo the unit's items. Proof: the gates pass after the revert.
- [ ] [AI] RC4 — Make a change to OUTPUT_TARGET affect the project. Trigger:
      `npx nx show projects --affected --files=OUTPUT_TARGET.md` does not list `account-ledger-cli` in Phase 6. Decision
      owner: the executor. Procedure: add the file to the named inputs of every test target so Nx attributes it, per the
      [Nx workspace policy](../../../repo-governance/development/workflow/nx-workspace-policy.md); if it still is not
      listed, set `cache: false` on `test:e2e`, the target that reads it, and record the finding and the choice in
      `learnings.md`. Proof: the command lists the project, or the target's configuration shows `cache: false`.

## Archival

After every substantive phase is terminal. Nothing here starts before the Phase 10 gate. The completion gate is the
execution check alone (D11).

- [ ] [AI] Give each dormant recovery item its dated disposition. Proof: every item carries one.
- [ ] [AI] Triage `learnings.md`: route each entry to one owner or discard it with a reason, or write the empty-log
      record. Proof: no entry left unresolved.
- [ ] [AI] Run [Execution Check](../../../repo-governance/workflows/plan/plan-execution-check.md) and record its
      terminal verdict; archival needs a permitting one. Proof: the verdict. Acceptance: AC-30.
- [ ] [AI] Run [Dev Artifact Clean-Up](../../../repo-governance/workflows/maintenance/dev-artifact-clean-up.md) and
      record what it removed. Proof: the record.
- [ ] [AI] Move the plan to `plans/done/YYYY-MM-DD__in-memory-account-ledger-init/` with the completion date; update
      `plans/in-progress/README.md`, `plans/done/README.md`, and every live link to the old path; run the full
      validation from the archived state; add the WORKLOG entry; commit as
      `docs(plan): archive the in-memory ledger plan` and push. Command: the command below finds only history. Proof:
      the command's output and the pushed range.

```bash
grep -rln --exclude-dir=.git --exclude-dir=.nx --exclude-dir=local-tmp --exclude-dir=node_modules \
  "plans/in-progress/in-memory-account-ledger-init" .
```

[cycle]: ../../../repo-governance/development/quality/testing/test-driven-development/001-cycle-and-evidence.md
