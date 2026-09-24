---
description: >-
  States that a reader reaches the rule for the task in hand without reading the rules for other tasks, with always-read
  surfaces kept short and detail one link away in its owner.
when_to_use: >-
  Use when an entry file, index, or document is growing or being split, or when deciding what an always-read instruction
  file should state itself.
---

# Progressive Disclosure

A reader reaches the rule that governs what they are about to do from where they start, without first reading the rules
that govern everything else.

Complexity stays available. It is never required before it is needed.

## What It Requires

**Always-read surfaces stay short.** An instruction file loaded on every task, a directory index, and the opening of a
document are read by everyone. Each word there is paid for by every reader, including the ones it does not concern.

**Detail lives with its owner, one link away.** Rationale, exceptions, examples, and procedure belong in the most
specific document that owns them. The surface above links to it and does not restate it.

**Split by reader task, not by size.** A document that outgrows its budget has usually acquired a second reader.
Splitting along that seam gives each part someone who wants it; cutting at an arbitrary length gives two halves that
both have to be read.

**Each layer is complete for its reader.** A first layer lets someone act correctly on the common case without the
layers below it. A layer that only makes sense after reading the next one is a table of contents posing as guidance.

**Nothing mandatory hides behind an optional path.** A prerequisite, a safety boundary, or a non-negotiable constraint
is visible where the task begins — stated there, or linked in a way no reader can mistake for further reading.

## Where It Is Already Load-Bearing

| Applied in                                                                                 | As                                                                         |
| ------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------- |
| [Repository Governance](../README.md)                                                      | the root names each level in a line and links to that level's own index    |
| [Plans Convention](../conventions/structure/plans.md)                                      | a deliberately short entrypoint whose modules are each independently read  |
| [File Naming](../conventions/structure/file-naming.md)                                     | a document over its budget becomes an entrypoint plus ordered modules      |
| [Shared Value Rules](../conventions/structure/artifact-metadata/002-shared-value-rules.md) | the description and trigger are read, and routed on, before the body loads |
| [Evidence and Quality](../conventions/structure/plans/007-evidence-and-quality.md)         | verification layers are linked to their owner rather than restated         |

## A Budget Is the Usual Mechanical Form

Where an adopter wants a mechanical check, the usual form is a word ceiling over always-read surfaces, enforced in its
own gate wherever its other checks run.

The ceiling is a maximum, never a target. Raising it hides the symptom while the document keeps growing. Cutting
substance to fit trades a long rule for one nobody can apply, and padding toward the ceiling is the same failure from
the other side.

An always-read file over its budget is split by moving detail to its owner. Compressing the text until it is hard to
read, or moving it into another file every reader also loads, leaves what each reader pays unchanged.

## Decide What the Root File States

One question has two defensible answers, and an adopter records which it chose: does the always-read root instruction
file state any rule itself?

| Root file holds                             | Gains                                                           | Costs                                                                                |
| ------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| links only, no rule of its own              | there is never a question of which statement is authoritative   | every rule costs a hop, and a reader who follows no link acts on nothing             |
| short actionable rules, each linking onward | the constraints that matter most reach every reader with no hop | each line is a second statement, and drifts unless owner and summary change together |

Links only suits a repository whose readers reliably follow them. Short rules suit one where the root file may be the
only thing a reader sees. Under either, the owning document stays the authority — see
[One Source Per Fact](one-source-per-fact.md) — and the rule that nothing mandatory hides behind an optional path still
holds.

## What It Costs

More files, and one more hop to most rules. The trade is accepted because an entry surface short enough to be read
completely is one whose rules are actually followed.
