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

[capture]: ../../../repo-governance/conventions/structure/plans/008-knowledge-capture-and-archival.md
[triage]: ../../../repo-governance/conventions/structure/plans/017-learning-triage.md
