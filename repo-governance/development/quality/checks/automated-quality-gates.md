---
description: >-
  Assigns each kind of automated quality check to the earliest gate surface able to see its problem: staged files before
  a commit, the message at commit time, affected work before a push, and a failing build in the pipeline.
when_to_use: >-
  Use when wiring a check into a hook or pipeline, deciding which surface a check belongs on, or when a gate is slow,
  scans too much, or cannot fail.
---

# Automated Quality Gates

A quality rule a contributor has to remember is enforced on the days they remember it. Every mechanical check therefore
runs by itself, at the earliest moment that can see the problem, and it blocks.

This standard implements [Automation Over Manual](../../../principles/automation-over-manual.md) and
[Fail Closed](../../../principles/fail-closed.md). What a surface is, and which gates may change files, is owned by
[Surfaces and Mutation](../../../conventions/structure/repository-configuration/003-surfaces-and-mutation.md); this
standard decides what belongs on each surface.

## Where Each Check Runs

| Surface                | Runs                                                                               | Never runs                                                                |
| ---------------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| before a commit        | formatters and file-level checks over staged files; fast deterministic repo checks | runtime test suites, except as recorded below; rewriting files not staged |
| at commit-message time | validation of the message against the repository's commit format                   | anything about file contents                                              |
| before a push          | fast checks scoped to what the pushed commits affect                               | slow integration or end-to-end suites                                     |
| continuous integration | every blocking check, on each proposed change and on the integration branch        | a step whose failure is discarded                                         |

Each row trades feedback speed against coverage. The earlier the surface, the cheaper the fix and the less the check may
cost; the later the surface, the more complete the check and the more a finding costs to act on.

## Tests Run Before a Push

Test suites stay off `pre-commit`, because a slow pre-commit hook gets bypassed and then checks nothing. They run at
`pre-push` or in `ci`.

A repository with no `ci` surface records one option:

| Option                        | Gains                                     | Costs                                       |
| ----------------------------- | ----------------------------------------- | ------------------------------------------- |
| fast tests at `pre-commit`    | failures stop before history records them | slower commits, and more pressure to bypass |
| fast tests at `pre-push` only | commits stay quick                        | the push hook is the only test gate         |

## Staged, Not the Whole Tree

A formatter or file-level check before a commit inspects what is being committed. Formatting the entire tree on every
commit is slow enough to resent, and it rewrites and stages files the author never touched, so the commit carries
changes nobody reviewed.

A formatter that rewrites a staged file restages it, so the commit holds the formatted version rather than needing a
follow-up fix.

## Affected, Not Everything

A pre-push gate runs the checks the pushed change can affect, derived from the dependency graph or the changed paths. A
check that genuinely cannot be scoped, because it reads links or invariants spanning the whole repository, runs over the
whole tree; naming each such exception and its reason is good practice, since an unexplained whole-tree check is where
gate time quietly grows.

A gate slow enough to be worked around protects nothing. Keeping the local gates fast is what keeps them run.

## The Pipeline Fails the Build

Where a repository has continuous integration, it runs the complete blocking set and a violation fails the run. It is
the one control a contributor cannot skip locally, so it is a superset of the hooks, never a subset.

A step written so it cannot fail, with its exit status discarded or its tool told to succeed regardless, is not a gate.
It reports green over exactly the state it exists to catch.

## Hooks Travel With the Repository

Hook definitions are committed and installed by the documented setup step, so every contributor and every fresh checkout
runs the same gates. Hooks dispatch the repository's declared gate list rather than transcribing it — see
[Gate Entries](../../../conventions/structure/repository-configuration/002-gate-entries.md).

## Decided Elsewhere

- Each gate returns one terminal result against a frozen snapshot:
  [Quality Gate Results](../manual-verification/001-quality-gate-results.md).
- The severity at which a linter fails, and how a lint gate is introduced: [Lint Strictness](lint-strictness.md).
- A gate that was already failing before a change: Preexisting Error Resolution.
- Which formatter and linter a stack uses belongs to that stack's own standard.

An adopter enforces this in its own hooks and pipeline configuration.
