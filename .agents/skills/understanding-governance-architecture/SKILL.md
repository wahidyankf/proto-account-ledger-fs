---
name: understanding-governance-architecture
description: >-
  Guides reading a governed repository as ordered levels, tracing any rule up to the principle behind it, and treating
  skills and agents as delivery forms rather than levels.
when_to_use: >-
  Use when orienting in a governed repository, tracing why a rule exists, or deciding where new guidance belongs.
compatibility: Requires read access to the repository's governance indexes.
---

# Understanding Governance Architecture

[Repository Governance](../../../repo-governance/README.md) orders the levels,
[Governance Layers](../../../repo-governance/conventions/structure/governance-layers.md) decides where a document
belongs and which level wins a conflict, and Principle Traceability records how each rule traces to a principle. This
skill covers how to use that structure while working in a repository.

## Read Top Down, Explain Bottom Up

Orient from the top: the root index, then the index of the level a task touches. Each level answers a different
question, from why something is valued down to the order work runs in, so the level a document sits at says what kind of
statement to expect from it.

Explain a rule from the bottom: follow a workflow step to the standard or convention it applies, then to the principle
that document names. A rule whose chain stops short of a principle is a preference until someone records its grounding,
and it deserves scrutiny before anything is built on it.

## Skills and Agents Are Not Levels

Skills and agents deliver governance rather than adding to it. A skill teaches the judgement a rule needs, and an agent
carries out a role within a boundary; both link the governing document instead of restating it, as
[Capability Forms](../../../repo-governance/development/agents/capability-forms.md) sets out. A skill that starts
declaring obligations has become a second, unranked source for them.

## Before Changing a Level

- Confirm the level by asking the Governance Layers questions in order, not by where a similar file happens to sit.
- Look below for what depends on the rule, because a change flows down.
- Look above for what the rule implements, because a lower rule never contradicts a higher one.

Repositories number their levels differently, and some keep vision outside the published tree; the order and these
habits hold either way.

## Related

- [understanding-shared-vocabulary](../understanding-shared-vocabulary/SKILL.md) — what individual terms cover; use both
  when placing a new document.
- [propagating-rules](../propagating-rules/SKILL.md) — the route for changing a rule found this way.
