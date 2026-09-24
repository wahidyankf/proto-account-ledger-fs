---
description: >-
  Fixes how documents and directories are named: lowercase kebab-case, a companion directory named after its parent
  document, and ordinal prefixes only where a reading order exists, with modules extending it to characters, dates, and
  source files.
when_to_use: >-
  Use when naming a new document or directory, or when splitting a document into an ordered companion set.
---

# File Naming

A reader should be able to predict a path before opening it. That is the whole purpose of these rules, and it is why
they are mechanical rather than tasteful.

## Lowercase Kebab-Case

Document and directory names use lowercase letters, digits, and hyphens. No spaces, no underscores, no capitals.

Case is the reason. Two of the operating systems this work runs on treat `Plans.md` and `plans.md` as the same file and
one does not, so a rename that differs only in case is a change that some checkouts see and others silently do not.
Removing capitals removes the entire class of problem rather than managing it.

Fixed names imposed by a tool keep their spelling: `README.md`, `LICENSE`, `SKILL.md`, `AGENTS.md`, and any root
instruction shim a harness requires.

## Companion Directories

A document too large for its budget splits into an entrypoint plus a sibling directory of modules. The directory is
named **exactly** after the document, without its extension and without a suffix:

```text
conventions/structure/plans.md
conventions/structure/plans/
  001-lifecycle-and-folders.md
  002-required-documents.md
  README.md
```

Not `plans-details/`, not `plans-modules/`, not `plans-parts/`. The relationship is already visible in the shared name,
and a suffix adds a word that every link, every index, and every reader has to carry without learning anything from it.

A companion directory carries a `README.md` that indexes its modules in reading order.

## Ordinals Where There Is An Order

A module filename carries a three-digit ordinal prefix — `001-`, `002-`, `003-` — when, and only when, its entrypoint
declares a reading order. Ordinals are contiguous and start at `001`.

The prefix is a claim: these documents are meant to be read in this sequence, and the third assumes the first. Where
that is untrue — a directory of independent conventions, one per topic — the prefix asserts a dependency that does not
exist and invites a reader to work through a list alphabetically for no reason.

Inserting a module between `002` and `003` renumbers what follows. The alternative, `002a-`, encodes the edit history
into the reading order, and the reading order is the only thing these names are for.

## Descriptive, Not Positional

After the ordinal, the name describes the content: `003-technical-shape-and-companions.md`, not `003-part-three.md`. The
ordinal already says where it sits; repeating that is the one thing the name cannot afford to spend its length on.

## Modules

The rules above hold for every name. These modules extend them and are read in order: the second builds on the character
set the first fixes, and the third names where source files depart from both.

1. [Portable Names](file-naming/001-portable-names.md)
2. [Dates and a Single Numbering System](file-naming/002-dates-and-single-numbering.md)
3. [Source Files](file-naming/003-source-files.md)
