---
description: >-
  Fixes how a change is scoped: understand the responsible path, prefer what already exists to what must be owned,
  refuse speculative scope, and stop once the outcome is verified.
when_to_use: >-
  Use when starting a task, choosing between reuse and new code, or deciding that work in progress is finished.
---

# Scope of a Change

A change is minimal when nothing in it is unnecessary, not when it is short. A large change whose parts must land
together can be minimal; a one-line change that adds an unused option is not.

## Understand Before Choosing

Read the task, the specification or tests governing the behaviour, and the code that implements it. Trace the flow to
the point responsible for the outcome, and find every caller of what is about to change.

Minimal is measured against the problem, never against the size of the diff; where the problem is a defect,
[Root Cause Orientation](../root-cause-orientation.md) decides where the repair belongs.

## Prefer What Already Exists

What already exists beats what must be added and owned. Once the problem is understood, stop at the first option that
fully meets the need:

1. No change, because the outcome already holds or is not needed.
2. An existing mechanism, helper, or pattern in the repository.
3. The language's standard library.
4. A capability the platform already provides.
5. A dependency already present.
6. One clear expression, where it stays correct and readable.
7. New code, as little as does the job.

A clear manual step is also an option where the need is rare; automating it is speculative scope, below.

The order is the default. An adopter may reorder options 2 to 6, for example ranking one clear expression above a
dependency the code otherwise barely touches, by recording the order it uses. A fixed order makes the choice mechanical
and quick to review; a local order can fit ownership costs better, at the price of a judgment each reviewer must check
against the record. The first and last options never move.

Prefer deletion to addition and the familiar construct to the clever one. Among equally small options, take the one that
handles the real edge cases. When a requested mechanism exceeds the underlying need, say so and show the smaller route
before building it.

## Refuse Speculative Scope

No option nobody asked for, no abstraction with one caller, no generalization of a one-off change, no automation of a
rare step merely because it can be automated, and no enforcement for a risk nobody has demonstrated beyond what the
obligations in [What Minimality Never Removes](002-what-minimality-never-removes.md) already require. Each is a promise
to keep with no present reason to keep it.

Two copies are refused for the same reason: a rule already enforced by something executable, restated beside it as
metadata that must then be kept in step, and a wrapper command that only renames another command a contributor could run
directly.

A maintained surface earns its place continuously, not once. When it grows, or the need that justified it disappears,
its value is judged again. Passing tests prove that something works, not that it deserves permanent upkeep.

## Stop

Stop when the outcome holds and every required check passes. Adjacent improvements noticed on the way are always
reported, not folded in: a change that fixes one thing and improves four others cannot be reviewed as any of them. A
defect found outside the task is not an adjacent improvement; it follows the disposition the adopter records under
[Root Cause Orientation](../root-cause-orientation.md).

A deliberate simplification that accepts a known ceiling — a coarse lock, a quadratic scan, a naive heuristic — names
the ceiling and the path past it where the code is written. An ordinary trade-off needs no such note.
