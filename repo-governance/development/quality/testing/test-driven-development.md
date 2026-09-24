---
description: >-
  Requires new or changed executable behaviour and every bug fix to be built test-first in small red, green, and
  refactor cycles, each red failing for its stated reason and each step leaving evidence.
when_to_use: >-
  Use when starting a change to executable behaviour, fixing a bug, or refactoring, or when deciding whether a change is
  exempt from writing its test first.
---

# Test-Driven Development

Nobody knows how a test fails until someone has watched it fail. It may check the behaviour, check something nearby, or
check nothing, and a green run looks identical in all three cases. Writing the test first and observing it fail is the
cheapest way to find out which.

This standard implements [Evidence Over Assertion](../../../principles/evidence-over-assertion.md),
[Explicit Over Implicit](../../../principles/explicit-over-implicit.md),
[Deliberate Problem-Solving](../../../principles/deliberate-problem-solving.md), and
[Root Cause Orientation](../../../principles/root-cause-orientation.md).

## Scope

It applies to all new or changed executable behaviour. That includes application and library code, and also the scripts,
validators, and gates a repository runs against itself, since a defect in a check silently switches off what the check
guards. Every bug fix is in scope.

It does not apply where no executable behaviour changes:

| Change                                                            | Why no test comes first                                                            |
| ----------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| prose, documentation, or governance text                          | no test target reads prose                                                         |
| generated output                                                  | the generator's own tests cover it                                                 |
| a typo or comment correction                                      | the existing tests already cover the behaviour                                     |
| a configuration value that alters no behaviour and no gate's rule | nothing executable changes; a change to what a gate accepts starts from a red test |
| an exploratory spike                                              | it is discarded, or rebuilt test-first, before anything ships                      |

Keep this list short. When it is unclear whether a change alters behaviour, treat it as one that does and write the test
first.

## The Cycle

1. **Red.** Write one test for the next small behaviour, run it, and confirm it fails for its stated reason: the
   behaviour does not exist yet.
2. **Green.** Make the smallest production change that passes it while the surrounding tests stay green.
3. **Refactor.** Improve the design with every test still green, adding no behaviour.

Repeat for the next behaviour. Where behaviour is specified as scenarios, the scenario is added or updated before the
red, as [Behaviour-Driven Development](behaviour-driven-development.md) requires. A refactor that changes no behaviour
starts from a green run and follows the characterization rule stated there.

This is the stricter reading of the practice. A test that appears after the code tends to confirm what the code does
rather than what was required, and nothing afterwards can show that it was ever able to fail.

## Modules

1. [Cycle and Evidence](test-driven-development/001-cycle-and-evidence.md)
2. [Test Design](test-driven-development/002-test-design.md)
3. [Regression Tests](test-driven-development/003-regression-tests.md)
4. [Intermittent Failures](test-driven-development/004-intermittent-failures.md)

## Related Standards

- [Test Boundaries and Gates](test-boundaries-and-gates.md) decides which layer a test belongs to and which gate runs
  it.
- [Layers and Adapters](behaviour-driven-development/002-layers-and-adapters.md) records whether coverage carries a
  numeric floor.
- [Manual Verification](../manual-verification.md) owns what a person still checks once the suite is green.
- Software Quality Enforcement records that test-first order is proven by evidence, since a gate only sees the final
  state.
