---
name: assess-alignment
description: >-
  Guides comparing a repository against the catalog by intent, choosing between the four equivalence statuses, and
  reporting contradictions honestly.
when_to_use: >-
  Use for a bounded read-only comparison against the catalog; do not use to adopt or modify artifacts.
compatibility: Requires read access to the repository being assessed.
---

# Assessing Alignment

The [Assess Alignment](../../../repo-governance/workflows/adoption/assess-alignment.md) workflow owns the sequence. This
is about the judgement inside it, which is almost entirely one question: does this repository already achieve what the
artifact is for?

## Compare Intent, Not Text

An artifact exists to make something true. Alignment is about whether that thing is true, in whatever form the
repository chose.

Two rules with different wording, different structure, and different examples can produce identical behaviour. Two rules
with nearly identical wording can produce different behaviour if one carries an exception the other does not. Reading
for text similarity gets both cases wrong.

The useful test: describe what the catalog artifact prevents or guarantees, in one sentence, without using its words.
Then ask whether the repository prevents or guarantees that.

## Choosing Between the Statuses

The hard boundary is between `locally-adapted-equivalent` and `conflict`, and it is worth being slow about.

Ask whether the difference changes what happens in any case either rule covers. If it does not, the local form is
equivalent. If it does, it is a conflict — even a small one, and even when the local form is arguably better.

`local-extension` is for behaviour the repository adds that the artifact does not address, and which does not contradict
it. Additional strictness is usually an extension. Additional permissiveness usually is not.

`not-applicable` needs a reason about the repository, not about the artifact. "We do not do that here" is a restatement;
"this repository has no user-facing surface" is a reason.

## Read the Local Instructions First

A repository's rules exist because of constraints an outside comparison cannot see. A deliberate divergence, recorded in
the repository's own instructions, is a decision — reporting it as a gap tells the user something false about their own
work and quietly proposes undoing it.

## Report Contradictions Plainly

A `conflict` or a `gap` is the most useful thing an assessment produces. Softening one into a success status makes the
report agreeable and worthless, and an assessment that never finds anything is one nobody needs to run.

## Write Nothing

Not a file, not a fix, not a branch. The value of this comparison is that it is safe to run on anything at any time, and
that property survives exactly as long as it is absolute.
