---
description: >-
  Requires each repeated operation to register a finite bound, a non-resetting progress measure, and both transaction
  branches before its first cycle.
when_to_use: >-
  Use before starting any step that can repeat, retry, poll, or iterate.
---

# The Loop Register

Every repeated operation registers a row **before its first cycle**. Registering afterwards records what happened; it
does not bound anything.

## The Row

| Field            | Holds                                                         |
| ---------------- | ------------------------------------------------------------- |
| identifier       | a stable name for this loop                                   |
| frozen input     | the exact worklist or subject, fixed at registration          |
| bound            | a finite worklist, an attempt count, or a wall-clock deadline |
| progress measure | the quantity that must strictly improve each cycle            |
| branches         | the two transaction branches this loop may end in             |
| result           | filled in when the loop closes                                |

## The Bound Is Finite and Stated

Either an exact worklist with each item processed once, or a hard ceiling on attempts or time. Not "a few", not "until
it looks right".

Encountering an item that should have been on the frozen worklist does not extend it. The item is evidence the input was
wrong, and the correct response is to rebaseline the input once — itself a bounded operation — rather than to append and
continue.

## The Progress Measure Cannot Reset

It must strictly improve each cycle: unresolved items decrease, open findings decrease, remaining deadline decreases.

And it must not reset because the failure changed shape. A repair cycle that resolves two findings and surfaces two new
ones has made no progress, however different the new ones look. This is the single most common way a bounded loop
quietly becomes unbounded — every reset feels justified, and each one is.

## Both Branches Are Declared First

Before the first cycle, the loop declares the two transaction branches it may end in: the planned target, and the
verified existing state. Each carries its own acceptance criteria and its own downstream routing.

Declaring the fallback at the start is what makes the ceiling survivable. Deciding it at the ceiling means deciding it
under partial information, sunk effort, and pressure to continue — the conditions under which the budget gets extended
instead.

## Every Row Reaches a Terminal Result

A loop closes with `TARGET_PASS`, `EXISTING_PASS`, or `SAFE_FAIL`, recorded in its row. It never closes by starting
another run, and no result recursively opens a new loop.

The operation that reaches the terminal outcome writes that result to the registered row in the same step. A result kept
in conversation or deferred to a later sweep is indistinguishable from an open loop after interruption. Ledger
reconciliation covers this rule by refusing a terminal operation whose row remains nonterminal.
