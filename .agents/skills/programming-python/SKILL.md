---
name: programming-python
description: >-
  Guides Python work under the shared quality standards: annotating every signature for a strict checker, handling paths
  as pathlib values, placing tests by the boundary they touch, and judging data shapes, failures, and async code.
when_to_use: >-
  Use when writing, changing, or reviewing Python code, before the first test of the change.
compatibility: Requires a Python project with its recorded type checker, linter, formatter, and test runner.
---

# Python Programming

Python rules this repository enforces are owned by
[Python Standards](../../../repo-governance/development/quality/stacks/python-standards.md); where a sentence here seems
to state a rule, the standard decides.
[Test-Driven Development](../../../repo-governance/development/quality/testing/test-driven-development.md) and
[Test Boundaries and Gates](../../../repo-governance/development/quality/testing/test-boundaries-and-gates.md) govern
tests and gates, [Red, Green, Refactor](../../../repo-governance/workflows/quality/red-green-refactor.md) runs each
cycle, [Lint Strictness](../../../repo-governance/development/quality/checks/lint-strictness.md) sets the threshold, and
[Developing Applications](../developing-applications/SKILL.md) carries the judgement on layers, errors, logs, and input.
Any tool named below is a marked example.

## The Choices This Skill Enforces

- **Every signature is annotated**, each parameter and the return, and a strict type checker reports zero findings
  before a commit.
- **The linter and formatter report nothing** before a commit.
- **A filesystem path is a `pathlib.Path`** from the point it enters the program, never a string assembled by hand.

Python checks no annotation at runtime, so an unannotated signature is a contract nothing verifies.

## Map the Tools to the Gates

| Target          | In Python                                                                  |
| --------------- | -------------------------------------------------------------------------- |
| type check      | example: `mypy --strict`                                                   |
| lint and format | example: `ruff check` and `ruff format --check`                            |
| unit            | the unit tree, with coverage measured in that run; example: `pytest --cov` |

## Make the Type Checker Mean Something

- `Any` turns checking off for everything it touches. A value of unknown shape is `object`, narrowed before use, and a
  structural need is a `Protocol`.
- `cast()` and `# type: ignore` are claims the checker cannot verify; each is a waiver with its reason beside it.
- Annotating parsed input is not validating it. Data crossing a boundary becomes a typed value through a check, as
  Developing Applications directs.

## Place a Test by What It Touches

Fixtures that create a temporary directory or set an environment variable reach a real filesystem or environment, which
the unit layer excludes, so a test using one belongs to the integration suite. To keep a decision under unit test, pass
in the text, the parsed value, or the setting, and let the shell do the reading. Example: pytest's `tmp_path` and
`monkeypatch.setenv` are integration tools in this sense.

Parametrize rows of one behaviour, giving each row an id that names its case, and add a row for a new behaviour only
after watching it fail.

## Shape Data Deliberately

A value object is a frozen dataclass. A default that is a list or a dictionary is built per instance through a factory:
a literal default is created once and shared by every call that omits the argument.

## Keep the Event Loop Moving

- A synchronous call inside `async def`, such as a file read, `time.sleep`, or a synchronous client, stalls every task
  on the loop. Move it off the loop, for example with `asyncio.to_thread`.
- `asyncio.run` belongs at the program's entry point only.
- Hold a reference to every task created, or create it inside a task group. The loop keeps only a weak reference, and an
  unreferenced task can vanish before it finishes.

## Adopter Decisions

| Decision            | Option                                       | Gains                                      | Costs                                                                 |
| ------------------- | -------------------------------------------- | ------------------------------------------ | --------------------------------------------------------------------- |
| boundary validation | standard-library dataclasses and hand checks | no dependency                              | validation and serialization written by hand                          |
|                     | a validation library; example: Pydantic      | declared rules, parsing, and serialization | a dependency, weighed per the ose-rules Dependency Selection standard |
| expected failures   | exceptions                                   | the idiom the standard library follows     | the signature does not show what can fail                             |
|                     | returned result values                       | the checker forces every caller to handle  | every raising library call needs wrapping                             |

Under either failure option, catch the narrowest exception type, never use a bare `except:`, which also swallows
interrupts, and name the type and reason wherever an exception is deliberately ignored.

## Before Handing Off

- the type checker, linter, and formatter report nothing;
- no unit test writes a file, reads the environment, or waits on a real clock;
- no synchronous call blocks inside async code; and
- each recorded red failed on an assertion about the missing behaviour.
