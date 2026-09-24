---
description: >-
  Requires an explicit state machine for any lifecycle with three or more states and meaningful transitions, fixing
  declared states and transitions, guards, rejection, events, and the audit record.
when_to_use: >-
  Use when an entity or workflow gains a lifecycle, when status is inferred from several flags, or when choosing between
  a state-machine library and hand-written transitions.
---

# Finite-State Machines

Which moves a lifecycle allows are business rules. Spread across conditionals and boolean flags, they cannot be read in
one place, cannot be tested as a whole, and are contradicted by the next change nobody checked against them.

This standard implements [Automation Over Manual](../../../principles/automation-over-manual.md),
[Explicit Over Implicit](../../../principles/explicit-over-implicit.md), and
[Immutability](../../../principles/immutability.md).

## When a State Machine Is Required

Model a lifecycle as an explicit state machine when it has three or more distinct states and the transitions between
them carry business meaning. Validation rules that depend on the current state, and a required audit trail of state
changes, are the usual signs that they do.

| Not a state machine                          | Use instead                     |
| -------------------------------------------- | ------------------------------- |
| a simple on-and-off toggle                   | a boolean field                 |
| validating the shape or range of a value     | a value object                  |
| state that exists only in the user interface | the interface's component state |

## The Machine Is Declared

- **States** form one closed set with an explicit type. A state is never a free-form string, so a misspelled state fails
  to compile or validate instead of becoming a new one.
- **Transitions** are declared as a source state, a triggering event, and a target state. Every allowed transition is
  configured; one that is not configured is rejected, and a rejected event leaves the state unchanged.
- **One state at a time.** The machine is in exactly one state, and the same state and event always lead to the same
  result. The declaration is fixed once the machine starts, and every transition event is immutable.
- **Guards** hold every business condition a transition depends on, declared on that transition and written as pure
  functions, so the condition is enforced by the machine rather than by callers remembering to check it.
- **Names** state the stage the business recognizes, such as `PENDING_APPROVAL`. The repository uses one casing for
  state names; `UPPER_SNAKE_CASE` is the form unless the stack's enumeration idiom differs.

## Transitions Leave Evidence

- Each successful transition publishes an event named for the entity and the transition it completed, in the past tense,
  such as `OrderShipped`, so other parts of the system react to the lifecycle without polling it.
- Each state change is recorded with its time and the actor who caused it.
- A lifecycle that outlives a process persists its state, so a restart resumes the machine instead of resetting it.

Where a repository applies Domain-Driven Design, the machine lives inside the aggregate root that owns the lifecycle,
and nothing outside that aggregate changes its state directly.

## Adopter Decision: Library or Hand-Written Transitions

Record one choice per stack. Every rule above holds under either.

| Option                                         | Gains                                                                       | Costs                                                                                            |
| ---------------------------------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| a state-machine library                        | declarative configuration, built-in guards and actions, generated diagrams  | a dependency and its idioms, which a domain layer that may import no framework cannot take on    |
| hand-written transitions over an explicit type | no dependency; the domain stays plain code in the language's own constructs | the transition table, rejection, and any diagram are the repository's own code to write and test |

A library configured through its declarative interface keeps that configuration in code, not in a separate markup file.

## Documentation

Each machine's states and transitions are documented as a diagram, generated from the declaration where the chosen
option allows it, under the repository's [Diagrams](../../../conventions/writing/diagrams.md) rule.

## Enforcement

An adopter verifies each machine in its own tests: every state is declared, every allowed transition is configured and
every other one rejected, guards enforce their conditions, transitions publish their events, and state changes are
recorded.
