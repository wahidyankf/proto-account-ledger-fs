---
name: docs-quality-gate
description: >-
  Audits human-facing documents on explicit request and returns a verdict with a finite ledger of stale, obsolete,
  misplaced, and unreadable documents, handing every finding to Docs Propagation instead of editing.
when_to_use: >-
  Use when someone explicitly asks for a documentation review or to sweep a whole repository.
---

# Docs Quality Gate

## Entry

Someone explicitly names this gate or directs its audit. A change or a propagation run never authorizes it alone.

- `scope` (`enum`: `change`, `all`; required): the documents one change affects, or the whole document set
  [Docs Propagation](../maintenance/docs-propagation.md) defines.
- `change` (`string`, required when `scope` is `change`): the revision range or working-tree change.

## Sequence

1. **Freeze the snapshot:** scope, revision, and uncommitted paths. A material change ends the run as input changed,
   never restarting it.
2. **Bound the audit.** Under `change`, the documents the change touches and every document citing what it changed;
   under `all`, the whole document set.
3. **Audit without editing.** Decide for each document whether:
   1. every claim is true to the implementation, per
      [Factual Validation](../../conventions/writing/factual-validation.md), and every command shown was run or is
      marked not exercised, per
      [Only What Was Run](../../conventions/structure/documentation-architecture.md#only-what-was-run);
   2. it still describes something the repository has; if not, it is obsolete and its resolution is removal;
   3. each fact has one home, a summary sits above its detail per
      [Progressive Disclosure](../../principles/progressive-disclosure.md), and a page serves one mode per
      [Documentation Architecture](../../conventions/structure/documentation-architecture.md);
   4. a newcomer learns from the opening what it is and why it matters, and finds the next step, per
      [README Quality](../../conventions/writing/readme-quality.md) and
      [Content Quality](../../conventions/writing/content-quality.md), judged by reading, never by a score;
   5. under `all`, or when setup changed, a reader with no prior context can follow the setup exactly as written from a
      clean checkout, each step marked smooth, frustrating, or blocking; and
   6. it agrees with its specification, which is canonical.
4. **Record a finite ledger.** Each row names the document, the gap, the required resolution — update, move, or remove —
   the evidence, and a status: open, resolved, not applicable with evidence, or blocked. Admit only a document that is
   wrong, obsolete, unreachable, or unusable by a newcomer; wording preference is not a finding, per
   [Minimal Sufficiency](../../principles/minimal-sufficiency.md).
5. **Leave machine checks to their tools.** Formatting, links, indexes, and budgets belong to deterministic checks, per
   [Deterministic and Judgement Validation](../../development/quality/checks/deterministic-and-judgement-validation.md);
   the audit consumes their result instead of repeating them.
6. **Return the verdict.** It passes when the ledger is clear and the repository's checks pass. Otherwise the gate hands
   its ledger to [Docs Propagation](../maintenance/docs-propagation.md). A finding only the owner can decide, such as a
   specification that disagrees with the implementation, is asked through
   [Grill Me](../../../.agents/skills/grill-me/SKILL.md).

The audit may delegate the reading in step 3 to the repository's documentation checkers.

## Exit

Outputs: `verdict` (`enum`: `pass`, `needs-propagation`, `input-changed`) and the ledger (`file`, in the scratch
location per [Temporary Files](../../conventions/structure/temporary-files.md)).

`needs-propagation` is a handoff, not a blocked result: the caller runs propagation with the ledger without another
request. Partial outcome: an input change ends the audit with its ledger kept. A verdict authorizes no commit or push.

## Example Usage

```text
Run docs-quality-gate with scope all.
Run docs-quality-gate with scope change for the current branch.
```

## Related Workflows

- [Docs Propagation](../maintenance/docs-propagation.md) repairs every finding, removals included.

## Recorded Decision: After a Finding

| Option                  | What happens                                                                                              | Trade-off                                                    |
| ----------------------- | --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| verdict only            | the caller reports propagation's result, and the gate does not run again                                  | one audit per request; a second audit needs a second request |
| repair to zero findings | propagation repairs, then the gate audits the effective state again while open findings strictly decrease | ends on a clean audit; costs repeated audits and a ceiling   |

This repository records **verdict only**, so no audit loop runs and no ceiling is needed; see
[Bounded Convergence](../../development/workflow/bounded-convergence.md). Either way the gate never edits a document.

## Why It Runs on Request

Judging whether a document is still true, still needed, and still readable is a reading task. Wired into every change,
it produces noise nobody reads or a pass nobody earned; propagation already refreshes each change. This workflow
implements [Evidence Over Assertion](../../principles/evidence-over-assertion.md) and
[Minimal Sufficiency](../../principles/minimal-sufficiency.md).
