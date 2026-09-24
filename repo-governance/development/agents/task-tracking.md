---
description: >-
  Requires a task list of small checkable items before every task, conversational ones included, kept in sync as work
  happens and reconciled before new direction is acted on.
when_to_use: >-
  Use before starting any task, whenever progress on it changes, and when new direction arrives while a list is open.
---

# Task Tracking

Two failures follow from an absent or stale task list.

**Lost context.** Work interrupted by compaction, a restart, or a handoff leaves no map of what was done, what is
underway, and what remains. Reconstructing that from the outputs is slow, and it misses things.

**Invisible drift.** A list that marks work done before it is, or omits work already started, misreports the task to
everyone reading it. The person reading it usually cannot see the reasoning behind it, so a stale list does not merely
describe the work briefly; it describes it wrongly.

A list that tracks the present, item by item, prevents both. It also makes interrupted work resumable, because the first
unfinished item says exactly where to restart.

## Modules

1. [List Lifecycle](task-tracking/001-list-lifecycle.md)
2. [Direction and Continuity](task-tracking/002-direction-and-continuity.md)
3. [Bindings and Verification](task-tracking/003-bindings-and-verification.md)

## This Repository's Binding

The live list is a Markdown checklist file under the gitignored `local-tmp/` directory, named for its task (for example
`local-tmp/todo-<task>.md`), kept in addition to any harness-native task tool. Because it is a file, it survives
compaction, restarts, and a switch between harnesses; because it is ignored, it never enters a commit.

## Scope

Every task, whatever its size: a one-line edit, a rename, a question answered in prose. The standard binds delegated
agents exactly as it binds the main thread, and every harness, whatever it calls the feature.

A plan's delivery checklist as a document is governed by the
[Delivery Contract](../../conventions/structure/plans/004-delivery-contract.md). This standard governs the live list
kept while any work, planned or not, is in progress.
