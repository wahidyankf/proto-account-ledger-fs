---
name: assess-alignment
description: >-
  Compares a repository against the catalog by intent and reports one status per artifact, without writing anything
  anywhere.
when_to_use: >-
  Use when a user asks how a repository compares with this catalog, or which artifacts it might be missing.
---

# Assess Alignment

## Entry

A user asks how a repository compares with the catalog. The request may name a scope, a full catalog commit, or specific
artifact paths; all three are optional.

## Sequence

1. **Resolve the scope and source.** No scope means every catalog artifact. A named commit must be a full SHA reachable
   from the canonical remote's published `main`; when omitted, resolve that published `main` head to a full SHA. Stop
   before comparison if the source is ambiguous or unverifiable.
2. **Read the target repository's own instructions first.** A local rule that deliberately contradicts a catalog
   artifact is a decision, not a deficiency, and an assessment that does not read those instructions will misreport it.
3. **Compare by intent, not by text.** The question is whether the repository already achieves what the artifact is for
   — not whether it says the same words.
4. **Assign exactly one status per in-scope artifact:**

   | Status                       | Means                                                          |
   | ---------------------------- | -------------------------------------------------------------- |
   | `adopted-equivalent`         | local intent and effect already match                          |
   | `locally-adapted-equivalent` | local form differs but preserves intent and effect             |
   | `local-extension`            | local behavior adds repository-specific value without conflict |
   | `not-applicable`             | repository characteristics make the artifact irrelevant        |

5. **Report anything that fits none of them** as a `conflict` — an unresolved contradiction — or a `gap` — a behavior
   the user appears to want and does not have.
6. **Write the report to the user**, not to the repository.

## Exit

Every in-scope artifact carries one status, and every contradiction is a `conflict` or a `gap`.

## Read-Only Is Absolute

No repository write. No file created, edited, or deleted. No branch, no commit, no external state changed anywhere,
including in the catalog.

The temptation is small and specific: fixing the one-line thing while looking at it. Refusing is what makes an
assessment safe to run without discussion — the moment it might change something, running it becomes a decision.

## Conflicts and Gaps Are Not Failures

A `conflict` says two rules disagree and something must decide between them. A `gap` says a behavior is missing. Neither
is forced into a success status, because a status that absorbs them makes the assessment useless: it would report
alignment for a repository that contradicts the catalog outright.
