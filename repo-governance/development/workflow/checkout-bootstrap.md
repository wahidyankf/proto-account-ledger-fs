---
description: >-
  Requires each new checkout to run the repository's one declared, idempotent bootstrap for dependencies and hooks at
  its own root before any commit, push, or task-runner command, and records when the bootstrap reruns.
when_to_use: >-
  Use after creating a worktree or clone, when a session starts in a checkout that may not be bootstrapped, or when a
  command reports missing dependencies or hooks.
---

# Checkout Bootstrap

A checkout is usable only once its own dependencies are installed and its own hooks are active. Version control tracks
neither, so neither arrives with the files: a new worktree or clone starts with nothing installed and nothing checking
its commits.

This standard implements [Reproducibility](../../principles/reproducibility.md),
[Explicit Over Implicit](../../principles/explicit-over-implicit.md), and
[Root Cause Orientation](../../principles/root-cause-orientation.md).

## The Rule

A new worktree, a fresh clone, or a session in a checkout that was never bootstrapped runs the repository's declared
bootstrap at that checkout's own root, and confirms it finished without errors, before any commit, push, or task-runner
command there.

- **Per checkout.** Installed dependencies and hook activation belong to one working tree. A bootstrap that succeeded in
  the primary checkout sets up no other worktree.
- **Declared, never inferred.** Run the command the repository declares for installing local dependencies and activating
  hooks. Where it declares several steps, such as a dependency install and then toolchain convergence, run each in its
  declared order. Never invent or infer an equivalent command.
- **One entry point.** Whatever triggers the bootstrap, whether an instruction file, a session-start hook, or a person,
  invokes that one declared command and never reimplements its logic.
- **Idempotent.** The bootstrap converges when something is missing and returns quickly when nothing is. That property
  is what makes running it on every creation cheap.
- **Triggered by creation, not by intent.** A worktree made for a documentation edit bootstraps too, because its hooks
  and gates can fan out to whatever the edit affects.

## Adopter Decision: When It Reruns

| Option             | Runs on                                                                                          | Gains                                                              | Costs                                                                               |
| ------------------ | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------ | ----------------------------------------------------------------------------------- |
| creation only      | a new worktree, clone, or unbootstrapped session; later gaps are recovered from evidence         | no repeated work on each return, and entry is never taken as drift | a checkout whose state changed after creation stays broken until a command shows it |
| creation and entry | also every session that enters or resumes a checkout when it is unsure the bootstrap already ran | a returning session never works in an unbootstrapped tree          | repeated runs, each cheap only while the bootstrap stays idempotent                 |

Record the option. Under creation only, entering or resuming an existing checkout triggers nothing.

## Recovery From Evidence

When a later command reveals an absent dependency, an inactive hook, a missing tool, or an outdated build artifact,
rerun only the declared step that covers that gap. Never reprovision the checkout from scratch, and never debug the
symptom as a new defect before ruling out a skipped or stale bootstrap.

## Why Before Any Commit

A checkout whose hooks were never activated still commits. The commit succeeds with no hook output, and that silence
reads as a pass when nothing ran at all: formatting, message, and safety checks are skipped without anyone deciding to
skip them, which is a bypass nobody authorized. See [Hook Verification](hook-verification.md).

A missing or stale dependency fails less visibly: as an obscure build, test, or lint error, or as a task-runner cache
that misses or serves a result computed against the wrong versions. Each costs more to diagnose than the bootstrap costs
to run.

## Related Standards

- Where worktrees live and how many a task uses: [Integration Path](integration-path.md).
- How the toolchain the bootstrap may converge is provisioned: [Native-First Toolchain](native-first-toolchain.md).

## Enforcement

An adopter binds the declared bootstrap to its own session-start or worktree-creation hook, and adds a health check that
fails while dependencies are absent or hooks are inactive.
