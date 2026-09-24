---
name: plan-creating-project-plans
description: >-
  Guides authoring the six documents of a formal plan so each answers its own question and the checklist is genuinely
  executable.
when_to_use: >-
  Use when writing a formal plan, after its pre-write decision gate has resolved the material branches.
compatibility: Requires read access to every repository the plan will touch.
---

# Creating Project Plans

The structural rules — six documents, one technical shape, ordered companions — belong to the plan convention. This is
about writing ones worth executing.

## Each Document Answers Its Own Question

| Document        | Answers                           | Fails by                                    |
| --------------- | --------------------------------- | ------------------------------------------- |
| `README.md`     | what is this and where do I start | duplicating the other five                  |
| `brd.md`        | why is this worth doing           | describing the solution instead of the need |
| `prd.md`        | what must be true when it is done | listing tasks instead of testable outcomes  |
| technical shape | how will it be built              | re-arguing whether it should be             |
| `delivery.md`   | what do I do, in order            | describing intentions rather than actions   |
| `learnings.md`  | what did executing it teach       | being written at the end from memory        |

A document that answers someone else's question is the most common defect, and it is invisible while writing — each
paragraph feels relevant. The check is to read each document alone and ask whether it still makes sense.

## Write `delivery.md` Last

It depends on everything else. Written first, it becomes a checklist for a plan that does not exist yet, and the rest of
the plan is then reverse-engineered to justify it.

## Granularity Is the Hard Part

An item should be small enough that failing it is informative. "Implement the validator" fails as a unit; the person
resuming learns nothing about where it stopped.

Two tests:

- **Independently verifiable.** Finishing it leaves something observable — a file, an output, a passing check. If not,
  it is a thought rather than an item.
- **Self-contained proof.** If proving it requires finishing the next item, the split is in the wrong place.

## Write for a Cold Executor

The reader is someone who was not present, has no memory of the discussion, and will not ask. Name paths in full, name
commands exactly, and state what the result should look like.

That reader is also, usually, you — later, having forgotten more than seems possible.

## Acceptance Criteria Must Be Falsifiable

Every criterion carries a stable identifier and states a condition that could fail. "The system is reliable" cannot
fail. "Restarting mid-write leaves no partial file" can.

Criteria that cannot fail are the ones that get marked complete without anyone checking, because there is nothing to
check.

## Check Each Claim While Writing It

Every path, command, version, test name, and outside behaviour is checked as it is typed, then labelled or left out, per
[Plan Anti-Hallucination](../../../repo-governance/development/quality/evidence/plan-anti-hallucination.md). Review is
too late: an invented path reads like a real one.

## A Rule Change Is Delivery Work

Compare both the intended behaviour and the file-impact tree with the repository's rules; changing what a gate,
validator, or hook accepts changes a rule. Each such change adds the
[Rules Propagation](../../../repo-governance/workflows/maintenance/rules-propagation.md) outcome to the delivery unit
making it, as concrete items per repository and action. One item reading "propagate the rules" can never be ticked
honestly.

A delivery unit that changes what a README, documentation page, or specification describes also carries a Docs
Propagation item, landing in the same commit as the change.

## Interface Plans Widen Before They Narrow

An interface-changing plan draws genuinely different alternatives before choosing, per Plan UI Design and
[Interface Alternatives](../../../repo-governance/development/quality/manual-verification/004-interface-alternatives.md).
Judgement sharpens the alternatives: inventory the components and tokens already present, so they are reused; study how
comparable products handle the task, so alternatives are informed; and judge each candidate on the smallest device class
it must serve first, since a layout that only works wide cannot be the selected alternative.

## Code Items Show the Test Failing First

Items shipping executable behaviour follow the test-first grammar recorded under
[Phase Boundaries and Delivery Choices](../../../repo-governance/conventions/structure/plans/011-phase-boundaries-and-delivery-choices.md).
Under the split cycle, red, green, and refactor are separate items naming test path, command, and expected result,
repeated per behaviour. Under either choice the item names the test before the production path, as
[Test-Driven Development](../../../repo-governance/development/quality/testing/test-driven-development.md) requires.
