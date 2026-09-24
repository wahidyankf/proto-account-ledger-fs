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
- **Owner.** Not yet routed.

### L2 — Editing AGENTS.md changes the generated adapters (2026-09-25 04:15)

- **Found.** Phase 1's gate failed `harness-adapters`: the eight `catalog.json` and `provenance.json` files under
  `.claude/`, `.codex/`, and `.opencode/` record a digest of `AGENTS.md`, so R1's edit made them divergent.
  `npm run generate:bindings` regenerated them and the gate passed.
- **Why it matters.** tech-docs 007 says no adapter changes, so `npm run generate:bindings` is not needed; that is wrong
  for any phase that edits `AGENTS.md`, Phase 2 included.
- **Handling.** Regenerate the bindings in each phase that edits `AGENTS.md`, and commit the adapters with it.
- **Owner.** Not yet routed.

### L3 — `decide` takes the available balance, not the log (2026-09-25 04:47)

- **Found.** tech-docs 001 gives `decide(log, event, today)`, but computing the available balance inside
  `authorizations.py` needs `balances.py`, which already imports `authorizations.records` for the holds: an import
  cycle. Cycle 4.4 wrote `decide(available, amount)`, and `processing.py` computes the available balance first.
- **Why it matters.** The rule is unchanged (AMB-008, AMB-009): the decision still reads the balance value-dated up to
  the processed day less the active holds; only where that balance is computed moved.
- **Owner.** Not yet routed.

### L4 — Pyright proves exhaustiveness only on the matched subject itself (2026-09-25 04:55)

- **Found.** In Cycles 4.10 and 4.14 pyright's strict `reportMatchNotExhaustive` rejected matches whose cases split a
  union through a nested class pattern, such as `Credit(posting=Whole())` and `Credit(posting=Instalments())`, or
  `SettlementAccepted(effect=ForcePosted())`: it does not narrow on an attribute. In Cycle 4.11, `case unreachable:`
  after an exhausted `match state, trigger:` was flagged as never matched, while `assert_never` needs a named subject.
- **Why it matters.** tech-docs 001 wants every match over the unions to end in `assert_never`, which only holds when
  pyright narrows the subject to `Never`.
- **Handling.** Match the inner attribute in its own `match`; bind a tuple subject to a name, `pair = state, trigger`,
  and end with `case _: assert_never(pair)`.
- **Owner.** Not yet routed.

### L5 — `AuthorizationRecord` holds the authorization, not its fields (2026-09-25 04:53)

- **Found.** tech-docs 001 gives `AuthorizationRecord` as `id, account, state, last_event`. Cycle 4.9 kept
  `AuthorizationRecord(authorization, state)`: the authorization event already carries the hold ID and account, and no
  cycle reads a last event.
- **Why it matters.** The record carries the same facts without copying them; a later phase that renders the last event
  adds that field then.
- **Owner.** Not yet routed.

[capture]: ../../../repo-governance/conventions/structure/plans/008-knowledge-capture-and-archival.md
[triage]: ../../../repo-governance/conventions/structure/plans/017-learning-triage.md
