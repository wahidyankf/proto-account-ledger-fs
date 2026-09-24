---
description: >-
  Fixes how a story is examined from business, development, and testing perspectives before formulation, and the rules
  every Gherkin scenario follows.
when_to_use: >-
  Use when preparing a story for formulation, choosing how discovery sessions run, or writing and reviewing a scenario.
---

# Discovery and Scenarios

A scenario is only as good as the conversation behind it. Discovery surfaces rules and disagreements while they are
cheap to settle; formulation then records what was agreed.

## Three Perspectives Before Formulation

Before a story's scenarios are written, the business, development, and testing perspectives examine it together. Each
asks a different question: what is wanted, what building it will take, and what could go wrong.

The session maps the story onto:

- its rules, the constraints the behaviour must respect;
- concrete examples that illustrate each rule, including boundaries and failures; and
- open questions nobody present can answer, each with an owner.

Scenarios are then written from the examples and reviewed by the same perspectives. A story that still has open
questions is not ready to formulate, because a scenario written over an open question encodes a guess.

How the practice runs is an adopter decision:

| Choice         | Option                                  | Trade-off                                                    |
| -------------- | --------------------------------------- | ------------------------------------------------------------ |
| cadence        | before every story                      | catches every misunderstanding; costs time on simple stories |
|                | only before stories judged non-trivial  | cheaper; the triage itself can miss a hidden rule            |
| session length | a short fixed timebox                   | keeps sessions focused; a large story needs several          |
|                | open until the questions settle         | finishes in one sitting; drifts without a facilitator        |
| role holders   | a different person for each perspective | independent viewpoints; harder to schedule                   |
|                | one person holding several perspectives | easy to arrange; the blind spots overlap                     |

What matters is that each perspective's question gets asked, whoever asks it.

## Scenario Rules

- **Independent.** Each scenario runs alone and in any order. A scenario that needs another to run first fails in
  isolation and hides the dependency.
- **Named for the behaviour.** The name states the specific outcome, such as "an expired token is rejected", never
  "token test 2".
- **One logical outcome.** A scenario checks one outcome, though several `Then` steps may assert facets of it. Two
  outcomes make two scenarios, so a failure names what broke.
- **Background holds shared preconditions only.** Actions and assertions never go in `Background`, where they would run
  unseen before every scenario.
- **Explicit action and result.** Every scenario has a `When` that performs the behaviour and a `Then` that observes it.
  Without both, it describes a state rather than a behaviour.

How much a scenario's `When` steps may do is an adopter decision:

| Option                                                                | Gains                                            | Costs                                                                      |
| --------------------------------------------------------------------- | ------------------------------------------------ | -------------------------------------------------------------------------- |
| exactly one action per scenario                                       | a failure points at the single action that broke | a continuous journey splits into scenarios that each rebuild earlier state |
| one continuous journey, repeating step keywords, never split for form | the journey stays whole, as a user performs it   | locating a failure part-way through depends on the step report             |

Under either option, the scenario still checks one logical outcome.

Guidance on writing acceptance criteria in Gherkin beyond these rules lives in the
[`plan-writing-gherkin-criteria`](../../../../../.agents/skills/plan-writing-gherkin-criteria/SKILL.md) skill.
