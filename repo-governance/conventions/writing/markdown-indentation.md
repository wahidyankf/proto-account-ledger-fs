---
description: >-
  Fixes Markdown indentation: bullets nested by two spaces, two-space YAML frontmatter, no tabs in list or frontmatter
  indentation, and each code block indented the way its own language is.
when_to_use: >-
  Use when nesting list items, indenting frontmatter keys, or placing a fenced example in Markdown, or when setting up a
  linter's indentation checks.
---

# Markdown Indentation

Markdown indentation is structure, not layout. A child indented by the wrong amount is not a slightly untidy child: a
renderer may read it as a sibling, a paragraph continuation, or a code block, and renderers disagree about which.

## Lists

A bullet is a dash, a single space, then its text; a tab never stands between the dash and the text.

A nested list item is indented by two spaces per level:

```markdown
- First level
  - Second level, two spaces before the dash
    - Third level, four spaces before the dash
```

Two is not an arbitrary number. A child aligns with the first character of its parent's text, and after a dash and its
space that character sits two columns in.

## No Tabs in List or Frontmatter Indentation

A tab never indents a list item or a frontmatter line.

A tab has no width of its own. CommonMark treats it as advancing to the next four-column stop wherever it defines block
structure, while editors expand it to whatever they are configured for, so the same file nests differently depending on
where it is opened. Spaces are the only indentation every tool counts the same way.

## Frontmatter

YAML frontmatter indents nested keys and list items by two spaces:

```yaml
---
tags:
  - first-topic
  - second-topic
---
```

YAML forbids tabs as indentation, so a tab-indented frontmatter block is not a style violation but a parse error. Two
spaces matches the list rule above, which keeps one number in a writer's head for everything outside code.

## Code Blocks Follow Their Language

Content inside a fenced code block is quoted source, indented the way that language's own formatter indents it:

| Language                                       | Indents with                          |
| ---------------------------------------------- | ------------------------------------- |
| JavaScript, TypeScript, JSON, YAML, CSS, shell | two spaces                            |
| Python                                         | four spaces                           |
| Go                                             | tabs                                  |
| any other language                             | whatever its standard formatter emits |

The block's own rules win over Markdown's because the block is meant to be copied. An example re-indented to suit the
document no longer matches what its language's formatter produces, so pasting it into a real file yields a formatting
diff on the first save — or, where indentation is syntax, a different program.

Go is therefore a case where a tab is correct: its formatter emits tabs, and a Go example indented with spaces is one no
Go project would accept. A linter that rejects hard tabs exempts code blocks in tab-indented languages rather than
forcing them to spaces; markdownlint's `MD010`, for instance, takes an `ignore_code_languages` list.

## Enforcement

An adopter enforces the list and tab rules with its own Markdown linter in its own gate — for instance, markdownlint's
`MD007` for list nesting and `MD010` for hard tabs — and leaves code-block content to the language formatters that own
it.
