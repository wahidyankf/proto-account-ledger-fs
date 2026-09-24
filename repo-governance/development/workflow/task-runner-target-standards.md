---
description: >-
  Fixes how a workspace task runner's project targets are declared: prerequisite chains, caching only deterministic
  targets, explicit inputs and outputs, canonical names without aliases, ordered aggregates, and no placeholders.
when_to_use: >-
  Use when adding, renaming, caching, or composing a project target in a workspace task runner, or when reviewing a
  project's target definitions.
---

# Task Runner Target Standards

Scoped to adopters whose workspace runs project work through a task runner with named per-project targets, a dependency
graph, and a computation cache, for example Nx. A target is a contract: its name says what it does, its cache setting
says whether a stored result may stand in for a run, and its presence claims that a boundary is covered.

This standard implements [Explicit Over Implicit](../../principles/explicit-over-implicit.md),
[Reproducibility](../../principles/reproducibility.md),
[Simplicity Over Complexity](../../principles/simplicity-over-complexity.md), and
[Evidence Over Assertion](../../principles/evidence-over-assertion.md).

## Prerequisites

A target that needs another target's result declares that prerequisite in the runner's dependency field, for example
code generation before type checking and before building. Never rely on invocation order.

## Caching

Cache a target only when its declared inputs fully determine its result.

| Target kind                                                           | Cached |
| --------------------------------------------------------------------- | ------ |
| builds, type checking, static analysis, unit tests, static validators | yes    |
| integration and end-to-end test runs                                  | no     |
| long-running processes, such as development and production servers    | no     |
| side-effectful runs, such as installs and cleans                      | no     |
| interactive sessions                                                  | no     |

- **Inputs are explicit.** A cached target lists what changes its result, including files another project owns, such as
  shared specifications or generated contracts. A default limited to the project's own files misses those, and the
  runner then serves a stale pass.
- **Artifact-writing targets declare outputs.** A cache hit replays a result without running the command, so a cached
  target that writes artifacts names every path it writes; otherwise the hit restores nothing and still reports success.
- **Uncached targets declare no outputs.** There the declaration does nothing, yet reads as a decision.
- **Cache is declared where defaults stop.** A target the workspace defaults do not reach declares its cache setting
  explicitly.
- **A single-command target sets a working directory** instead of writing a path into its command.

## Names

- Each operation has one canonical name, used identically in every project, and no aliases. A development server is
  `dev` and a production server `start`; neither is `serve`.
- Qualifiers are joined with a colon, as in `test:unit` and `test:e2e`, never a hyphen or underscore.
- Every segment is lowercase kebab-case.
- A renamed target keeps no alias for its old name.

## Real Targets Only

A target exists only where the project has the capability it names. Never add an echo, no-op, always-passing, or
duplicate target to fill a slot: it reports a tested boundary where nothing is tested. Omit an inapplicable target and
record the reason in the project's README. A dedicated end-to-end project exposes no unit or coverage target it cannot
really run. A check selected by file type that judges each file alone runs over staged files before commit, not as a
project target.

## Ordered Aggregates

An aggregate that runs several gates in a fixed order is non-parallel and invokes the existing targets by name. It never
copies their commands, so each command keeps a single owner. The ordered list expresses gate order; anything that must
finish before the whole aggregate starts is a declared prerequisite.

Integration and end-to-end runtime targets stay uncached, out of every fast aggregate, and out of commit and push hooks.

## Adopter Decision: Runner Plugins

| Option             | Gains                                                                                                                      | Costs                                                                                     |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| raw commands only  | every target owns a plain command, tools arrive as ordinary exact-pinned dependencies, and no plugin layer needs upgrading | scaffolding and target definitions are written by hand                                    |
| technology plugins | generators, executors, and inferred targets for each framework                                                             | a plugin layer between each target and its real tool, pinned and upgraded with the runner |

Record the option. Under raw commands only, a plugin needs explicit owner direction naming it and the capability it
adds, recorded in the introducing change with an exact version.

Tag vocabularies and per-language target catalogs stay in each adopter's own documentation.

## Enforcement

An adopter checks target declarations in its own project-configuration validator: names, cache decisions, aggregate
delegation, and the absence of placeholder targets.
