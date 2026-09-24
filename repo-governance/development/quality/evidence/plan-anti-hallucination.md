---
description: >-
  Requires every factual claim in an agent-authored or agent-checked plan to be grounded in the repository or a cited
  source, labelled with its confidence, or refused, and sets the evidence absence and completeness claims need.
when_to_use: >-
  Use when writing, reviewing, or validating a plan, or whenever a check reports that something is absent, that nothing
  matches, or that a list is complete.
---

# Plan Anti-Hallucination

A plan is read as a statement of fact about the repository it will change. A path, command, flag, test name, or number
that sounds right but was never checked becomes a delivery item nobody can execute, or one that quietly does something
else.

This standard implements [Evidence Over Assertion](../../../principles/evidence-over-assertion.md),
[Explicit Over Implicit](../../../principles/explicit-over-implicit.md), and
[Fail Closed](../../../principles/fail-closed.md).

## Scope

Grounding and labelling bind every factual claim about the repository, its tools, or external facts in a plan that an
agent writes or checks. Goals, scope choices, and rationale are decisions rather than facts, and need no verification
label. The rules for absence and completeness bind any checker, person or agent, that reports something missing,
unmatched, or complete, in a plan or anywhere else.

## Verify, Label, or Refuse

Every factual claim ends in one of three states: verified, and labelled with how; labelled honestly as a judgement or as
unverified; or left out. No fourth state exists. An unlabelled factual claim that nobody checked is exactly what this
standard forbids.

Fluent text is not evidence. The more plausible an invented reference sounds, the less likely a reviewer is to check it,
so the check has to happen when the claim is written.

## Related Standards

- The [Plans](../../../conventions/structure/plans.md) convention and its
  [Evidence and Quality](../../../conventions/structure/plans/007-evidence-and-quality.md) module govern the plan these
  claims appear in.
- The [`plan-validating-quality`](../../../../.agents/skills/plan-validating-quality/SKILL.md) and
  [`plan-verifying-execution`](../../../../.agents/skills/plan-verifying-execution/SKILL.md) skills apply these checks
  during plan review and execution review.

## Modules

1. [Grounding and Labels](plan-anti-hallucination/001-grounding-and-labels.md)
2. [Absence and Completeness](plan-anti-hallucination/002-absence-and-completeness.md)
3. [Anti-Pattern Examples](plan-anti-hallucination/003-anti-pattern-examples.md)
