---
description: >-
  Defines the portable grouped repository-configuration contract: owned policy groups, typed lifecycle gates, and how a
  repository records extensions without hiding an owner.
when_to_use: >-
  Use when writing or validating a repository configuration file, or when adding a gate.
---

# Repository Configuration

One grouped file declares the repository-owned policy that a shared validator needs. Everything else remains where it is
owned: tool settings stay with their tool, product behavior stays with its product, and workstation overlays stay local.

The file is small on purpose. Configuration attracts fields — each individually reasonable, collectively a second, worse
place for facts that already have a home.

The catalog ships no runner or validator. An adopter pins the validator it selected; where a module below says a
declaration fails or is refused, that validator or its declared gate supplies the result.

## Modules

1. [Top-Level Schema](repository-configuration/001-top-level-schema.md)
2. [Gate Entries](repository-configuration/002-gate-entries.md)
3. [Surfaces and Mutation](repository-configuration/003-surfaces-and-mutation.md)
4. [Governance Categories](repository-configuration/004-governance-categories.md)

## What It Is Not

Not a build configuration, not a dependency manifest, not a place for tool settings. A formatter's configuration belongs
to the formatter; a test runner's belongs to the test runner.

The file owns lifecycle membership, input binding, and policy values. It does not own an untyped command language or a
second copy of a tool's configuration.
