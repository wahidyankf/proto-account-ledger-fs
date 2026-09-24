---
name: dev-artifact-clean-up
description: >-
  Removes the scratch files, reports, branches, and worktrees a task created, and proves they are gone, then reconciles
  the default branch, retaining with reasons what it cannot safely remove.
when_to_use: >-
  Use after finishing any task, plan, or investigation that produced artifacts the repository should not keep.
---

# Dev Artifact Clean-Up

## Entry

A task, plan, or investigation has finished, and it produced artifacts that were useful during the work and are not part
of its result.

Finished means landed on the default branch or deliberately abandoned: never between units sharing a worktree, and never
as a periodic sweep.

- `integration` (`enum`: `pull-request`, `local-main`; required): the adopter's integration path. `pull-request`
  isolates each task and reviews its head, and leaves worktrees and branches that step 3 guards; `local-main` leaves
  only files and build output, without isolation or a reviewed head.
- `outcome` (`enum`: `pass`, `partial`, `fail`; required): how the producing run ended.

## Sequence

1. **Enumerate what the task created.** Scratch directories, generated reports, temporary scripts, downloaded fixtures,
   task branches, task worktrees, and any tooling installed only for this work. Include regenerable build output. No
   real environment file, per Agent Environment-File Access, or other local secret is ever listed: nothing rebuilds one.

   Never delete a secret-bearing file or directory from the primary `main` checkout. An exact ignored, nonshared cache
   such as `.fvm-cache/` is scratch after recorded regeneration, non-use, and secret-free evidence, regardless of
   origin.

2. **Classify each one:**

   | Class    | Disposition                                                                                                                                                                                                                                        |
   | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
   | result   | keep; it is part of what the work delivered                                                                                                                                                                                                        |
   | evidence | keep, in the location the plan declared for evidence, which for a plan is its `evidence/` folder, per [Evidence Files](../../conventions/structure/plans/016-evidence-files.md); a task outside a plan keeps evidence where its own rules place it |
   | scratch  | remove                                                                                                                                                                                                                                             |
   | unknown  | investigate before removing; never delete something you cannot classify                                                                                                                                                                            |

   After a `partial` or `fail` outcome, the worktree and build output are evidence until diagnosis; logs and traces a
   diagnosis needs always are.

3. **Remove the scratch class.** Delete files, remove worktrees, delete task branches that have served their purpose.
   Under `pull-request`, a worktree or branch goes only when the tool's own listing shows this task created it, nothing
   in it is uncommitted, unpushed, or running, and its pull request merged at the local tip or was deliberately
   abandoned; otherwise retain it with the reason. Remove from outside the directory, and never force a worktree removal
   or stash to empty one, since all worktrees of a clone share one stash stack. A plain branch delete refuses after a
   rebase or squash merge; force it only when the merged head equals the local tip, or every commit is patch-equivalent
   to one on the remote default branch. Delete the remote branch only if merging did not.
4. **Preserve unrelated work.** A dirty file that this task did not create is not cleanup's business. Cleanup removes
   what the task made; it never restores a working copy to some imagined clean state.
5. **Prove absence.** Re-list the paths and confirm they are gone, and confirm the working tree holds only what it
   should. A cleanup that was performed but not verified is a claim.
6. **Reconcile the default branch.** With a remote, fetch with pruning, fast-forward, and prove zero divergence both
   ways. A refused fast-forward is a local commit to inspect, never to force, and ends the run `retained`, naming that
   commit.

## Exit

A `clean` result means every task-created artifact is classified, the scratch class is removed, its absence is verified,
and unrelated changes are untouched. It also requires zero divergence from any remote default branch.

Outputs: `result` (`enum`: `clean`, `retained`) and `retained-items` (`string`, each kept artifact and why). `retained`
is the partial outcome; it is terminal and never authorizes a forced removal.

## Example Usage

```text
Run dev-artifact-clean-up with integration pull-request and outcome pass.
```

## Related Workflows

- [Execution](../plan/plan-execution.md) produces most of what this removes.

## Deletion Is Not Reversible in the Way People Assume

Version control restores what was committed. Scratch artifacts are, by definition, uncommitted — deleting one is
permanent.

That is why `unknown` exists as a class and why it routes to investigation rather than to removal. The cost of keeping
one unrecognized file for another day is a stale file. The cost of deleting the one thing that was not reproducible is
the work itself.
