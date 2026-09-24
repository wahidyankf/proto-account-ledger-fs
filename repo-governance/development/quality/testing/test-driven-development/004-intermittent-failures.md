---
description: >-
  Treats a test that passes and fails on the same code as a defect, requires reproducing it and removing its source of
  nondeterminism, and rules out retries, sleeps, loosened assertions, and quarantine as remedies.
when_to_use: >-
  Use the moment a test both passes and fails with no code change, before re-running it, or when a tool labels a test as
  flaky.
---

# Intermittent Failures

A test that passes and fails on the same code is a defect, either in the test or in the code it tests. It is never noise
to live with, and never a reason to run the job again.

This is the stricter rule. Tolerating one known flaky test teaches everyone to re-run red results, and the next red that
matters is re-run as well.

## Confirm It Was the Same Code

The rule binds when both outcomes came from the same code in the same environment. A tool's flaky label does not show
that. Build tools commonly compare only their declared inputs, so an installed dependency, a toolchain change, or a
cleared cache between two runs yields two outcomes with no nondeterminism anywhere.

Before investigating, name what changed outside those declared inputs between the runs. If something did, the defect is
an environment that was never properly prepared, and the fix is to prepare it. If nothing did, the rule applies in full.
"The environment changed" is a claim to check and record, never a default explanation for an awkward red.

## Required Response

1. Reproduce the failure, repeating or stressing the test until it fails on demand.
2. Find the source of nondeterminism: ordering, timing, shared state, the real clock, randomness, fixtures left behind,
   or reliance on the network or the filesystem.
3. Remove that source, then confirm the test stays stable under the same repetition that reproduced the failure.

## Remedies That Only Hide It

None of these resolves an intermittent failure:

- re-running the test, the job, or the pipeline until it passes;
- adding a sleep, or lengthening a timeout, to outlast a race;
- loosening, narrowing, or deleting an assertion so the unstable value stops mattering;
- reordering, isolating, or serializing tests so the interaction no longer surfaces;
- skipping, quarantining, marking as an expected failure, or deleting the test; and
- recording it as an infrastructure fault without evidence that names the infrastructure cause.

A retry, delay, or timeout is legitimate only when it models real behaviour of the subject, such as documented latency
in an external dependency, with the reason recorded where it is added.
[Root Cause Orientation](../../../../principles/root-cause-orientation.md) states the general rule against suppression.

## When the Race Is in Production Code

When the nondeterminism lives in the code under test, it is a production defect and is fixed in that code. Surfacing in
a test first does not make it acceptable; it makes the test the earliest evidence of a failure users would meet later.

## Enforcement

No check can tell a timeout raised to model real latency from one raised to outlast a race, so the response itself is
judged in review. The gates support it by failing on a red test instead of tolerating one. An adopter enforces the ban
on automatic test retries and quarantine markers in its own test runner configuration and review.
