---
description: >-
  Indexes the catalog's canonical skills, one directory per skill, each holding the SKILL.md a harness reads and the
  resources that skill resolves beside it.
when_to_use: >-
  Use when locating a canonical skill or deciding where a new skill's resources belong.
---

# Canonical Skills

Skills in their canonical form. One directory per skill, each containing a `SKILL.md` and whatever resources that skill
resolves relative to its own directory.

Codex and OpenCode read this layout natively, so for those harnesses the canonical file is already the surface and an
adapter would be a second copy of a file they were going to read anyway. Claude Code reads only `.claude/skills/`, so it
is the one harness that needs a generated route.

## Directory Map

- [adopt-artifact](adopt-artifact/SKILL.md) — mapping a catalog artifact into a repository
- [applying-content-quality](applying-content-quality/SKILL.md) — ordering and repairing a document's quality passes
- [applying-maker-checker-fixer](applying-maker-checker-fixer/SKILL.md) — judgement inside make, check, and fix loops
- [assess-alignment](assess-alignment/SKILL.md) — comparing a repository with the catalog by intent
- [assessing-criticality-confidence](assessing-criticality-confidence/SKILL.md) — rating a finding's consequence and
  certainty
- [building-command-line-interfaces](building-command-line-interfaces/SKILL.md) — judging exit statuses, streams, and
  which runtime default to override
- [developing-applications](developing-applications/SKILL.md) — placing layers, errors, logs, and input checks
- [generating-validation-reports](generating-validation-reports/SKILL.md) — audit and fix reports that survive
  interruption
- [grill-me](grill-me/SKILL.md) — resolving a decision through recommended options
- [plan-creating-project-plans](plan-creating-project-plans/SKILL.md) — authoring a formal plan's six documents
- [plan-grooming-idea-briefs](plan-grooming-idea-briefs/SKILL.md) — promoting, keeping, or retiring an idea brief
- [plan-validating-quality](plan-validating-quality/SKILL.md) — judging whether a plan draft is executable
- [plan-verifying-execution](plan-verifying-execution/SKILL.md) — checking delivered work against its plan
- [plan-writing-gherkin-criteria](plan-writing-gherkin-criteria/SKILL.md) — acceptance scenarios that can actually fail
- [practicing-trunk-based-development](practicing-trunk-based-development/SKILL.md) — keeping work on one trunk in small
  pieces
- [programming-fsharp](programming-fsharp/SKILL.md) — F# work under the F# standard
- [propagating-rules](propagating-rules/SKILL.md) — routing rule work through propagation
- [understanding-governance-architecture](understanding-governance-architecture/SKILL.md) — reading a repository as
  ordered levels
- [understanding-shared-vocabulary](understanding-shared-vocabulary/SKILL.md) — the terms scope decisions turn on
- [validating-governance-rules](validating-governance-rules/SKILL.md) — a repository-wide rules check
- [writing-readme-files](writing-readme-files/SKILL.md) — a root README template and repairs
