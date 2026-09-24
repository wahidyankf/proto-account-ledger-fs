---
name: validating-governance-rules
description: >-
  Guides a repository-wide rules check across names, links, duplicated bodies, contradictions between levels,
  traceability, and word budgets, writing findings as they are confirmed and recommending consolidation only when safe.
when_to_use: >-
  Use when checking a repository's rules for consistency as a whole, or when judging whether two skills or agents should
  be merged.
compatibility: Requires read access to the whole repository and write access to its own report.
---

# Validating Governance Rules

[Rules Quality Gate](../../../repo-governance/workflows/maintenance/rules-quality-gate.md) owns the semantic audit of
one rule, and [Rules Grooming](../../../repo-governance/workflows/maintenance/rules-grooming.md) owns the sweep that
proposes reductions; both hand their findings to
[Rules Propagation](../../../repo-governance/workflows/maintenance/rules-propagation.md), which alone writes. This skill
covers the judgement a repository-wide consistency check needs: what to look at, and how to report it without fixing.

## What a Full Check Covers

| Concern                                  | Owned by                                                                                                                     |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| file names                               | [File Naming](../../../repo-governance/conventions/structure/file-naming.md), read per Repository Validation Methodology     |
| internal links                           | [Internal Links](../../../repo-governance/conventions/writing/internal-links.md), read per Repository Validation Methodology |
| two capabilities carrying one body       | [Capability Forms](../../../repo-governance/development/agents/capability-forms.md)                                          |
| a lower level contradicting a higher one | [Governance Layers](../../../repo-governance/conventions/structure/governance-layers.md)                                     |
| a rule with no recorded principle        | Principle Traceability                                                                                                       |
| a document over its ceiling              | [Document Word Budget](../../../repo-governance/conventions/structure/document-word-budget.md)                               |

A deterministic check the repository already runs is not repeated by reading. Where a calling gate names checks it
delegates, leave them out and record missing evidence as pending, never as a local re-run or an imitation of the check.
Judgement checks, such as whether the levels still cohere, stay in scope.

## Write Findings as They Are Confirmed

A repository-wide check runs long enough to be interrupted. Write each finding to the report as soon as it is confirmed,
per [Temporary Files](../../../repo-governance/conventions/structure/temporary-files.md), so an interruption loses
nothing and a resumed check continues from the report instead of starting over.

## Consolidate Conservatively

When two skills or agents overlap, recommend merging only when every distinct obligation, trigger, and path to finding
it would survive at the kept home. When unsure, recommend keeping them separate: a wrong merge silently loses an
obligation, while a kept overlap stays visible to the next check.

## Report, Never Repair

Each finding names the file, the line, the rule it breaks, and what the rule expects, as Repository Validation
Methodology requires. The check changes nothing it inspects; every repair goes through Rules Propagation.

## Related

- [understanding-governance-architecture](../understanding-governance-architecture/SKILL.md) — the level structure the
  coherence checks rely on.
