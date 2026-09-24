---
description: >-
  States that behaviour a reader depends on is written where it applies, and that a default, an inference, or an
  unstated convention is a decision nobody can see.
when_to_use: >-
  Use when a value, permission, dependency, or outcome is about to be left for a tool or a reader to infer, or when
  deciding which fields a schema requires.
---

# Explicit Over Implicit

Behaviour that matters is written where it applies. Whatever a reader has to infer, the next reader will infer
differently.

## A Default Is a Hidden Decision

Every implicit behaviour was chosen by someone: a framework author, a tool maintainer, whoever wrote the fallback
branch. Leaving it implicit does not remove that decision. It removes the only place a reader could have seen it.

That is harmless while the default matches intent, and on the day anyone relies on it, it does. It stops matching when
the tool changes version, when the file is copied somewhere with a different default, or when a new reader brings a
convention from elsewhere. None of those raises an error. The behaviour simply changes, and the first sign is a
consequence.

## What It Requires

| Concern       | Explicit form                                                  | Implicit form it replaces                        |
| ------------- | -------------------------------------------------------------- | ------------------------------------------------ |
| configuration | every value a reader depends on, written out                   | whatever the tool happens to do today            |
| permissions   | granted by name, the narrowest that does the job               | inherited, or assumed from what is available     |
| dependencies  | declared at the point of use                                   | reached through global state or auto-discovery   |
| outcomes      | a recorded decision, disposition, or authorization             | inferred from silence, or from nothing objecting |
| assumptions   | checked where they are made, and failed loudly when they break | trusted until something distant goes wrong       |

Mechanical parts belong in the adopter's own schema validation: a required key that is missing fails there rather than
being filled with a default.

## Where It Is Already Load-Bearing

| Applied in                                                                                              | As                                                                           |
| ------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| [Top-Level Schema](../conventions/structure/repository-configuration/001-top-level-schema.md)           | visibility is required rather than guessed from where the repository lives   |
| [Governance Categories](../conventions/structure/repository-configuration/004-governance-categories.md) | a category is declared, never inferred from a directory                      |
| [Verification Layers](../development/quality/manual-verification/002-verification-layers.md)            | an assertion states its procedure, observation, failure signal, and evidence |
| [Executor Authority](../development/agents/planning-capabilities/004-executor-authority.md)             | authorization is granted explicitly and recorded, not assumed from context   |
| [Adopt Artifact](../workflows/adoption/adopt-artifact.md)                                               | only an explicit request naming the artifact opens the workflow              |
| [Deletion With Proof](../development/quality/deletion-with-proof.md)                                    | every responsibility names its successor explicitly, by path                 |

## The One Explicit Omission

Every setting a reader depends on is written out. The only exception is an omission whose meaning a published contract
defines: an optional setting whose documented contract says the host tool's own default applies tells a reader holding
only that contract exactly what happens. One instance is an omitted model mapping, which the adapter standard documents
as leaving the harness's own inheritance in place — see [Harness Adapters](../development/agents/harness-adapters.md).

This is a narrow exception, not a general allowance. An absence whose meaning a tool picks for itself, or that no
published contract defines, is implicit, and the value is written out. The test is whether a reader holding only the
written contract can predict the behaviour.

## Not the Same as Fail Closed

The two meet, but they answer different questions. This principle is about how behaviour is specified, so that nothing
is left to guess. [Fail Closed](fail-closed.md) is about what a control does when a specification is missing anyway. An
explicit contract gives a closed control something to check; a closed control makes missing explicitness visible instead
of quietly filling it in.

## The Cost Is Verbosity

Writing out what a tool would have done anyway is more text, and it looks redundant next to the default it repeats. The
repetition is the point, because it survives the default changing. It is also not a second copy of anything: what the
repository decided and what a tool defaults to are different facts, and only the first is the repository's to state —
see [One Source Per Fact](one-source-per-fact.md).

Where the verbosity becomes a burden, the fix is a contract with fewer choices, not a contract with hidden ones.
