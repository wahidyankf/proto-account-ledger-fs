---
description: >-
  Fixes this repository's Python baseline: the pinned toolchain, ruff and strict pyright gates, a functional core, the
  Python shapes for domain types and money, and how failures are expressed.
when_to_use: >-
  Use when creating, configuring, or reviewing a Python project here, or when modelling a domain value, an amount of
  money, or a failure in Python.
---

# Python Standards

A local standard: ose-rules ships no Python stack standard, so this one records the choices this repository enforces.
The [Python programming skill](../../../../.agents/skills/programming-python/SKILL.md) defers here for each rule it
applies. It implements [Explicit Over Implicit](../../../principles/explicit-over-implicit.md),
[Immutability](../../../principles/immutability.md), and [Pure Functions](../../../principles/pure-functions.md).

## Gates

- **Toolchain:** each project is a uv project with `.python-version`, `requires-python`, and a committed `uv.lock`,
  following [Native-First Toolchain](../../workflow/native-first-toolchain.md).
- **Lint and format:** `ruff check` and `ruff format --check` report nothing.
- **Types:** pyright in `strict` mode reports zero errors and warnings; every signature is annotated.
- **Suppressions:** `Any`, `cast()`, `# type: ignore`, and `# noqa` each take the narrowest scope and state their
  reason, as [Lint Strictness](../checks/lint-strictness.md) requires.

## Functional Core

Domain and application decisions are pure functions returning typed values. Standard output, files, the clock, and
processes stay in the shell and reach the core as arguments, as
[Functional Core, Imperative Shell](../architecture/functional-core-imperative-shell.md) requires.

## Domain Types

| Concept              | Python shape                                                                                                          |
| -------------------- | --------------------------------------------------------------------------------------------------------------------- |
| closed set of states | an `Enum` or `Literal`, never bare strings or booleans                                                                |
| data                 | `@dataclass(frozen=True, slots=True)`; collections are tuples or frozen mappings                                      |
| amount of money      | one frozen dataclass per currency, in a union, wrapping a `Decimal` at its places; same-type operators, never `float` |
| positive amount      | a frozen wrapper whose constructor refuses zero and below; the event kind gives the direction                         |
| identifier or day    | a frozen value object whose constructor refuses a malformed value, never a bare `str` or `int`                        |
| state carrying data  | one frozen dataclass per state, joined in a union, each holding only its own data                                     |
| domain event         | one frozen dataclass per event kind, joined in a union type                                                           |

A `match` over a closed set ends with `case _: assert_never(value)`, so pyright reports a newly unhandled case. No type
may represent an illegal value: its constructor raises on one, which only a bug reaches, and its `parse` or `of` returns
a typed fault for input. State machines are hand-written: one `match` over the state and trigger unions is the table.

## Failures

This repository records **returned result values**: an expected failure is returned as a named fault type in a union
with the success value, and exceptions are left for bugs and the shell. Under either option, a failure has a named type,
never a bare string; an unexpected fault is handled at the shell; and no code uses a bare `except:`.

## Enforcement

The `lint`, `typecheck`, and `test:*` Nx targets enforce the gates in hooks. Review applies the domain shapes and
failure rules. Test levels and coverage follow [Test Boundaries and Gates](../testing/test-boundaries-and-gates.md).
