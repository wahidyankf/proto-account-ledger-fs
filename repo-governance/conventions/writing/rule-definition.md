---
description: >-
  Defines what a rule is, how its wording fixes its strength, which rule-bearing locations hold rules, and what every
  rule carries: one canonical source, a stated reason, and a named enforcement point.
when_to_use: >-
  Use when writing or changing a rule, when judging how strongly a sentence binds, or when deciding whether a file holds
  rules at all.
---

# Rule Definition

A rule is a statement that directs or constrains a decision, behaviour, standard, or procedure within a stated scope. It
tells a reader — person or agent — what is required, prohibited, expected, or permitted, and names its scope or inherits
it from the document it sits in.

Counting documents does not count rules. One convention can carry many of them, and an index line can point at a rule
whose full wording sits in another document.

## Supporting Text

Rationale, explanation, and examples support a rule and add no obligation unless they carry their own direction or
constraint; supporting text that does binds like any rule. An example that only implies a requirement the prose never
states is a defect: a reader who skips examples and one who copies them follow different rules.

## Strength Is Read From the Wording

| Wording                    | Strength                                                         |
| -------------------------- | ---------------------------------------------------------------- |
| **must**, **must not**     | a mandatory requirement or prohibition                           |
| **should**, **should not** | expected behaviour; a deviation is allowed and states its reason |
| **may**                    | permission; never an obligation, and never a polite "must"       |

Strength comes from the words, never from tone. Two documents stating one requirement at different strengths contradict
each other.

A bare imperative binds like **must** unless its context marks it optional. An unqualified declarative's strength is the
adopter's decision:

- **Like must:** unambiguous and scannable, but ordinary prose binds too.
- **Context decides:** natural prose, but each reader judges whether it does.

## One Canonical Source

Every rule has exactly one canonical source, and that source sits in the [governance hierarchy](../../README.md), whose
level fixes its precedence. Root instruction files, agent and skill definitions, gate declarations, and tool
configuration implement or summarize a hierarchy rule: they link to it and yield to it on conflict.

Any other place that needs the rule links to it instead of restating it, because a restatement is a second copy that
will eventually disagree — see [One Source Per Fact](../../principles/one-source-per-fact.md). When a summary and the
canonical source disagree, the canonical source wins and the summary is the defect.

## Every Rule States Its Reason

A rule says what must be true and why. A rule without a reason survives only until following it is inconvenient.

State the rule as a constraint on an outcome rather than an instruction for a tool. "Every internal link resolves"
outlives the validator that checks it; "run the link checker" does not.

## Every Rule Names Its Enforcement

Prefer a rule a gate or validator can check. A rule names what would catch a violation — a gate, a hook, a validator, or
a review step. Where nothing checks it, the rule says so: an unenforced rule depends on attention, and the document
should not pretend otherwise.

When a check and its rule disagree, the check carries the defect; the rule is never rewritten to fit the check.

## Rule-Bearing Locations, Not a Directory

A repository's rules sit in every location that binds how work happens, whatever tree holds it: governance prose, root
instruction files, agent and skill definitions, machine-readable gate declarations, and the hooks, pipeline jobs, and
linter configuration that make those declarations bite. A rules sweep limited to one directory misses the rest without
warning.

An unclear file holds rules only if it passes both questions, asked in order:

1. Does editing it change what someone is **required** to do, rather than what they know?
2. Does that requirement outlive the piece of work that prompted it?

Explanatory documentation fails the first question. A plan fails the second: it expires with its delivery.

The declaration that a gate runs is a rule; the code implementing that gate is product code, governed through its own
tests and review. The boundary grants no exemption: a rules review checks each gate declaration against its
implementation for drift.

## Enforcement

The repository's own review checklist or gate checks every new or changed rule for strength wording, a single canonical
source, and its reason and enforcement clauses.
