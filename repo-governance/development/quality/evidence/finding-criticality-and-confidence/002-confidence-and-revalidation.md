---
description: >-
  Requires whoever applies findings to re-validate each one first, assign one of three confidence levels, act according
  to that level, and record the reasoning.
when_to_use: >-
  Use when a fixer, maker, or repair pass is about to apply findings from a checker, or when a finding looks wrong.
---

# Confidence and Re-Validation

A finding is a claim made at one moment. By the time anyone applies it, the file may have changed, the checker may have
misread the context, or the rule may not apply. Applying findings without looking again turns a checker's mistake into a
defect.

## Re-Validate Before Applying

Whoever applies findings, whether a dedicated fixer, the original maker, or a repair pass, re-validates every finding
against the current state before acting:

1. Classify it as objective, a fact that can be checked such as a missing field, or subjective, a judgement such as
   unclear wording.
2. Re-check it: read the current file and confirm the problem exists, at the stated location, under the stated rule.
3. Assess the fix: whether it is unambiguous, confined to the finding, and unable to break anything else.
4. Assign a confidence level and act on it.
5. Record the decision.

## Three Levels

| Level            | When                                                                                     | Action                                                      |
| ---------------- | ---------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| `HIGH`           | the finding is objective, re-validation confirms it, and the fix is safe and unambiguous | apply the fix                                               |
| `MEDIUM`         | the finding is subjective, ambiguous, or depends on context the applier cannot settle    | skip it and flag it for human review                        |
| `FALSE_POSITIVE` | re-validation disproves the finding                                                      | skip it and report it, with a suggested checker improvement |

## Record the Decision

For each finding, record what was re-validated, the confidence level, the reasoning, and the action taken. An unrecorded
skip is indistinguishable from a finding nobody read.

## False Positives Improve the Checker

Every `FALSE_POSITIVE` report names the finding, why it is wrong, and what change to the checker would stop it
recurring. The finding's criticality sets how urgent that improvement is, because a false `CRITICAL` erodes trust in
every gate that relies on the checker.

A false-positive shape that keeps recurring and can be written as an exact predicate is a candidate to move under
[Deterministic and Judgement Validation](../../checks/deterministic-and-judgement-validation.md).
