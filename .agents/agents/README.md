---
description: >-
  Indexes the catalog's canonical agent definitions, each declaring what it needs and what it must not do before any
  harness adapter translates that declaration.
when_to_use: >-
  Use when locating a canonical agent definition or deciding what a new one must declare.
---

# Canonical Agents

Agent definitions in their canonical, harness-neutral form. One Markdown file per agent.

An agent here declares what it needs and what it must not do in this repository's own vocabulary, and a harness adapter
translates that declaration into whatever the harness understands. The canonical file is the one a human edits; an
adapter is generated from it and is never edited in place.

## Directory Map

- [plan-checker](plan-checker.md) — auditing a plan draft against the plan specification
- [plan-execution-checker](plan-execution-checker.md) — auditing finished plan execution before archival
- [plan-maker](plan-maker.md) — authoring a formal plan through both decision gates
- [repo-explorer](repo-explorer.md) — locating repository evidence with cited files and lines
- [repo-rules-checker](repo-rules-checker.md) — auditing a repository's rules for contradictions and drift
- [repo-rules-fixer](repo-rules-fixer.md) — applying re-validated rule repairs through Rules Propagation
- [repo-rules-maker](repo-rules-maker.md) — authoring a rule at its level inside Rules Propagation
- [swe-code-checker](swe-code-checker.md) — auditing project code against adopted standards and test-first evidence
- [swe-code-fixer](swe-code-fixer.md) — applying re-validated code findings, test-first where a fix needs a test
- [swe-code-maker](swe-code-maker.md) — building behaviour test-first under the adopted and stack standards
