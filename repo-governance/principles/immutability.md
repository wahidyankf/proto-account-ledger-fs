---
description: >-
  States that a value other code or other readers can observe is never changed underneath them: a change produces a new
  value, and mutation stays confined where nothing else can see it.
when_to_use: >-
  Use when deciding whether to update data, shared state, or a published version in place, or when reviewing code that
  shares state between components.
---

# Immutability

A value that something else can observe does not change underneath it. A change produces a new value, and mutation stays
confined to where nothing else is looking.

## Shared Mutable State Is Action at a Distance

The hazard is never the change itself. It is that a holder of the value finds it different from what it read, with
nothing in its own code or its own record to explain why.

In code, that is the argument altered by the function it was passed to, the object two components both write, the race
between two threads. In a repository, it is a published version that now resolves to different content, an input edited
while a review was still reading it, a check that quietly fixes the files it was meant to judge. The failure is the
same: the state a reader relied on has been replaced, and nothing records that it was.

A new value leaves the old one intact. Whoever held it still holds what they read, the difference between the two can be
inspected, and the sequence of values is an audit trail that exists for free rather than being reconstructed.

## What It Requires

- Produce a new value rather than modifying one that anything outside its owner can observe, and treat anything passed
  in as read-only.
- Share no mutable state across components, threads, or readers. Where state must change, one owner changes it and
  everyone else receives new values.
- Supersede an artifact others have pinned or recorded against — a released version, a frozen input — with a new one;
  never edit it in place.
- Make the guarantee checkable where the stack allows it: read-only types, frozen structures, protected release tags. An
  adopter enforces this in its own compiler settings, linter, or release protection rather than in review alone.

## Confined Mutation Is Not a Violation

Observability is the test. Mutation that nothing outside its owner can observe carries none of the hazard, and it needs
no further justification: a function that fills a local list and returns it has changed nothing anyone else holds.

These are common ways of keeping mutation behind that boundary. They are examples, not a closed list:

| Example                                         | Stays confined because                                                                         |
| ----------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| a local accumulator or buffer                   | it is created and filled inside one owner, and callers receive only the finished value         |
| a performance-critical loop or profiled hotspot | the mutable structure never escapes the loop or the owner that runs it                         |
| a dataset too large to copy                     | one owner updates it while nothing else holds it, then hands out a new value or read-only view |
| a mutable library or platform interface         | the mutation happens at the call site, and values crossing into the rest of the code are new   |

The boundary decides, not the reason for approaching it. A mutable structure that is returned, stored, shared, or
captured by something that outlives the change is observable, and no speed gain makes it confined. A library that
mutates is not a licence to spread its style past the boundary where it is called.

## Where It Is Already Load-Bearing

| Applied in                                                                                              | As                                                              |
| ------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| [Surfaces and Mutation](../conventions/structure/repository-configuration/003-surfaces-and-mutation.md) | a check leaves the working tree unchanged                       |
| [Quality Gate](../workflows/plan/plan-quality-gate.md)                                                  | the draft is frozen at a named commit for the gate's duration   |
| [Harness Adapters](../development/agents/harness-adapters.md)                                           | an adapter is regenerated from its source, never edited by hand |

## Examples Are Not the Rule

Each stack has its own idiom for this — a read-only modifier, a persistent collection, a copy-on-write update, an
ownership system that makes shared mutation impossible to express. Those idioms change between languages and versions.
The rule does not: whatever can be observed from outside is not changed from underneath.
