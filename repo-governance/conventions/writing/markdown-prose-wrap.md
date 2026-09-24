---
description: >-
  Requires Markdown prose to be hard-wrapped at one fixed width by the formatter, never by hand, with a per-file
  preserve override reserved for text pasted elsewhere verbatim.
when_to_use: >-
  Use when configuring a Markdown formatter's wrapping, editing a paragraph, or adding a file whose text is copied
  verbatim into another destination.
---

# Markdown Prose Wrap

Markdown prose is hard-wrapped at **120 columns**, and paragraphs are separated by exactly one blank line. The formatter
applies the wrap. Nobody maintains it by hand, and it is not a judgement made at the keyboard.

## Why a Fixed Width

Source is read in terminals, diffs, and review tools as often as it is read rendered. Soft wrap solves overflow there
but not measure: it breaks wherever the window happens to end, so a wide pane produces lines too long to track back to
the left margin, and the same paragraph reads differently on every screen.

A fixed width gives every reader the same line. The cost is real and accepted: changing one word can reflow the rest of
its paragraph, so a one-word edit becomes a several-line diff. `git diff --word-diff` shows such a change as the word it
was; nothing restores the readability of an unwrapped paragraph in a terminal.

## The Formatter Owns the Wrap

With Prettier the rule is two settings:

```json
{
  "printWidth": 120,
  "proseWrap": "always"
}
```

A hand-maintained wrap drifts on the first edit, and a reviewer then has to ask whether a ragged paragraph is
deliberate. When a tool owns the line breaks, a line break in prose never carries meaning, and nobody argues about one.

The width applies to Markdown. Whether code files share it is a separate decision, made in the same configuration with a
per-file-type override.

A line still longer than the width after formatting holds something the formatter cannot break — a long URL or a long
inline code span. It stays as it is. Breaking it by hand changes the content, and a line-length lint rule would fail a
line neither tool can fix, which is why line length belongs to the formatter.

## Structure Instead of Breaks

Content that is structurally distinct uses structural Markdown: a heading, a list, a table, a blockquote, or a fenced
block. A paragraph is never split, and a manual line break is never inserted, to make text look arranged — the formatter
rewraps it, and a single line break never reached a rendered reader anyway.

Diagrams and schemas follow [Diagrams](diagrams.md), which decides their form separately.

## The One Exemption: Copy-Paste Targets

A file whose text a downstream consumer receives verbatim — a draft to be pasted into a web form, a profile field, or a
message body — is exempt. There the line break is content: a rewrap inserts newlines that travel with the pasted text
and arrive as ragged breaks in the destination.

Exempt such a file with a formatter override that preserves its line breaks, never by ignoring the file:

```json
{
  "overrides": [
    {
      "files": "<drafts-directory>/*.md",
      "excludeFiles": "<drafts-directory>/README.md",
      "options": { "proseWrap": "preserve" }
    }
  ]
}
```

The distinction matters. The override hands back line-break control and nothing else. Ignoring the file also drops its
tables, lists, and format check, so an exempted draft would silently stop being formatted at all. The directory's own
index is not a copy-paste target and stays wrapped.

The exemption belongs to the destination, not to preference. A file is exempt because its text leaves the repository as
text, and for no other reason.

## Enforcement

An adopter enforces the wrap by running the formatter in its own pre-commit hook and a format check in its own gate, so
the wrap is applied whether or not anyone ran the formatter by hand.
