---
description: >-
  Requires every material decision in a plan to record its selected option, viable alternatives, prior art,
  consequences, and the trigger that would reopen it.
when_to_use: >-
  Use when writing a plan's technical shape, or when reviewing whether a plan's reasoning survives without its author.
---

# Decision Records

A plan records the route from evidence to delivery completely enough that a reader with no context — new to the
repository, its stack, and the conversation that produced the plan — can follow why the delivery is shaped as it is
without asking anyone. [Documentation First](../../../principles/documentation-first.md) says a decision records its
context, choice, rejected alternatives, and consequences; this module fixes what that means inside a plan.

## What Counts as Material

A decision is material when it changes the delivered product, architecture, implementation contract, delivery boundary,
rollout, operation, testing strategy, or recovery behaviour.

The plan's own authoring history is not material. Rewordings, moved sections, review findings, and drafting order belong
to version control and review threads. A record listing rejected phrasings as alternatives has become a changelog, and
it buries the decisions a reader needs.

## What Each Record Holds

| Element         | Holds                                                                            |
| --------------- | -------------------------------------------------------------------------------- |
| evidence        | the current state and the constraints the choice responds to                     |
| selected option | what was chosen                                                                  |
| alternatives    | at least two other viable options, including the status quo where it is viable   |
| prior art       | what the repository and its history already do, then relevant external precedent |
| trade-offs      | what each option costs, and why each rejected one lost                           |
| consequences    | what the choice commits the repository to                                        |
| revisit trigger | the observable condition that would reopen the choice                            |

Records live in the technical shape, beside the design they justify. Many come out of the
[Decision Gates](../../../development/agents/planning-capabilities/003-decision-gates.md); the record is how a gate's
outcome stays readable once the conversation is gone.

## Alternatives Are Searched, Not Invented

Search the repository first — its documents, its history, its archived plans — then cite applicable external precedent.
Where fewer than three viable options exist, record the search and the constraints that disqualify what is missing.

Never fabricate an alternative to meet the count. A straw option exists to lose, and a record containing one teaches the
reader that the other options may be straw as well.

## Why the Revisit Trigger

A decision without a trigger is either treated as permanent or re-argued whenever someone dislikes it. Naming the
condition — a volume threshold, the end of a dependency's support, a constraint lifted — lets a later reader tell a
choice that still holds from one whose premise has expired.

## Where the Teaching Lives

The technical shape and `delivery.md` carry the teaching; the other documents orient. A summary cannot compensate for a
technical shape that leaves the design unexplained, or for a checklist that leaves an action underspecified.

Define repository and domain terms where they first appear. Show the current and target flows wherever prose would force
the reader to reconstruct them. Leave no product, security, data, migration, interface, testing, rollout, or rollback
behaviour for the executor to invent.

## Example

A storage decision compares keeping the existing store, extending it, and introducing a new one. It states how each
could meet the goal, why one was selected, the operational consequence, and the load at which the choice would be
reopened. "The new store is best" records nothing a reviewer can disagree with.

Plan quality review judges these records. No structural validator can tell a viable alternative from a straw one.
