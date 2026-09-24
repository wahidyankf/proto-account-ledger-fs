---
description: >-
  Restricts Nx to raw commands and explicitly ordered command aggregates, and fixes the targets every project exposes
  and which of them the push gate runs.
when_to_use: >-
  Use when changing Nx configuration, adding a project, or adding, renaming, or reordering a target.
---

# Nx Workspace Policy

Nx is this repository's task runner and nothing more. It schedules and caches commands; it does not generate, scaffold,
or wrap a technology. This local policy applies [Task Runner Target Standards](task-runner-target-standards.md) to Nx.

## Required Approach

Define a target that owns one command with the `command` shorthand in the project's `project.json`. Define an aggregate
that runs several existing targets in order with the built-in `nx:run-commands` executor, an explicit `options.commands`
list of `npm exec -- nx run <project>:<target>` entries, and `options.parallel` set to `false`. The aggregate invokes
targets instead of copying their commands, so each command has exactly one owner.

Use ordinary, exact-pinned npm or language-native dependencies (for example Python tools locked in a project's
`uv.lock`). Do not add framework-, language-, or platform-specific `@nx/*` plugins, generators, or executors. An
exception needs explicit owner direction naming the plugin and the capability it provides, recorded in the change that
introduces it.

## Targets

| Target             | Owns                                                                              | Cached |
| ------------------ | --------------------------------------------------------------------------------- | ------ |
| `install`          | syncing the project's pinned toolchain; every other target depends on it          | no     |
| `build`            | a publishable build, only for a project that publishes one                        | yes    |
| `typecheck`        | static type checking with no errors or warnings allowed                           | yes    |
| `lint`             | formatter check and linter                                                        | yes    |
| `test:unit`        | in-process tests with every OS-facing dependency injected, with the coverage gate | yes    |
| `test:integration` | tests against real, isolated local resources, never the network                   | yes    |
| `test:e2e`         | tests that run the application through its public process boundary                | yes    |
| `test:quick`       | aggregate: `typecheck`, `lint`, `test:unit`, in that order                        | yes    |
| `run`              | running an application locally                                                    | no     |
| `<test>:watch`     | rerunning `test:quick`, `test:integration`, or `test:e2e` on every change         | no     |

Test levels follow [Test Boundaries and Gates](../quality/testing/test-boundaries-and-gates.md).

## The Push Gate

`.husky/pre-push` runs `nx affected -t test:quick test:integration test:e2e` against `origin/main` for every pushed ref.
Running the integration and end-to-end suites on every push, not only `test:quick`, is this repository's choice: both
are fast and local, and a push is the moment publication begins.

## Verification

Run `npm exec -- nx show projects` to confirm project discovery, then the affected targets. Keep `.nx/` and build output
directories in `.gitignore`.
