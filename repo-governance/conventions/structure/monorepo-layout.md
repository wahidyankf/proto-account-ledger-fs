---
description: >-
  Fixes the dependency direction inside a monorepo, where applications consume libraries and libraries form no cycle,
  and keeps each project's code, tests, and imports within its own boundary.
when_to_use: >-
  Use when a project joins a monorepo whose tooling builds a project graph, or when an import crosses a project
  boundary.
---

# Monorepo Layout

This convention is stack-scoped to monorepos whose tooling builds a project graph from declared dependencies and runs
tasks only for the projects a change affects. Every rule below exists so that graph stays true.

## Two Kinds of Project

| Kind        | Is                    | May depend on   |
| ----------- | --------------------- | --------------- |
| application | a deployable unit     | libraries       |
| library     | reusable, shared code | other libraries |

Applications and libraries live under separate top-level directories, so a project's kind is visible from its path.

- **An application never imports another application.** Code two applications share moves into a library. An import
  between applications couples two deployment units, so releasing one silently changes the other.
- **Library dependencies form no cycle.** A cycle leaves no valid build order, and the graph can no longer say which
  projects a change affects.

## A Project Keeps Its Own Contents

A project's implementation and tests live inside the project's own directory, and an asset lives only in the project
that uses it. A file outside every project belongs to nothing in the graph, so no affected-project run ever selects it,
and its tests are skipped by construction.

## Import by Package Name

A project imports an internal library by the library's package name, never by a relative path that climbs out of its own
directory into another project.

A relative path across a project boundary hides the dependency from the project graph. A change to the library then does
not mark the importer affected, and the importer's tests are skipped in exactly the change that could break it.

## Names and Entry Points

Project directories are named in lowercase kebab-case, per [File Naming](file-naming.md). Each project carries a
`README.md` saying what the project is and how to run its tasks.

The adopter enforces the dependency and import rules with its monorepo tooling's module-boundary constraints, run in its
own pre-commit or CI gate, so a forbidden import fails before review rather than in it.

## Principles

This convention implements [Explicit Over Implicit](../../principles/explicit-over-implicit.md), because every
dependency between projects is declared where the project graph can see it.
