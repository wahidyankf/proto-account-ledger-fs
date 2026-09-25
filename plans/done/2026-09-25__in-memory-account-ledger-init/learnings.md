# Learnings

What execution discovers, recorded when it is discovered, and routed to one durable owner or discarded with a reason
before archival, per [Knowledge Capture and Archival][capture] and [Learning Triage][triage].

Each entry records when, what was found, why it matters, and, once routed, its owner or its discard reason.

## Entries

### L1 — A mutation restored within the same second leaves stale bytecode (2026-09-25 04:09)

- **Found.** Phase 1's greeting mutation was restored by `sed` in the same second, at the same file size, so Python's
  timestamp-based `.pyc` check kept the mutated bytecode, and the next `pytest tests` failed three tests against a
  correct source. Deleting every `__pycache__` under `src` and `tests` made the run pass.
- **Why it matters.** Every mutation proof in this plan restores code the same way; a stale cache turns a restored green
  into a false red, or a mutation into a false green.
- **Handling.** After each mutation's restore, delete `__pycache__` under `src` and `tests` before the confirming run.
- **Owner.** Governance: `repo-governance/development/quality/stacks/python-standards.md`, Mutation Proofs, landed
  through Rules Propagation on 2026-09-25 at 06:55. Kept: nothing caught a same-second restore before.

### L2 — Editing AGENTS.md changes the generated adapters (2026-09-25 04:15)

- **Found.** Phase 1's gate failed `harness-adapters`: the eight `catalog.json` and `provenance.json` files under
  `.claude/`, `.codex/`, and `.opencode/` record a digest of `AGENTS.md`, so R1's edit made them divergent.
  `npm run generate:bindings` regenerated them and the gate passed.
- **Why it matters.** tech-docs 007 says no adapter changes, so `npm run generate:bindings` is not needed; that is wrong
  for any phase that edits `AGENTS.md`, Phase 2 included.
- **Handling.** Regenerate the bindings in each phase that edits `AGENTS.md`, and commit the adapters with it.
- **Owner.** Discarded: already covered. `check:hygiene`'s `harness-adapters` gate failed on it in Phase 1 and names the
  regeneration, so the repository already catches it.

### L3 — `decide` takes the available balance, not the log (2026-09-25 04:47)

- **Found.** tech-docs 001 gives `decide(log, event, today)`, but computing the available balance inside
  `authorizations.py` needs `balances.py`, which already imports `authorizations.records` for the holds: an import
  cycle. Cycle 4.4 wrote `decide(available, amount)`, and `processing.py` computes the available balance first.
- **Why it matters.** The rule is unchanged (AMB-008, AMB-009): the decision still reads the balance value-dated up to
  the processed day less the active holds; only where that balance is computed moved.
- **Owner.** Discarded: specific to this plan. The rule is unchanged, the code states the signature as built, and no
  rule would catch a different split next time.

### L4 — Pyright proves exhaustiveness only on the matched subject itself (2026-09-25 04:55)

- **Found.** In Cycles 4.10 and 4.14 pyright's strict `reportMatchNotExhaustive` rejected matches whose cases split a
  union through a nested class pattern, such as `Credit(posting=Whole())` and `Credit(posting=Instalments())`, or
  `SettlementAccepted(effect=ForcePosted())`: it does not narrow on an attribute. In Cycle 4.11, `case unreachable:`
  after an exhausted `match state, trigger:` was flagged as never matched, while `assert_never` needs a named subject.
- **Why it matters.** tech-docs 001 wants every match over the unions to end in `assert_never`, which only holds when
  pyright narrows the subject to `Never`.
- **Handling.** Match the inner attribute in its own `match`; bind a tuple subject to a name, `pair = state, trigger`,
  and end with `case _: assert_never(pair)`.
- **Owner.** Discarded: already covered. Strict pyright reports the unexhausted match, and python-standards requires
  each match over a closed set to end in `assert_never`.

### L5 — `AuthorizationRecord` holds the authorization, not its fields (2026-09-25 04:53)

- **Found.** tech-docs 001 gives `AuthorizationRecord` as `id, account, state, last_event`. Cycle 4.9 kept
  `AuthorizationRecord(authorization, state)`: the authorization event already carries the hold ID and account, and no
  cycle reads a last event.
- **Why it matters.** The record carries the same facts without copying them; a later phase that renders the last event
  adds that field then.
- **Owner.** Discarded: specific to this plan. The architecture's L4 view shows `AuthorizationRecord` as built, the
  authorization and its state.

### L6 — Rule tests with incidental overdrafts break once fees exist (2026-09-25 05:17)

- **Found.** Cycle 5.1's fee step made four Phase 4 tests fail: their streams let a day close negative, which had no
  consequence before fees, and each asserted a closing that now carried a fee. Their streams now open with a credit.
- **Why it matters.** A rule test should keep every day at or above zero unless the fee rule is what it tests, or each
  later end-of-day step can move its figures.
- **Owner.** Discarded: already covered. The suite failed at once when fees landed, and the four streams were fixed; any
  later rule that moves a figure fails its tests the same way.

### L7 — A resolved rule with no figure in the stream needs its own test (2026-09-25 05:52)

- **Found.** AMB-035 lets a reversal undo an interest event or a capitalization, but the brief's stream reverses
  neither, and no planned test did. Phase 5's `interest_fired`, `accrued`, and `interest_base` ignored reversals
  unnoticed until Cycle 6.8's day list read them.
- **Why it matters.** A plan that derives its tests from the brief's figures misses every rule the stream never
  exercises; each such clause of a resolution needs a test of its own.
- **Owner.** Governance: `repo-governance/development/quality/testing/behaviour-driven-development.md`, This
  Repository's Binding, landed through Rules Propagation on 2026-09-25 at 06:55. Kept: no rule mapped tests to clauses,
  only to entries.

### L8 — A `git add` naming a deleted path stops before the rest (2026-09-25 06:36, logged 07:15)

- **Found.** Phase 9's `git add` listed `ACCEPTANCE_CRITERIA.feature`, already staged as deleted by `git rm`; git
  refused the pathspec, and the commit that followed took only the deletion, so `58e690d` holds one file and `02ce7aa`
  the rest.
- **Why it matters.** A commit that runs after a failed stage looks complete from its message.
- **Owner.** Discarded: specific to one command. Chaining the stage and the commit with `&&`, as every later commit did,
  stops at the failure, and no rule would add protection that operator does not.

### L9 — An editor's format-on-save rewrapped `cli.py` during a gate (2026-09-25 06:34, logged 07:15)

- **Found.** While `check:hygiene` ran, `cli.py` was reformatted at 88 columns, against the app's `line-length = 120`;
  none of the gates formats Python, so the change came from outside the run. It was layout only, backed up to
  `local-tmp/cli.py.reformatted-0634`, and restored from HEAD.
- **Owner.** Discarded: the relevance gate. The subject is a tool outside this repository, and `ruff format --check` in
  `test:quick` already fails such a change before it can be pushed.

### L10 — The Phase 9 WORKLOG item was ticked late (2026-09-25 06:48, logged 07:15)

- **Found.** The Phase 9 WORKLOG row landed with its commit, but its delivery item stayed unticked until the Phase 10
  close.
- **Owner.** Discarded: already covered. The row itself was written on time, and the Execution Check reads every item's
  state, as it did here.

[capture]: ../../../repo-governance/conventions/structure/plans/008-knowledge-capture-and-archival.md
[triage]: ../../../repo-governance/conventions/structure/plans/017-learning-triage.md
