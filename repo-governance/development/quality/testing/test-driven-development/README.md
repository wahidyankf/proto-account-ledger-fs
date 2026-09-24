---
description: >-
  Indexes the ordered modules that hold the red, green, and refactor steps with their evidence, test design, regression
  tests for fixes, and intermittent failures for test-driven development.
when_to_use: >-
  Use to locate the module covering one part of test-driven development, such as a valid red, a bug fix's test, or a
  flaky test.
---

# Test-Driven Development Modules

The modules below are read in sequence and carry the detail behind the
[Test-Driven Development](../test-driven-development.md) entrypoint.

| Module                                                | Holds                                                                                 |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------- |
| [Cycle and Evidence](001-cycle-and-evidence.md)       | valid red, green, and refactor steps, cycle size, harness reds, and recorded evidence |
| [Test Design](002-test-design.md)                     | arrange-act-assert, test properties, names, one logical assertion, and derived sets   |
| [Regression Tests](003-regression-tests.md)           | a reproducing test with every fix, its form by defect, and planned fixes              |
| [Intermittent Failures](004-intermittent-failures.md) | confirming the same code, the required response, and the remedies that only hide it   |

## Directory Map

- [001 Cycle and Evidence](001-cycle-and-evidence.md)
- [002 Test Design](002-test-design.md)
- [003 Regression Tests](003-regression-tests.md)
- [004 Intermittent Failures](004-intermittent-failures.md)
