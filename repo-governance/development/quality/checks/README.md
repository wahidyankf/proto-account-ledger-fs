---
description: >-
  Indexes the repository check standards: how every rule is enforced, which gate runs each check, how strict lint and
  Markdown checks are, how validators are built, and what a new check needs before it is added.
when_to_use: >-
  Use when adding, placing, or tightening an automated check, or deciding whether a validation belongs to a
  deterministic check or a judgement review.
---

# Checks and Gates Standards

Check and gate standards. They answer which automated check runs where, how strict it is, and how it earns its place.

## Directory Map

- [Automated Quality Gates](automated-quality-gates.md) — which checks run at commit, message, push, and pipeline time
- [Deterministic and Judgement Validation](deterministic-and-judgement-validation.md) — one owning layer per category,
  and the handoff between layers
- [Lint Strictness](lint-strictness.md) — failing at warning severity, cleaning a backlog before a gate goes live,
  documented waivers, and reviewed autofixes governs, anchored and escaped patterns, file-relative paths, recorded edge
  cases, and documented checks superficial satisfaction, and nothing inspected is no pass
