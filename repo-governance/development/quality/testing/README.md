---
description: >-
  Indexes the testing standards: which layer and gate a test belongs to, how tests come first, what API, behaviour, and
  end-to-end tests assert, how tests isolate data and fixtures, and which test doubles replace what.
when_to_use: >-
  Use when deciding how a change is tested, which test layer or gate applies, how a test isolates its data and fixtures,
  or which test double replaces a collaborator.
---

# Testing Standards

Testing standards. They answer which test proves a behaviour, where it runs, and what a test may replace or touch.

## Directory Map

- [Behaviour-Driven Development](behaviour-driven-development.md) — Gherkin corpora, scenario-first changes, strict
  bindings, scoped exemptions; this repository binds only its layers
- [Behaviour-Driven Development Modules](behaviour-driven-development/README.md) — discovery, layers, bindings and
  exemptions, compliance
- [Test Boundaries and Gates](test-boundaries-and-gates.md) — what each test boundary excludes, separate suites, gates
  composed from named targets, the fast gate, and gating coverage
- [Test-Driven Development](test-driven-development.md) — test-first red, green, and refactor cycles for behaviour
  changes and bug fixes, with scope and exemptions
- [Test-Driven Development Modules](test-driven-development/README.md) — cycle evidence, test design, regression tests,
  and intermittent failures
