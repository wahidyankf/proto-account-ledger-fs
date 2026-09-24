---
description: >-
  States that a solution takes the shape with the fewest concepts a reader must hold, and that abstraction, indirection,
  and new mechanisms answer a demonstrated need rather than a predicted one.
when_to_use: >-
  Use when choosing how to structure a solution, before extracting an abstraction or adding a layer or mechanism, and
  when reviewing a design that feels heavier than its job.
---

# Simplicity Over Complexity

Choose the shape a reader can predict while holding the fewest things in mind. Complexity is added in response to a need
that has been shown, never in anticipation of one that has been imagined.

## Shape, Not Scope

[Minimal Sufficiency](minimal-sufficiency.md) decides what a change includes, and its
[Scope of a Change](minimal-sufficiency/001-scope-of-a-change.md) already prefers an existing mechanism to a new one and
refuses an abstraction with a single caller. This decides the shape of what remains.

They fail independently. A change can contain exactly what was required and still route it through a factory, a
registry, and an option with one possible value. That change is sufficient, and it is not simple.

## Abstraction Is Earned

The first time, write it directly. The second time, notice the resemblance and tolerate it. Extract only once the real
variation has been observed, so the abstraction captures what actually differs. The default heuristic is the third case,
which is usually when that variation becomes visible; the count is a guide, not a threshold.

An abstraction built from one case encodes a guess about which parts will vary. The second case varies somewhere else,
so the abstraction gains a parameter, then a flag, then a branch on the flag — and every caller now depends on a shape
that fits none of them. Removing a wrong abstraction costs more than the duplication it replaced.

The waiting applies to things that merely look alike. Two statements of one fact — a value or rule that must change
together — are not a resemblance to watch but a copy, and [One Source Per Fact](one-source-per-fact.md) removes the
second one now.

## Prefer

| Prefer                        | Over                                          | Because                                                            |
| ----------------------------- | --------------------------------------------- | ------------------------------------------------------------------ |
| a direct call or plain data   | a layer, plugin point, or option with one use | every indirection is a place a reader must visit to learn anything |
| flat structure                | deep nesting                                  | depth is paid on every read and rarely earns it                    |
| one job per part              | a part that does several                      | a part with several jobs changes for several unrelated reasons     |
| composing small parts         | a deep inheritance hierarchy                  | a change to a base reaches every descendant, wanted or not         |
| code about as long as its job | code much longer than its job                 | needless length is a signal to restructure, not to annotate        |
| validation where input enters | checks inside for states that cannot occur    | a branch for an impossible case is code no test can reach          |

The last row does not relax [Fail Closed](fail-closed.md). The boundary where input enters is exactly where a control
that cannot decide must refuse.

## Where It Is Already Load-Bearing

| Applied in                                                                                          | As                                                                          |
| --------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| [Principles](README.md)                                                                             | a rule gets a page only after several artifacts already apply it            |
| [Bounded Convergence](../development/workflow/bounded-convergence.md)                               | a fixed sequence of three named steps is three steps, not a loop to govern  |
| [Skill and Agent Roster](../development/agents/planning-capabilities/002-skill-and-agent-roster.md) | no separate fixer role; the maker repairs within a bound                    |
| [Gate Entries](../conventions/structure/repository-configuration/002-gate-entries.md)               | the runner schedules, retries, and parallelizes nothing                     |
| [Top-Level Schema](../conventions/structure/repository-configuration/001-top-level-schema.md)       | an omitted tier defers to the harness instead of reimplementing inheritance |

## When Complexity Is Right

When the need is real: a case that shows the real variation, a measured problem, a failure that recurs. The change that
adds the complexity names that need, so a later reader can tell an earned layer from a speculative one — and remove it
once the need is gone.

Before adding anything structural, ask what a reader will have to hold in mind to predict what this does, and compare it
with what they had to hold before.
