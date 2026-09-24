---
description: >-
  Defines the four criticality levels, the order in which one is assigned, fixed adjustments for builds, security,
  accessibility, and requirement keywords, and which levels block a gate.
when_to_use: >-
  Use when a checker assigns criticality to a finding, or when deciding whether a finding blocks a quality gate.
---

# Criticality Levels

Criticality measures how much a problem matters, independent of how certain anyone is about it.

## Four Levels

| Level      | Meaning                                                                              | Examples                                                       |
| ---------- | ------------------------------------------------------------------------------------ | -------------------------------------------------------------- |
| `CRITICAL` | breaks functionality, blocks users, weakens security, loses data, or violates a MUST | a failing build, an exposed credential, a broken required link |
| `HIGH`     | significantly degrades quality, or violates a documented SHOULD convention           | an accessibility failure at level AA, misleading documentation |
| `MEDIUM`   | a minor quality issue, a style inconsistency, or a MAY guideline not followed        | inconsistent formatting, missing optional metadata             |
| `LOW`      | a suggestion that would improve an already acceptable artifact                       | alternative wording, an optional reorganization                |

## Assign in Order

Stop at the first question answered yes:

1. Does it break something, block a user, weaken security, lose data, or violate a MUST? `CRITICAL`.
2. Does it seriously lower quality, or break a documented SHOULD convention? `HIGH`.
3. Does it amount to a minor quality issue, a style inconsistency, or an unfollowed MAY? `MEDIUM`.
4. Otherwise, `LOW`.

Asking in this order stops a finding from being rated by how easy it is to fix rather than by what it does.

## Fixed Adjustments

Some contexts fix the level whatever category the finding came from:

| Context                                               | Level      |
| ----------------------------------------------------- | ---------- |
| a build failure, or a security weakness of any kind   | `CRITICAL` |
| an accessibility failure at WCAG conformance level A  | `CRITICAL` |
| an accessibility failure at level AA                  | `HIGH`     |
| an accessibility failure at level AAA                 | `MEDIUM`   |
| an unmet MUST or MUST NOT requirement                 | `CRITICAL` |
| an unmet SHOULD or SHOULD NOT requirement             | `HIGH`     |
| an unfollowed MAY guideline, or a style inconsistency | `MEDIUM`   |
| a style preference                                    | `LOW`      |

Requirement keywords carry the meanings given in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

## What Blocks

| Level           | Effect on a gate                                                                        |
| --------------- | --------------------------------------------------------------------------------------- |
| `CRITICAL`      | always blocks; the gate cannot pass until it is fixed                                   |
| `HIGH`          | fixed before publication; blocks unless explicitly dispositioned with a recorded reason |
| `MEDIUM`, `LOW` | never blocks; reported, and each one left unfixed still carries an explicit disposition |

Results and dispositions follow [Quality Gate Results](../../manual-verification/001-quality-gate-results.md). Treating
`HIGH` as blocking unless dispositioned is deliberately the stricter choice: a significant problem left without a
recorded decision is silence, and silence afterwards looks exactly like oversight.

## Status Labels Stay Separate

Some checkers also mark each item's observed status, such as verified or broken. Those labels say what was seen;
criticality says how much it matters. A report keeps both.
