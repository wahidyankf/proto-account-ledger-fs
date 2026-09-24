---
description: >-
  States what each test boundary excludes, keeps the layers in separate suites, builds gates from named targets, and
  fixes what the fast gate holds, how gating coverage is measured, and which choices an adopter records.
when_to_use: >-
  Use when classifying a test, defining a project's test targets, composing the fast gate, or deciding where coverage is
  measured and where a slow suite runs.
---

# Test Boundaries and Gates

A test result means something only when the test sits where it claims to. A unit test reading a real file is slow,
order-sensitive, and running in a gate that promised neither.

This standard implements [Reproducibility](../../../principles/reproducibility.md),
[Explicit Over Implicit](../../../principles/explicit-over-implicit.md), and
[Automation Over Manual](../../../principles/automation-over-manual.md). The three layers, classification by the
strongest boundary a test touches, the loopback choice, and whether a coverage floor exists are owned by
[Layers and Adapters](behaviour-driven-development/002-layers-and-adapters.md).

## What Each Boundary Excludes

| Layer       | Never                                                                                                               |
| ----------- | ------------------------------------------------------------------------------------------------------------------- |
| unit        | touches a real filesystem, database, environment, clock, random source, child process, or network; each is injected |
| integration | reaches an external network, drives a browser, or observes the served origin; it uses only local resources it owns  |
| end-to-end  | calls an external service nobody controls without explicit authorization                                            |

The unit exclusion covers setup and assertions as well as the subject. End-to-end means observing the public boundary,
not permission to use more resources.

## Keep the Suites Apart

Unit, integration, and end-to-end tests live in separate trees or targets, so a gate selects one layer without filtering
by name. Support that never executes on its own, such as contracts, bindings, and fixtures, may be shared.

## Gates Compose Named Targets

Each layer and each static check is its own named target. Aggregate gates compose those names instead of repeating their
commands, because a copied command drifts from the original.

| Target                        | Holds                                                                                                            |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| lint                          | formatting, style, suspicious-code, and dependency findings, per [Lint Strictness](../checks/lint-strictness.md) |
| type check                    | compiler and static-type findings, leaving no build output behind                                                |
| unit, integration, end-to-end | one layer's suite each; the unit run also measures coverage                                                      |
| static behaviour coverage     | scenario and binding resolution, executing nothing, where scenarios exist                                        |

## The Fast Gate

The fast gate runs type check, lint, unit with coverage, and static behaviour coverage, in that order, so the cheapest
failure to read comes first. It runs before a push over what the change affects, and after the last cycle of
[Test-Driven Development](test-driven-development.md). A dedicated end-to-end project's fast gate holds only its type
check, lint, and static behaviour coverage.

It never runs an integration or end-to-end suite. Those run where
[Compliance and Reporting](behaviour-driven-development/004-compliance-and-reporting.md) places them, with integration
ahead of the complete end-to-end run, so a local failure surfaces before the slower journeys that depend on it.

## Coverage Is Measured Where It Gates

Gating coverage comes from the run that executed the tests, because two runs can disagree. Each module excluded from
measurement is named in the project's README, with the reason a test at that layer may not reach it.

Lowering a floor or widening an exclusion changes what the repository is willing to ship. It is a change to a gate, made
as Software Quality Enforcement requires.

## Adopter Decisions

| Decision              | Option               | Gains                                         | Costs                                             |
| --------------------- | -------------------- | --------------------------------------------- | ------------------------------------------------- |
| layers a floor covers | unit only            | the floor stays inside the fast gate          | code that only real resources reach is unmeasured |
|                       | unit and integration | real-boundary code is measured as well        | a second floor, run outside the fast gate         |
| task runner           | a task-graph tool    | affected selection and ordering come built in | one more tool to pin and maintain                 |
|                       | plain scripts        | nothing beyond the language toolchain         | affected selection is maintained by hand          |

Record each applicable choice. Each project's README names the commands its targets resolve to, and every omitted target
with its reason.

## Enforcement

A failing gate is fixed at its cause, never weakened or bypassed. Review applies the classification as tests change, and
a validator for it is added only when Repository Check Policy admits one. The adopter enforces the gate contracts in its
own task configuration and `ci`.
