---
description: >-
  Restricts emoji to semantic markers with one recorded meaning each, keeps them out of metadata, names, configuration,
  and code, and requires every heading to read correctly without them.
when_to_use: >-
  Use when deciding whether an emoji belongs in a document, or when choosing or reviewing a repository's emoji
  vocabulary.
---

# Emoji Usage

An emoji is permitted only where it carries meaning a reader would otherwise have to find in the text. Using none at all
complies with this convention; decoration does not.

## Semantic Only

Each emoji a repository uses has exactly one meaning, recorded in one vocabulary, and means that everywhere. The
vocabulary is the repository's choice. One emoji meaning two things, or two emoji meaning one thing, is not.

A marker works only when it is predictable. Once the same symbol means "warning" on one page and "important" on the
next, a reader has to read the text to learn what the symbol meant, and the symbol has become cost with no benefit.

## Text First

An emoji supplements text and never replaces it. A heading reads correctly with its emoji removed, and a status marker
in an example sits beside a word saying the same thing.

Screen readers announce an emoji by its name, which is rarely the meaning the author intended. Search ignores it or
matches it unpredictably, and some terminals and renderers show a missing-glyph box instead. Text is the only form every
reader receives.

## Restraint

Place an emoji only where it helps a reader locate something: one marker at the start of a heading, or a status marker
in a correct-and-incorrect example. Never stack them, never prefix every list item, never use one as a bullet, and never
use one to set a mood in prose.

A marker signals by being rare. When every heading and every bullet carries one, none stands out, and the page is harder
to scan than it was without them.

## Where Emoji Never Appear

| Location                                       | Why                                                              |
| ---------------------------------------------- | ---------------------------------------------------------------- |
| frontmatter and other metadata                 | metadata is parsed, indexed, and displayed before the body loads |
| file and directory names                       | names are typed, sorted, and matched by tools                    |
| configuration files                            | parsers, diffs, and encodings handle them inconsistently         |
| code blocks, commands, file paths, identifiers | a copied command or path must run exactly as written             |

These are prohibitions, not density limits. A repository enforcing them mechanically does so in its own lint gate,
scanning metadata, names, configuration files, and fenced code.
