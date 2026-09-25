---
description: >-
  Returns every expected failure as a Result, Ok or Err, keeps T | None for a lookup, wraps each raising library call,
  and leaves exceptions to bugs and the shell's signals.
when_to_use: >-
  Use when writing a Python function that can fail, handling one that does, or deciding whether to raise, return None,
  or return a Result.
---

# Failures

A failure a caller can meet belongs in its signature, so pyright makes every caller handle it. An exception that might
go uncaught hides the failure until it ends the run.

- **Result:** a function that can fail for any reason but a bug must return `Result[T, Fault]` from `common/result.py`:
  `Ok` holding the value, or `Err` holding a named fault type. It never returns a bare string, a bare `T | Fault` union,
  or a raised exception. The caller takes the result apart in one of three ways:
  - `match`;
  - an `isinstance(result, Err)` early return, which suits a chain of several fallible steps;
  - the combinators `map`, `map_err`, `flat_map`, `flat_map_err`, `tap`, and `tap_err`, which suit a single step.
- **Option:** a lookup that may find nothing returns `T | None`. A check that passes or names a fault returns
  `Result[None, Fault]`, never `Fault | None`.
- **Raising calls:** a library call that refuses by raising, such as `Decimal(text)` or `Path.read_text`, is wrapped
  where it is made. The wrapper catches the narrowest exception type and returns it as `Err`.
- **Exceptions:** code raises only where a bug alone can reach it:
  - a value object's constructor raises on an illegal value, which a bug alone can pass it, since code builds values
    through `parse` or `make`;
  - an `assert` states an invariant only a bug breaks;
  - an operator given a foreign type returns `NotImplemented`, so Python raises `TypeError`.
- **The shell:** apart from those wrappers, only the shell catches. It catches `BrokenPipeError` and `KeyboardInterrupt`
  as signals, and `Exception` as the floor tier's last resort. No code uses a bare `except:`.

Pyright strict gates the Result rule. A function annotated `Result` must return `Ok` or `Err`, and its caller cannot
read `.value` or `.error` before narrowing. Review applies the rest: it judges whether a failure is a bug or an expected
one, and it looks for any `raise`, `except`, or `Fault | None` outside the places above.
