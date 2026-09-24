---
description: >-
  Rates every validation finding on two independent scales, criticality for how much it matters and confidence for how
  certain its fix is, and combines them into one order of work.
when_to_use: >-
  Use when a checker reports findings, when a fixer or repair pass decides which findings to apply, or when deciding
  whether a finding blocks completion.
---

# Finding Criticality and Confidence

A finding answers two questions that are easy to run together. Criticality asks how much the problem matters. Confidence
asks how certain the one applying a fix is that the finding is real and the fix is safe. A critical finding can be
doubtful and a trivial one certain, so the two are rated separately and combined only to decide order.

This standard implements [Explicit Over Implicit](../../../principles/explicit-over-implicit.md),
[Evidence Over Assertion](../../../principles/evidence-over-assertion.md), and
[Automation Over Manual](../../../principles/automation-over-manual.md).

## Who Rates What

| Scale       | Rated by                                               | Values                              |
| ----------- | ------------------------------------------------------ | ----------------------------------- |
| criticality | the checker that reports the finding                   | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW` |
| confidence  | whoever applies findings, after re-validating each one | `HIGH`, `MEDIUM`, `FALSE_POSITIVE`  |

The checker cannot rate confidence. It cannot know whether the file has changed since it looked, or whether a reading it
was sure of turns out ambiguous in context; only a fresh look at the current state can tell.

## Shared Scales Make Findings Comparable

When every checker uses the same four levels, findings from a link checker and from an accessibility review can be
merged, sorted, and gated by one rule. A private scale per checker forces every consumer to translate, and translations
disagree.

## Modules

1. [Criticality Levels](finding-criticality-and-confidence/001-criticality-levels.md)
2. [Confidence and Re-Validation](finding-criticality-and-confidence/002-confidence-and-revalidation.md)
3. [Priority and Reporting](finding-criticality-and-confidence/003-priority-and-reporting.md)
