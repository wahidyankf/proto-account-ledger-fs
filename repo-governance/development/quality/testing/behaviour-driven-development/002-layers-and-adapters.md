---
description: >-
  Defines the unit, integration, and end-to-end layers that bind the scenario corpus, how a test is classified, which
  test targets each project role carries, and the layer choices an adopter records.
when_to_use: >-
  Use when deciding which layer a test belongs to, which test targets a project needs, or whether integration tests may
  open a loopback listener or must meet a coverage threshold.
---

# Layers and Adapters

Each layer binds the same scenarios through its own adapter and proves them against a different boundary. Classifying a
test honestly is what gives its result a meaning.

## Three Layers

| Layer       | Boundary                                                           | Rule                                                       |
| ----------- | ------------------------------------------------------------------ | ---------------------------------------------------------- |
| unit        | in process, with every operating-system-facing dependency injected | mandatory for every scenario, with no exemption            |
| integration | real local resources the test starts and owns, isolated per run    | no external network, and no service the test did not start |
| end-to-end  | the real public boundary, with synthetic data                      | governed by End-to-End Testing                             |

The unit layer is never exempt because it is the only one cheap enough to run on every change. A scenario without a unit
binding has no fast signal at all.

## Classify by the Strongest Boundary

A test belongs to the layer of the strongest real boundary it touches, whether in setup, in the subject, or in an
assertion. A unit test that reads a real file is an integration test. An integration test that calls an outside service
is an end-to-end test, or a defect.

A misclassified test runs in the wrong gate and breaks the speed and isolation promises of the layer it claims.

## Targets Follow the Project Role

| Project role                 | Test targets it carries                                                                    |
| ---------------------------- | ------------------------------------------------------------------------------------------ |
| application or service       | unit; integration where it owns local resources; end-to-end here or in a dedicated project |
| library                      | unit; integration where it touches real resources                                          |
| executable tool              | unit; integration where it touches real resources; end-to-end through the built executable |
| dedicated end-to-end project | end-to-end only, implementing the corpus of the owner it tests                             |

Omit a target the project cannot meaningfully run, and document the omission. Each project's README names its scenario
corpus, adapters, and test targets, and states every omitted target or inapplicable layer with its reason, so an absence
reads as a decision rather than a gap.

Never define a target that only prints a message or exits successfully without testing anything: a no-op target reports
coverage that does not exist.

## This Repository's Binding

No scenario corpus exists here (see the parent standard's binding), so each layer proves plain pytest tests: read "every
test" wherever this module says "every scenario", and "its tests" for its scenario corpus.

## Adopter Decisions

| Decision                         | Option                                                | Gains                                | Costs                                              |
| -------------------------------- | ----------------------------------------------------- | ------------------------------------ | -------------------------------------------------- |
| loopback listener in integration | allowed when the test starts, owns, and allowlists it | request handling is proven early     | port collisions and slower runs to manage          |
|                                  | forbidden, leaving network use to end-to-end          | integration stays fast and hermetic  | request handling is proven only end-to-end         |
| coverage threshold               | a fixed line-coverage floor on unit tests             | untested code is visible and blocked | tests get written to the number, not the behaviour |
|                                  | no numeric floor, with review judging adequacy        | no metric to game                    | gaps depend on reviewer attention                  |

Record each choice. An unrecorded choice is made differently by every contributor. The adopter enforces a recorded
threshold in its own gate or CI.
