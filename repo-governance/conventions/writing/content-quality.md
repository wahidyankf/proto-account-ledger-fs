---
description: >-
  Owns the writing rules for authored Markdown: voice and clarity, heading structure, accessible content, formatting,
  and the prohibition on time estimates in documentation and learning content.
when_to_use: >-
  Use when writing or reviewing any Markdown document, or when a skill, checker, or template needs the complete writing
  rules to apply.
---

# Content Quality

How a document reads. Where it lives and what it is named belong to the structure conventions; this convention decides
what is inside it.

The rules are stated completely in the modules below. A skill, checker, or template that applies them links here rather
than restating them, so a correction reaches every consumer at once.

## Modules

1. [Voice and Clarity](content-quality/001-voice-and-clarity.md)
2. [Headings and Structure](content-quality/002-headings-and-structure.md)
3. [Accessible Content](content-quality/003-accessible-content.md)
4. [Formatting](content-quality/004-formatting.md)
5. [No Time Estimates](content-quality/005-no-time-estimates.md)

## Scope

In scope: every Markdown document a repository authors for readers — documentation, governance, learning material,
plans, and root and directory READMEs.

Out of scope: generated output, verbatim quotations, and archived material. A quotation keeps its original wording, and
rewriting an archive to satisfy a later rule destroys the record it exists to keep.

## Owned Elsewhere

| Concern                       | Owner                                       |
| ----------------------------- | ------------------------------------------- |
| colour, contrast, and palette | Colour Accessibility                        |
| diagrams                      | [Diagrams](diagrams.md)                     |
| link form and link integrity  | [Internal Links](internal-links.md)         |
| emoji                         | [Emoji Usage](emoji-usage.md)               |
| factual accuracy              | [Factual Validation](factual-validation.md) |
| the structure of a plan       | [Plans](../structure/plans.md)              |

## Enforcement

An adopter enforces the mechanical subset — one top-level heading, no skipped heading levels, a language on every code
fence, and alt text present on every image — in its own Markdown lint gate. The remaining rules are judged in review.
