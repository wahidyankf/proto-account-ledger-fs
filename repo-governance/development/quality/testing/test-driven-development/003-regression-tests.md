---
description: >-
  Requires every bug fix to land with a test that fails on the defective code, passes on the fix, and keeps passing, in
  a form chosen by the kind of defect, with no exemption for small or urgent fixes.
when_to_use: >-
  Use when fixing a bug or regression, when planning such a fix, or when reviewing whether a fix's test proves the
  defect cannot quietly return.
---

# Regression Tests

A defect fixed without a test that would have caught it is gone only until the next change brings it back. The test is
what turns a fix into a guarantee.

## The Rule

When a bug or regression is discovered, its fix lands with a test that reproduces the defect, in the same commit or the
same proposed change as the fix. That test:

1. fails on the code as it stood before the fix, for the reason the defect gives;
2. passes on the fixed code; and
3. keeps passing on every later build without anyone attending to it.

No exemption exists for a trivial fix, a cosmetic defect, an obvious one-line change, or an urgent hotfix. A fix whose
test is promised for a later change is incomplete until that test lands. The reproducing test is the red of the fix's
first cycle.

## The Form Follows the Defect

| Defect                    | Test that pins it                                                                                                                                                          |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| behavioural or functional | a scenario stating the correct behaviour, bound at the layers [Layers and Adapters](../behaviour-driven-development/002-layers-and-adapters.md) requires, or a narrow test |
| visual or layout          | an assertion on the specific rendered property that was wrong, such as a document element, a computed style, or a compared capture                                         |
| content or copy           | an assertion on the corrected text or translation key, where it is produced or where it is rendered                                                                        |
| integration or API        | an assertion on the response shape, status, or state transition that was wrong                                                                                             |

Whatever the form, a test that also passes on the broken code does not satisfy the rule. It has to make this particular
defect impossible to reintroduce without a failure.

## When the Specification Was Wrong Too

A fix for code that departed from a correct specification needs only the reproducing test. When the specification also
described the wrong behaviour, the specification is corrected in the same change, as Specification Maintenance requires,
and the test follows the corrected statement.

## Planned Fixes

A plan that fixes a defect carries an explicit delivery item that adds the reproducing test, naming the test path and
the defect it pins. The test is then scheduled rather than remembered, and it is written and verified when the plan
runs.

## Before Calling a Fix Complete

- a test targets the specific defect condition, not a general path that passed while the defect existed;
- the test lands with the fix;
- it sits at a layer able to observe the defect; and
- the fast gate passes with both the fix and the test in place.

The adopter enforces the mechanical part, a fix that changes source without adding or changing any test, in its own
review or gate.
