---
description: >-
  Fixes the Conventional Commits message format of lowercase type, optional scope, imperative subject, explanatory body,
  and breaking-change footer, and stops message types from deciding commit boundaries.
when_to_use: >-
  Use when writing or reviewing a commit message, choosing a commit type, or when a split is proposed because the
  changes carry different types.
---

# Commit Messages

History is read far more often than it is written: in review, in a bisect, in a changelog, in a revert months later. A
fixed format makes every one of those readings cheaper, and a machine-readable one lets tooling derive release notes and
version bumps.

This standard implements [Explicit Over Implicit](../../principles/explicit-over-implicit.md) and
[Automation Over Manual](../../principles/automation-over-manual.md).

## Format

Messages follow [Conventional Commits](https://www.conventionalcommits.org/):

```text
<type>(<scope>): <subject>

<body>

<footer>
```

- **Type** is required and lowercase.
- **Scope** is optional. A repository using scopes keeps a stable list instead of coining a synonym per commit.
- **Subject** is required, in the imperative ("add", not "added" or "adds"), with no closing period. Write to about 50
  characters; the ceiling a hook enforces is the adopter's, commonly 100.
- **Body** is optional, follows a blank line, and explains what changed and why: the failing case, the constraint, the
  alternative rejected. It does not narrate how the diff was produced. Body lines keep within the ceiling the message
  hook enforces, such as 100 characters.
- **Footer** carries `BREAKING CHANGE:` for an incompatible change, and issue references.

## Types

| Type       | For                                                                   |
| ---------- | --------------------------------------------------------------------- |
| `feat`     | a capability the change's users can see                               |
| `fix`      | correcting wrong behaviour                                            |
| `docs`     | documentation only                                                    |
| `style`    | formatting that leaves meaning unchanged                              |
| `refactor` | restructuring without a behaviour change                              |
| `perf`     | a measured performance improvement                                    |
| `test`     | adding or correcting tests only                                       |
| `build`    | build, packaging, or compiler configuration                           |
| `chore`    | dependency updates and housekeeping touching neither source nor tests |
| `ci`       | pipeline configuration                                                |
| `revert`   | undoing an earlier commit, which the message names                    |

A repository may narrow this list.

## Name the Change, Not the Process

"Address review feedback", "updates", and "WIP" tell a later reader nothing they can act on. Name the change. A message
is also outbound text and passes the same screen as the diff; see
[Public Outbound Safety](../../conventions/security/public-outbound-safety.md).

## Types Do Not Draw Boundaries

Practices disagree here, and this standard records which side it takes. One splits commits by type or by area: the
feature in one commit, its documentation in the next, its tests in a third. The other keeps each commit to one purpose
with its tests and documentation inside, in the fewest commits that each still build.

The purpose rule is selected because a commit should be self-contained, build, carry one purpose, and revert cleanly,
and a feature separated from its tests or documentation is none of those. A `feat` commit may therefore hold test and
documentation files. How a change set divides is owned by [Thematic Commits](thematic-commits.md).

## Enforcement

A commit-message hook validates the syntax; an adopter wires its own message linter there. No linter can tell whether a
subject is true, so review reads each message against its diff.
