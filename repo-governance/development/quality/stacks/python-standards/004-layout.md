---
description: >-
  Parts each step of a Python body with one blank line: after the docstring, around a block or a long statement, between
  clauses, before a return, and after a test's assertions.
when_to_use: >-
  Use when writing or reviewing how a Python function, method, or test is laid out.
---

# Layout

A body written as one dense run hides where one step ends and the next begins. One blank line between steps shows a
reader the body's shape before its detail, and a formatter keeps it once it is written.

## Blank Lines in a Body

Inside a function or method, one blank line must come:

1. **After the docstring,** before the first statement.
2. **Around each block,** an `if`, `for`, `while`, `with`, `try`, `match`, or nested definition, between it and the
   statement before or after it in the same body.
3. **Between the clauses** of an `if` or a `try`: before each `elif`, `else`, `except`, and `finally`.
4. **Between the cases** of a `match` in which any case's body is longer than one line. A `match` whose every case is
   one line keeps its cases together, read as a table.
5. **Around each assignment or call of three lines or more,** such as a tuple written one item a line.
6. **Before a `return` or `raise`** that follows another statement in its body.
7. **After a test's assertions,** before the next statement that is not one, so each arrange, act, and assert step
   stands apart.

A comment above a statement stays with it, so the blank line goes above the comment. A block's first statement has none
above it, since `ruff format` removes a blank line that opens a block and the formatter decides. A protocol method's
`...` stays under its docstring, since it is no step. Beyond these, a long run of statements is split where one step
ends and the next begins, and a run of assertions stays together.

## Enforcement

No tool places these lines: `ruff format` keeps a blank line inside a body but never adds one. Review applies this
module. It is followed when every body keeps the blank lines above, and violated when a listed step runs into its
neighbour.
