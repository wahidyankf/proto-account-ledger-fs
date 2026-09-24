---
description: >-
  Confines agent scratch files and reports to designated ignored directories, names them without collisions, writes them
  progressively, and makes each tree-walking tool exclude them.
when_to_use: >-
  Use when an agent or tool writes a scratch file or report, or when choosing and configuring ignored working
  directories.
---

# Temporary Files

Agents and tools write files that are not results: scratch notes, intermediate output, audit reports, the log of a run
still in progress. Left wherever they happen to land, those files get built, formatted, committed, or mistaken for
source. This convention gives them a place, a name, and a way of being written.

## Designated Directories Only

Scratch files and reports go only into directories the repository designates for them, and version control ignores every
designated directory. Nothing is written at the repository root, or inside a source, test, documentation, or governance
tree.

A scratch file beside source is picked up by the next build, formatter pass, test discovery, or broad `add`. The
repository's instructions name its designated directories once, such as `<scratch-dir>/` and `<reports-dir>/`, so no
agent has to guess.

## Names Never Collide

Two runs, or two agents working at once, never write the same path. A report name carries a generated identifier and a
timestamp:

```text
<scope>-<yyyy-mm-dd-hh-mm>-<uuid>-<report-type>.md
```

Every part stays within [Portable Names](file-naming/001-portable-names.md), and the timestamp precedes the identifier,
so one scope's reports list in the order they were written. Both values are produced at write time: the identifier by a
UUID generator, the timestamp by the clock. A placeholder left in the name, an invented identifier, or a rounded time
collides on the second run and names a report nobody can trace to the run that wrote it.

## Written Progressively

A report exists from the moment the work begins:

1. Create the file at the start, with its status marked in progress.
2. Append each finding as soon as it is established.
3. Set a final status — complete, partial, or failed — when the work ends.

The conversation carries a summary and the path, not the findings themselves. A run that is interrupted, compacted, or
killed then leaves a file holding everything found so far. A report composed at the end leaves nothing.

## Ignored Is Not Excluded

An ignore rule keeps a directory out of commits and out of nothing else. Formatters, linters, link checks, index and
word-budget checks, and test discovery each walk the tree by their own rules, and each needs its own exclusion for every
designated directory. Without one, a check fails on scratch nobody meant to keep, or a test runner executes a stale
copy.

## Reclaimed Only on Purpose

No ambient or background cleanup ever empties a designated directory. A finished task's scratch is removed under
[Dev Artifact Clean-Up](../../workflows/maintenance/dev-artifact-clean-up.md); any other entry is reclaimed
deliberately, once unmodified for an age the adopter states.

## Other Rules Win Where They Apply

Evidence a plan keeps belongs in its `evidence/` folder under [Evidence Files](plans/016-evidence-files.md), not in a
scratch directory. This convention covers everything else.

## What an Adopter Decides

| Decision                  | Options                                                                                                                                                                                                                                                                                           | Trade-off                                                                                                                                                                                                                                    |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| how directories split     | by who asked — an artifact a person asked for that is itself the answer goes to the reports directory, and everything an agent makes for itself or another agent goes to scratch, one directory per agent, or per agent group the adopter names — or by artifact type, scratch apart from reports | by requester, one test places even an unanticipated artifact, but a requested audit whose next reader is an agent still lands in scratch; by type, every report sits in one place, but a type list cannot place a new kind of artifact       |
| report timestamp timezone | UTC, or the repository's declared local zone                                                                                                                                                                                                                                                      | UTC sorts and compares across machines and contributors, and reads awkwardly beside local events; a local zone reads naturally, is named where the repository names its designated directories, and misorders across zones and clock changes |

An adopter enforces the exclusions in each tool's own configuration, and may add a check that fails when an untracked
file appears outside the designated directories.

## Principles

This convention implements [Explicit Over Implicit](../../principles/explicit-over-implicit.md), because the places a
temporary file may go are named rather than guessed, and
[Governance Continuity](../../principles/governance-continuity.md), because a report written as the work proceeds
survives the loss of the context that produced it.
