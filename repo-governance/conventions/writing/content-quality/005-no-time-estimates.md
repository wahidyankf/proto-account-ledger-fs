---
description: >-
  Prohibits time estimates in documentation and learning content, and states what a document says about scope and
  outcome instead.
when_to_use: >-
  Use when writing a tutorial, guide, course, or reference that might state how long something takes, or when reviewing
  one for duration claims.
---

# No Time Estimates

Documentation and learning content carries no time estimate: no "takes 30 minutes", no "estimated time: two hours", no
"learn this in an afternoon".

## Why

Readers work at different speeds and start from different places, so an estimate is wrong for most of them. It is wrong
in the most harmful direction for the reader who most needs the material: a learner who takes longer than promised
concludes that they are failing, not that the estimate was a guess.

An estimate is also a claim nobody maintains. The content changes and the tools change, and the stated duration stays,
still presented as fact.

## What to Say Instead

State the outcome, the prerequisites, and the depth:

```text
Incorrect: This tutorial takes about 45 minutes.
Correct:   By the end of this tutorial you can deploy a service and roll it back.
Correct:   Prerequisites: a working shell and a container runtime.
Correct:   Covers the fundamentals at introductory depth.
```

Depth and coverage are allowed because they describe what the content contains, not how long a reader will take with it.

## Scope

Applies to tutorials, how-to guides, courses, and any reference or explanation with a learning component.

A duration that is a fact about a system rather than a prediction about a reader is not an estimate. A token lifetime, a
timeout, or a retention period is documented as configured.

Plans are governed by [Plans](../../structure/plans.md), not by this module.
