---
description: >-
  Defines typed lifecycle gate entries: one semantic ID, declared inputs, direct executable and argv projections, and
  explicit membership without a shell command string.
when_to_use: >-
  Use when adding a gate, or when a gate needs to decide which files to inspect.
---

# Gate Entries

A gate entry contains a semantic `id`, a `type` (`check` or `mutation`), a direct `command`, optional typed `inputs`,
and direct `run-on` memberships. A mutation additionally declares its local and replay modes.

| Field      | Holds                                                              |
| ---------- | ------------------------------------------------------------------ |
| `id`       | a stable identifier, unique within the repository                  |
| `type`     | `check` or `mutation`                                              |
| `inputs`   | named `files`, message, range, or repository-state data            |
| `command`  | one executable plus literal or typed argv and environment mappings |
| `run-on`   | lifecycle membership and each input binding                        |
| `mutation` | `apply-index` locally and `verify-clean` for replay                |

No shell string, caller-supplied trailing argv, enabled flag, timeout, or continue-on-error belongs here. Those turn a
reviewed declaration into a second programming language.

## `command` Is Typed

`command.executable` and every `command.args` item are direct. An argument is exactly one literal or one typed input
projection; an environment entry likewise names one resolved input field. No shell, interpolation, globbing, or word
splitting runs between the declaration and the child.

A command string is executed by a shell, and a shell rewrites it: it expands globs against the current directory, splits
on whitespace, and interprets quotes, `$`, and `&&`. A path with a space then becomes two arguments, and a filename
containing a metacharacter becomes an instruction.

The vector form has no such layer. What is written is what runs.

## Bind Inputs at Their Lifecycle Boundary

Inputs are generic: `files`, `commit-message`, `commit-range`, and `repository-state`. Their sources are explicit:
`git-index`, `hook-message-file`, `push-updates`, `explicit-range`, or `checkout`. A hook or workflow only supplies the
declared boundary input; it never appends an unreviewed argument after `--`.

The runner validates the complete configuration, resolves those bindings, preserves declaration order, starts each
direct argv, stops at the first nonzero result, and prints a sanitized summary. It exposes only its documented runtime
context; repository-owned environment variables remain the repository's choice.

That is the whole runner. It is not a task scheduler and does not retry, parallelize, or continue past a failure.

## Inputs Decide Scope

The declaration, not a caller guess, selects the scope. `git-index` is a local mutation boundary; `explicit-range`
resolves an immutable pull-request selection; `checkout` means the complete checked-out state. A tool-specific selector
does not belong in the shared input vocabulary.

## Identifiers Are Stable

A gate's `id` appears in summaries, evidence records, and any exclusion someone writes. Renaming one silently breaks
every reference; a gate whose meaning changes gets a new identifier.
