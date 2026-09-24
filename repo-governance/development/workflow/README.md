---
description: >-
  Indexes the workflow standards that govern how work is bounded, ordered, committed, integrated, deployed, and brought
  to a terminal state, and how a working environment and its toolchain are prepared.
when_to_use: >-
  Use when designing a repeated operation, when committing, integrating, or deploying a change, when preparing an
  environment or toolchain, or when a process has no obvious stopping point.
---

# Workflow Standards

Standards about the shape of work rather than its subject. Version-control, integration, environment, and toolchain
standards sit alongside them.

| Standard                                                          | Governs                                                                                                          |
| ----------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| [Bounded Convergence](bounded-convergence.md)                     | how a repeated operation is bounded and how it ends, and the defaults an iterative gate declares                 |
| [Checkout Bootstrap](checkout-bootstrap.md)                       | the declared per-checkout bootstrap before any commit, push, or task-runner command, and when it reruns          |
| [Commit Authorization](commit-authorization.md)                   | when staging, committing, and pushing are permitted, and why each grant is single-use                            |
| [Commit Messages](commit-messages.md)                             | the Conventional Commits format and type list, and why types never decide commit boundaries                      |
| [File-Touch Discipline](file-touch-discipline.md)                 | the touched-path ledger, carrying it through context loss, reconciling before staging, and foreign paths         |
| [Hook Verification](hook-verification.md)                         | hook bypass as a separate per-operation permission, fixing a failing hook at its cause, and bypass disclosure    |
| [Integration Path](integration-path.md)                           | the branch or direct route to the trunk, branch lifespan, one worktree per task, reconcile, and cleanup          |
| [Native-First Toolchain](native-first-toolchain.md)               | pinned native toolchain managers, the idempotent health command, what repair may change, and when to revisit     |
| [Nx Workspace Policy](nx-workspace-policy.md)                     | Nx as a raw task runner, the targets every project exposes, and what the push gate runs                          |
| [No Destructive Git Operations](no-destructive-git-operations.md) | per-instance approval and additive equivalents for operations that destroy work or rewrite history               |
| [Task Runner Target Standards](task-runner-target-standards.md)   | target prerequisites, caching only deterministic targets, inputs and outputs, names, aggregates, no placeholders |
| [Thematic Commits](thematic-commits.md)                           | one complete purpose per commit, the boundary test, and splitting and ordering a change set                      |

## Directory Map

- [Bounded Convergence](bounded-convergence.md)
- [Bounded Convergence Modules](bounded-convergence/README.md) — the modules on loop register and ceiling scorecard
- [Checkout Bootstrap](checkout-bootstrap.md)
- [Commit Authorization](commit-authorization.md)
- [Commit Messages](commit-messages.md)
- [File-Touch Discipline](file-touch-discipline.md)
- [Hook Verification](hook-verification.md)
- [Integration Path](integration-path.md)
- [Native-First Toolchain](native-first-toolchain.md)
- [Nx Workspace Policy](nx-workspace-policy.md)
- [No Destructive Git Operations](no-destructive-git-operations.md)
- [Task Runner Target Standards](task-runner-target-standards.md)
- [Thematic Commits](thematic-commits.md)
