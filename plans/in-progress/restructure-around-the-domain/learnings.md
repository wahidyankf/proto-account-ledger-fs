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
- **2026-09-25 19:35, Phase 1.** The scratch width checker walked only directories, so a Markdown file named on its
  command line was silently skipped; a 123-column line reached the Phase 1 gate, where `check-md.sh` caught it. The
  checker now takes files too and exits 1 on a long line. Why it matters: a check that passes on input it never reads
  proves nothing, so each scratch check should fail loudly on an argument it cannot use.
- **2026-09-25 20:24, Phase 4.** The first run of the seven ban mutations counted no failures: it grepped ruff's output
  for `TID251`, but this ruff prints a rule by its name, `banned-api`, not its code. Rerun matching the name, all seven
  failed as they should. Why it matters: a mutation check that greps for a failure proves nothing until one deliberate
  failure has been seen to match; each such grep should be tried once against a failure first.

[capture]: ../../../repo-governance/conventions/structure/plans/008-knowledge-capture-and-archival.md
[triage]: ../../../repo-governance/conventions/structure/plans/017-learning-triage.md
