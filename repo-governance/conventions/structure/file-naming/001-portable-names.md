---
description: >-
  Restricts names to ASCII letters, digits, and single hyphens, forbids URL and shell metacharacters, and requires names
  in one directory to differ regardless of case.
when_to_use: >-
  Use when a proposed name contains a non-ASCII character or punctuation, or differs from a sibling only by case.
---

# Portable Names

A name is copied into links, URLs, shell commands, archives, and checkouts on several operating systems. Each rule below
removes one way for a copy to stop matching the file.

## ASCII Letters, Digits, and Single Hyphens

A basename uses ASCII `a`–`z`, `0`–`9`, and `-` only. Words are separated by exactly one hyphen, and no hyphen begins or
ends the name. The extension is the one standard extension for the file's type.

A non-ASCII letter can be encoded more than one way while rendering identically, so two files a reader cannot tell apart
can sit side by side, and a link typed on another machine resolves to neither. A doubled or trailing hyphen is invisible
in most listings, which makes the name impossible to reproduce from memory.

## No URL or Shell Metacharacters

No name contains a space or any of `:` `?` `*` `<` `>` `|` `"` `\`, or another character a URL must escape or a shell
must quote.

Such a name works in the file browser that created it and breaks in the first script, glob, or link that uses it
unquoted. Some of these characters are also illegal in filenames on at least one common operating system, so a checkout
there fails outright.

## Unique Regardless of Case

Within one directory, no two names may be equal after lowercasing — tool-fixed names included, so `README.md` and
`readme.md` cannot coexist.

Lowercase names prevent new collisions; this rule catches the ones that arrive anyway, such as a tool-fixed uppercase
name beside a lowercase twin, or a file added on a case-sensitive system. A case-insensitive checkout keeps one of the
pair and silently loses the other.

## Enforcement

These are mechanical, and an adopter enforces them in its own pre-commit or CI name check rather than in review. The
check admits the exceptions stated alongside these rules:

- tool-fixed names such as `README.md` and `SKILL.md`, per [File Naming](../file-naming.md);
- a dated form that a convention fixes for its own kind of folder, such as an archived plan's folder, per
  [Dates and a Single Numbering System](002-dates-and-single-numbering.md); and
- source files that follow their toolchain, per [Source Files](003-source-files.md).
