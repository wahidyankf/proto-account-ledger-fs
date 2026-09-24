---
description: >-
  Requires the planning owner's explicit request before a formal plan is written, and a dated execution record at the
  top of every delivery checklist.
when_to_use: >-
  Use before writing a formal plan or any document in its root, or when starting, executing, or resuming a formal plan.
---

# Authorization and Execution Record

## A Plan Is Written Only on Request

A formal plan, or any document inside a formal plan's root, is written only when whoever owns the repository's planning
has explicitly asked for it. A plan promoted from an idea brief is no exception: a brief marked for promotion during
[Ideas Grooming](../../../workflows/plan/plan-ideas-grooming.md) becomes a plan only once that owner explicitly requests
it.

Nothing else authorizes one:

- the size, risk, or kind of the work;
- an approach designed in conversation;
- a harness planning mode, which produces a proposal for the session rather than a repository artifact; or
- an agent judging that the work would benefit from a plan.

A plan is a commitment the repository carries. It occupies a lifecycle root, and it is groomed, reviewed, and archived,
each at the cost of someone's attention. An agent that files a plan because the work looked substantial has spent that
attention on the owner's behalf without asking. Without a request, the work proceeds under the repository's ordinary
change rules, or stops and asks.

Authorizing a plan does not authorize executing it. Approving a design and approving the changes it prescribes are
different decisions, made with different information.

The request that authorized a plan does cover the records its execution writes — ticks and Execution Record lines in
`delivery.md`, entries in `learnings.md`, and files in `evidence/` — so none of them needs a request of its own.

## The Execution Record

`delivery.md` opens with an `## Execution Record` section, before the declarations the
[Delivery Contract](004-delivery-contract.md) requires and before the first phase. It is a dated, append-only log with a
line for each of these events:

- a phase completed;
- a gate passed or failed;
- a retry established something the first attempt did not; or
- execution changed the plan — a reordered phase, a split item, a revised criterion.

```markdown
## Execution Record

- YYYY-MM-DD: Phase 1 gate passed; `<validation-command>` exited 0.
- YYYY-MM-DD: Phase 2 stopped at the link check; a renamed document left two dead links. Fixed at the source, and the
  gate passed on re-run.
```

Each line is written when its event happens. A record reconstructed at archival states what the author already believed
about the order of events, which is the one thing the record exists to check.

## Why a Separate Record

Ticks and per-item results say what was intended and what eventually held. They do not say what happened in between —
the failed gate, the retry, the change of course — and that is what a reader of a finished plan needs most when
something later breaks.

`learnings.md` is drained before archival, and per-item notes scatter the sequence across the checklist. The record is
the one place the order of events survives.

## Lifecycle of the Record

A plan that has not started carries the heading with no lines. The record then survives archival unchanged.

An archived plan is never edited to add a record it did not keep. Plans under `done/` are history — see
[Exclusions](../plan-validator-contract/004-exclusions.md) — and a record written after the fact is a reconstruction
with a date attached.

An adopter that wants this checked mechanically verifies the heading and the `YYYY-MM-DD:` line shape in its own plan
gate.
