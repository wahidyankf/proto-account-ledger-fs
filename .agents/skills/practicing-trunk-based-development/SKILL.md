---
name: practicing-trunk-based-development
description: >-
  Guides keeping work on a single trunk: telling whether a branch is warranted under the adopted integration mode,
  landing incomplete work safely, spotting a branch that outlives its task, and retiring feature flags.
when_to_use: >-
  Use before creating a branch or worktree, when work will not finish in one small change, or when a branch or a flag
  has outlived its task.
compatibility: Requires the repository's recorded integration route and integration state.
---

# Practicing Trunk-Based Development

The standards own the rules. [Integration Path](../../../repo-governance/development/workflow/integration-path.md) fixes
the route, branch lifespan, worktrees, and cleanup; Integration Hygiene fixes checking, rebasing, and a red trunk;
[Thematic Commits](../../../repo-governance/development/workflow/thematic-commits.md) shapes each commit;
[Commit Authorization](../../../repo-governance/development/workflow/commit-authorization.md) grants permission; and
[Delivery Seams and Ownership](../../../repo-governance/development/agents/planning-capabilities/005-delivery-seams-and-ownership.md)
records the integration state. This skill covers the judgement of working within them.

## Adopter Decision: The Integration Mode

Every mode keeps one long-lived line that work reaches in small pieces. They differ in how work reaches it, and this
skill selects none of them:

| Mode                                                         | Gains                                                | Costs                                                                             |
| ------------------------------------------------------------ | ---------------------------------------------------- | --------------------------------------------------------------------------------- |
| a short-lived branch in a worktree, merged by a pull request | review and hosted gates before the trunk moves       | branch, worktree, and cleanup overhead for every unit, and time waiting on review |
| commits pushed directly to a shared trunk                    | the least ceremony and the fastest integration       | no buffer: local gates and post-push verification carry everything                |
| commits on a local trunk with no remote                      | nothing leaves the machine, and no network is needed | no hosted evidence and no second copy                                             |

Integration Path records the first two as its routes and runs the third as the direct route locally. Record the mode.
Everything below holds under each, with differences stated where they matter.

## A Branch Needs a Reason the Mode Accepts

Under the pull-request mode, a task branch is the default; what needs a reason is a branch outliving its task. Under the
two direct modes no task branch or worktree is created, and a branch a tool creates for another purpose is removed when
that purpose ends, as Integration Path states.

Reasons that do not justify a branch living on, and what to do instead:

| Reason offered              | Instead                                                               |
| --------------------------- | --------------------------------------------------------------------- |
| the feature is not finished | land a complete increment that stays inert, per the integration state |
| it might break something    | rely on the gates, and add the test that would catch it               |
| it has taken a week already | cut what remains into short units at genuine seams                    |
| several people are on it    | split it into independent units that land separately                  |
| it feels cleaner separate   | nothing; preference is not a reason                                   |

The only line that legitimately lives longer is an environment branch tracking what is deployed, which receives from the
trunk and is never developed on, as Integration Path records.

## Land Incomplete Work Safely

The integration state decides the technique. Where the trunk is releasable, incomplete work lands unreachable from any
public surface. Where it deploys continuously, incomplete behaviour lands behind a flag disabled in production.

- A flag hides complete but unreleased behaviour. It never excuses broken or half-written code: if the disabled path
  would fail its tests, the change is not ready.
- Test both paths, enabled and disabled.
- Record the rollout, rollback, and removal when the flag is introduced. A flag without a removal plan becomes permanent
  configuration by accident.
- Keep flags boolean and independent of each other, since each dependency between flags multiplies untested
  combinations.
- Once the behaviour is stable, remove the flag and the old path together.
- A change that lands complete in one commit needs no flag.

## Integrate When a Unit Is Done

Integrate each unit once it is complete and green, not when the day ends. A next commit that cannot be described as one
purpose is too large or mixed. Review is a buffer, never a parking space.

## Signals of Drift

- a branch or worktree older than its task's ceiling;
- conflicts that grow with each sync;
- a flag nobody can say when to remove;
- a red trunk left for later; and
- under a direct mode, a task branch or worktree that exists.
