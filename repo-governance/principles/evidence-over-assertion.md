---
description: >-
  States that a claim about what happened is worth nothing until something outside the claim confirms it, and that
  confidence is not a substitute for the confirmation.
when_to_use: >-
  Use when recording that work is done, when reviewing such a record, or when deciding whether a demonstration is worth
  the time it costs.
---

# Evidence Over Assertion

A claim that something happened is not the thing happening. The gap between them is where most wrong beliefs about a
repository live.

## Confidence Is Not the Variable

The failure this prevents is rarely dishonesty and almost never carelessness. It is a competent person being sure, and
being sure feels identical whether or not the belief is true. That is the whole difficulty: the internal signal that
would tell you to check is the one thing certainty removes.

So the standard cannot be how confident the claimant is. It has to be whether something outside the claim agrees, and
whether a later reader can see that agreement without re-doing the work.

## Where It Is Already Load-Bearing

| Applied in                                                                         | As                                                                |
| ---------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| [Deletion With Proof](../development/quality/deletion-with-proof.md)               | disable the thing and demonstrate that something fails            |
| [Delivery Contract](../conventions/structure/plans/004-delivery-contract.md)       | a ticked box says an action happened, not what it produced        |
| [Dev Artifact Clean-Up](../workflows/maintenance/dev-artifact-clean-up.md)         | a cleanup performed but not verified is a claim                   |
| [Execution Check](../workflows/plan/plan-execution-check.md)                       | a declared gate that never ran is not a passing gate              |
| [Evidence and Quality](../conventions/structure/plans/007-evidence-and-quality.md) | evidence is a file with a command, a commit, a time, and a result |
| [Manual Verification](../development/quality/manual-verification.md)               | a green pipeline does not become sufficient by being convenient   |

## The Demonstration That Can Contradict You

Not all evidence is equal. A demonstration that could only ever confirm what you already believed has cost time and
established nothing.

The valuable one is the step that can come back wrong: disabling the thing you are about to delete, re-running the
command rather than re-reading its recorded output, checking the file exists at the path the item named. These are the
steps most often skipped, and they are skipped precisely because they are the only ones with anything at stake.

When skipping one is rationalized as obvious, notice that obvious things are cheap to demonstrate.

## Sanitized, and Still Evidence

A record that reproduces what made a finding a finding has published it a second time. Evidence that cannot be recorded
safely is recorded structurally — how many findings, of what class, on what surface — and the unsafe detail stays out.

Summarizing is not weakening. A count and a class are checkable by someone who was not there, which is the property that
made it evidence in the first place.
