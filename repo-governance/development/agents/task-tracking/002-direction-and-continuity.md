---
description: >-
  Requires new direction to be reconciled against every open item before work responds, and the list and active rule
  decisions to survive compaction, handoff, and concurrent tasks.
when_to_use: >-
  Use when an instruction, correction, or follow-up arrives mid-task, when resuming compacted or handed-off work, or
  when other tasks share the repository.
---

# Direction and Continuity

## New Direction Reaches the List First

When new, follow-on, or changed direction arrives while a list is open, reconcile the list against it before acting on
it. Read the direction against every open item: some items are now wrong, some are superseded, some are unaffected, and
the direction usually implies more than one new item.

The reconciliation records which items the direction invalidates, which it supersedes, which it leaves alone, and which
new items it creates. An item the direction kills is closed with that reason, not left open to look abandoned later.

This is not the discovered-work rule. Discovery comes from the actor and only ever adds items. Direction comes to the
actor and can make existing items wrong, which is why appending the new work without re-reading the old is not enough.

Acting first and updating afterwards produces a list that describes the task as it was requested rather than as it is
being done. The reconciliation is also where a contradiction between old and new direction becomes visible. Carrying
both forward resolves the contradiction by accident, and that resolution is never recorded as the decision it was.

## Surviving Compaction and Handoff

The list, and each item's accurate status, carry across context compaction, restarts, and handoff to another agent. A
list held in the repository, such as a plan checklist updated in the same change as the work, satisfies this carry-over
on its own, because compaction cannot reach it.

Every active rule decision a user has established for the work is recorded when it is made, with its operative
statement, its scope, its source, and its status, and it is reproduced in every compaction summary and every handoff.
Before the first action after restored context:

1. re-read the repository's canonical instructions;
2. reconcile the recorded decisions against them;
3. mark an entry superseded only by naming what superseded it;
4. stop and report any conflict that cannot be resolved, rather than silently weakening either statement.

A decision held only in conversation is the first thing compaction loses, and the loss is invisible: the next action
simply stops honouring it.

## Other Tasks Share the Repository

Another session, another harness, or a person may be changing the repository at the same time, and plans, governance
documents, and harness directories are where tasks collide, since each task depends on them. Check the current state of
such an area each time you are about to use or change it. Re-read the file rather than trusting what the list says about
it: the list records what was intended, and the file records what is there.

A change you do not recognize belongs to someone else's task. Keep it and work around it; never revert it, overwrite it,
or fold it into your own commit. Where it truly conflicts with your task, the owner of that work decides; it is not
yours to merge.

## A List Grants No Authority

A task list records intended work. Committing, pushing, merging, and every other action with its own authorization rules
stay governed by those rules. An item that reads "commit the change" authorizes nothing.
