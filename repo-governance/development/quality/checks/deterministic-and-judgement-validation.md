---
description: >-
  Assigns every validation category to exactly one layer, a deterministic preflight or a judgement checker, and fixes
  the machine-readable handoff between the two.
when_to_use: >-
  Use when adding a validation category, deciding whether a check belongs in a script or with a reviewing agent, or
  wiring a judgement checker to consume deterministic results.
---

# Deterministic and Judgement Validation

Validation runs in two layers. A deterministic preflight settles every question an exact predicate can answer; a
judgement checker, whether a person or an agent, handles only what needs reading for meaning. Each category belongs to
exactly one of them.

This standard implements [Automation Over Manual](../../../principles/automation-over-manual.md),
[One Source Per Fact](../../../principles/one-source-per-fact.md),
[Reproducibility](../../../principles/reproducibility.md), and [Fail Closed](../../../principles/fail-closed.md).

## One Owner Per Category

| The rule can be decided by                                                            | Owner                                                     |
| ------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| an exact predicate: a pattern, a file's existence, field equality, a hash comparison  | deterministic preflight                                   |
| judging a passage for a semantic property: meaning, contradiction, accuracy, or voice | judgement checker                                         |
| both                                                                                  | split into a mechanical sub-rule and a judgement sub-rule |

Never give one rule to both layers. Two owners report the same finding twice, leave it unclear which report counts, and
spend judgement on what a script already settled.
[Exclusions](../../../conventions/structure/plan-validator-contract/004-exclusions.md) draws the same boundary for plan
validation.

## Deterministic Contract

A deterministic category:

- runs as a dedicated command;
- emits its findings in a versioned, machine-readable envelope;
- gives each finding a stable key built from its category, file, and a digest of its message, so a finding keeps its key
  from run to run;
- produces byte-identical output for identical input and a fixed clock; and
- ships with unit tests for its pure check logic and an integration test that runs the check against a real fixture
  tree, together covering both a passing and a failing input.

| Envelope member | Holds                                                   |
| --------------- | ------------------------------------------------------- |
| schema          | the envelope name and version                           |
| status          | whether the preflight itself completed                  |
| revision        | the commit or content digest that was checked           |
| categories      | for each category: name, command, result, and findings  |
| findings        | for each finding: key, criticality, file, line, message |

## Judgement Contract

A judgement category defines the predicate it applies, declares a criticality under Criticality Levels, and names the
rule it enforces. Where a deterministic check exists for the same rule, it delegates to that result rather than
evaluating the rule again.

## The Handoff

1. The preflight runs first and writes its envelope.
2. The checker reads the envelope and validates its schema name and version.
3. The checker skips every category the envelope covers.
4. Its report carries the deterministic findings verbatim, in their own section ahead of the judgement findings.
5. On a re-validation pass, an unchanged envelope digest lets it reuse that section and re-evaluate only the judgement
   categories.

When the envelope is missing, unreadable, or of an unexpected version, the checker records the preflight as not run and
evaluates those categories in full. It never reports them clean: a skipped category that reads as a passing one is
exactly the failure the split exists to prevent.

## Move a Category When Its False Positives Repeat

A judgement category becomes a candidate for a deterministic check when all three conditions hold:

- the same false-positive shape appears in three or more consecutive reports;
- the shape can be written as an exact predicate; and
- encoding it loses no meaning the judgement supplied.

The move is proposed as planned work, and the judgement category's coverage shrinks by exactly what moved.

## Out of Scope

This standard fixes the contract between the layers, not how either is built. Which model or reviewer performs
judgement, and the language a preflight is written in, stay with the adopter.
