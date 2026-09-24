---
description: >-
  Requires a single top-level heading, heading levels that never skip, descriptive heading text, headings used only for
  structure, and the list, table, or prose form that matches the content.
when_to_use: >-
  Use when outlining a document, naming a heading, or choosing between prose, a list, a table, a callout, and a code
  block.
---

# Headings and Structure

## One Top-Level Heading

A document has exactly one level-one heading, and it is the document's title. Frontmatter does not replace it.

The top-level heading is the name assistive technology announces and the root every document outline starts from. Two of
them make the outline claim two documents.

## No Skipped Levels

Each heading is at most one level deeper than the heading before it: a level-three heading sits under a level-two
heading, never directly under the title. Returning to a shallower level is always allowed.

Screen-reader users navigate by heading level. A skipped level reads as a missing section, and a reader jumping between
level-two headings misses whatever was filed one level too deep.

## Descriptive Headings

A heading names what its section contains: "Configuring Token Expiry", not "Configuration"; "Why Counts Go Stale", not
"Notes". Vague headings — "Miscellaneous", "Other", "Details" — fail, because a reader scanning an outline cannot tell
whether the section holds what they came for.

## Headings Are Structure, Not Emphasis

A heading starts a section. Bold text is not a heading, and a heading is not a way to make a warning loud. A section
that needs a title gets a heading; a warning inside a section gets a callout, per [Formatting](004-formatting.md).

A bold line posing as a heading is invisible to heading navigation, and a heading used for emphasis inserts a section
that contains nothing.

## Choosing the Form

| Content                                          | Form                    |
| ------------------------------------------------ | ----------------------- |
| an argument, explanation, or rationale           | prose                   |
| a sequence where order matters                   | ordered list            |
| items of equal standing with no order            | unordered list          |
| items compared across the same attributes        | table with a header row |
| a note, warning, or tip that interrupts the flow | blockquote callout      |
| literal code, commands, output, or file trees    | fenced code block       |

Use list and table syntax, never characters that imitate them. A typed bullet character or a column aligned with spaces
looks the same to a sighted reader and is plain text to everything else.

A table cell holds a short value. When cells need paragraphs, the content is not tabular; give it sections instead.
