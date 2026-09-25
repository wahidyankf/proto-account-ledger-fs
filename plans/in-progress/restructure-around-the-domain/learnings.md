# Learnings

What execution discovers, recorded when it is discovered, and routed to one durable owner or discarded with a reason
before archival, per [Knowledge Capture and Archival][capture] and [Learning Triage][triage].

Each entry records when, what was found, why it matters, and, once routed, its owner or its discard reason.

## Entries

- **2026-09-25 19:03, Phase 0.** The first evidence file failed `check:hygiene`: the directory-map gate requires every
  directory under a mapped one, `evidence/` included, to carry a README and an entry in its parent's map, and that
  README to map every file in it. The plan did not list `evidence/README.md`. Fixed in Phase 0: the README, its map
  entry in the plan README, and 008 updated. Why it matters: every plan here that files evidence meets the same gate,
  and neither the plans convention nor the template names it.

[capture]: ../../../repo-governance/conventions/structure/plans/008-knowledge-capture-and-archival.md
[triage]: ../../../repo-governance/conventions/structure/plans/017-learning-triage.md
