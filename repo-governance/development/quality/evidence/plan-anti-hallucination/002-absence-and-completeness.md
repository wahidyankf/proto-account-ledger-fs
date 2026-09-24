---
description: >-
  Sets the evidence that claims of absence and completeness need: an error-checked search with a positive control, a
  diff against ground truth from its owning authority, and a concept sweep no single pattern satisfies.
when_to_use: >-
  Use when a plan, check, or report states that something no longer exists, that nothing matches, that a list is
  complete, or that a rule was changed everywhere.
---

# Absence and Completeness

An empty result is the easiest evidence to fabricate by accident. A mistyped pattern, a wrong directory, a failed tool,
and a genuinely absent token can all print the same nothing.

## A Zero Result Must Have Been Able to Fail

A search that found nothing counts as evidence of absence only when all of these hold:

1. the exact command is recorded verbatim, because a zero with no command cannot be checked;
2. its error output was not discarded, because a discarded error turns a failed search into a clean-looking zero;
3. its exit status was inspected, separating "ran and matched nothing" from "failed to run";
4. a positive control passed: the same command shape, in the same tree, found a token known to be present; and
5. where the plan itself spells the token, the plan's own folder was excluded, or the count can never reach zero.

An acceptance clause requiring that nothing match a removed name conflicts with a test that names it to prove the
removal. Scope the clause to exclude such tests, or it can never be met.

## Completeness Needs a Diff

A claim that a document lists every item of some kind is checked by enumerating the real set independently and diffing
it against the document. Text searches cannot show completeness; they only show what was phrased the way the search
expected.

Take the real set from the authority that owns it. That is often not a file: a build tool's project graph, a service's
live registry, or a command's own listing. An enumeration that assumes the set lives on disk repeats the gap it was
meant to find.

## A Concept Sweep Is More Than a Pattern

When a plan changes a rule, proving the change landed everywhere is a sweep for the concept, not the phrase. One regular
expression is a single instrument with blind spots, and it is never acceptance evidence by itself. A sweep:

1. searches the key terms in both orders and each term alone;
2. searches for the rule's worked examples as well as its statement;
3. counts a hit only once the file around it has been read;
4. treats every copy of the rule as one atomic edit;
5. enumerates every file that links to the changed document, indexes included, and reads each; and
6. reads every document whose title or description names the rule being inverted.

The instrument that proves the sweep differs from the one used to make the edits. A sweep checked by its own pattern
measures phrasing, never coverage.

## Evidence From Tools Must Be Real

Before citing a validator's result, confirm how it is actually invoked. A missing flag invents failures, and a target
that does nothing invents passes.

A count read from a capped or paginated listing undercounts without looking wrong. Take counts from an uncapped query,
and re-derive at least one foundational quantity of a plan directly from its source.
