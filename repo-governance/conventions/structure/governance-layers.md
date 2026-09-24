---
description: >-
  Gives an ordered test for placing a document at the governance level whose question it answers, and makes a higher
  level win any conflict with a lower one.
when_to_use: >-
  Use when deciding which governance level a new document belongs to, or when rules at two levels appear to disagree.
---

# Governance Layers

[Repository Governance](../../README.md) orders the levels and says what each holds. This convention adds how a document
is placed among them, and what happens when two levels disagree.

Agents and skills are not levels. They are forms a capability takes, and
[Capability Forms](../../development/agents/capability-forms.md) decides between them. Repositories differ on how many
levels they number and whether vision is one of them; the ordering and the rules below hold either way.

## Placing a Document

Ask in order, and stop at the first yes:

1. Does it state why the repository exists? **Vision.**
2. Does it state why something is valued, true in any repository? **Principle.**
3. Does it record a choice about an artifact's shape, naming, or configuration, where another repository could
   defensibly choose otherwise? **Convention.**
4. Does it say how work is done well, whatever order the work runs in? **Development.**
5. Is it only meaningful as an ordered sequence? **Workflow.**
6. None of these: it is not governance. It is product documentation, a plan, or reference material — see Documentation
   Architecture.

Asking from the top places a statement at the most durable level it genuinely belongs to. "Genuinely" carries weight: a
candidate principle must already be load-bearing in rules below it, as [Principles](../../principles/README.md)
requires, or it is a preference being promoted.

A document that answers two of these questions is two documents.

## A Higher Level Wins

A lower level never contradicts a higher one. When they conflict, the higher level governs, and the lower document is
corrected.

When the higher level is what is wrong, it is changed explicitly — as its own decision, with its own reason — and the
lower rule is then brought into line. It is never overridden in practice by a lower rule that everyone happens to follow
instead.

A lower rule quietly beating a higher one leaves two authorities for the same question, and which one a reader obeys
depends on which file they opened first.

## Changes Flow Down

Changing a level obliges a review of what depends on it below. A changed principle may invalidate conventions that
implement it; a changed convention may invalidate a workflow's steps. Principle Traceability is what makes those
dependents findable rather than remembered.

## Principles

This convention implements [One Source Per Fact](../../principles/one-source-per-fact.md), because a conflict between
levels is settled so that one authority answers each question, and
[Explicit Over Implicit](../../principles/explicit-over-implicit.md), because a wrong higher rule is changed openly
rather than overridden in practice.
