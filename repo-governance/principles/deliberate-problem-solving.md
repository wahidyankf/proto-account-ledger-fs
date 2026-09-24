---
description: >-
  States that before acting on a problem its assumptions are made explicit, its readings, valid approaches, and a
  simpler option are surfaced with their trade-offs, and confusion stops the work, resolved by inspection before any
  question.
when_to_use: >-
  Use before implementing a nontrivial change, when a request admits more than one reading, or when work rests on an
  assumption nobody checked.
---

# Deliberate Problem-Solving

Understand the problem before solving it. An assumption is stated, an ambiguity is surfaced, and confusion stops the
work rather than being guessed past.

## The Expensive Mistake Is the Early One

A wrong assumption costs nothing on the day it is made and everything built on it afterwards. An integration written
against the format its author expected, rather than the one the interface documents, is not repaired; it is rewritten. A
request read one way and delivered is not partly right when the requester meant the other. It is the wrong thing,
finished.

Few of these mistakes come from not thinking. They come from thinking silently: the choice was made, just not anywhere
someone could see it and disagree.

## What It Requires

| Practice                                                                                                                    | Instead of                                        |
| --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| state each assumption the work depends on, and verify those that can be verified                                            | proceeding on what is probably true               |
| name every reasonable reading of a request, and every valid approach where several exist, each with what it gains and costs | picking one and presenting it as the only option  |
| say so when a simpler approach meets the need, before building the complex one                                              | defaulting to whatever felt most thorough         |
| stop when something is unclear, and name exactly what                                                                       | guessing and hoping the result reveals the answer |

A clear request does not settle its approach. Where several valid approaches exist, each is presented with what it gains
and what it costs before one is chosen.

## Inspect Before Asking

Stopping is not the same as asking. Most confusion is resolved by reading: the repository, its instructions, the
interface's own documentation, the code that already does something similar. A question the available material already
answers spends someone else's attention on work that was skipped.

So the order is fixed. Inspect first. What inspection resolves is stated as a verified fact, with where it came from.
Only what remains — a choice with more than one defensible answer, an intent only the requester holds — is asked, and
precisely: what is undecided, and what depends on the answer. The format for putting such a choice to someone is a
convention; [Decision Gates](../development/agents/planning-capabilities/003-decision-gates.md) fixes one.

## Where It Is Already Load-Bearing

| Applied in                                                                          | As                                                                           |
| ----------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| [Decision Gates](../development/agents/planning-capabilities/003-decision-gates.md) | inspect first, then offer exclusive choices with exactly one recommendation  |
| [Grill Me](../../.agents/skills/grill-me/SKILL.md)                                  | a material choice is resolved openly, not settled by whoever writes first    |
| [Planning](../workflows/plan/plan-planning.md)                                      | no plan document is written until every material branch is resolved          |
| [Adopt Artifact](../workflows/adoption/adopt-artifact.md)                           | ambiguous resolution stops, and a contradiction is reported, never absorbed  |
| [Assess Alignment](../workflows/adoption/assess-alignment.md)                       | the target's own instructions are read before anything is compared           |
| [Backlog Grooming](../workflows/plan/plan-backlog-grooming.md)                      | each plan is re-read against the current repository, because assumptions age |

## Proportion

This is not analysis without end. A small, reversible change with one obvious reading needs no interview, and demanding
one is ceremony that teaches everyone to ignore the next real question. The weight of deliberation scales with the cost
of being wrong.

Nor is it a way to avoid deciding. Surfaced options end in a recommendation, and a recommendation ends in action. When
the simpler option is enough, it is the one to build — see [Minimal Sufficiency](minimal-sufficiency.md). When a stated
assumption can be checked, it is checked, and the check is what counts — see
[Evidence Over Assertion](evidence-over-assertion.md).
