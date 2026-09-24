---
name: understanding-shared-vocabulary
description: >-
  Carries the operative meaning of the terms scope decisions turn on, such as rule, governance tree, delivery unit,
  surface, and adapter, to agents that do not read the root instructions, each linked to the document that owns it.
when_to_use: >-
  Use before deciding what a rule covers, which tree a file belongs in, or whether two pieces of work are one delivery
  unit or two.
compatibility: Requires read access to the documents each term links.
---

# Understanding Shared Vocabulary

A delegated agent does not inherit the root instruction file, so the vocabulary that decides scope reaches it here. Each
entry gives the operative meaning and links the document that owns the term; where the two differ, the owning document
wins.

Most scope disputes are vocabulary disputes: two readers who disagree about whether a rule applies usually agree on the
rule and differ on one word in it.

## Terms

- **Rule and rule-bearing location.** A rule directs or constrains a decision within a scope, and it binds wherever it
  sits: governance prose, root instruction files, agent and skill definitions, gate declarations, and the hooks and
  pipeline jobs enforcing them. A file holds rules only if editing it changes what someone is required to do, and that
  requirement outlives the work that prompted it. See
  [Rule Definition](../../../repo-governance/conventions/writing/rule-definition.md).
- **Governance and documentation.** A document belongs to one tree, chosen by its reader: someone changing the
  repository reads governance, and someone using what it produces reads documentation. Plans expire with their delivery,
  and specifications hold the as-built behaviour that durable outcomes become, never a plan's acceptance criteria. See
  Documentation Architecture, [Plans](../../../repo-governance/conventions/structure/plans.md), and
  [Specification Tree](../../../repo-governance/conventions/structure/specification-tree.md).
- **Governance level.** Levels are ordered, and a higher one wins a conflict. See
  [Governance Layers](../../../repo-governance/conventions/structure/governance-layers.md).
- **Capability form.** A convention, workflow, skill, or agent, told apart by what each owns: a durable rule, a
  sequence, judgement, or a bounded role. See
  [Capability Forms](../../../repo-governance/development/agents/capability-forms.md).
- **Delivery unit.** One reviewable change reaching the integration branch in the repository's recorded delivery mode: a
  transaction that ships on its own, cut at a valid seam. A phase is smaller, and mapping one change to one phase is the
  common error. See
  [Delivery Seams and Ownership](../../../repo-governance/development/agents/planning-capabilities/005-delivery-seams-and-ownership.md).
- **Surface.** The moment a gate runs, such as before a commit or on hosted checks. See
  [Surfaces and Mutation](../../../repo-governance/conventions/structure/repository-configuration/003-surfaces-and-mutation.md).
- **Canonical artifact, adapter, and binding.** The canonical artifact is the one file a person edits; an adapter is
  generated from it for one harness; a binding is harness-specific configuration; vendor detail lives only in bindings,
  generated adapters, and marked examples. A link inside a file a harness loads is not itself loaded. See
  [Harness Adapters](../../../repo-governance/development/agents/harness-adapters.md) and
  [Vendor-Neutral Governance](../../../repo-governance/conventions/writing/vendor-neutral-governance.md).

## Related

- [understanding-governance-architecture](../understanding-governance-architecture/SKILL.md) — how the levels relate,
  where this skill covers what individual terms mean.
