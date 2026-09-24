---
description: >-
  Names the assessment docs at the repository root, gives each fact in them one owning document, and keeps repeated
  values, open markings, identifiers, and worklog entries in agreement across the set.
when_to_use: >-
  Use when editing any assessment doc, or when a change to one of them may make another stale.
---

# Assessment Docs

The assessment docs are the root files that answer the challenge brief: `challenge-raw.md`, `AMBIGUITIES.md`,
`NUMBERS.md`, `REJECTED.md`, `WORKLOG.md`, `MOVEMENT.md`, `OUTPUT_TARGET.md`, and `ACCEPTANCE_CRITERIA.feature`. They
are read side by side and defended figure by figure, so one fact told two ways is a wrong answer in one of them.

## Owners

| Document                      | Owns                                                                                |
| ----------------------------- | ----------------------------------------------------------------------------------- |
| `challenge-raw.md`            | the brief's wording                                                                 |
| `AMBIGUITIES.md`              | each reading: its `AMB-nnn` identifier, options, status, recommendation, and reason |
| `NUMBERS.md`                  | each constant: its value, given or chosen, status, and why not half                 |
| `REJECTED.md`                 | each criterion's verdict, and each abandoned approach                               |
| `MOVEMENT.md`                 | criterion identifiers, events, each day's figures, and what a pending one waits on  |
| `OUTPUT_TARGET.md`            | the exact text the command-line program prints                                      |
| `ACCEPTANCE_CRITERIA.feature` | the criteria as Gherkin, each with its verdict tag and ambiguity list               |
| `WORKLOG.md`                  | when each piece of work happened                                                    |

## Rules

A rule below holds after every change to any assessment doc.

**One owner.** A fact is stated in full only by its owner; another assessment doc cites the owner by link or identifier,
and repeats a value only where quoting it is that doc's job, unchanged. Followed: every repeated value, status,
identifier, verdict, and quotation matches its owner. Violated: two assessment docs disagree, or one restates reasoning
its owner holds.

Reason: a second copy is corrected late or never, per [One Source Per Fact](../../principles/one-source-per-fact.md).
Quoting is deliberate redundancy: `MOVEMENT.md` quotes the brief to tag each rule, the feature file restates each
criterion as Gherkin, and `OUTPUT_TARGET.md` repeats `MOVEMENT.md` because a test compares the program against it.

**Open values are marked.** A value that differs between the options of an open ambiguity names that entry where it
appears, unless its document declares once which basis its figures take: every open option agreeing, or the current
recommendations. Followed: each such value carries its `AMB-nnn`, or its document's basis covers it. Violated: a value
another option would change appears with neither, or a basis that omits an entry the figures rest on.

Reason: a figure that silently assumes an undecided reading reads as decided.

**Identifiers resolve.** Every `AMB-nnn` and criterion identifier cited in an assessment doc exists in its owner, except
inside a `WORKLOG.md` entry. Followed: each cited identifier has its entry. Violated: a cited identifier with none.

Reason: an identifier that points nowhere hides which decision a figure waits on.

**Work is logged.** Every commit that changes an assessment doc other than `WORKLOG.md` adds at least one `WORKLOG.md`
entry stamped with the real local time of the work it records. Followed: each such commit adds a row. Violated: one that
adds none.

Reason: the brief requires a timestamped, real worklog, and a reconstructed one is neither.

**The worklog is newest first and never rewritten.** A new `WORKLOG.md` entry goes at the top of the table, directly
under its header, and an entry is never edited or removed once committed, even when a later change renames what it
mentions. Followed: every committed row survives unchanged in every later revision, and no row is older than the row
below it. Violated: a revision that edits or drops a committed row, or places a row above a newer one.

Reason: an entry records what was true when the work happened, and rewriting it turns a log into a story; the newest
work comes first because a reader most often checks what happened last.

## Enforcement

Every rule here is unenforced by decision: no hook or gate checks them, and each change is read against them before it
is committed. Identifiers and worklog rows are mechanically checkable; a change adding a check is recorded here.

## Principles

This convention implements [One Source Per Fact](../../principles/one-source-per-fact.md), because each fact has one
owner, and [Explicit Over Implicit](../../principles/explicit-over-implicit.md), because a figure resting on an open
reading says so.
