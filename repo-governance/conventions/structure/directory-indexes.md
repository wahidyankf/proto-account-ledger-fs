---
description: >-
  Requires every directory in an indexed tree to carry a README index whose Directory Map links each direct sibling and
  child directory exactly once, annotated, with no orphan or ghost entry.
when_to_use: >-
  Use when adding, moving, renaming, or removing an indexed file or directory, or when an index fails a completeness
  check.
---

# Directory Indexes

A reader arriving in a directory learns what is there, and what each entry is for, from one file. That file is only
useful if it is complete, and only trusted if it is never wrong.

## The Rule

Every directory in an indexed tree carries a `README.md` holding:

- a short statement of the directory's purpose;
- a `## Directory Map` linking every direct sibling document and every direct child directory, each exactly once within
  that section, by a relative link that resolves to a document; and
- an annotation for every entry saying what it is for, in a table column or in a clause beside the link. An annotated
  table elsewhere in the same `README.md` satisfies this, and the Directory Map may then list the entries bare.

A child directory is linked through its own `README.md`, which owns everything below it. A parent never repeats the
recursive tree: one level per index keeps each index short and makes a change touch one index.

An annotation that repeats the link text, or an adjacent column, says nothing and does not count.

## Four Findings

| Finding     | Means                                                 |
| ----------- | ----------------------------------------------------- |
| missing     | a directory in an indexed tree has no `README.md`     |
| orphan      | a sibling or child directory exists and is not linked |
| ghost       | the index links something that does not exist         |
| unannotated | an entry says nothing about what it links             |

An orphan hides work and a ghost promises work that is gone. Either way the map is wrong somewhere, and a reader can no
longer tell which entries to trust.

## Maintenance

The index changes in the same change that adds, removes, moves, or renames an entry, and a new directory is created with
its index. A companion directory lists its modules in reading order, as [File Naming](file-naming.md) requires.

In a governed tree, a directory holding nothing but its index is empty and fails, per
[Governance Categories](repository-configuration/004-governance-categories.md). In an indexed tree outside governance
where such a directory must exist, its map says explicitly that it has no entries, because silence cannot be told apart
from a map nobody maintains.

## Never Fit an Index by Dropping Entries

An index that reaches its [word budget](document-word-budget.md) is not too wordy; its directory has too many peers.
Group related entries into a subdirectory with its own index and link that one child. Dropping entries or annotations to
fit hides exactly what the index exists to show.

## What an Adopter Decides

| Decision                | Options and trade-off                                                                                                                                                                                                                |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| which trees are indexed | Governance alone is the minimum. Adding specifications and plans makes every scenario and plan findable. Documentation navigated by landing pages may be left out — see [Documentation Architecture](documentation-architecture.md). |
| which files count       | Markdown only suits prose trees; a tree whose content is not Markdown, such as behaviour specifications, lists every file type.                                                                                                      |
| generated directories   | They carry no hand-written index, because regeneration removes it; the source is indexed instead.                                                                                                                                    |
| vendored or tool-bound  | A vendored copy is indexed from its parent so the copy stays identical. A directory where a tool registers every file as a command is indexed from its parent unless the tool ignores an index there.                                |

An adopter enforces the findings with its own index check in pre-commit or CI, scoped to the trees it declares.

## Principles

This convention implements [Progressive Disclosure](../../principles/progressive-disclosure.md), because each index
shows one level and hands the rest to its children, and
[Explicit Over Implicit](../../principles/explicit-over-implicit.md), because an entry and an empty directory are stated
rather than left for a reader to infer.
