---
description: >-
  Fixes the value rules every metadata field obeys: scalar forms, length bounds, array discipline, and diagnostic
  content.
when_to_use: >-
  Use when writing a description or trigger, or when implementing metadata validation.
---

# Shared Value Rules

## Frontmatter Form

YAML, bounded by the first pair of `---` delimiters. Anything after the second delimiter is body.

Duplicate keys fail before decoding. A YAML parser resolves a duplicate by discarding one silently, which means the file
says one thing and validates as another.

## `description`

A plain or folded scalar, 20 to 300 characters after normalization.

It says what the artifact does. Not why it exists, not when to reach for it, and not what it used to be called.

## `when_to_use`

A folded scalar, one to three sentences, 20 to 240 characters after normalization.

It says when to reach for the artifact — the situation, not the summary. Normalized, it must differ from `description`;
two fields carrying the same sentence is one field and a formatting artifact.

The distinction is load-bearing. A capable harness routes on the trigger and displays the description, and an artifact
whose trigger merely restates its description cannot be routed to.

## Arrays

Nonempty, unique, and in the order the schema declares. An empty array is not a smaller array; it is a field that should
have been omitted, and it fails.

## Diagnostics

A metadata finding reports the path, the position, the rule, and the field at fault. Diagnostics sort by path, then
line, then column, then rule, then field — never by discovery order, which depends on the filesystem.

The message says what is wrong and why the schema is shaped that way. It does not prescribe a remedy: an unknown key is
either a key that should be deleted or a key the schema should have declared, and the validator cannot tell which.

## Metadata Is Content

In a public repository, metadata is published. Descriptions, triggers, compatibility text, and constraints pass the same
safety boundary as bodies: no private path, internal host, credential, or private repository identifier.

This is easy to overlook precisely because metadata feels like configuration. It is read first, indexed first, and in
many harnesses shown before the body ever loads.

## Semantics Are Authored

Automation may normalize syntax, order keys, and reflow scalars. It may never generate a description or a trigger from a
filename.

A generated description is a filename with more words in it. It passes validation, tells a reader nothing, and is worse
than a missing field because nothing flags it as absent.
