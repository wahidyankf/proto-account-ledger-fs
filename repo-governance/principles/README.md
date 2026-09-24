---
description: >-
  Indexes the principles layer, which holds the durable constraints this catalog applies everywhere and argues for
  nowhere else.
when_to_use: >-
  Use when locating a principle, or when deciding whether a rule is durable enough to belong at this level rather than
  in a convention.
---

# Principles

A principle is true regardless of which repository is reading it. A convention below this level records a choice that
could reasonably have gone the other way; a principle records something that could not.

Everything here was **discovered rather than declared**. Each of these was already load-bearing in several artifacts
before it had a page, and each page names where — a principle with no existing application is a preference that has been
promoted.

| Principle                                                   | Holds                                                                                                    |
| ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| [Fail Closed](fail-closed.md)                               | a control that cannot decide refuses, and never reports a clean run                                      |
| [One Source Per Fact](one-source-per-fact.md)               | every fact has one place; a second copy is a scheduled contradiction                                     |
| [Evidence Over Assertion](evidence-over-assertion.md)       | a claim is worth nothing until something outside it agrees                                               |
| [Minimal Sufficiency](minimal-sufficiency.md)               | carry what the purpose or the change requires, and record what was left out                              |
| [Accessibility First](accessibility-first.md)               | content is usable by every intended reader from its first draft                                          |
| [Automation Over Manual](automation-over-manual.md)         | recurring rule-bound work goes to machines; judgement stays with people                                  |
| [Consumer Independence](consumer-independence.md)           | a shared tool holds none of its consumers' answers and never guesses one                                 |
| [Deliberate Problem-Solving](deliberate-problem-solving.md) | state assumptions, surface readings, inspect before asking, then act                                     |
| [Documentation First](documentation-first.md)               | knowledge is written down when it becomes true, why as well as what                                      |
| [Explicit Over Implicit](explicit-over-implicit.md)         | behaviour a reader depends on is written down, never left to a default                                   |
| [Governance Continuity](governance-continuity.md)           | rules, authority, and state survive context loss unchanged                                               |
| [Immutability](immutability.md)                             | what others can observe gets a new value, never an in-place change                                       |
| [Progressive Disclosure](progressive-disclosure.md)         | a reader reaches the rule for the task in hand without reading the rest                                  |
| [Pure Functions](pure-functions.md)                         | decide without effects, and carry out the decision at a thin edge                                        |
| [Reproducibility](reproducibility.md)                       | a clean checkout reaches the same environment and result on any machine meeting documented prerequisites |
| [Root Cause Orientation](root-cause-orientation.md)         | fix the cause at the layer that owns it; a hidden symptom is not a fix                                   |
| [Simplicity Over Complexity](simplicity-over-complexity.md) | the fewest concepts that do the job; abstraction waits for a real need                                   |

## What Is Not Here

Bounded repetition is not a principle here. It is owned as a development standard by
[Bounded Convergence](../development/workflow/bounded-convergence.md), which states it once and completely — and
restating it at this level would break the second principle on the list above.

Portability is not here either. [Portability](../conventions/structure/plans/009-portability.md) owns it for the plan
system and this repository's instructions own it for the catalog, which is two places already.

## Directory Map

- [Fail Closed](fail-closed.md)
- [One Source Per Fact](one-source-per-fact.md)
- [Evidence Over Assertion](evidence-over-assertion.md)
- [Minimal Sufficiency](minimal-sufficiency.md)
- [Minimal Sufficiency Modules](minimal-sufficiency/README.md)
- [Accessibility First](accessibility-first.md)
- [Automation Over Manual](automation-over-manual.md)
- [Consumer Independence](consumer-independence.md)
- [Deliberate Problem-Solving](deliberate-problem-solving.md)
- [Documentation First](documentation-first.md)
- [Explicit Over Implicit](explicit-over-implicit.md)
- [Governance Continuity](governance-continuity.md)
- [Immutability](immutability.md)
- [Progressive Disclosure](progressive-disclosure.md)
- [Pure Functions](pure-functions.md)
- [Reproducibility](reproducibility.md)
- [Root Cause Orientation](root-cause-orientation.md)
- [Simplicity Over Complexity](simplicity-over-complexity.md)
