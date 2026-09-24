---
description: >-
  Requires strict resolution of every scenario step, forbids bindings that pass without exercising the subject, and
  limits an exemption to one scenario at one layer with a boundary reason and alternative proof.
when_to_use: >-
  Use when writing or reviewing step bindings, when a step is undefined, ambiguous, or unused, or when proposing that a
  scenario skip a layer.
---

# Bindings and Exemptions

A binding connects a sentence to a check. When it can pass without the check running, the scenario becomes documentation
that claims to be a test.

## Strict Resolution

Every step resolves to exactly one binding in each applicable layer. The adopter configures its test run so that each of
these fails it:

- an undefined step;
- an ambiguous step that matches more than one binding;
- a duplicate binding for the same expression; and
- an unused binding that no step matches.

Each expanded row of a scenario outline counts as a scenario of its own. Bindings stay thin, translating the step and
calling the subject, with shared setup and helpers kept in support modules.

## A Binding Must Exercise the Subject

A binding never:

- asserts a value it was handed instead of one the subject produced;
- returns early or does nothing;
- remains a stub or pending placeholder; or
- passes without invoking the subject under test.

Each of these is a defect even when the run is green, and review treats it as a failure.

## Exemptions

An exemption excuses one scenario from one layer, and only for a boundary reason: that layer cannot reach the behaviour
at all, as with a hardware sensor or a page hosted by a third party. Every exemption names its alternative proof, the
target and scenario in another layer that does cover the behaviour.

Difficulty, runtime, flakiness, cost, and unfinished work are never valid reasons. Each describes a problem to fix, not
a boundary.

An exemption never applies to a `Feature`, a `Rule`, or a `Background`, never to the unit layer, and never removes all
proof of a behaviour.

How exemptions are recorded is an adopter decision:

| Option                            | Gains                                          | Costs                                               |
| --------------------------------- | ---------------------------------------------- | --------------------------------------------------- |
| a comment and tag on the scenario | the reason sits beside the scenario it excuses | the corpus carries test-layer vocabulary            |
| a reviewed inventory file         | the corpus stays a pure statement of behaviour | the inventory can drift from the scenarios it names |

In the tag form, a comment directly above the tag carries the reason and the alternative proof:

```gherkin
# Exemption(e2e): <boundary reason>; alternative-proof: <target> / <scenario name>
@e2e-exempt
Scenario: <scenario name>
```

The integration layer uses `@integration-exempt` in the same way. The adopter enforces the exemption format and these
limits in its own gate or CI.
