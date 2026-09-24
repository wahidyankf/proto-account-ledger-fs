---
description: >-
  Requires each commit to carry one coherent purpose together with every file that purpose needs, divides a change set
  into the fewest build-valid commits by intent, and orders dependent commits.
when_to_use: >-
  Use when staging and committing, especially after work that touched several concerns or when asked to commit
  everything at once.
---

# Thematic Commits

A commit is the unit history works in. Review reads whole commits, a revert removes one, a bisect lands on one, and
release notes are written from them. Each treats a commit as one idea, so a commit holding two ideas serves none of
them, and a commit holding half of one records a state the repository never worked in.

This standard implements [Minimal Sufficiency](../../principles/minimal-sufficiency.md) and
[Simplicity Over Complexity](../../principles/simplicity-over-complexity.md).

## One Purpose, Complete

Each commit carries exactly one coherent purpose and everything that purpose requires: the code, its tests, its
specification, the documentation describing it, any migration with its rollback, the references it updates, and the
generated files derived from it.

Each commit also leaves out whatever serves a different purpose, even work from the same session sitting in the same
working tree. Intent defines a theme, not file type or directory. A feature with its tests and documentation is one
theme; an unrelated typo fixed along the way is another.

## The Boundary Test

Divide a change set into the fewest commits that each pass all three tests:

- **Build-valid.** The repository's required local checks pass at that commit.
- **Independently reviewable.** It states one purpose without relying on a later commit to explain or finish it.
- **Independently revertible.** Reverting it strands no reference, migration, or generated file.

File types, scopes, and message types never justify a split by themselves; see [Commit Messages](commit-messages.md). A
renamed symbol and every call site it touches are one commit. A new feature and an unrelated lint repair are two.

## Splitting

- Inspect the working tree and the staged diff before committing, and stage one theme at a time when several are
  present.
- Split by intent before pushing, not by size. A large commit with one theme is fine; a small commit with two is not.
- Order dependent commits so that each builds on the one before it, by dependency and never by message type.
- A request to commit everything asks for as many commits as the work needs. Answering it with one mixed commit throws
  away exactly what the request assumed would be kept.

Each message follows [Commit Messages](commit-messages.md), and whether committing is permitted at all is decided by
[Commit Authorization](commit-authorization.md).

## Verification

Review reads each commit against its own diff: the message accounts for everything in it, and the diff holds nothing the
message leaves out. No tool can judge intent, so this is a review check rather than an automated gate.
