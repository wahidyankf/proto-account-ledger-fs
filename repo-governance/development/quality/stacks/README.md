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

- [F# Standards](fsharp-standards.md) — F# formatter and warnings gates, dependency-ordered compilation, a functional
  core, F# domain and failure types, and the adopter's framework choices
