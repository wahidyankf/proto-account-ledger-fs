# Specification and Rule Changes

What this plan changes in the repository's specifications and rules, file by file, as
[Plan Specification Changes](../../../../repo-governance/conventions/structure/plan-specification-changes.md) requires.
The proposal stays here; each file is changed in the phase that makes it true, never in one sweep at the end.

## What Becomes a Durable Contract

No Gherkin scenario becomes durable: D12 retires the corpus. The durable contracts are three:

- the as-built architecture, `specs/apps/account-ledger/cli/architecture.md` (AC-26);
- the printed report, owned by [OUTPUT_TARGET](../../../../OUTPUT_TARGET.md) and pinned by the end-to-end test (AC-01);
  and
- the command-line contract, published in the application README (AC-02 to AC-04, D13).

Every other criterion in [prd](../prd.md) stays plan-only. Each is proven by the pytest test it names, which is the
durable form of a rule once the plan is archived, and by the delivery item that creates the test:

- AC-05 to AC-23 and AC-31 to AC-36: the rule or criterion is owned by AMBIGUITIES, MOVEMENT, or REJECTED, which name
  the test (Phase 9); a second statement in `specs/` would be a copy. Verified by the RED and GREEN items of the cycle
  each criterion names, and by Phase 9's name check.
- AC-24, AC-25, AC-27: document outcomes, verified by the Phase 9 and Phase 10 items that write them.
- AC-28 to AC-30: repository state at the end, verified by the Phase 10 items and gate.

## Specification Delta

### [E] `specs/apps/account-ledger/cli/architecture.md`

```diff
- Scope: a hello-world scaffold that prints one line
+ Scope: the in-memory ledger replaying a CSV stream and printing one report per day
- System Context: Developer -> account-ledger-cli -> terminal stdout
+ L1 System Context: operator -> account-ledger-cli; stream CSV in; report on stdout, diagnostics on stderr
- Containers: one Python package, reached through nx run
+ L2 Containers: one Python 3.14 process; the stream file; standard output and error
- Components: cli (shell) -> greeting (core)
+ L3 Components: shell (cli, stream_csv, render) around the core (money, ids, config, events, log, balances,
+   authorizations, processing, end_of_day, replay, report), with every dependency pointing inward
+ L4 Code: Money and Amount, the ID types, the IncomingEvent and FiredEvent unions, the LogEntry union and Rejection,
+   AuthorizationState and its transition table, DayReport, and how each refers to the others
+ Dynamic: one day, from the first event processed to the report, through the three end-of-day steps
+ Constraints: every effect in the shell; balances recomputed from the log (D7); holds never expire (AMB-018)
```

- = Preserve: "Every effect sits in the shell; the core stays pure and deterministic." and the no-web, no-persistence
  constraint.
- → Views: every diagram is plain-text ASCII, per
  [Diagrams](../../../../repo-governance/conventions/writing/diagrams.md).
- ✓ Proof: every component the document names is a module under `src/account_ledger/`, checked by reading in the phase
  that adds the component; `./rhino md internal-link validate`.

### [D] `specs/apps/account-ledger/cli/behaviours/greeting.feature`

```diff
- Scenario: Running the CLI with no arguments greets the world
```

- = Preserve: nothing; the greeting is replaced by the replay, and the program with no argument now exits 2 (AC-04).
- → Bindings: the three `tests/*/steps/test_greeting_steps.py` files and `tests/conftest.py` are deleted with it.
- ✓ Proof: `test:quick`, `test:integration`, and `test:e2e` pass with no feature file left.

### [D] `specs/apps/account-ledger/cli/behaviours/README.md`

```diff
- Gherkin feature files for account-ledger-cli, bound at every test level through pytest-bdd
```

- ✓ Proof: `./rhino md internal-link validate` finds no link to it.

### [E] `specs/apps/account-ledger/cli/README.md` and `specs/README.md`

```diff
- a behaviours/ tree of Gherkin scenarios, executed by the test projects
+ an as-built architecture; behaviour is resolved in AMBIGUITIES.md and proven by the application's pytest suite
```

- ✓ Proof: `./rhino md internal-link validate` and `heading-hierarchy validate`.

## Rule Changes

Each goes through [Rules Propagation](../../../../repo-governance/workflows/maintenance/rules-propagation.md), with its
record in `local-tmp/`, and through
[Docs Propagation](../../../../repo-governance/workflows/maintenance/docs-propagation.md) for the documents it makes
stale.

### R1 — Retire Gherkin and pytest-bdd (D12, D12c)

- `AGENTS.md` [E]: the `specs/` line in Project Structure and the Testing section drop Gherkin; behaviour is proven by
  plain pytest at three layers, test-first.
- `repo-governance/development/quality/testing/behaviour-driven-development.md` [E]: a binding section records, per
  module, that the Gherkin corpus, scenario-first order, bindings and exemptions, and compliance reporting are not
  applicable, with the reason (D12), and that Layers and Adapters stays adopted with "every test" for "every scenario".
- `repo-governance/development/quality/testing/behaviour-driven-development/002-layers-and-adapters.md` [E]: the same
  wording in the module that stays adopted.
- `repo-governance/development/quality/testing/README.md` [E]: the index line says the standard binds only its layers
  here.
- `repo-governance/conventions/structure/specification-tree.md` [E]: a binding section records `behaviours/` as not
  applicable, with the reason (D12c).
- `repo-governance/development/workflow/nx-workspace-policy.md` [E]: the sentence listing feature files among the test
  targets' inputs is dropped. The sentence naming the stream files and `OUTPUT_TARGET.md` in their place is added in
  Phase 6, when those inputs exist, through its own Rules Propagation record.
- `README.md` [E]: the prerequisites row drops pytest-bdd.

Two adopted texts also mention scenarios and stay unchanged, since catalog text is changed only through adoption:
`repo-governance/workflows/quality/red-green-refactor.md` asks that "any scenario that specifies the behaviour was added
or updated first", and `.agents/agents/swe-code-maker.md` that "A scenario that specifies the behaviour is added or
updated before its red". Under the binding above no scenario specifies any behaviour here, so each requires nothing;
Phase 10's search lists both with that reason.

### R2 — Record the Python Choices (S3, D8, D14 to D18)

- `repo-governance/development/quality/stacks/python-standards.md` [E]:
  - Failures records typed result values (S3).
  - Domain Types changes the money row to one frozen dataclass per currency, joined in a union, wrapping a `Decimal`
    quantized to its places and adding only to its own type (D14, D14b); adds a positive-amount row (D18), a
    value-object row for identifiers and days (D15), and a row for a state that carries data, one frozen dataclass per
    state joined in a union (D17).
  - One sentence under the table records that no type may represent an illegal value, each constructor refusing one
    (D16), and one that this stack's state machines are hand-written over those unions (D8).
- `AGENTS.md` [E]: the Coding Conventions summary reads "frozen dataclasses and unions for the domain, one type per
  currency for money" in place of "frozen dataclasses and enums for the domain, `Decimal` for money".

### R3 — Record the Delivery Grammar (D9a to D9d, D11)

- `repo-governance/conventions/structure/plans/011-phase-boundaries-and-delivery-choices.md` [E]: under each of its four
  adopter tables, one sentence records this repository's option: phase gates (D9c), the Phase 0 baseline (D9b), the
  split cycle (D9a), and reopening a defective archived plan (D9d), the last as `plans/done/README.md` states.
- `repo-governance/workflows/plan/plan-execution.md` [E]: under the Completion Gate table, one sentence records the
  execution check only (D11).

### R4 — Drop ACCEPTANCE_CRITERIA.feature From the Assessment Docs (D12b)

- `repo-governance/conventions/structure/assessment-docs.md` [E]: the file leaves the list and the owners table; the
  criteria as Gherkin are no longer owned anywhere, and MOVEMENT's criterion list names each test.

Each recorded choice is one sentence in the form `This repository records **X**`, as
`repo-governance/workflows/quality/docs-quality-gate.md` records its own, so no file needs a new section. Before the
change the tightest files stand at 711 words (`plan-execution.md`), 699 (`specification-tree.md`), and 650 (module 011),
under the 750-word cap `./rhino governance word-budget validate` enforces. `specification-tree.md`'s binding is the
longest, about forty words; if it passes the cap, its binding moves to the new module
`repo-governance/conventions/structure/specification-tree/001-adopter-bindings.md`, listed in the file impact.
