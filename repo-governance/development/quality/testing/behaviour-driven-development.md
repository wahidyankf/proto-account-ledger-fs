---
description: >-
  Makes one canonical Gherkin corpus per behaviour owner the statement of acceptance behaviour, bound strictly at every
  applicable test layer, with each scenario written before the code that satisfies it.
when_to_use: >-
  Use when adding or changing observable behaviour, organizing feature files, binding scenarios to tests at a layer, or
  deciding whether a scenario may be exempt from a layer.
---

# Behaviour-Driven Development

Behaviour is agreed as examples before it is built, and the same examples then drive every test layer able to prove
them. One written scenario, bound strictly, replaces several descriptions of intent that drift apart.

This standard implements [Explicit Over Implicit](../../../principles/explicit-over-implicit.md),
[Documentation First](../../../principles/documentation-first.md),
[Automation Over Manual](../../../principles/automation-over-manual.md), and
[Evidence Over Assertion](../../../principles/evidence-over-assertion.md).

## One Corpus Per Behaviour Owner

Each behaviour owner, whether an application, a library, or a tool, keeps one canonical Gherkin corpus in one directory
tree, discovered recursively. Nothing registers feature files in a list; a list is a second source that falls out of
date the first time someone forgets it.

A dedicated end-to-end project implements the corpus of the owner it tests. It keeps no scenarios of its own, so a
behaviour never has two competing statements.

## Scenario First, Then Code

For every behaviour change:

1. Read the scenarios that already describe the behaviour.
2. Add or update the scenario so it states the new behaviour.
3. Bind its steps in every applicable layer.
4. Run them and confirm they fail for the expected reason.
5. Implement until they pass.

A step that passes before the code exists proves only that its binding checks nothing.

A refactor that changes no behaviour leaves every scenario unchanged and starts from a passing run. Where no scenario
covers the code, a characterization test first records its current behaviour, so the refactor has something to preserve.

## Modules

1. [Discovery and Scenarios](behaviour-driven-development/001-discovery-and-scenarios.md)
2. [Layers and Adapters](behaviour-driven-development/002-layers-and-adapters.md)
3. [Bindings and Exemptions](behaviour-driven-development/003-bindings-and-exemptions.md)
4. [Compliance and Reporting](behaviour-driven-development/004-compliance-and-reporting.md)
