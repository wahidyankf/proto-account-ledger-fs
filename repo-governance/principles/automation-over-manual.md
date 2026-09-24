---
description: >-
  States that repetitive, rule-bound work is done by machines once automating it costs less than doing it by hand, and
  that judgement and one-off work stay with people.
when_to_use: >-
  Use when a check or transformation is being done by hand again, or when automation is proposed for work that needs
  judgement.
---

# Automation Over Manual

Work that follows a rule and recurs is done by a machine. Work that needs judgement, or happens once, is done by a
person.

## A Rule Enforced by Memory Is Enforced Sometimes

A manual step depends on someone remembering it, knowing how, and having time — all three, every time. The failure is
not dramatic. The checklist is followed on calm days and skipped on the day it mattered, by the person who was sure this
change could not be affected.

A machine has no calm days. It applies the rule identically to the first change and the thousandth, to a new contributor
and to the maintainer, and it reports a failure while the change is still cheap to fix rather than whenever a reviewer
happens to notice.

It also frees review. Attention spent confirming that formatting is consistent is attention not spent on whether the
approach is sound, which is the question no tool answers.

## When to Automate

| Automate when                                                          | Keep it manual when                                        |
| ---------------------------------------------------------------------- | ---------------------------------------------------------- |
| the task recurs                                                        | it happens once or twice                                   |
| the rule can be written down completely                                | it needs judgement, taste, or knowledge of intent          |
| an omission causes real harm                                           | the rule is still changing faster than automation can keep |
| building and keeping it costs less than the manual work and its errors | the automation would be more complex than the task         |

The comparison includes maintenance. Automation is code, and code nobody keeps current becomes a check enforcing last
year's rule with full confidence.

## The Boundary Runs Both Ways

Leave a mechanical rule to people and it holds only as well as their attention does. Turn a judgement into a machine
rule and it meets situations its author never pictured with the same certainty as the ones they did; the people it
misjudges learn to satisfy the check instead of its intent.

So the principle is not "automate everything". It is: automate what is mechanical, and state plainly what the automation
does not establish, so nobody mistakes a green run for a finished review.

## Where It Is Already Load-Bearing

| Applied in                                                                                   | As                                                                   |
| -------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| [Structural Validation](../conventions/structure/plans/006-structural-validation.md)         | everything mechanically checkable is checked mechanically            |
| [Exclusions](../conventions/structure/plan-validator-contract/004-exclusions.md)             | what needs judgement is deliberately kept out of the validator       |
| [Harness Adapters](../development/agents/harness-adapters.md)                                | adapters are generated and verified by regeneration, never hand-kept |
| [Shared Value Rules](../conventions/structure/artifact-metadata/002-shared-value-rules.md)   | automation normalizes syntax and never authors a description         |
| [Public Outbound Safety](../conventions/security/public-outbound-safety.md)                  | the screen runs first on every surface, not when someone remembers   |
| [Verification Layers](../development/quality/manual-verification/002-verification-layers.md) | green automation never closes a user-facing change on its own        |

## Early, Fast, and Legible

Automation that runs at the earliest point able to see the problem prevents rather than reports. A formatting check
before a commit costs seconds; the same finding in review costs a round trip and someone else's attention.

Automation slow enough to resent gets skipped, so it inspects what changed rather than everything. Automation whose
failure says only "invalid" gets re-run until someone disables it, so it names what was expected, what was found, and
where.

And what is automated is written down. A contributor who cannot see what runs cannot tell whether a green result covered
the thing they changed.

## Where Enforcement Lives

An instruction to run a check is not automation; it is a manual step with better formatting. An adopter enforces an
automated rule in its own hook, gate, or continuous integration, where skipping it takes a deliberate act rather than a
lapse of memory.
