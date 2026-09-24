---
description: >-
  Requires an append-only ledger of every path a task mutates, carried intact through compaction and handoff, and
  confines staging, reverting, and cleanup to paths on that ledger while leaving every other path to its owner.
when_to_use: >-
  Use before the first file mutation in a shared checkout, before staging or committing, when resuming after a summary
  or handoff, and whenever an unrecognized change appears in the tree.
---

# File-Touch Discipline

A shared working tree mixes the changes of every actor editing it, people, agents, and background processes alike, and
nothing marks whose is whose. A deliberate record of the paths this task touched is the only evidence, so every path
missing from it is presumed to belong to another actor.

This standard implements [Explicit Over Implicit](../../principles/explicit-over-implicit.md),
[Governance Continuity](../../principles/governance-continuity.md), and
[Root Cause Orientation](../../principles/root-cause-orientation.md).

## Keeping the Ledger

| Rule                  | Requirement                                                                                                                   |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| start first           | open it before the first mutation, never at commit time; a late start leaves a gap of unknown size                            |
| record as it happens  | add each path when it is mutated, with the operation and a short reason tied to the task                                      |
| never shrink          | remove no entry; a path changed and later restored is still worth knowing                                                     |
| from actions only     | derive it from the task's own actions, never from status, diff, or stash listings, which show every actor                     |
| every mutation counts | edits, creations, deletions, moves, formatters, generators, and version-control commands that alter the tree, index, or stash |
| one per tree          | a ledger covers one working tree of one repository; work across several trees keeps a separate ledger for each                |

Read-only work needs no entry. A delegated agent returns its own ledger with its result, and the delegating agent merges
it explicitly, never assuming the delegate stayed within its request.

A file a generator rewrites because of this task's change is on the ledger and lands in the same commit as its source.
Generated output is regenerated, never edited by hand; [Harness Adapters](../agents/harness-adapters.md) applies this to
one kind.

## Carrying It Through Context Loss

Every summary, compaction, and handoff reproduces the ledger in full. "Edited several documents" cannot say whether a
given path is the task's, which is the one question the ledger answers. On a long unattended run, keep the ledger in a
file outside the context, at a location the adopter records.

## When the Ledger Is Lost

1. Rebuild it from the session transcript, which shows the actions actually taken.
2. Until that succeeds, treat every modified or untracked path as foreign.
3. Stage, commit, revert, stash, clean, or delete nothing whose authorship is not established.
4. If rebuilding fails and the work must continue, say so and ask which paths belong to the task.

## Reconciling Before Staging

Immediately before staging, compare the ledger with the tree in both directions and state every difference:

| Found                                  | Means                                            | Action                                           |
| -------------------------------------- | ------------------------------------------------ | ------------------------------------------------ |
| a changed path missing from the ledger | another actor's work                             | leave it unstaged and untouched                  |
| a ledger path whose change is gone     | something overwrote or reverted this task's work | stop, and find out what happened before going on |

Stage by explicit path only. [No Destructive Git Operations](no-destructive-git-operations.md) owns the prohibitions on
whole-tree staging and discarding; this standard decides which paths may be named.

Deferring to foreign changes has a limit. When the foreign set is large (roughly fifty paths or more), matches a state
an earlier session already deferred to, or blocks a gate the task must pass, run a bounded read-only identification that
touches none of those paths, and report whether it is live work or stale drift before deferring again.

## Foreign Paths

A path not on the ledger gets no action at all, however stray or broken it looks: no staging, reverting, stashing,
cleaning, deleting, reformatting, or fixing in passing. Uncommitted work has no undo. If a foreign path blocks the task,
report it and why, and stop.

When a whole-tree check fails only because of another actor's unfinished work, never stash, revert, or stage that work
to pass it. Do other work, retry within a declared bound per [Bounded Convergence](bounded-convergence.md), and report
the blocker. Skipping the check is a separate permission; see [Hook Verification](hook-verification.md).
