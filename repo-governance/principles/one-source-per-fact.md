---
description: >-
  States that every fact this catalog governs has exactly one authoritative place, and that a second copy is a future
  contradiction with no rule for which copy wins.
when_to_use: >-
  Use when a fact is about to be written in a second place, or when deciding which of two artifacts owns something they
  both describe.
---

# One Source Per Fact

Every fact has one place. A second copy is not redundancy; it is a contradiction that has not happened yet.

## The Argument Is About Time

Two copies agree on the day they are written. That is the only day anyone checks, and it is why the duplication always
looks harmless when it is introduced.

What happens next is not a risk, it is a schedule. One copy gets corrected. The other does not, because the person
correcting it did not know it existed. Now a reader can follow either, both look authoritative, and nothing decides
between them — so the answer depends on which file that reader happened to open.

The cost is never the storage. It is that every change to the fact costs two edits, and the second is the one that gets
forgotten.

## Where It Is Already Load-Bearing

| Applied in                                                                                | As                                                                               |
| ----------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| [Schemas by Path](../conventions/structure/artifact-metadata/001-schemas-by-path.md)      | governance documents carry no `name`, because the path is the identity           |
| [Harness Adapters](../development/agents/harness-adapters.md)                             | an adapter holds no authored body, and is never read to learn about the artifact |
| [Gate Entries](../conventions/structure/repository-configuration/002-gate-entries.md)     | hooks dispatch the ordered registry rather than transcribing it                  |
| [Capability Forms](../development/agents/capability-forms.md)                             | two artifacts carrying the same instructions fail review                         |
| [Lifecycle and Folders](../conventions/structure/plans/001-lifecycle-and-folders.md)      | a slug in two lifecycle roots is a failure, not a merge to resolve               |
| [Knowledge Capture](../conventions/structure/plans/008-knowledge-capture-and-archival.md) | a learning is promoted to exactly one owner, not copied into three               |

## A Link Is Not a Weaker Copy

When two artifacts need the same fact, one owns it and the other links. The link is not a compromise — it is the only
arrangement in which the fact can be corrected once.

The reflex to inline "so the reader does not have to click" is the reflex this principle exists to interrupt. A reader
who follows a link reads the current text. A reader given a copy reads whatever was true when the copy was made.

## What This Does Not Forbid

Restating a fact **in different terms for a different purpose** is not a copy. A convention states a rule; a workflow
says when it applies; a skill says how to apply it well. Each answers a different question, and none of them is the
authority on the others — see [Capability Forms](../development/agents/capability-forms.md).

Deliberate redundancy with a stated reason is also not a copy. An agent declares `constraints` that its `capabilities`
list already implies, because a granted capability and a decided restriction are different claims and the second must
survive someone widening the first.

The test is whether the two would ever need to change together. If they would, one of them should not exist.
