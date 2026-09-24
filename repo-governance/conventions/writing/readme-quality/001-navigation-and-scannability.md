---
description: >-
  Requires each README section to be a short summary that links to its detail, forbids duplicated content, and caps
  paragraphs at five lines within a scannable structure.
when_to_use: >-
  Use when a README section is growing, repeats another document, or reads as a wall of text.
---

# Navigation and Scannability

## Summarize, Then Link

Each section is a summary of three to five lines, followed by links to the documents that hold the detail. An essential
command may appear inline; the explanation of it does not.

```markdown
## Layout

Applications live in `apps/` and shared libraries in `libs/`. A library declares which applications may depend on it.

- [Repository layout](docs/reference/repository-layout.md)
- [Adding an application](docs/how-to/add-an-application.md)
```

The failure this prevents is the README that reproduces its reference documentation section by section: sixty accurate
lines that repeat what the documentation already says, drift from it, and push the part the reader needed out of sight.

## Never Duplicate

Content that lives in another document is linked, not repeated — not in full, and not "briefly, for convenience". A
summary written for this README is not duplication; a copied paragraph is.

The test: if the linked document changed, would this README need the same edit? If it would, it holds a copy.

## Short Paragraphs

A paragraph is at most five lines, counted in the wrapped source — see [Markdown Prose Wrap](../markdown-prose-wrap.md).
Longer content becomes several paragraphs that each make one point, or becomes a list.

A reader scanning a README decides within a few lines whether a paragraph is the one they need. A paragraph longer than
that is skipped whole, including the sentence that mattered.

## Scannable Structure

The most important information comes first within each section, so a reader who stops after its opening lines still
leaves with what they came for.

The rest of a scannable structure is shared with every document and applies to a README unchanged: headings, lists, and
tables follow [Headings and Structure](../content-quality/002-headings-and-structure.md); code fences and bold follow
[Formatting](../content-quality/004-formatting.md); and link text follows
[Accessible Content](../content-quality/003-accessible-content.md).

## Emoji

Emoji in a README follow [Emoji Usage](../emoji-usage.md).
