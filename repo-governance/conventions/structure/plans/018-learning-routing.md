---
description: >-
  Keeps a learning that changes what code does out of the plan that found it, and leaves how quickly routed learnings
  land as an adopter decision with each option's trade-off.
when_to_use: >-
  Use when a learning calls for a code change, or when a repository fixes how soon promoted learnings and briefs land.
---

# Learning Routing

[Knowledge Capture and Archival](008-knowledge-capture-and-archival.md) decides where a learning goes. This module adds
two things it leaves open: what happens to a learning whose resolution is a code change, and how soon a routed learning
actually lands.

## A Behaviour Change Is Work

Promotion to the code-comment owner records context a reader needs at one line, and changes nothing the code does. A
learning whose resolution changes what code does — a fix, a refactor, a new capability — is work, not knowledge. Under
Follow-Ups it becomes an idea brief, deduplicated against existing briefs, unless the owner-confirmation choice below
reports it instead. Either way, it never lands in the plan that found it.

Landing it there widens a scope that was reviewed and [authorized](010-authorization-and-execution-record.md) without
it, and its proof rides on a checklist that never planned for it. The change deserves the same review as any other work,
and a brief is how it gets one.

The carve-out is narrow. A defect that stops the current plan from meeting its own acceptance criteria is not a
learning. Fixing it is ordinary execution, recorded in the Execution Record and, where the plan changes, as a revised
item.

Tests need a selection of their own. Routing every test change out of the plan is the stricter reading; this convention
selects a narrower one. A test covering behaviour this plan delivered may land with the plan, because it pins down what
the authorized change already does and widens no reviewed scope. Any other test change follows the behaviour-change
rule.

## When a Routed Learning Lands: an Adopter Decision

A small governance or documentation promotion may land in the plan's own change, while its context is fresh; larger new
work leaves as a follow-up.

Each choice below is made once, in the repository's own plan rules. Whatever is chosen, every entry still reaches one
owner or a reasoned discard before archival, and work never lands in the plan that found it.

| Decision                     | Options                                                                        | Trade-off                                                                                                                                                                                                                                                                              |
| ---------------------------- | ------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| a brief marked ready to plan | wait for the next grooming pass, or allow the owner to request a plan now      | waiting keeps the ideas root the single queue; an immediate request lets an urgent follow-up skip a grooming cycle, and still needs the owner's explicit request                                                                                                                       |
| who files a brief            | the executor files it during triage, or the planning owner confirms each first | executor filing loses nothing, but the ideas root fills with briefs the owner never wanted; owner confirmation keeps that root deliberate, and a follow-up the owner does not confirm is reported to that owner, with the handoff evidence recorded in its entry as its terminal state |

An adopter enforces the behaviour-change rule in its own execution check, which fails a plan whose own change alters
what code does because of a `learnings.md` entry. A test or comment that records behaviour the plan delivered is not
such a change.

## Principles

This module implements [Minimal Sufficiency](../../../principles/minimal-sufficiency.md), because a plan carries the
changes its authorized outcome requires and then stops, and
[Explicit Over Implicit](../../../principles/explicit-over-implicit.md), because each timing choice is recorded once
rather than decided afresh by every executor.
