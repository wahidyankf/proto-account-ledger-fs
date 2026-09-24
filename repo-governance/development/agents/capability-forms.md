---
description: >-
  Defines the four capability forms, gives each a distinct responsibility, fails substantially duplicated instruction
  bodies, and keeps delegation out of skills.
when_to_use: >-
  Use when deciding which form new guidance should take, when two artifacts appear to say the same thing, or when a
  skill appears to hand work to an agent.
---

# Capability Forms

One concern may need several forms. Each form owns a different responsibility, and they compose rather than compete.

| Form           | Owns                                                              | Answers                       |
| -------------- | ----------------------------------------------------------------- | ----------------------------- |
| **convention** | a durable rule                                                    | what must be true             |
| **workflow**   | an ordered procedure with an entry condition and a terminal state | what happens, in what order   |
| **skill**      | reusable judgement                                                | how to do it well             |
| **agent**      | a bounded role with its own tools and stopping rule               | who does it, and when to stop |

These are the executable capability forms. Principles and development standards are governance documents rather than
capability forms, and the test under Choosing a Form sorts guidance only among these four.

## They May Coexist

A single concern legitimately having all four is not duplication. Adoption is a good example: a convention says what
adoption may touch, a workflow says the order, a skill teaches the adaptation judgement, and an agent carries it out
within a boundary.

The test is not how many artifacts exist. It is whether each answers a different question.

## Duplicated Bodies Fail

Two artifacts carrying substantially the same instructions fail review, even when both are individually good.

The cost is not storage. It is that they will drift — one gets improved, the other does not — and nothing decides which
one an agent should have believed. Meanwhile every change to the concern costs two edits, and the second is the one that
gets forgotten.

The usual shape is a workflow that starts explaining how to decide well, or a skill that starts prescribing sequence.
Each has begun doing the other's job.

## Choosing a Form

Ask what kind of statement the guidance is.

If it is true regardless of when you read it, it is a convention. If it only makes sense as a sequence, it is a
workflow. If it is advice for a decision that recurs in different contexts, it is a skill. If it needs its own tools and
its own idea of being finished, it is an agent.

Guidance that does not fit any of them is usually two pieces of guidance.

## Splitting Rather Than Duplicating

When two artifacts overlap, the fix is to decide who owns the overlapping part and have the other link to it.

A link is not a weaker copy. It is the only arrangement in which the guidance can be corrected once.

## Skills Never Delegate

A skill holds judgement. It never spawns an agent, hands work to one, or instructs its reader to.

A skill cannot know where it is loaded. The same skill serves a top-level session and an agent that declared it, and a
harness commonly refuses delegation from inside a delegated context. A skill that delegates therefore works when tried
directly and fails when an agent loads it — in exactly the context nobody tried first.

It is also an undeclared grant. Delegation is the `subagent` capability, and only an agent declares capabilities. A
delegation step inside a skill gives every agent that loads it an ability its own definition does not show.

Where a concern needs delegation, the sequence belongs to a workflow or to the session running it, and the delegating
step to an agent that declares `subagent`. The skill teaches how to do the delegated work well. A delegated agent that
finds work needing further delegation returns it to its caller.

Review enforces this: delegation is phrased too many ways for a text pattern to catch reliably.
