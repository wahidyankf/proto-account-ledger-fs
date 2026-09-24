---
description: >-
  Keeps governance prose, the canonical root instruction file, and canonical agent and skill bodies free of coding-agent
  products, model names, and binding paths, confining vendor detail to bindings, generated adapters, and marked
  examples.
when_to_use: >-
  Use when governance prose, the canonical root instruction file, or a canonical agent or skill body would name a coding
  agent, model, or harness path, or when reviewing such text.
---

# Vendor-Neutral Governance

Governance prose, the canonical root instruction file, and canonical agent and skill bodies name no coding-agent
product, model vendor, model, or binding path outside a citation. Vendor detail lives only in bindings, generated
adapters, binding configuration, and marked examples.

## Why

Governance serves every contributor, whatever coding agent they use. A rule in one product's vocabulary:

- excludes readers of other tools, who must translate before obeying;
- ties the rule's correctness to one vendor's naming and release cycle; and
- turns each vendor change into a governance sweep instead of a binding edit.

[Portable Tiers](../structure/artifact-metadata/003-portable-tiers.md),
[Portable Capabilities](../structure/artifact-metadata/004-portable-capabilities.md), and
[Harness Adapters](../../development/agents/harness-adapters.md) already keep vendor names out of agent metadata and
confine harness files to generated outputs; this convention extends that to prose.

## Scope

| Location                                                           | Vendor-neutral                  |
| ------------------------------------------------------------------ | ------------------------------- |
| every governance document                                          | yes                             |
| the canonical root instruction file                                | yes                             |
| canonical agent definitions and skill bodies                       | yes                             |
| a vendor-named root instruction shim                               | the adopter's decision          |
| binding directories, generated adapters, and binding configuration | no — vendor detail belongs here |

Canonical agent and skill bodies are in scope because a generator copies each body unchanged into every harness's
adapter. The excluded locations exist to say, in one harness's terms, how it reaches the neutral rules, so adding or
retiring a harness changes them and never governance prose.

A shim is a root instruction file whose name one harness requires. The adopter either holds its prose body to this rule,
allowing only the import line, or treats the shim as a binding. The first keeps additions reviewable; the second skips
scanning a file meant only for the import, but lets additions reach one harness unreviewed.

## The Neutral Vocabulary

| Instead of                                             | Write                                                                                               |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------------------- |
| a coding-agent product name                            | "the coding agent" or "the harness"                                                                 |
| a model vendor's name                                  | nothing, or "the model provider" where the role matters                                             |
| a model or model-family name                           | the workload tier defined in [Portable Tiers](../structure/artifact-metadata/003-portable-tiers.md) |
| a harness binding path                                 | the role, such as "the agent definition", or `<binding-root>/<path>`                                |
| a vendor-named instruction file presented as canonical | "the canonical root instruction file"                                                               |
| a product-specific feature name                        | the generic capability, such as "pre-edit hook" or "delegated agent"                                |

Each replacement names what the rule needs from a tool, not which tool provides it.

## Marked Examples

Outside a citation, a vendor reference appears only inside an explicit, visible, delimited marker holding only
illustrative examples, never a rule statement, in a form the adopter chooses:

| Marker form                                 | Trade-off                                                     |
| ------------------------------------------- | ------------------------------------------------------------- |
| a fenced block with a dedicated info string | exempts exactly one example; each example needs its own fence |
| a page-level heading region                 | exempts a whole page region, neutral prose included           |
| a comment before the line, with a rationale | records why each exception exists, one comment per exception  |

This illustration uses a fence with the info string `binding-example`:

```binding-example
<binding-root>/agents/<agent-name>.md maps the plan tier to <model-name>
```

The marker makes every exception deliberate and visible, and gives a scanner a boundary it recognises without judgement.

A clearly attributive citation of an external source whose name is a vendor term needs no marker, unlike a product
mention. Every other unmarked vendor reference fails.

## The Term List Belongs to the Adopter

This document names no product, which would date it. An adopter records its forbidden terms — products, vendors, model
families, binding paths — and its marker form in its own copy of this convention, which the scan exempts.

## Enforcement

A reviewer checks new in-scope text against the vocabulary above. An adopter enforcing it mechanically scans every
in-scope location for its term list, skipping the exception regions and citations it declares and failing on any other
match; the exemption set, and whether the scan runs in a hook or a gate, are the adopter's.
