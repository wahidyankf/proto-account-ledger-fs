---
description: >-
  Lists the obligations minimal sufficiency never discounts, requires a narrow regression check for non-trivial logic,
  and keeps verification proportional to risk.
when_to_use: >-
  Use when a smaller change would skip a test, a safeguard, or a required rule, or when deciding how much verification a
  change needs.
---

# What Minimality Never Removes

Minimality bounds scope creep. It never bounds correctness, and keeping a change small is no defence for skipping work
that a rule or the outcome requires.

## Obligations Are Part of Sufficiency

These are the work, not additions to it:

- validating input at a trust boundary;
- handling errors that would otherwise lose data;
- security and accessibility requirements;
- test-first development, specifications, and documentation the repository requires;
- propagating a rule change to everywhere the rule applies;
- calibrating against the real environment where a simulated one cannot prove the behaviour;
- anything the requested outcome states explicitly.

Where a genuinely smaller change would leave a rule unenforced or a boundary untested, the larger change is the minimal
one. Say so rather than shipping the smaller one quietly.

A known defect inside the code a change touches is fixed, not stepped around.
[Plan Execution](../../workflows/plan/plan-execution.md) applies the same rule to failures that predate the work:
pre-existing is an explanation, not an exemption.

## The Narrowest Check That Can Fail

New or changed non-trivial logic leaves behind the narrowest runnable check that would fail if that logic broke. The
check reuses the repository's existing test infrastructure; a framework or fixture set added only to host it is scope
the change did not need.

A trivial one-line change needs no dedicated check only when it alters no governed behaviour and no rule requires one.
Where a testing policy demands stronger evidence, the policy wins.

The check matters more than its size suggests. A change verified only by reading it is a change nobody verified — see
[Evidence Over Assertion](../evidence-over-assertion.md).

## Proportional, Then Stop

Verification scales with the change and its risk: a wording fix and a data migration do not earn the same proof. Every
mandatory gate still runs, whatever the size. Beyond that, among compliant options, choose the one that leaves less to
maintain.

Whether a mechanism was necessary depends on context, so no gate decides it reliably. Review applies this test; the
adopter's own gates keep enforcing the mandatory obligations listed above.
