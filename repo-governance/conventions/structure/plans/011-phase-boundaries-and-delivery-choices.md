---
description: >-
  Names the delivery-grammar choices an adopter fixes once for all its plans — phase gates, a baseline phase, test-first
  item splitting, and defects found after archival — with each option's trade-off.
when_to_use: >-
  Use when adopting the plan system and fixing the local delivery grammar, or when an archived plan turns out to be
  defective.
---

# Phase Boundaries and Delivery Choices

The [Delivery Contract](004-delivery-contract.md) fixes what every checklist item contains. Four questions about
delivery grammar stay open, because repositories answer them differently for sound reasons. An adopter answers each
once, records the answer with its [Portability](009-portability.md) statuses, and applies it to every plan. A single
plan does not choose for itself.

## 1. How a Phase Ends

| Option                  | Requires                                                                                                       | Trade-off                                                                          |
| ----------------------- | -------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| phase gate              | every phase closes on a `### Phase N Gate` of exact commands and observable criteria, then a pause-safety note | every boundary is auditable and resumable; the checklist grows by a gate a phase   |
| plan-level pause safety | only the single pause-safety declaration the delivery contract already requires                                | shorter; a resumed executor re-derives whether the last phase left things coherent |

Under a phase gate, phase N+1 does not begin while any item of phase N's gate fails, and the failure is repaired inside
phase N. Gate items carry executor labels like any other item. The pause-safety note names the coherent state the phase
reached and the one command that re-verifies it. A phase whose gate cannot be written as commands has not been thought
through.

## 2. Whether a Baseline Phase Exists

| Option           | Requires                                                                                         | Trade-off                                                                                    |
| ---------------- | ------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------- |
| Phase 0 baseline | a first phase that installs dependencies and records the gates passing before any change is made | a later failure is attributable to the work, not the environment; costs a phase every time   |
| no baseline      | the first phase starts changing the repository                                                   | faster start; a pre-existing failure still has to be fixed, but looks like one the work made |

Either way, a failure that predates the plan is fixed rather than exempted — see
[Execution](../../../workflows/plan/plan-execution.md). The baseline only decides whether its origin stays visible.

## 3. How a Test-First Item Is Written

| Option      | Requires                                                                                                           | Trade-off                                                                              |
| ----------- | ------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------- |
| split cycle | an item that ships code becomes three — RED, GREEN, REFACTOR — each naming the test path, command, and expectation | proves the test failed before the change, which cannot be shown afterwards; more items |
| single item | one item whose proof is the passing test                                                                           | a shorter checklist; nothing shows the test was ever able to fail                      |

A repository that builds its own validators or gates has the strongest reason to split: a check never observed failing
has not been shown to check anything.

## 4. What Happens When an Archived Plan Is Defective

| Option         | Requires                                                                                                         | Trade-off                                                                                      |
| -------------- | ---------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| follow-up plan | the defect becomes an idea brief or a new plan linking the archived one; `done/` stays untouched                 | keeps the lifecycle's single reverse edge; the repair lives apart from the claim it corrects   |
| reopen         | move the folder back to `in-progress/`, strip the date prefix, and add a dated note in `README.md` on what broke | the correction sits beside the original claim; adds a second reverse edge, recorded as adapted |

The follow-up plan is the rule as [Lifecycle and Folders](001-lifecycle-and-folders.md) states it. Reopening adapts that
rule, so an adopter choosing it records the adaptation and its reason.

Neither option permits quietly editing a plan in `done/`. A silently corrected archive reads as though the plan had been
right all along.
