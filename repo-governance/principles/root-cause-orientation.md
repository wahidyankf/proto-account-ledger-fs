---
description: >-
  States that a defect is diagnosed before it is fixed, repaired at the layer responsible for it, and never hidden by
  making its symptom disappear.
when_to_use: >-
  Use when a check fails, a bug is reported, or a fix is proposed, and when a defect outside the current task turns up
  along the way.
---

# Root Cause Orientation

Fix the cause, at the layer that owns it. A change that makes a symptom disappear while the cause remains has fixed
nothing; it has removed the only signal that something was wrong.

## Diagnose Before Changing Anything

A fix proposed before the cause is known is a guess. Establish, in order, the exact failure, the path that produces it,
and why that path was taken. Only the last answer names something to fix — so ask of any candidate change which of the
three it addresses.

## Repair at the Responsible Layer

Locate the responsible point first, the way [Scope of a Change](minimal-sufficiency/001-scope-of-a-change.md) requires
before any change is chosen.

Then look past the reported path. When sibling paths share the cause, repair the shared place once. A guard added to
each caller, or a patch on only the path named in the report, leaves the defect for the next caller to find.

## Suppression Is Not a Fix

Each of these makes a report go away and leaves the defect in place:

- catching an error and discarding it, or substituting a default nobody chose;
- loosening an assertion until it holds;
- re-running a check until it passes;
- skipping, quarantining, or deleting the test that found it; and
- adding a bypass or an exception for the one input that failed.

Where the signal itself is genuinely wrong, the rule that produced it is narrowed in a reviewed change. That repairs the
check in the open, which is the opposite of silencing it — see [Fail Closed](fail-closed.md).

## Where It Is Already Load-Bearing

| Applied in                                                                                     | As                                                                   |
| ---------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| [Public Outbound Safety](../conventions/security/public-outbound-safety.md)                    | a false positive is fixed by narrowing the rule, never by a bypass   |
| [Quality Gate Results](../development/quality/manual-verification/001-quality-gate-results.md) | a gate is not re-run until it agrees                                 |
| [Deletion With Proof](../development/quality/deletion-with-proof.md)                           | a failure after retirement means finding what was missed, not a shim |
| [Plan Execution](../workflows/plan/plan-execution.md)                                          | a check already failing before the work began is still fixed         |

## Finished Means the Cause Cannot Recur

A fix is finished when it holds under every condition the cause could produce, not only the one that was reported. What
else the change may carry is owned by [Minimal Sufficiency](minimal-sufficiency.md), under which an adjacent improvement
is always reported rather than folded in. A defect found outside the task is not an adjacent improvement; it follows the
disposition below.

## Decide What Happens to a Defect Beyond Scope

A known defect inside the code a change touches, or a required check that was already failing, is fixed — see
[What Minimality Never Removes](minimal-sufficiency/002-what-minimality-never-removes.md). A defect that lies outside
the task entirely has two defensible dispositions, and an adopter records which it uses.

| Disposition                                                      | Gains                                                                         | Costs                                                                          |
| ---------------------------------------------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| fix it at its cause, in the current work                         | a known defect never outlives its discovery; "already broken" exempts nothing | the change outgrows what was planned and reviewed, and mixes in unrelated risk |
| report it to its owner with the failure, impact, and a next step | the change stays reviewable, and the owner decides                            | the defect survives until someone acts, and unread reports accumulate          |

Under either, a defect once found is never silently worked around or ignored. And a fix that needs a decision only its
owner can make is reported with evidence, whichever disposition applies, rather than guessed.
