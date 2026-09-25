---
description: >-
  Indexes the stack standards: the enforced gates, defaults, and design rules one language or framework adds, each
  adopted only by a repository that builds with that stack.
when_to_use: >-
  Use when a repository builds with a language or framework that has a stack standard, or when deciding whether a rule
  belongs to one stack or to every repository.
---

# Stack Standards

Stack standards. Each governs one language or framework by design: it records the normative choices that stack's
repositories enforce, and links the language-neutral standards instead of restating them. A repository adopts a stack
standard only when it uses that stack, and the stack's programming skill defers to it.

## Directory Map

- [Python Standards](python-standards.md) — the uv, ruff, strict pyright, and pytest gates, a functional core, Python
  domain shapes, `Decimal` money, and failures
- [Python Standards Modules](python-standards/README.md) — naming functions by a verb and its object and variables by
  nouns, and returning failures as Results
