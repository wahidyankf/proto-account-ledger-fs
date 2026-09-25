---
description: >-
  Fixes this repository's Python baseline: the pinned toolchain, ruff, strict pyright, and vulture gates, a functional
  core, the Python shapes for domain types and money, and how failures are expressed.
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
- **Dead code:** vulture, reading `src` and `tests` together, reports nothing, so unused names and unreachable code are
  deleted; ruff and pyright, reading one module at a time, miss a public name no module uses.
- **Complexity:** each function's McCabe complexity must stay at most 10 (ruff `C901`) and its nesting at most 3 blocks
  (`PLR1702`), so an overgrown function is split early.
- **Docstrings:** every module, class, method, and function must carry a docstring, private ones included, so a reader
  learns each piece's purpose without its body. Magic methods are exempt, as Python fixes their meaning. Ruff's `D1`
  checks public names and pylint private ones; neither reads a nested function, which should carry one too.
- **Types:** pyright in `strict` mode reports zero errors and warnings; every signature is annotated.
- **Suppressions:** `Any`, `cast()`, `# type: ignore`, and `# noqa` each take the narrowest scope and state their
  reason, as [Lint Strictness](../checks/lint-strictness.md) requires.

## Naming

Functions are named by a verb and its object, variables by nouns, and a type generic over the currency by its noun and
`In`, with the plain noun for the union, as [Naming](python-standards/001-naming.md) holds.

## Operations

Each operation is a method of its subject type, save four named cases, and no class derives from another but a
`Protocol`, `Generic`, `Enum`, or exception, as [Operations](python-standards/003-operations.md) holds.

## Layout

A blank line parts each step of a body, after its docstring, around each block, and before its return, as
[Layout](python-standards/004-layout.md) holds.

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
may represent an illegal value: its constructor raises on one, which only a bug reaches, and its `parse` or `make`
returns `Err` with a typed fault for input. State machines are hand-written: one `match` over the state and trigger
unions is the table.

## Failures

This repository records **returned result values**: an expected failure is returned as `Result[T, Fault]`, `Ok` or `Err`
with a named fault type, and exceptions are left for bugs and the shell's signals, as
[Failures](python-standards/002-failures.md) holds.

## Mutation Proofs

Once a mutation is restored, every `__pycache__` under `src` and `tests` is deleted before the confirming run, because
CPython reuses bytecode whose source kept its size and modification second.

## Enforcement

The `lint`, `typecheck`, and `test:*` Nx targets enforce the gates, inheritance included, in hooks. Review applies the
domain shapes, the failure rules, the variable names, where each operation lives, the layout, and the mutation-proof
step. Test levels and coverage follow [Test Boundaries and Gates](../testing/test-boundaries-and-gates.md).

## Modules

1. [Naming](python-standards/001-naming.md)
2. [Failures](python-standards/002-failures.md)
3. [Operations](python-standards/003-operations.md)
4. [Layout](python-standards/004-layout.md)
