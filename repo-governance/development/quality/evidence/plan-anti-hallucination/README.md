---
description: >-
  Indexes the ordered modules on grounding and confidence labels, evidence for absence and completeness claims, and
  supporting anti-pattern examples for plans.
when_to_use: >-
  Use to locate the module covering how a plan claim is grounded, labelled, refused, or proven absent or complete.
---

# Plan Anti-Hallucination Modules

The modules below are read in sequence and carry the detail behind the
[Plan Anti-Hallucination](../plan-anti-hallucination.md) entrypoint.

| Module                                                      | Holds                                                                        |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------- |
| [Grounding and Labels](001-grounding-and-labels.md)         | reference grounding, the four labels, refusal order, and checks per claim    |
| [Absence and Completeness](002-absence-and-completeness.md) | zero-result evidence, completeness diffs, concept sweeps, and real tool runs |
| [Anti-Pattern Examples](003-anti-pattern-examples.md)       | invented references and invented evidence, each with its catching check      |

## Directory Map

- [001 Grounding and Labels](001-grounding-and-labels.md)
- [002 Absence and Completeness](002-absence-and-completeness.md)
- [003 Anti-Pattern Examples](003-anti-pattern-examples.md)
