---
description: >-
  Separates product documentation from governance, organizes it into the four Diátaxis modes with one mode per page, and
  admits only commands and transcripts that were actually run.
when_to_use: >-
  Use when placing a documentation page, when a page mixes teaching, tasks, reference, and explanation, or when writing
  a language standard.
---

# Documentation Architecture

## Documentation Is Not Governance

A document belongs to exactly one tree, and its reader decides which. Someone using or trying to understand what the
repository produces reads documentation. Someone changing the repository reads governance. Rules for contributors live
in the governance tree, and documentation does not restate them.

Nothing is copied into documentation to fill it. A page whose content already has a canonical home — a project README, a
plan, a governance rule — links to that home instead.

## Four Modes, One Per Page

Documentation follows [Diátaxis](https://diataxis.fr/). Each page serves exactly one mode:

| Mode         | Reader                                     | The page succeeds when                                        |
| ------------ | ------------------------------------------ | ------------------------------------------------------------- |
| tutorial     | a newcomer learning by doing               | the reader reaches a working result without deciding anything |
| how-to guide | someone with a stated goal                 | that one problem is solved                                    |
| reference    | someone looking something up while working | the description is exact and complete                         |
| explanation  | someone wanting to understand              | the reasons, context, and trade-offs are clear                |

A page is classified by the reader need it primarily serves. Material spanning modes becomes one primary page in the
best-fitting mode, linked to pages in the others. A page serving two modes serves neither: the learner stalls on
reference tables and the person looking something up wades through a lesson.

Each mode has one directory with its own index. The exact directory names are the repository's choice, made once.

## Only What Was Run

Every command and transcript on a page has been executed against the current build. An invented transcript looks exactly
like a real one and stays wrong long after the behaviour changes. Where a path cannot be exercised safely — a
destructive operation, or a state that cannot be arranged — the page says so plainly instead of showing output.

Where a behaviour specification exists, it is canonical, and a page that contradicts it is a defect in the page.

## Language and Technology Standards

A repository's standard for a language or technology is a governance document, not documentation; this section fixes
only its scope. The standard records only the repository's own choices. It opens by stating the prerequisite knowledge
it assumes, with a link to general learning material, and never re-teaches fundamentals that material covers.

A tutorial embedded in a standard duplicates a better-maintained one, drifts from it, and buries the choices a reader
came to find.

## What an Adopter Decides

| Decision                     | Options                                                 | Trade-off                                                                                                                       |
| ---------------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| directory maps for this tree | map every page, or let landing pages link into sections | a map makes every page findable and checkable; landing pages serve a reader who arrives wanting a mode rather than an inventory |
| page metadata                | a title, description, mode, and tags per page, or none  | metadata supports search and a mode-to-directory check; every field is one more thing to keep true                              |

A repository mapping this tree applies [Directory Indexes](directory-indexes.md). Metadata on governance documents is
not part of this decision; [Artifact Metadata](artifact-metadata.md) governs it.

An adopter recording the mode in page metadata enforces agreement between mode and directory in its own documentation
check.

## Principles

This convention implements [Evidence Over Assertion](../../principles/evidence-over-assertion.md), because a page shows
only commands that were run, and [One Source Per Fact](../../principles/one-source-per-fact.md), because a page links to
content's canonical home instead of copying it.
