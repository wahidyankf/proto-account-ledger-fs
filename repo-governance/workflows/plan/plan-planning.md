---
name: plan-planning
description: >-
  Authors a complete formal plan from a request or a groomed brief, bounded by two sequential decision gates.
when_to_use: >-
  Use when a formal plan is requested, after the material choices have been surfaced but before any plan document
  exists.
---

# Planning

## Entry

Someone has asked for a formal plan, or a brief has been promoted by [Ideas Grooming](plan-ideas-grooming.md).

The request is explicit, as
[Authorization and Execution Record](../../conventions/structure/plans/010-authorization-and-execution-record.md)
requires. Inputs: `request` (`string`, required), the change or brief; `target-stage` (`enum`: `backlog`, `in-progress`;
optional, default the adopter's recorded stage, or `backlog` for a promoted brief), which a calling workflow may pass.

## Sequence

1. **Inspect before asking.** Read the repository — its instructions, its current state, the surfaces the work touches —
   so the first gate presents real choices rather than questions the repository already answers.
2. **Run the pre-write gate.** Every material branch is resolved here, and **no plan document is authored until it
   completes**. A plan written first and questioned afterwards has already committed to the answers.

   The gate also confirms the plan identifier, the target stage unless a caller passed it, the delivery target the
   repository's topology allows per
   [Delivery Seams and Ownership](../../development/agents/planning-capabilities/005-delivery-seams-and-ownership.md),
   whether the change alters a repository rule, which adds a [Rules Propagation](../maintenance/rules-propagation.md)
   outcome, split into actions rather than one generic checkbox, to the delivery unit changing it; whether it changes
   what a document describes, which adds a [Docs Propagation](../maintenance/docs-propagation.md) item to that unit; and
   whether any claim needs outside verification.

3. **Verify unstable facts before authoring.** Check each flagged claim, such as a library version, an interface's
   behaviour, or a third-party practice, against an authoritative source, and cite it. A finding that changes an answer
   reopens that branch of the pre-write gate; no plan document is written until it closes again.
4. **Author all six documents.** `README.md`, `brd.md`, `prd.md`, one technical shape, `delivery.md`, `learnings.md`.
   The document set and its rules are the [Plans Convention](../../conventions/structure/plans.md)'s; this workflow does
   not restate them. They land in `plans/<target-stage>/<identifier>/`.
5. **Write `delivery.md` last.** It depends on every other document, and writing it first produces a checklist for a
   plan that does not exist yet.
6. **Check structure before judgement.** Run the checks
   [Structural Validation](../../conventions/structure/plans/006-structural-validation.md) lists and fix what fails, so
   the gates that follow weigh substance rather than missing headings.
7. **Run the post-write gate.** A separate gate, on the complete draft, resolving what only became visible once the plan
   existed. It does not merge into the first gate — see
   [Decision Gates](../../development/agents/planning-capabilities/003-decision-gates.md).
8. **Run the [Quality Gate](plan-quality-gate.md)** and repair within its bounded budget.
9. **Land the plan as the repository authorizes.** Commit and integrate it by the delivery target the first gate
   confirmed, where the repository's rules permit, then release the checkout it was written in per
   [Dev Artifact Clean-Up](../maintenance/dev-artifact-clean-up.md).

## Exit

Six documents exist, both gates have completed and left decision records, and the quality gate has returned a terminal
verdict.

Output: `plan` (`directory`, `plans/<target-stage>/<identifier>/`). Partial outcome: a post-write decision nobody can
resolve puts the plan in `plans/backlog/`, its open question written into `README.md` rather than guessed past.

## Adopter Decision: Default Target Stage

| Option        | The finished plan                                                   | Trade-off                                                    |
| ------------- | ------------------------------------------------------------------- | ------------------------------------------------------------ |
| `backlog`     | waits as a proposal until someone schedules it                      | nothing looks active before it is chosen; one more move      |
| `in-progress` | is active at once, for work that executes as soon as its gate holds | no scheduling step; unscheduled work can crowd the live root |

Record the default. Neither stage executes the plan: execution is [Execution](plan-execution.md)'s, after its own entry
condition holds.

## Gate Ordering Is Not Negotiable

The two gates ask different questions at different times. Before authoring, the open questions are about approach,
scope, and constraint. After a draft, they are about what the draft revealed — a dependency nobody expected, a seam that
turned out to be in the wrong place.

Running one gate instead of two means asking the second set of questions before the information needed to answer them
exists.
