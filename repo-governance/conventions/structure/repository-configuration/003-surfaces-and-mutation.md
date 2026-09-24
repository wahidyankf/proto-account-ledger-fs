---
description: >-
  Defines the closed lifecycle surfaces, pull-request composition, index-snapshot mutation replay, and thin hook and
  workflow adapters.
when_to_use: >-
  Use when choosing which surfaces a gate runs on, when a gate needs to modify files, or when writing a version-control
  hook file.
---

# Surfaces and Mutation

## Surfaces

A surface is the moment a gate runs:

| Surface        | Runs                                           |
| -------------- | ---------------------------------------------- |
| `commit-msg`   | when Git supplies a commit-message file        |
| `pre-commit`   | before a commit is created                     |
| `pre-push`     | when Git supplies outbound ref updates         |
| `pull-request` | against a reviewed immutable base and head     |
| `main`         | after a change reaches the default integration |
| `scheduled`    | at a declared recurring interval               |
| `manual`       | only from an explicit operator action          |

A gate declares every surface it applies to. `ci` is not a lifecycle surface: a hosted workflow selects `pull-request`
or `main` according to its event.

## Public Safety Runs First

Where a repository publishes anything, its public-safety gate is the first entry for every surface it applies to.

Order matters because the alternative is discovering a leak after the formatter has already rewritten the file, or after
a push has already happened. The cheapest moment to refuse is before anything else has acted.

## Pull Requests Compose Local Quality

Every local quality gate must also run in the pull-request replay. Composition is `exact` when the two sets are equal or
`at-least` when a pull-request-only gate has a direct, non-empty reason. A hosted-only test does not acquire a fake
local membership merely to satisfy the model.

## Mutations Have Two Bounded Modes

At `pre-commit`, a mutation runs only against a Git-index snapshot and writes/restages only the selected files. It never
uses arbitrary unstaged bytes. In a pull request, the same mutation runs in a disposable snapshot of the explicit range
and must finish clean; a diff is a finding, not a hosted rewrite.

The configuration pairs `local: apply-index` with `ci: verify-clean`. The latter name describes replay behavior, not a
legacy lifecycle surface. Other surfaces do not gain mutation behavior by implication.

## Checks Do Not Mutate

A `check` leaves its boundary unchanged. The separate types make a write boundary visible rather than relying on a leaf
command's name or a caller convention.

## Hook and Workflow Adapters Are Thin

Each hook invokes one lifecycle surface and supplies only its declared input: message-file for `commit-msg`, standard
input for `pre-push`, and no trailing arguments otherwise. A hosted workflow bootstraps its checkout, then invokes one
of `pull-request` or `main`; it does not repeat a child gate list.

The registry is the sole declaration of membership and order. A command list copied into a hook or workflow is a second
registry that will drift, so a configuration validator should reject it.
