---
description: >-
  Defines a valid red, green, and refactor step, how large one cycle is, how a new harness or gate proves it can fail,
  and what each step records as evidence.
when_to_use: >-
  Use while running a test-first cycle, when a red fails for an unexpected reason, or when recording what a cycle
  observed.
---

# Cycle and Evidence

## Read the Tests First

Before interpreting or changing production code, read the tests that cover it. They state intended behaviour, its
limits, and its boundaries more exactly than the code does. They stay trustworthy only while tests, their support code,
and the behaviour they describe change together.

## A Red Shows the Behaviour Is Missing

A red counts only when the new test fails on an assertion about the missing behaviour while every previously passing
test still passes. A compile error, a missing import or binding, a wrong fixture, or broken configuration or
infrastructure does not produce a red. It produces a broken test, and nothing built on top of it says anything about the
change.

A new test that passes before the code exists checks nothing. Repair the test until it fails for its stated reason, and
never move to green from a vacuous pass.

## A Green Is the Smallest Honest Change

Green adds only what the failing test demands. It never passes through a hard-coded result, a success sentinel, or a
production path that skips the logic under test. Nothing else is improved while red becomes green, because a refactor
folded into green hides which edit made the test pass.

## A Refactor Changes Shape, Not Behaviour

Refactoring begins only from green, moves in small steps, and runs the tests after each one. A test that goes red during
a refactor marks a defect the refactor introduced, not a planned failure. A behaviour change noticed along the way is a
new cycle with its own red.

## Small Cycles

Split a feature or a fix into cycles that each cover one behaviour: the simplest case first, then each edge case, error,
and boundary in turn. A cycle covering several behaviours hides which one a failure belongs to. A long run of cycles is
the normal shape of real work, not a reason to merge them. A cycle whose work outlasts a few minutes is split.

```text
red: empty input is rejected          -> green -> refactor
red: input missing its separator fails -> green -> refactor
red: well-formed input is accepted    -> green -> refactor
```

After the final cycle, run the fast gate from [Test Boundaries and Gates](../test-boundaries-and-gates.md) to catch
regressions elsewhere. A deliberately failing test is evidence in progress during red, never a finished state.

A behaviour that is checked by hand follows the same order: write the expected observations, observe them fail, change
the code, and repeat the whole check. Automate it once automating it is cheap.

## A New Harness Needs Its Own Red

A cycle proves a test case. It proves nothing about a new harness, driver, runner, or gate the case runs inside, and
such a harness can pass while exercising nothing: asserting on a process it never started, loading a stale build, or
binding no scenarios at all. Prove it in reverse. Break the behaviour or remove the fix, run the check, watch it fail,
and restore. Keep the failing run as the evidence, since a broken harness also produces the passing one.

The same demonstration proves a change to a script or a gate. A check that stays green under the mutation does not cover
the change. [Deletion With Proof](../../deletion-with-proof.md) asks for the same demonstration before a removal.

## What Each Step Records

| Step     | Records                                                                           |
| -------- | --------------------------------------------------------------------------------- |
| red      | the test path, the command run, the failure message, and why it was meant to fail |
| green    | the command and its passing output                                                |
| refactor | the command and its passing output after the last refactoring step                |

"Tests pass" is a claim, and so is "tested locally"; the command with its observed output is evidence. Automation proves
the final state of a suite, not the order it was built in, so only these records show that the test failed before the
change.

How each step becomes a task item is owned by [List Lifecycle](../../../agents/task-tracking/001-list-lifecycle.md). How
a plan's delivery item carries a cycle is an adopter choice under
[Phase Boundaries and Delivery Choices](../../../../conventions/structure/plans/011-phase-boundaries-and-delivery-choices.md).
