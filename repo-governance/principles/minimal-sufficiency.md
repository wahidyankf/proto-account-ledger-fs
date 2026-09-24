---
description: >-
  States that an artifact carries what its purpose requires and nothing more, and that what is deliberately left out is
  worth recording alongside what is in. A change likewise carries what its outcome and rules require, then stops.
when_to_use: >-
  Use when a field, section, option, or document is about to be added, and when judging whether an existing one still
  earns its place. Also use when scoping a change or deciding it is finished.
---

# Minimal Sufficiency

An artifact holds what its purpose requires. Everything beyond that is cost with no owner.

## Additions Are Individually Reasonable

Nothing is ever added because it is a bad idea. Each field, flag, and section arrives with a real case behind it, and
refusing it in isolation looks like pedantry.

The cost is collective and arrives later. A configuration that accepted every reasonable field becomes a second, worse
place for facts that already had a home. A gate list that accepted a description, an enable flag, a timeout, and a
continue-on-error is no longer data — it is a small programming language, and the runner reading it has become an
interpreter of one.

The question is therefore never "is this reasonable?". It is "what is this the only place for?".

## Where It Is Already Load-Bearing

| Applied in                                                                                       | As                                                                             |
| ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------ |
| [Repository Configuration](../conventions/structure/repository-configuration.md)                 | a formatter's settings belong to the formatter                                 |
| [Gate Entries](../conventions/structure/repository-configuration/002-gate-entries.md)            | exactly four fields: no description, no flag, no timeout, no continue-on-error |
| [Schemas by Path](../conventions/structure/artifact-metadata/001-schemas-by-path.md)             | the list of excluded fields is longer than the list of fields                  |
| [Portable Capabilities](../conventions/structure/artifact-metadata/004-portable-capabilities.md) | declare what is needed, not what might one day be convenient                   |
| [Exclusions](../conventions/structure/plan-validator-contract/004-exclusions.md)                 | a judgement call encoded as a rule is enforced in cases nobody considered      |
| [Adopt Artifact](../workflows/adoption/adopt-artifact.md)                                        | change the requested scope; note what else you noticed and leave it            |

## Record the Omission

What was deliberately left out is as informative as what was included, and it is lost by default.

An absent field with no record is indistinguishable from a field nobody thought of, so the next person adds it — and the
argument that was already settled is had again, with less context. The excluded list, the not-applicable row, and the
stated reason are all the same move: making a decision survive the person who made it.

## Sufficiency Is Half the Name

This is not a principle about smallness. An artifact that omits something its purpose requires has failed the same test
from the other side, and "we kept it minimal" is not a defence for a rule nobody can apply.

The target is the smallest form that still does the whole job — and the whole job includes being usable by someone who
was not there when it was written.

## Applied to a Change

The same test governs work as well as artifacts. A change carries what its outcome and the applicable rules require, and
then stops: understood before it is chosen, built from what already exists, proven by a check that could have failed,
and never smaller than the obligations it touches.

1. [Scope of a Change](minimal-sufficiency/001-scope-of-a-change.md)
2. [What Minimality Never Removes](minimal-sufficiency/002-what-minimality-never-removes.md)

Where the change half is already load-bearing:

| Applied in                                             | As                                                                |
| ------------------------------------------------------ | ----------------------------------------------------------------- |
| [Quality Gate](../workflows/plan/plan-quality-gate.md) | the budget is not extended because the next attempt looks close   |
| [Plan Execution](../workflows/plan/plan-execution.md)  | a failure that predates the work is an explanation, not exemption |
