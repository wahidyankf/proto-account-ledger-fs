---
description: >-
  Requires a repository to declare one authoring rule for conceptual diagrams and, for rendered diagrams, its size
  limits; fixes the accessibility requirement for each form, and excludes literal content.
when_to_use: >-
  Use when adding a conceptual diagram, or when changing a repository's diagram authoring rule.
---

# Diagrams

A repository declares exactly one authoring rule for conceptual diagrams and applies it consistently.

**This repository declares `plain-text`.** Its files are read mostly in a terminal editor, where Mermaid never renders.
Draw every conceptual diagram as ASCII inside a fenced `text` block, with prose beside it, and never add Mermaid.

## The Two Rules

| Rule       | Requires                                                                          |
| ---------- | --------------------------------------------------------------------------------- |
| rendered   | a Mermaid diagram carrying both an accessible title and an accessible description |
| plain-text | an ASCII diagram with prose immediately beside it, and no Mermaid                 |

Rendered diagrams read better where supported but are opaque elsewhere. Plain text reads consistently in terminals,
diffs, and mail at the cost of expressiveness. Mixing them is invalid: readers and tooling cannot predict which rule
applies.

## Accessibility Is Not Optional in Either Form

A rendered diagram carries a title and a description of what it shows, not a caption repeating the title. Mechanically
generated accessibility prose must be reviewed for readable word boundaries, including around dotted names. This
semantic review is unenforced by decision because no portable mechanical rule covers every language.

A plain-text diagram carries equivalent prose beside it. ASCII art is not self-describing merely because it is text.

## When a Diagram Earns Its Place

Draw relationships, sequence, state, or hierarchy only when a diagram is materially clearer. Put simple facts in prose
and exact mappings in tables; do not decorate or repeat a table less precisely.

Update a diagram in the same change as the structure it depicts.

## One Concept per Diagram

A diagram shows one idea. Split distinct concepts, side-by-side comparisons, or content exceeding a declared size limit,
and give each part a short heading. Oversized diagrams become unreadable on narrow screens and dense elsewhere.

## Declared Size Limits

A repository using the rendered rule declares two limits in configuration, nodes per level and label-line length, and
validates every diagram against them. The numbers and how a label is counted are its own decision. Illustrative options:

| Option  | Nodes per level | Label-line length | Counted as                | Trade-off                                                                 |
| ------- | --------------: | ----------------: | ------------------------- | ------------------------------------------------------------------------- |
| tighter |               4 |                20 | characters                | readable on narrow screens; more splitting                                |
| looser  |               6 |                30 | user-perceived characters | fewer splits and fair counting of non-Latin text; clips in some renderers |

Limits are proxies because clipping depends on glyph widths and layout; inspect every new or materially changed diagram
as rendered.

## Colour in Diagrams

A styled diagram takes its fills, text pairings, and outlines from Colour Accessibility, and its labels and shapes carry
every distinction its colours draw.

## Enforcement

An adopter enforces the limits and the palette in its own diagram validator.

## Before Rewriting Existing Diagrams

Before a conceptual-diagram rewrite, screen every source line the rewrite will republish through the repository's
outbound-safety boundary. An edited line returns on the added side even when its sensitive text already existed. The
outbound screen over the frozen pre-rewrite selection covers this rule.

Palette-naming comments and default flow direction remain adopter decisions because neither changes meaning.

## What Is Excluded

The rule covers **conceptual** diagrams — ones drawn to explain a relationship. It does not cover:

- literal code, command output, or file trees;
- interface wireframes; or
- archived material.

A directory tree is not a diagram of a structure; it is the structure, quoted. Converting it into a rendered graph makes
it harder to copy, harder to diff, and no clearer.

Archives are excluded because rewriting history to satisfy a rule introduced afterwards destroys the record the archive
exists to keep.

## Reversals Are Recorded

A repository changing its authoring rule records the change, reason, and date, and migrates existing diagrams in the
same decision. A silent reversal leaves two styles and no discoverable authority, so both keep being used.
