---
name: red-green-refactor
description: >-
  Runs each behaviour increment through a red, green, and refactor cycle on the narrowest test target, recording the
  failing, passing, and refactored runs before the item closes.
when_to_use: >-
  Use for each behaviour increment Test-Driven Development requires, including a bug fix or a change to a script or
  gate.
---

# Red, Green, Refactor

## Entry

A change alters executable behaviour within the scope of
[Test-Driven Development](../../development/quality/testing/test-driven-development.md), the specifications it could
affect were assessed per Specification Maintenance, and any scenario that specifies the behaviour was added or updated
first per [Behaviour-Driven Development](../../development/quality/testing/behaviour-driven-development.md).

- `behaviours` (`string`, required): the increments, each one observable behaviour, simplest first.
- `target` (`string`, required): the narrowest test target that can demonstrate them.
- `evidence` (`string`, optional, default the change's delivery record): where each run is recorded.

## Sequence

1. **List the increments** before the first test, each small enough for one cycle. A behaviour discovered during a cycle
   is appended as a new increment, never folded into the cycle in flight.
2. **Read the tests that cover the code** before changing it, per
   [Cycle and Evidence](../../development/quality/testing/test-driven-development/001-cycle-and-evidence.md).
3. **Red: write one test and watch it fail.** Run `target` and confirm the new test fails on an assertion about the
   missing behaviour while every previously passing test still passes. A compile error, missing binding, wrong fixture,
   or broken harness is repaired first and never counts as red. Record the test path, command, failure message, and why
   it was meant to fail.
4. **Red for a script, gate, or new harness: mutate.** Remove the fix or break the behaviour, run the check, record its
   failure, and restore. A check that stays green under the mutation does not cover the change.
5. **Green: make the smallest honest change.** Change only what the failing test demands, with no hard-coded result and
   no path that skips the logic under test. Run the same target and record the new test and its neighbours passing.
6. **Refactor with every test green.** Improve names, structure, and duplication without adding behaviour, in small
   steps, running `target` after each, and record the last passing run. A test turning red here marks a defect the
   refactor introduced.
7. **Repeat from step 3** for the next increment.
8. **Run the fast gate** from
   [Test Boundaries and Gates](../../development/quality/testing/test-boundaries-and-gates.md) after the final cycle.
9. **Close the item on evidence.** Every increment carries its red, green, and refactor records in `evidence`. "Tests
   pass" or "tested locally" without the command and its output closes nothing.

## Exit

Every increment has a recorded red that failed for its stated reason, a green run, and a refactor-green run, and the
fast gate passed.

Outputs: `cycle-records` (`table` in `evidence`: one row per increment with test path, command, expected red reason,
observed red, green, and refactor-green) and the fast-gate run (`record`, command and exit status).

Partial outcome: an increment whose red cannot be reached because the harness or environment is broken stops with its
diagnosis recorded. Finished increments stand, and no later increment starts on the broken harness.

## Example Usage

```text
Run red-green-refactor with behaviours "empty input is rejected; input missing its separator fails; well-formed input is accepted" and target "parser unit tests".
```

## Related Workflows

- Gherkin Implementation Review checks that each scenario's test fails when its behaviour breaks.
- Exploratory and Usability Review judges the user-facing result once automated checks are green.

## Why Watch It Fail

A green run looks the same whether a test checks the behaviour, something nearby, or nothing. Only a failure observed
before the change, for the reason the test states, shows the test can detect the behaviour's absence, and only the
recorded run proves that order afterwards, since a gate sees just the final state. Each run is bounded by its increment
list. This workflow implements [Evidence Over Assertion](../../principles/evidence-over-assertion.md) and
[Deliberate Problem-Solving](../../principles/deliberate-problem-solving.md).
