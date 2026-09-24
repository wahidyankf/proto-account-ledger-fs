---
description: >-
  Fixes date prefixes to ISO 8601 inside an otherwise kebab-case name, and forbids a name from carrying an ordinal and a
  second step or phase number.
when_to_use: >-
  Use when naming a dated file, or when a name carries both an ordinal prefix and an embedded step or phase number.
---

# Dates and a Single Numbering System

## Dates Are ISO 8601

A name that begins with a date writes it as `YYYY-MM-DD-` followed by the kebab-case subject, as in
`YYYY-MM-DD-initial-setup.md`. The whole name remains within the character set of
[Portable Names](001-portable-names.md).

Year first and zero-padded, dates sort chronologically as plain text, so a directory listing is already the timeline.
Every other order sorts by day or month and needs a tool before it can be read.

A date prefix records when something happened. It is not an ordinal and declares no reading order. A convention that
fixes its own dated form for a particular kind of folder governs that folder.

## One Numbering System Per Name

A name carries at most one number that orders it. An ordinal prefix together with a `step-N` or `phase-N` token inside
the name is two numbering systems, and the day they disagree a reader has no rule for which one is true.

When both appear, the ordinal stays and the token leaves the name:

- **They name the same step.** The ordinal is already that step's own number, so the token only repeats it. For a range
  of steps, they agree when the ordinal matches the first step.
- **They disagree.** The ordinal is the file's place in the set's reading order, contiguous from `001`, so it still
  stays. The token leaves, and the step or phase number moves into the document's title or body.

| Name                         | Problem                                     | Becomes                  |
| ---------------------------- | ------------------------------------------- | ------------------------ |
| `004-step-4-review.md`       | both numbers name the same step             | `004-review.md`          |
| `002-step-1-and-2-review.md` | the two numbers disagree                    | `002-review-of-steps.md` |
| `002-phase-3-rollout.md`     | the phase number disagrees with the ordinal | `002-rollout.md`         |

A rule that drops the ordinal instead and keeps the token is not adopted. Inside an ordered set, the reading-order
ordinal that [File Naming](../file-naming.md) requires, and that the plan companion rules in
[Technical Shape and Ordered Companions](../plans/003-technical-shape-and-companions.md) check, must hold.

Outside an ordered set a name has no ordinal, and a token that names a real step or phase may stay, because it is then
the only number the name carries.

The two systems drift by construction. Inserting a module renumbers every ordinal after it and leaves every embedded
token untouched, so the first insertion turns a redundant number into a contradictory one.
