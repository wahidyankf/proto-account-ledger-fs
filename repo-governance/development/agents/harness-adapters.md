---
description: >-
  Requires every harness-specific agent or skill file to be generated from one canonical artifact and declared profile,
  never authored, with lossless capability projection and no competing instruction source.
when_to_use: >-
  Use when adding support for a harness, when a harness-specific file appears to have been edited directly, when a
  second instruction file appears, or when editing a harness's project configuration.
---

# Harness Adapters

Canonical artifacts live in one place and are the only ones a person edits. A harness that needs another path or format
gets a **generated** adapter. The configuration declares the canonical field mapping, requirements, and exactly the
three profiles the repository supports; it never copies a body into the profile.

## The Rule

An adapter holds no authored body. Everything in it is derived: the body from the canonical artifact, the harness-shaped
metadata from the canonical metadata, by a mapping the generator owns.

Copying a skill body into a harness directory appears to work, then silently goes stale. A profile is a rendering
contract, not a second source: it selects native paths, metadata, permissions, routes, and any explicit tier mapping.

## What a Profile Translates

| Canonical      | Becomes                                                |
| -------------- | ------------------------------------------------------ |
| body           | the body, unchanged                                    |
| `name`         | whatever the harness calls an identifier               |
| `capabilities` | the harness's tool or permission names                 |
| `tier`         | a model and effort, only where that profile maps both  |
| `constraints`  | the harness's equivalent restriction, where one exists |

A requirement with no equivalent in a profile is a hard failure before any write. It is never silently omitted and never
replaced by a broader permission. Where a harness cannot express a restriction, the artifact is not published for it.

Failing loudly here matters because the silent alternatives both grant more than was declared.

## Omission Is a Valid Mapping

An absent tier mapping means the renderer emits no model or effort, and the harness applies its own inheritance.

That is the designed default rather than a gap. Emitting a default the repository did not choose replaces the harness's
current behaviour with a guess frozen at generation time.

## Generation and Validation Are Separate

`harness adapters generate` renders the three profile families, their catalogs, and provenance atomically from canonical
input. `harness adapters validate` is read-only and rejects missing, stale, handwritten, or semantically lossy output.
Regenerating unchanged input is byte-identical, so an adapter edit becomes a diff rather than a surprise.

## Adapters Are Not Canonical Input

Nothing reads an adapter to learn about the artifact — not another renderer, validator, or author. An adapter is output,
and treating it as source creates two authorities.

## Modules

The instruction body, vendor-specific notes, and harness configuration and discovery are held in ordered modules:

1. [Instruction Body and Vendor Notes](harness-adapters/001-instruction-body-and-vendor-notes.md)
2. [Configuration and Discovery](harness-adapters/002-configuration-and-discovery.md)
