---
description: >-
  Provisions development toolchains through version-pinned native package and version managers verified by one
  idempotent check, repair, and preview health command, not infrastructure-as-code tooling or development containers.
when_to_use: >-
  Use when deciding how contributors install and verify toolchains, when adding a toolchain, or when a container-based
  or infrastructure-as-code development environment is proposed.
---

# Native-First Toolchain

A development environment is provisioned with the host's native package managers and per-language version managers, each
required version declared in a committed file and verified by one idempotent health command. Infrastructure-as-code
tooling and development containers are not the primary way to set one up.

This standard implements [Simplicity Over Complexity](../../principles/simplicity-over-complexity.md),
[Reproducibility](../../principles/reproducibility.md),
[Automation Over Manual](../../principles/automation-over-manual.md), and
[Explicit Over Implicit](../../principles/explicit-over-implicit.md).

## The Rule

- **Versions live where each ecosystem reads them:** a runtime field in a package manifest, a toolchain file, or an SDK
  version file. A contributor finds each requirement in the place that ecosystem already looks.
- **One health command has three modes,** mirroring the plan-and-apply shape of infrastructure tooling:

| Mode    | Does                                                                               |
| ------- | ---------------------------------------------------------------------------------- |
| check   | reports every required tool as present at its declared version, drifted, or absent |
| repair  | converges the environment to the declared state                                    |
| preview | lists what repair would change, and changes nothing                                |

- **The installed binaries are the state.** Asking a tool for its version is the state query. No separate state file
  tracks what is installed; it would only be a stale copy of what the check reads directly.
- **Every install step is non-interactive and idempotent,** so repair is safe to rerun and does nothing when nothing has
  drifted. A step that would prompt runs with its non-interactive option, and a step that changes the shell's search
  path loads the new path before any later step depends on it.
- **Containers keep their place** for networked end-to-end stacks and hosted pipelines.

## Why Not Infrastructure Tooling or Development Containers

Native package managers already skip what is present, so a convergence engine, a state file, or a configuration language
adds nothing for one contributor machine; those tools answer fleet problems. A container carrying many toolchains
becomes a very large image, and bind-mounted file access on some hosts is several times slower than native. Hooks that
finish in seconds natively then take close to a minute, slow enough that contributors disable them, which costs more
quality than the container gains. Containers also sit poorly with worktrees: one container per worktree multiplies the
cost and gives up the cheap isolation that worktrees are used for.

## Adopter Decision: What Repair May Change

| Option                 | Repair may                                                                                                                   | Gains                                                     | Costs                                                                                         |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| converge machine tools | install missing or drifted machine-level toolchains through the native managers                                              | one command takes a new machine to a working state        | a repository command changes the machine outside the checkout, sometimes with elevated rights |
| repository state only  | restore dependencies, hooks, and other state the repository owns, and report each absent machine tool with how to install it | the repository never alters anything outside its own tree | contributors install machine tools by hand before repair can succeed                          |

Record the option. Either way, the per-checkout part runs as [Checkout Bootstrap](checkout-bootstrap.md) requires.

## When to Revisit

Revisit this choice when any of these holds:

- the contributor count and onboarding rate grow until setup friction outweighs container overhead;
- container file access on contributor hosts reaches native speed;
- contributors need a hosted development environment because they cannot install toolchains locally;
- the number of toolchains outgrows what a flat list of checks can manage.
