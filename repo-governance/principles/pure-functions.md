---
description: >-
  States that logic deciding what should happen is deterministic and free of effects, and that effects sit at a thin
  boundary which gathers inputs and carries out the decision.
when_to_use: >-
  Use when designing a tool, gate, generator, or module, or when a result changes between runs over what looks like the
  same input.
---

# Pure Functions

Decide in one place; act in another. The part that decides returns the same answer for the same inputs and changes
nothing outside itself. The part that acts is thin, sits at the edge, and holds no decision worth testing.

## What It Requires

**Every input is visible.** The clock, a random source, the working directory, the environment, a global setting, and
the order a filesystem happens to list files in are all inputs. A decision that reads one of them directly has an
argument its caller cannot see. Pass it in.

[Explicit Over Implicit](explicit-over-implicit.md) asks that a dependency be declared. This asks something narrower:
that a decision's answer depend on nothing its caller did not pass.

**The decision has no effect.** It does not write a file, send a request, or print, and it does not change a value its
caller still holds — see [Immutability](immutability.md). It returns what should happen, and something else makes it
happen.

**Effects sit at the boundary.** Reading configuration, calling the network, touching disk, and reporting results happen
in a shell that gathers inputs, calls the decision, and carries out its answer. The shell stays thin enough that there
is little in it to get wrong.

## Where It Is Already Load-Bearing

| Applied in                                                                                          | As                                                                               |
| --------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| [Inputs and Exit Classes](../conventions/structure/plan-validator-contract/001-inputs-and-exits.md) | output is identical from any working directory and byte-identical across runs    |
| [Shared Value Rules](../conventions/structure/artifact-metadata/002-shared-value-rules.md)          | diagnostics sort by position, never by the order the filesystem listed them      |
| [Gate Entries](../conventions/structure/repository-configuration/002-gate-entries.md)               | an argument vector has no shell to rewrite it against the current directory      |
| [Harness Adapters](../development/agents/harness-adapters.md)                                       | an adapter derives from canonical input alone, so a regeneration can be compared |
| [Assess Alignment](../workflows/adoption/assess-alignment.md)                                       | the assessment decides and reports; changing the repository is another workflow  |

## Why the Boundary Matters

A pure decision is tested with an input and an expected output. Nothing is mocked, nothing is set up, and the test means
the same thing on every machine. An impure one is tested by rebuilding the world it reads, and the test is only as good
as that rebuild.

A pure decision can be repeated to confirm a result, run by two implementations and compared, cached, and run
concurrently without coordination. Each of those breaks the moment the decision reads something its caller did not pass.

The failure is quiet. A hidden input produces two runs that look identical and disagree, and the usual response —
running again until the answer settles — teaches everyone that the result is negotiable.

## A Design Rule, Not a Paradigm

This does not choose a language, a paradigm, or a style. A class can hold a pure core, and a function written in a
functional language can still read the clock. What breaks the rule is a decision that reads or changes something its
caller cannot see, whatever it is written in.

Effects are not the problem. They are usually the reason the program exists, and the rule is only about where they sit.

Where the effect is the whole job — copy this file, send this message — there is no decision to separate, and inventing
one is complexity with no return. The rule applies wherever logic worth verifying would otherwise be tangled with the
act of carrying it out.
