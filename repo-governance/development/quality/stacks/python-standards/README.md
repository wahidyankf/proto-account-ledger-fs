---
description: >-
  Indexes the modules that carry the detail behind the Python Standards entrypoint: how functions and variables are
  named, how failures are returned, and where each operation lives.
when_to_use: >-
  Use to locate the module covering one part of the Python standards, such as how to name a function or return a
  failure.
---

# Python Standards Modules

The modules below carry the detail behind the [Python Standards](../python-standards.md) entrypoint.

| Module                          | Holds                                                                                 |
| ------------------------------- | ------------------------------------------------------------------------------------- |
| [Naming](001-naming.md)         | functions by verb and object, variables by nouns, currency generics by `In`, gates    |
| [Failures](002-failures.md)     | Result for an expected failure, `T \| None` for a lookup, and where exceptions remain |
| [Operations](003-operations.md) | each operation a method of its type, the cases left as functions, shared bases        |

## Directory Map

- [001 Naming](001-naming.md)
- [002 Failures](002-failures.md)
- [003 Operations](003-operations.md)
