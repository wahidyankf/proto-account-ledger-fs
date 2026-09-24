---
description: >-
  Requires a plan that changes behaviour, interfaces, or architecture to state its specification delta file by file,
  keeping proposed design apart from as-built specifications.
when_to_use: >-
  Use when a formal plan changes observable behaviour, a public interface, architecture, or an executable specification.
---

# Plan Specification Changes

A plan that changes what a system does states, before implementation starts, exactly which specifications change and
how. Specification work discovered mid-execution is done in a hurry, by whoever notices, and usually only for the files
that broke.

This convention adds to the [Plans Convention](plans.md). It applies when a plan changes observable behaviour, a command
or configuration surface, an exit code, an interface, architecture, or an executable specification.

## Where It Lives

In the single-file shape, a section of `tech-docs.md` holds the planned specification work. In the directory shape, it
may be its own companion, such as `tech-docs/NNN-specification-changes.md`, when it serves a distinct reader. Every
planned path also appears in the plan's [File Impact](plans/013-file-impact.md) tree, with the labels defined there.

## What Becomes a Durable Contract

Acceptance criteria in `prd.md` accept the plan. They are not an instruction to copy every scenario into the
repository's specifications.

Before listing files, state which outcomes become durable specifications and which stay plan-only. Each plan-only
outcome records why, and names the `delivery.md` item that verifies it. Each durable outcome names its target
specification. A plan that adds no durable scenario says so rather than leaving the question open.

## The Delta, File by File

Use one heading per file with nested bullets, not a wide table. The delta goes in a fenced `diff` block — `-` for
current or removed behaviour, `+` for resulting or added behaviour — with three ordinary bullets beneath it:

````markdown
### [E] `specs/importer/header-row.feature`

```diff
- Scenario: Reject a file whose first row is a header
+ Scenario: Accept a file whose first row is a header
```

- = Preserve: `Reject an empty file`
- → Bindings: `<unit-binding-path>`, `<integration-binding-path>`
- ✓ Proof: `<specification-command>`
````

An `[N]` file shows only `+`, a `[D]` file only `-`, and an `[M]` file both paths.

For each scenario file, state:

- every existing scenario to preserve, change, move, or delete, by name, and the observable behaviour that results;
- every new scenario by name, with its actor, preconditions, action, and expected outcome;
- the binding path that changes at each test boundary the repository declares, or the boundary that cannot carry the
  scenario and why; and
- the command that proves the changed corpus and, for a user-facing change, the focused journey that proves it running.

For each architecture file, name each changed view, element, relationship, data store, or constraint, and give the
reason. A planned diagram follows the repository's [Diagrams](../writing/diagrams.md) rule.

## Binding Boundaries: an Adopter Decision

A plan cannot state bindings until the repository has said where scenarios bind.

| Option                  | Requires                                                                                               | Trade-off                                                                       |
| ----------------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| one declared boundary   | every scenario binds at one declared adapter, such as the unit boundary                                | fast, deterministic proof; says nothing about integration or deployed behaviour |
| every declared boundary | every scenario binds at each declared boundary, unless the plan names one that cannot carry it and why | strongest end-to-end proof; costs more adapters and slower gates                |

## Public Contracts

Where the repository declares a public contract — a command, flag, exit code, configuration key, or interface a consumer
depends on — a plan that would change one says it is proposing a release decision, in those words. Adding to a contract
and changing one cost a consumer differently, and the plan states which it does.

## Proposed Now, As-Built Later

The proposal stays in the plan. The repository's specifications remain the as-built description, and they are updated
during execution, once the implemented result is settled.

The implementation phase that changes the behaviour carries an `[AI]` item naming the canonical specification path and
the affected elements. Its outcome is synchronized as-built content, and its proof is the repository's specification
gates.

Never defer every specification update to one documentation item at the end. That is how a model and the code it claims
to describe come apart.

## Principles

This convention implements [One Source Per Fact](../../principles/one-source-per-fact.md), because the specifications
stay the single as-built description while the proposal lives in the plan, and
[Explicit Over Implicit](../../principles/explicit-over-implicit.md), because every specification delta is stated file
by file before implementation.
