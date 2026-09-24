---
name: plan-handover-and-takeover
description: >-
  Writes a resumable handover record before unfinished plan work changes hands, and on resumption discovers, adopts, and
  cleans up every trace of the plan so execution resumes.
when_to_use: >-
  Use when unfinished plan work passes to another session, agent, or person, or when resuming a plan that may already be
  partly worked.
---

# Plan Handover and Takeover

## Entry

Handover: unfinished plan work is about to leave its session, agent, or person; a finished plan is archived instead.
Takeover: a plan resumes and nobody has confirmed whether it was already worked; one already executing in the right
worktree this session continues.

- `mode` (`enum`: `handover`, `takeover`; required).
- `plan` (`string`, required): a plan folder or its bare identifier.
- `repositories` (`string`, optional): extra candidate repositories.

## Sequence

Handover runs steps 1–4 and takeover steps 5–12. Both key on the plan identifier, the folder name without a date prefix,
and track each probe, anomaly, and cleanup candidate as its own task per
[Task Tracking](../../development/agents/task-tracking.md).

1. **Gather verified state per repository:** checkout, branch, head commit, uncommitted changes, pull request and
   pipeline status, and checkbox counts, re-checking anything possibly stale.
2. **Write the record in fixed section order:** one-line status; verified per-repository state; next steps naming the
   checklist item and first command; active user rule decisions with statement, scope, source, and status, or `None`
   after checking; learned constraints with why they bite; files touched, or where they are listed; and settled
   decisions not to reopen. Status and next steps are never empty; no required section is absent.
3. **Save it dated and named by plan identifier** under the scratch location, keeping earlier records.
4. **Report the path** of the non-empty record.
5. **Re-read the instructions and reconcile active rule decisions** before resuming anything; stop on an unresolved
   conflict.
6. **Read the newest handover record as a lead** that narrows probes but proves nothing, and reconcile its rule
   decisions too.
7. **Fix the candidates:** this repository, any repository the plan or a handover names, and `repositories`.
8. **Probe each candidate, persisting every hit to the takeover report:** linked worktrees, local and remote branches,
   pull requests in any state, where the plan folder sits on the trunk, and each found copy's ticks and uncommitted
   state. Judge nothing stale.
9. **Classify each repository into one bucket:** nothing found; delivered (archived on the trunk, every found pull
   request merged; report the invocation as possibly stale); live (partial ticks, nothing contradicting); or anomaly.
   Evidence fitting no bucket, two buckets, or contradicting itself, such as a worktree without its branch, a pushed
   branch with neither worktree nor pull request, or two worktrees for one plan, is an anomaly: stop and escalate with
   the evidence.
10. **Adopt live work.** Enter its worktree or create one from its branch, never the trunk, and sync as Execution does.
    Uncommitted changes await the user's direction, never stashed or discarded; a rebase conflict is aborted and
    reported. Until the touched-file record is rebuilt from branch history, every changed path is unattributed. Reuse an
    existing pull request, and tick a checkbox only from cited discovery evidence.
11. **Clean up only after classification.** A found worktree or branch not adopted passes the pre-removal checks of
    [Dev Artifact Clean-Up](../maintenance/dev-artifact-clean-up.md). Anomalies are never cleaned, anything not proven
    idle stays and is reported, and each removal or skip is logged.
12. **Hand each live or plan-owning nothing-found repository to [Execution](plan-execution.md).**

## Exit

Handover: a non-empty record (`file`, `handovers/<date>__<plan>.md` in the scratch location per
[Temporary Files](../../conventions/structure/temporary-files.md)), its path reported.

Takeover: every candidate is classified, each stale leftover removed or kept for a stated reason, and step 12's
repositories handed to Execution. Outputs: the takeover report (`file`, scratch location) and reconciled targets (`map`:
repository to bucket, worktree, branch, and pull request).

Partial outcome: an anomaly awaits the user, its evidence in the report; that repository is neither cleaned nor handed
off until resolved.

## Example Usage

```text
Run plan-handover-and-takeover with mode handover and plan "plans/in-progress/add-export/".
Run plan-handover-and-takeover with mode takeover and plan "rename-billing".
```

## Related Workflows

- [Execution](plan-execution.md) runs the plan once takeover hands it on.
- Multi-Plans Execution schedules several resumed plans.

## Why a Handover Is Only a Lead

A checklist records what is done, not what is safely half-done or which lessons were paid for; the record carries both.
Any later touch makes it stale, so takeover verifies everything. Each run is bounded by its fixed candidate set. This
workflow implements [Evidence Over Assertion](../../principles/evidence-over-assertion.md) and
[Explicit Over Implicit](../../principles/explicit-over-implicit.md).
