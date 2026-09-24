---
name: maintenance
description: >-
  Indexes the workflows that keep a repository clean, current, and releasable, and its documents true to each change:
  artifact clean-up, dependency bumps, release cuts, docs propagation, and the workflows that write, groom, and judge
  its rules.
when_to_use: >-
  Use after finishing a task, plan, or investigation that created scratch files, branches, or worktrees, when planning
  dependency bumps or a release, before any rule edit, or before committing a change that a document describes.
---

# Maintenance Workflows

Work produces debris: scratch files, reports, branches, worktrees, generated output. None of it is a mistake while the
work is happening. All of it is a mistake once the work is done.

A repository also drifts while nobody works in it: dependencies age, releases wait, and rules pile up copies. The rest
of these workflows keep it current, releasable, and governed by rules written in one place.

## Directory Map

- [Dev Artifact Clean-Up](dev-artifact-clean-up.md)
- [Docs Propagation](docs-propagation.md)
- [Rules Propagation](rules-propagation.md)
- [Rules Propagation Modules](rules-propagation/README.md)
- [Rules Grooming](rules-grooming.md)
- [Rules Quality Gate](rules-quality-gate.md)
