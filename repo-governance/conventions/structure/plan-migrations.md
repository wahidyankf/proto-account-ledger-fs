---
description: >-
  Requires a plan that relocates, restructures, or retires data, configuration, or repository structure to list every
  affected source first and to stage the change so each step can be undone.
when_to_use: >-
  Use when any formal plan will move, copy, normalize, replace, or retire stored data, configuration, dependencies, or
  repository structure.
---

# Plan Migrations

Data rarely disappears during the obvious part of a change. It disappears in the step everyone assumed was safe: the old
copy deleted a day early, the consumer nobody listed, the record the converter skipped. This convention settles, while
the plan is still being written, how every source survives and how the change is reversed if it does not.

It extends the [Plans Convention](plans.md). It applies whenever a plan relocates, duplicates, normalizes, replaces, or
retires something another part of the system reads: persisted or runtime data, a schema, an API or wire format,
configuration, a dependency, or the layout and content of the repository. The breadth is intended. Renaming a directory
that other documents link to breaks those readers as surely as dropping a database column.

## Modules

1. [Source Inventory and Contracts](plan-migrations/001-source-inventory-and-contracts.md)
2. [Transition and Recovery](plan-migrations/002-transition-and-recovery.md)

## Where It Lives

With a single-file technical shape, `tech-docs.md` describes today's state and the intended state in separate sections,
and carries the precise before-and-after shapes. With the directory shape, when the transition flow and the data
contracts are read by different people, each may get its own companion, for example `tech-docs/NNN-migration-design.md`
and `tech-docs/NNN-data-contracts.md`. A plan with nothing to migrate adds neither.

## The Delivery Claim

`delivery.md` shows, for every source in the inventory, one of three outcomes: left untouched, copied and then
confirmed, or reported safely so the step can be retried.

The plan does not say that nothing was lost until every reader, writer, source format, owner, and fallback touched by
the change has been accounted for. The one left out is the one that breaks after archival, when no one is looking.

## Principles

This convention implements [Evidence Over Assertion](../../principles/evidence-over-assertion.md), because survival is
shown source by source rather than asserted, and [Fail Closed](../../principles/fail-closed.md), because a target that
has taken over refuses to run instead of quietly reaching back to the old source.
