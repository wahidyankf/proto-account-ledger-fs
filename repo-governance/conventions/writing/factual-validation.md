---
description: >-
  Requires technical claims to be verified against authoritative sources before publication, labels each with one of
  four confidence levels, and forbids fabricated case studies and metrics.
when_to_use: >-
  Use when writing or reviewing a command, version, API usage, citation, or illustrative claim before the content is
  published.
---

# Factual Validation

A technical claim in published content is verified against an authoritative source before it ships, or it is marked as
unverified. Nothing is presented as true because its author is sure — see
[Evidence Over Assertion](../../principles/evidence-over-assertion.md).

## What to Verify

| Claim              | Verified by confirming                                                                         |
| ------------------ | ---------------------------------------------------------------------------------------------- |
| a command          | the command, its flags, and its arguments exist as written in the tool's current documentation |
| a feature          | the feature exists under that name, in the version the content targets                         |
| a version          | the version is real, and any "latest" or "current" qualifier is still true                     |
| a code example     | imports, signatures, parameter order, and return values match the current API                  |
| a citation or link | the source is reachable and actually supports the claim it is cited for                        |

Priority follows the cost of being wrong. Commands, versions, code, installation steps, configuration syntax, and
citations are always verified, because a wrong one blocks or misleads the reader. Performance claims, comparisons, and
recommended practices are verified whenever they look doubtful. Background and history are rechecked periodically.

## Authoritative Sources

Prefer, in order: the project's official documentation; its official source repository and release notes; the package
registry, for versions; the standards body, for specifications.

Avoid unofficial blog posts, forum threads, outdated question-and-answer pages, and third-party wikis. A search result
is a pointer to a source, not a source: open the page and read the claim there. When a source cannot be retrieved, use
an official mirror, and record which route confirmed the claim.

## Confidence Labels

| Label      | Means                                                                                  |
| ---------- | -------------------------------------------------------------------------------------- |
| Verified   | an authoritative source, read now, confirms the claim                                  |
| Unverified | no authoritative source could be reached, or confirming the claim needs a test         |
| Error      | an authoritative source contradicts the claim, or the command or code fails as written |
| Outdated   | the claim was true and has since been superseded                                       |

A verification record gives the label, the claim, and the source, plus the correction or required action for every label
but Verified.

## When a Claim Cannot Be Verified

Say so explicitly, give the reader the step that would verify it, and never present it as verified. Where the answer
depends on context, state each context and the answer that applies to it.

## No Fabricated Evidence

Illustrative content — a "why it matters" paragraph, a motivating example, a case study — never invents evidence. It
never contains:

- a named organization paired with a specific outcome, such as a percentage, count, cost, or throughput figure, without
  a citable primary source;
- a story in which an organization discovered, measured, or migrated something no primary source records;
- a generic stand-in such as "a large retailer" used to keep an anecdote's shape without its evidence; or
- precision implying a measurement nobody made.

Before writing any organization-attributed claim or specific figure, ask: **can the primary source be linked right
now?** If so, link it inline. If not, state the underlying principle — what the pattern enables, prevents, or trades
away — without the name and the number.

Fabricated precision persuades precisely because it looks like data, and a reader cannot tell it from the real thing.
General design consequences, mathematical properties, and public facts cited to their primary source remain available,
and they are true.

## Enforcement

Verification is review. An adopter can flag the fabrication pattern — an organization name, a past-tense verb, and a
number in one illustrative sentence — in its own documentation checker.
