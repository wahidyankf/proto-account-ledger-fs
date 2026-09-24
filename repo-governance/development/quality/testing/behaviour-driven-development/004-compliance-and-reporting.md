---
description: >-
  Separates static binding compliance from semantic review, places each scenario check in its gate, and requires a
  generated per-feature status report built from runner and binding evidence.
when_to_use: >-
  Use when configuring behaviour-driven development gates, deciding which scenario checks run in hooks, or publishing
  the scenario status of a feature.
---

# Compliance and Reporting

Green bindings prove that steps resolve and pass. They do not prove that a scenario's words match what the code does,
and that takes a different check.

## Static Compliance Is Not Semantic Proof

Static compliance resolves every step to its binding and applies the limits in
[Bindings and Exemptions](003-bindings-and-exemptions.md). It neither executes scenarios nor judges whether a binding
tests what its sentence says.

After a material change to scenarios or to their implementation, run the Gherkin Implementation Review. It checks the
scenarios against the real behaviour of the implementation and its tests, across every applicable layer and every part
of the corpus the change reaches, not only the files that changed.

## Each Check in Its Gate

Placement uses the surfaces
[Surfaces and Mutation](../../../../conventions/structure/repository-configuration/003-surfaces-and-mutation.md)
declares.

| Check                                | Runs                                                                                                                       |
| ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| unit scenarios                       | at `pre-push` for what the pushed commits affect, and in `ci`                                                              |
| static compliance                    | at `pre-push` for what the pushed commits affect, and in `ci`                                                              |
| integration and end-to-end scenarios | for affected scenarios before completion, and in full in `ci` or a scheduled `ci` run; never at `pre-commit` or `pre-push` |
| semantic review                      | after a material change to scenarios or implementation, before completion                                                  |

Integration and end-to-end runtime stays out of hooks for the reason End-to-End Testing gives: a slow hook gets
bypassed.

A repository with no `ci` surface runs unit scenarios where the option it records under
[Automated Quality Gates](../../checks/automated-quality-gates.md) places fast tests, which may be `pre-commit`. Its
integration and end-to-end scenarios still stay out of hooks and run for affected scenarios before completion. It
records when it makes the full run its status report is produced from.

## Generated Status Report

Each feature has a status report generated from runner results and binding evidence, never written by hand. For every
scenario and layer it shows passed, failed, or exempt, with the recorded reason for an exemption.

A hand-maintained status table reports what someone believed. A generated one reports what ran, so it is produced from
the latest full run.

## Manual Confirmation at the Boundary

Scenarios do not replace a person checking the running system. A behaviour change still receives the direct checks in
[Behaviour Change Verification](../../manual-verification/006-behaviour-change-verification.md), and an API change the
request that API Testing requires.
