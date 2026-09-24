---
description: >-
  States that every control in this catalog refuses when it cannot decide, and that a check which could not run is never
  reported as a check that passed.
when_to_use: >-
  Use when designing a gate, a validator, or any control that can be absent, unreadable, or unable to reach a verdict.
---

# Fail Closed

A control that cannot decide refuses. It does not guess, default, or pass.

This is the most frequently applied rule in this catalog and, until now, the one stated nowhere as a truth in its own
right. It is written here once so that the places applying it can stop re-arguing it.

## What It Requires

Three distinct outcomes, never two: clean, a finding, and could-not-decide. Collapsing the third into the first is the
failure this principle exists to prevent, because the two are indistinguishable to everyone downstream and one of them
is a lie.

A missing input is a refusal. An unreadable one is a refusal. An unknown value where a closed set was expected is a
refusal. Silence is never consent.

## Where It Is Already Load-Bearing

| Applied in                                                                                              | As                                                                       |
| ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| [Public Outbound Safety](../conventions/security/public-outbound-safety.md)                             | a scan that failed to run never counts as a pass                         |
| [Inputs and Exit Classes](../conventions/structure/plan-validator-contract/001-inputs-and-exits.md)     | exits `2` and `3` are never reported as a clean run                      |
| [Top-Level Schema](../conventions/structure/repository-configuration/001-top-level-schema.md)           | an unknown top-level key fails rather than being ignored                 |
| [Surfaces and Mutation](../conventions/structure/repository-configuration/003-surfaces-and-mutation.md) | a gate declaring no surface fails rather than being silently skipped     |
| [Governance Categories](../conventions/structure/repository-configuration/004-governance-categories.md) | an undeclared category fails rather than being inferred from a directory |
| [Harness Adapters](../development/agents/harness-adapters.md)                                           | a capability with no harness equivalent is a hard failure                |

Six applications, one rule. That count is the argument for stating it here.

## Why Not the Convenient Default

Every failure-open default is chosen to be helpful in the common case, and every one of them is wrong in exactly the
case that mattered — the one where something was already broken.

A validator that treats an unreadable configuration as an empty one reports a clean repository. A scanner that treats a
crashed detector as a clean scan publishes the secret it was installed to catch. A generator that emits a default the
repository never chose replaces the harness's own behaviour with a guess frozen at generation time.

In each, the failure is not that the tool was wrong. It is that the tool was wrong _and said it was right_, which is the
only outcome from which nobody recovers.

## The Cost Is Real and Is Accepted

Failing closed is louder. It stops work for a missing file, an unreadable path, a term set nobody updated. That noise is
the price, and it is paid deliberately: an alarm that fires when it cannot see is annoying, and an alarm that goes quiet
when it cannot see is worthless.

Where the noise is genuinely wrong, the fix is to narrow the rule in a reviewed change. It is never to add a bypass —
see [Public Outbound Safety](../conventions/security/public-outbound-safety.md), which says the same thing about the
same temptation.
