---
description: >-
  Requires a README at the root of every application and library project, fixes what it covers, and keeps interface
  detail in the specification it links to.
when_to_use: >-
  Use when creating or changing an application or library project, or when deciding whether detail belongs in its README
  or in its specification.
---

# Project READMEs

A project root is where a new contributor lands. The README there answers what the project is, how to work on it, and
where the detail lives, so nobody has to reverse-engineer a directory to start.

## Every Project Has One

Every application and library project carries a `README.md` at its root, added in the same change that creates the
project. [Monorepo Layout](monorepo-layout.md) already requires one; this convention fixes what it holds. In a
single-project repository, the root `README.md` is the project README: it holds these sections itself and needs no link
to itself.

## What It Covers

| Section    | States                                                                                                                                    |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| purpose    | what the project is for, in a sentence or two                                                                                             |
| ownership  | what it owns, and what a reader might expect it to own but it does not                                                                    |
| stack      | the languages, frameworks, and tool versions it runs on                                                                                   |
| setup      | prerequisites, installation, and configuration needed before the first command                                                            |
| commands   | the repository's declared task entry point, run from the repository root, to build, run, and test                                         |
| layout     | where its source, tests, configuration, and entry points live                                                                             |
| boundaries | its dependencies, its consumers, and the interfaces it exposes, each named at the boundary                                                |
| testing    | how to run its tests, and at which levels                                                                                                 |
| links      | the root `README.md`, the project's specification, and the canonical architecture, security, operations, and governance documents it uses |

The most useful information comes first, and every command runs as written. A section that does not apply is left out
rather than filled: a library with no configuration has no configuration section. Content with a canonical home
elsewhere, such as a shared setup guide, is linked rather than copied.

Commands go through the declared entry point from the root because that is the path the repository runs and tests, and a
README that teaches a direct tool call teaches the one path it does not. Where a workspace task runner is that entry
point, a direct call also bypasses the runner's caching and affected-project selection.

## README or Specification

Repositories draw this line two ways: a README that documents the whole interface, or a README that names the interface
and points at its specification. This convention selects the second.

The README names each interface and consumer and links to the specification that defines it. It does not enumerate
routes, endpoints, request and response shapes, events, or internal architecture. Those belong to the project's
canonical specification, in whatever form the repository declares; where [Specification Tree](specification-tree.md) is
adopted, that is the project's corpus. The specification is the statement a test is checked against. An endpoint list in
a README is a second copy, and the copy is the one that goes stale, because no test reads it.

A project with no specification links each interface to the source that defines it instead.

No fixed length cap is adopted. A line limit is only a proxy for this boundary: a short README can still copy interface
detail, while a long one may be long because setup is genuinely involved. The boundary is checked directly instead.

The links run both ways. The README links its specification, whose index or entry document, where its form has one,
links back to the project.

## Checked on Every Project Change

A change to a project asks whether its README is still true: a new command, a moved entry point, a new consumer, a
changed prerequisite. A needed update lands in the same change. A changed boundary beside an unchanged README is a
review finding.

An adopter enforces presence and, outside a single-project repository, the root link with its own project check in
pre-commit or CI, adding the specification link wherever the project has a specification; whether the content is still
true stays a review question.

## Principles

This convention implements [Progressive Disclosure](../../principles/progressive-disclosure.md), because the README
orients a reader and hands interface detail to the specification one link away, and
[One Source Per Fact](../../principles/one-source-per-fact.md), because each interface is described in exactly one
place.
