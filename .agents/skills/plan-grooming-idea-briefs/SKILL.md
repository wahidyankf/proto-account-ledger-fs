---
name: plan-grooming-idea-briefs
description: >-
  Judges whether an idea brief is worth promoting to a formal plan, keeping with a stated trigger, or retiring outright.
when_to_use: >-
  Use when reviewing the ideas root, or when deciding whether a request should become a formal plan.
compatibility: Requires read access to the repository the idea concerns.
---

# Grooming Idea Briefs

An idea brief is cheap by design: what the problem is, why it might be worth solving, roughly what solving it involves,
and what would make it not worth doing. Grooming decides which of those survive contact with the current repository.

## The Judgement

Three questions, in order:

1. **Is the problem still real?** Briefs age against a moving repository. The most common outcome of grooming is
   discovering that something else already solved this, differently.
2. **Is it worth solving now?** Not "is it good" — almost everything in an ideas folder is defensible. Worth planning
   _now_, against everything else that could be planned instead.
3. **Is it understood well enough to plan?** A brief nobody can restate in a sentence will produce a plan nobody can
   execute.

## Dispositions

| Disposition | Requires                                                     |
| ----------- | ------------------------------------------------------------ |
| promote     | all three answers are yes                                    |
| keep        | a named trigger — the event that would make this worth doing |
| retire      | a stated reason                                              |

A `keep` without a trigger is indecision with a label on it. It costs a full re-read at every future grooming pass, and
it will get the same non-answer each time, because nothing about it changed.

## Retiring Is the Useful Outcome

Most briefs should be retired, and the reason matters more than the deletion. "Superseded by X", "the constraint that
motivated this is gone", "tried and it did not work" — each of these prevents someone rediscovering the idea and
spending the same thought on it again.

Deleting silently loses that. The next person will have the same idea, and it will look new.

## Grooming Several Repositories at Once

When one pass covers several repositories, as
[Ideas Grooming](../../../repo-governance/workflows/plan/plan-ideas-grooming.md) permits, three judgements decide
whether it consolidates or destroys.

- **Matching names prove nothing.** Compare bodies before merging: two same-named briefs, each rebuilt from its own
  repository's measurements, are separate ideas, and merging discards findings. If both keep the name, every brief
  carrying it gets the rename judgement.
- **Residency comes from the trees.** A brief belongs to one repository only when what it names exists there and in no
  other groomed repository, checked in each; the brief's own claim about its scope is not evidence.
- **Index lines stay local.** Take each index summary from that repository's copy, or one index ends up describing
  another repository's variant.

A merge, split, residency, rename, or placement choice that neither the rubrics nor the files settle goes to
[Grill Me](../grill-me/SKILL.md); one they do settle is never asked.

## Reading Urgency

Where the recorded layout separates urgent briefs, urgency is read from the brief's why-now section alone and importance
from the whole brief. A why-now that begins by denying urgency is the author's own verdict and beats any urgent-sounding
word elsewhere.

## A Pass Ends When the Exit Holds

Completion means every exit clause holds in every repository, checked clause by clause. Passing gates do not show it: a
gate scoped to changed files stays green while a brief sits in two repositories. Confirm at least that:

1. no brief lives in more than one repository;
2. each brief sits where the recorded layout places it, under a name its own text echoes;
3. every moved or renamed brief carries its provenance note, found by reading the whole leading note rather than a fixed
   number of lines;
4. no link in any repository still points at an old location; and
5. every touched ideas index records the pass.

Before charging a broken link to the pass, check whether the untouched revision already had it. When a clause fails,
repair it and rerun the whole check.

## What This Skill Does Not Do

It does not improve briefs. A brief too vague to judge is retired or rewritten, and rewriting is authoring — the same
work as writing it the first time, and it belongs to whoever wants the idea to survive.

It does not order work. Deciding a brief is worth planning says nothing about whether it is planned next.
