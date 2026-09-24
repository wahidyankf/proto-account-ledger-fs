---
description: >-
  Defines what makes a valid delivery seam, lands each unit as one integration change, and fixes the boundary when one
  plan coordinates work across several repositories.
when_to_use: >-
  Use when splitting a plan into delivery units, or when a plan touches more than one repository.
---

# Delivery Seams and Ownership

## What Makes a Valid Seam

A delivery unit is a transaction. A seam between two of them is valid only when the unit on each side has:

1. **one owner** — the repository or component responsible for the change;
2. **one independently testable outcome** — something that can be verified without the other unit landing;
3. **one recoverable transaction** — a rollback that restores a known state on its own; and
4. **one coherent review surface** — a change a reviewer can hold in their head at once.

A split that fails any of the four is not a seam; it is a partition drawn for convenience, and the first failure will
cross it.

Two units that must land together are one unit. Splitting them produces a state where half the work is deployed and the
other half is in review, which is exactly the state neither unit's rollback was designed for.

Conversely, a unit nobody can review is too large regardless of how coherent it is internally.

## Foundation Before Content

Where a unit establishes something later units depend on — a safety layer, a gate, a configuration contract — it lands
first and separately.

Landing them together looks efficient and removes the only opportunity to prove the foundation works on its own. A gate
introduced alongside the content it is meant to check has never been observed passing or failing for its own reasons.

## One Unit, One Integration Change

A unit reaches the integration branch as one reviewable change, in the delivery mode the adopter records under
[Portability](../../../conventions/structure/plans/009-portability.md): a pull request from one branch, a direct commit,
or a local-only commit. Its description justifies the seam and the resulting integration state.

Changes follow unit boundaries, never phases. The last change-producing phase always ends a unit; a setup phase with
nothing reviewable never ends one alone, and joins the next. Independent units deliver as separate changes in any order;
dependent units in dependency order, each still its own change. A ready unit never waits for later work.

Beyond the seam criteria above, a boundary adds one requirement, **safe to land**: every applicable gate passes on it,
and its integration state meets the rule below.

Size never creates or erases a boundary: unrelated purposes split, and an unreviewable unit splits only along a genuine
seam.

Units land one at a time, each starting only after the previous one lands. Before landing, each refreshes against the
current integration branch and re-runs its gates; a unit built on an unlanded sibling is reviewed against a state that
may never exist.

## The Integration State Is an Adopter Decision

The adopter records which state every landed change leaves:

- **Releasable**, where versions are cut from the integration branch: incomplete work lands inert, and a public surface
  lands complete or not at all. Partial work is exposed later.
- **Deployable**, where the branch ships live: incomplete behaviour lands behind a disabled flag, both paths tested,
  with rollout, rollback, and flag removal recorded. Flags cost upkeep and a second path.

Neither permits landing on a promise that later work makes it safe.

## The Cross-Repository Boundary

A plan may coordinate work across several repositories. Coordination is the only thing that crosses the boundary.

| Crosses           | Does not cross                     |
| ----------------- | ---------------------------------- |
| sequencing        | each repository's own instructions |
| dependency order  | its mutations                      |
| a shared deadline | its proof and its gates            |
|                   | its cleanup                        |

Each repository retains its own instructions, performs its own mutations, produces its own proof, and runs its own
cleanup. A coordinating plan may say _when_ a repository acts; it never says _how_, and it never acts on that
repository's behalf under its own rules.

The reason is ownership, not politeness. A repository's rules exist because of constraints a coordinating plan does not
know about. A plan that overrides them has substituted its own incomplete model for the one that was actually checked.

Coordination also transfers nothing permanently. A repository that participated in a coordinated change is not
thereafter governed by the coordinating plan, and nothing propagates to it automatically afterwards.
