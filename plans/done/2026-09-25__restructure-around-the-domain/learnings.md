# Learnings

What execution discovers, recorded when it is discovered, and routed to one durable owner or discarded with a reason
before archival, per [Knowledge Capture and Archival][capture] and [Learning Triage][triage].

Each entry records when, what was found, why it matters, and, once routed, its owner or its discard reason.

## Entries

- **2026-09-25 19:03, Phase 0.** The first evidence file failed `check:hygiene`: the directory-map gate requires every
  directory under a mapped one, `evidence/` included, to carry a README and an entry in its parent's map, and that
  README to map every file in it. The plan did not list `evidence/README.md`. Fixed in Phase 0: the README, its map
  entry in the plan README, and 008 updated. Why it matters: every plan here that files evidence meets the same gate,
  and neither the plans convention nor the template names it. Triage 2026-09-25 21:15: discarded. The directory-map gate
  already catches a missing evidence README on the first commit that adds the folder, so routing it would change nothing
  the repository fails to catch.
- **2026-09-25 19:35, Phase 1.** The scratch width checker walked only directories, so a Markdown file named on its
  command line was silently skipped; a 123-column line reached the Phase 1 gate, where `check-md.sh` caught it. The
  checker now takes files too and exits 1 on a long line. Why it matters: a check that passes on input it never reads
  proves nothing, so each scratch check should fail loudly on an argument it cannot use. Triage 2026-09-25 21:15:
  discarded. It concerns a scratch script under `local-tmp/`, deleted at archival, and the declared gate, `check-md.sh`,
  caught the long line; no durable rule or tool changes.
- **2026-09-25 20:24, Phase 4.** The first run of the seven ban mutations counted no failures: it grepped ruff's output
  for `TID251`, but this ruff prints a rule by its name, `banned-api`, not its code. Rerun matching the name, all seven
  failed as they should. Why it matters: a mutation check that greps for a failure proves nothing until one deliberate
  failure has been seen to match; each such grep should be tried once against a failure first. Triage 2026-09-25 21:15:
  discarded. The ban itself was sound, ruff exited non-zero on each mutation; the fault was in a throwaway grep over its
  output, which no repository rule or gate owns.
- **2026-09-25 21:13, Phase 8.** The Phase 8 record line and its WORKLOG entry were left out of 26f2e12: the script that
  wrote them failed an assertion on a stale anchor, which Prettier had reflowed, but the commit and the push after it
  ran on their own lines of the same command, so nothing stopped them. The two lines followed in the next commit. Why it
  matters: a chain of dependent steps should stop at the first failure, with `set -e` or `&&` through the commit, and an
  anchor into Prettier-formatted text should be read from the file just before it is used. Triage 2026-09-25 21:15:
  discarded. The omission was caught and closed in 9305a7b before archival, and the plan-execution check audits every
  phase's record line, so the repository already catches a missing one.
- **2026-09-25 21:28, the execution check.** The check found the trade-offs document's three-bullet list on the state
  that grows joined into one bullet since 9827e54: the Phase 7 edit that replaced "history" rewrapped its paragraphs by
  joining lines, and the joined bullets stayed valid Markdown, so Prettier and the width check passed them. Split again
  as a forward fix. Why it matters: a scripted rewrap of Markdown can change its structure while every format gate
  passes, so a prose edit's diff should be read for structure, not only words. Triage 2026-09-25 21:29: discarded. The
  script that joined it was scratch, deleted at archival, and the execution check, which reads each changed document,
  caught it before archival; no durable rule or gate would change.

[capture]: ../../../repo-governance/conventions/structure/plans/008-knowledge-capture-and-archival.md
[triage]: ../../../repo-governance/conventions/structure/plans/017-learning-triage.md
