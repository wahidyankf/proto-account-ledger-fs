---
description: >-
  States that a system, rule, decision, or procedure is written down with or before the change that creates it,
  explaining why as well as what, and kept true by every later change.
when_to_use: >-
  Use when a change introduces or alters behaviour, a rule, or a decision, or when documentation is deferred or replaced
  by code said to be readable.
---

# Documentation First

What a repository knows is written down at the time it becomes true. Knowledge that exists only in someone's memory is
on loan, and the loan is called in without notice.

## Later Does Not Arrive

Documentation deferred until after the change competes with the next change and loses. By the time anyone returns to it,
the context that made it easy to write — why this approach, what was rejected, which edge case forced the odd line — is
gone, including from the person who wrote the code.

Written with or before the change, it costs least and does something extra: explaining a design before building it
exposes the parts that do not survive being explained.

## What It Requires

| Kind                  | Records                                                                               |
| --------------------- | ------------------------------------------------------------------------------------- |
| a system or component | what it is, why it exists, how to use it, and where a newcomer starts                 |
| a rule or convention  | the rule, why it is shaped that way, and when it applies                              |
| a decision            | the context, the choice, the alternatives rejected and why, the consequences accepted |
| a public interface    | its inputs, outputs, error conditions, and a usage example                            |
| a procedure           | the entry condition, the ordered steps, what it produces, and what to do on failure   |

A change that alters any of these updates the record in the same change. The documentation is part of the change, not a
follow-up to it.

## Readable Code Does Not Record Intent

Clear code shows what happens. It cannot show why that and not the alternative, which constraint forced the unusual
branch, or which behaviour is deliberate and which is an accident nobody has noticed yet.

`total * 1.15` is perfectly readable, and says nothing about whether the constant is a negotiated rate, a legal figure,
or a placeholder someone meant to replace. A maintainer without that cannot tell what is safe to change. Readable code
is a real virtue for the what, and no excuse for the why. Non-obvious logic records why it is written as it is, where a
maintainer changing it will see the reason.

## Conversation Is Not a Record

A decision reached in a meeting, a chat, or a review thread is undocumented. It cannot be searched, it is not shared
with the next contributor, and it is not there when the question returns — which it does, as "was this considered, or
overlooked?".

## Wrong Documentation Is Worse Than None

A missing page sends a reader looking. A stale one sends them confidently in the wrong direction. That is why updating
is part of every change, why live documentation that has become obsolete is removed or visibly superseded rather than
left to mislead, and why each fact is written in one place and linked from the rest — see
[One Source Per Fact](one-source-per-fact.md).

Recorded history is different. A decision record or an archived plan was true when written, so it is superseded by a new
record, never rewritten to match what is true now.

## Where It Is Already Load-Bearing

| Applied in                                                                                             | As                                                                            |
| ------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------- |
| [Decision Gates](../development/agents/planning-capabilities/003-decision-gates.md)                    | both gates leave a record, because conversation is neither durable nor shared |
| [Knowledge Capture and Archival](../conventions/structure/plans/008-knowledge-capture-and-archival.md) | every learning reaches a durable owner or is discarded with a reason          |
| [Required Documents](../conventions/structure/plans/002-required-documents.md)                         | a plan holds a place for discoveries so they are not lost mid-execution       |
| [Interface Alternatives](../development/quality/manual-verification/004-interface-alternatives.md)     | every rejected alternative records why it lost                                |
| [Exclusions](../conventions/structure/plan-validator-contract/004-exclusions.md)                       | archived plans are history, never rewritten to satisfy a later rule           |
| [Diagrams](../conventions/writing/diagrams.md)                                                         | reversing the authoring rule records the change and its reason                |
| [Portability](../conventions/structure/plans/009-portability.md)                                       | an adopter's divergence is recorded with a reason, never left silent          |
| [Execution](../workflows/plan/plan-execution.md)                                                       | the plan itself carries enough state to resume at any pause                   |
