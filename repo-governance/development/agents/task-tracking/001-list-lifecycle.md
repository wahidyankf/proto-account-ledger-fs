---
description: >-
  Fixes when a task list is created, how granular its items are, which statuses they carry, and when each status
  changes.
when_to_use: >-
  Use when opening a task list, writing its items, or changing the status of an item.
---

# List Lifecycle

## Before the First Action

Before any task, including a purely conversational one, create or update the task list, and mark its first item in
progress before the task's first action. The list may start with one item and grow as work is discovered. It never
starts after the work.

There is no step-count threshold. A threshold asks for an estimate of the work before the work is recorded, which is
exactly when that estimate is least reliable, and "too small to track" is the judgement that lets a list lapse
unnoticed.

Opening the list is automatic. Nobody has to ask for one, and no plan, workflow, or agent treats the absence of a
request as permission to skip it.

## One Item, One Checkable Outcome

An item is too coarse when judging it done means accepting several separate claims at once. Two verbs in one item
usually mean two items.

```text
too coarse:  "Write the standard, index it, and run the checks"
granular:    "Write the standard"
             "Add its row and Directory Map line to the category index"
             "Run the validation gates"
```

Prefer the smaller split when unsure. A list that is too fine costs a line of output; a list that is too coarse hides
how much work remains. Discovery, implementation, validation, documentation, and delivery each get items when they are
in scope, rather than being folded into a broad one.

Where the repository works in test-first increments, each red, green, and refactor step is its own item carrying the
test it concerns. A red item records why the test is expected to fail before implementation begins, and every step
records the result actually observed. A red that fails for some other reason has not shown the missing behaviour.

## Statuses

Each item is `pending`, `in progress`, `completed`, or `blocked`. At most one item is in progress, unless work genuinely
proceeds in parallel.

| Moves to      | When                                                                                |
| ------------- | ----------------------------------------------------------------------------------- |
| `in progress` | before the item's first action, never after it succeeds                             |
| `completed`   | once its outcome exists and has been verified; a failing check leaves the item open |
| `blocked`     | when it cannot proceed; it stays open, with what blocks it recorded                 |

An item still `pending` while its work is underway is a stale list, which is a defect rather than a detail: the
`in progress` marker is where a reader resumes after an interruption. A completed marker tells every later reader the
outcome was confirmed, so marking one on belief rather than verification makes the list lie. A blocked item that is
quietly closed is a decision nobody made.

## Update as Items Resolve

Change an item's status when its state changes, not in a sweep at the end. Completions recorded together report a
sequence of states that was never observed, and an interruption before the sweep leaves a list that cannot be resumed
from.

## Discovered Work

Work found along the way becomes a new item immediately, rather than widening an existing one, so the list reflects the
true remaining scope. Work mentioned in a reply but never added to the list is work that gets lost.

## Before Reporting Completion

Reconcile the whole list against the actual state of the repository. Finish what remains, or state plainly what does not
and why.
