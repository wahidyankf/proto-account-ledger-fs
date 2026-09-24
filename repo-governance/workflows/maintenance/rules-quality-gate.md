---
name: rules-quality-gate
description: >-
  Audits one proposed or effective rule state on explicit request and returns a semantic verdict, handing every finding
  to Rules Propagation instead of editing.
when_to_use: >-
  Use when someone explicitly asks for a semantic review of a rule, before a change is written or after propagation
  wrote it.
---

# Rules Quality Gate

## Entry

Someone explicitly names this gate or directs its semantic audit, or [Rules Grooming](rules-grooming.md) asks for a
verdict on the state it produced. A rule change, a review request, or a propagation run never authorizes it alone.

- `mode` (`enum`: `proposal`, `effective`; required): compare a requested outcome with the current rules before any
  edit, or judge the repository after propagation wrote.
- `outcome` (`string`, required): the requested rule outcome and its reason.

## Sequence

1. **Freeze the snapshot:** mode, outcome and reason, intended strength, scope and consumers, any move or deletion, the
   canonical sources, the enforcement route, the revision, and uncommitted paths. A material change ends the run as
   input changed, never restarting it.
2. **Bound the audit** to the affected rule, where it is used, the authority above it, and directly overlapping
   guidance. For grooming, the bound is that run's manifest.
3. **Audit without editing.** Decide whether:
   1. the need, outcome, and reason are concrete enough to judge;
   2. the wording's strength matches the intended strength, per
      [Rule Definition](../../conventions/writing/rule-definition.md);
   3. scope, trigger, action, boundaries, and necessary exceptions are explicit;
   4. the rule sits at the right level, and nothing lower contradicts a higher rule;
   5. one canonical source owns the meaning, and links keep it findable without copies;
   6. every enforcement claim names a truthful route, with evidence where automation cannot decide;
   7. the rule survives compaction and handover at every entry point;
   8. a reasonable reader can act without inventing policy; and
   9. a move or deletion keeps unique intent and updates its consumers.
4. **Record a finite ledger.** Each row names its source, the gap, the required resolution, evidence, and a status:
   open, resolved, not applicable with evidence, or blocked. Admit only a rule violation, or a gap leaving the outcome
   unsafe, contradictory, undiscoverable, or materially ambiguous. Wording preference, speculative cases, and unneeded
   automation are not findings, per [Minimal Sufficiency](../../principles/minimal-sufficiency.md).
5. **Leave machine checks to their tools.** Links, indexes, budgets, and formatting belong to deterministic checks, per
   [Deterministic and Judgement Validation](../../development/quality/checks/deterministic-and-judgement-validation.md);
   effective mode consumes their result instead of repeating them. A check proposed but not yet built needs only an
   owner, a delivery, and a proof obligation.
6. **Return the verdict.** Proposal mode passes with no change when current rules already satisfy the outcome. Effective
   mode passes when the ledger is clear and the repository's gates pass. Otherwise the gate hands its ledger and
   evidence to [Rules Propagation](rules-propagation.md).

## Exit

Outputs: `verdict` (`enum`: `pass-no-change`, `pass-effective`, `needs-propagation`, `input-changed`) and the ledger
(`file`, in the scratch location per [Temporary Files](../../conventions/structure/temporary-files.md)).

`needs-propagation` is a handoff, not a blocked result: the caller runs propagation with the frozen outcome, ledger, and
evidence without another request. Partial outcome: an input change ends the audit with its ledger kept. A verdict
authorizes no commit or push.

## Example Usage

```text
Run rules-quality-gate with mode proposal and outcome "Require a dry run for every script that deletes files."
Run rules-quality-gate with mode effective and outcome "the dry-run rule as propagated".
```

## Related Workflows

- [Rules Propagation](rules-propagation.md) repairs every finding.
- [Rules Grooming](rules-grooming.md) may request an effective verdict after its reductions.

## Adopter Decision: After a Finding

Repositories differ on what follows a finding, and the choice is recorded.

| Option                  | What happens                                                                                              | Trade-off                                                    |
| ----------------------- | --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| verdict only            | the caller reports propagation's result, and the gate does not run again                                  | one audit per request; a second audit needs a second request |
| repair to zero findings | propagation repairs, then the gate audits the effective state again while open findings strictly decrease | ends on a clean audit; costs repeated audits and a ceiling   |

Either way the gate never edits a rule. The loop's ceiling is declared per
[Bounded Convergence](../../development/workflow/bounded-convergence.md).

## Why It Runs on Request

Judging whether a rule is well placed, well reasoned, and still true is a reading task. Wired into every change, it
produces noise nobody reads or a pass nobody earned. This workflow implements
[Evidence Over Assertion](../../principles/evidence-over-assertion.md) and
[Minimal Sufficiency](../../principles/minimal-sufficiency.md).
