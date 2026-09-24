---
description: >-
  Lets source filenames follow their language toolchain instead of document kebab-case, with fixed choices for Python
  modules and scripts and for Go source and test files.
when_to_use: >-
  Use when naming a Python or Go source file, or when a document naming rule is proposed for source code.
---

# Source Files

Document names serve readers and links. A source filename also serves a toolchain that derives meaning from it, so a
source file follows its toolchain's naming, and the kebab-case rule governs documents and directories. These are
enforced choices among names a toolchain would accept, not a restatement of its documentation.

## Python

An importable module or package is lowercase `snake_case`. A hyphen cannot appear in an `import` statement, so a
hyphenated module cannot be imported by name; see [PEP 8](https://peps.python.org/pep-0008/).

A file that is run but not imported — launched directly, spawned as a subprocess, or called from a shell — can take a
kebab-case name that matches the repository's other commands. That allowance lasts only while nothing imports the file:
the change that first imports it also renames it to `snake_case`.

The allowance stays narrow because a kebab-case file that later has to be imported forces a rename everywhere it is
called, the very churn the naming choice was made to prevent.

## Go

Go source filenames are lowercase, with no hyphens and no mixed case. A multi-word name joins its words with
underscores, as in `<word>_<word>.go`, which is the separator the toolchain's own suffixes use.

Toolchain suffixes stay exactly as written: `_test.go`, and the operating-system and architecture suffixes such as
`_linux.go`, `_arm64.go`, and `_linux_arm64.go`. The build decides what compiles from them — see the
[go command documentation](https://pkg.go.dev/cmd/go#hdr-Build_constraints) — so renaming one changes behaviour, not
style.

For the same reason, a multi-word name never ends in a GOOS or GOARCH value, such as `js`, `wasm`, or `windows`, or in
`test`, unless that build constraint is intended; reorder or rename the words instead.

Integration tests pair a dedicated filename suffix with a build tag. Each such file starts with a
`//go:build integration` constraint and is named `<name>.integration_test.go`. The tag keeps the tests out of an
ordinary `go test ./...` run; the suffix shows in a listing which files carry the tag, without opening them. Neither is
removed without the other.

## Enforcement

An adopter using either language enforces these in its own pre-commit or CI source-name check.
