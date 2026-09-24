---
description: >-
  Fixes how code blocks, inline code, emphasis, callouts, and tables are formatted, so that each format keeps a single
  meaning.
when_to_use: >-
  Use when adding a code block, choosing between bold, italic, and inline code, or writing a callout or a table.
---

# Formatting

Each format carries one meaning. When bold marks a key term on one line, a button name on the next, and a warning on a
third, it marks nothing.

## Code Blocks

- **Every fence declares a language** — `bash`, `yaml`, `json`, or `text` for output, file trees, and anything without a
  grammar. The tag drives highlighting, tells the reader what they are about to copy, and lets tools lint the block.
- **Fence, never indent.** An indented block cannot declare a language and breaks easily when a surrounding list is
  reflowed.
- **Minimal and realistic.** Show only the lines that matter, using names from a plausible situation rather than
  abstract placeholders.
- **Indented the way its own language is**, per [Markdown Indentation](../markdown-indentation.md).
- **Introduced by prose** saying what the block is and when to use it.
- **Explicit placeholders** such as `<api-token>` and `<repository-path>` — never a real credential, host, or personal
  path, per [Public Outbound Safety](../../security/public-outbound-safety.md).

## Inline Formatting

| Format      | Use for                                                               |
| ----------- | --------------------------------------------------------------------- |
| inline code | file paths, commands, identifiers, configuration keys, literal values |
| bold        | a key term at its first use, or the one phrase a reader must not miss |
| italic      | light emphasis, and the titles of published works                     |

Use bold sparingly. A paragraph with several bold phrases has no emphasis left.

## Callouts

A note, warning, or tip is a blockquote that opens with its label in bold:

```markdown
> **Warning**: Clearing the cache removes every stored session.
```

The label is a word, so it survives every renderer and every screen reader. An emoji may accompany it only as
[Emoji Usage](../emoji-usage.md) allows, never in its place.

## Tables

Every table has a header row naming its columns, and every cell is short. A table whose cells need sentences is holding
content that wants sections.
