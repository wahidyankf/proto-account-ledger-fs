---
name: rules-propagation
description: >-
  Writes a rule being added, changed, moved, or removed as one bounded transaction: a falsifiable statement, a conflict
  scan, one canonical home, an enforcement disposition, and verification.
when_to_use: >-
  Use automatically before any rule is added, changed, moved, or removed, or when rules grooming or a rules quality gate
  hands over findings.
---

# Rules Propagation

## Entry

A rule, as [Rule Definition](../../conventions/writing/rule-definition.md) defines one, is about to be added, changed,
moved, or removed, or [Rules Grooming](rules-grooming.md) or the [Rules Quality Gate](rules-quality-gate.md) hands over
findings. Entry is automatic: an agent or person who proposes or detects the change starts here as part of the work in
hand, without a separate request. Edits made inside one run start no second one.

- `rules` (`string`, required): each rule as stated, with its reason.
- `findings` (`file`, optional): a handed-over finding ledger.
- `dry-run` (`boolean`, optional, default `false`): record placements without writing.

## Sequence

1. **Freeze the inputs:** each rule with its reason, strength, scope, and enforcement, plus the revision and uncommitted
   paths, kept through compaction. A material change ends the run blocked.
2. **Make each rule falsifiable,** one obligation per statement with the observations that show it followed and
   violated, per [Statement and Conflict](rules-propagation/001-statement-and-conflict.md). A rule that stays
   unfalsifiable halts alone, and the rest of the batch continues.
3. **Stop where the rules already suffice.** When existing rules carry the meaning in full, record their source and end
   that rule with no change.
4. **Resolve conflict by level,** per [Governance Layers](../../conventions/structure/governance-layers.md): a lower
   rule is amended to agree, a same-level or unclear contradiction goes to the owner, and a new rule contradicting a
   higher one halts. Record every supersession.
5. **Place each rule on the narrowest surface that reaches its audience,** per
   [Placement](rules-propagation/002-placement.md). No ceiling rises for a placement; a full surface relocates its
   weakest entry in the same change.
6. **Write and tidy the subject.** Keep one canonical statement, merge unique meaning into it, and replace copies with
   links. A budget may move a rule but never generalize or drop its obligation, audience, scope, exception, or
   condition. A wrong rule is corrected here, never worked around, and an adapted rule records what changed and why.
   Under `dry-run`, steps 6 to 9 record without writing.
7. **Give each rule one enforcement disposition,** covered, gated, or unenforced by decision, per
   [Enforcement and Verification](rules-propagation/003-enforcement-and-verification.md).
8. **Verify** by exit codes rather than output, returning a failure to the step that owns it, and repair findings the
   run caused only while their count strictly decreases, per
   [Bounded Convergence](../../development/workflow/bounded-convergence.md).
9. **Deliver, and record obligations beyond this repository.** Commit only with explicit authority, through the
   repository's own route, stating each rule's home, disposition, and relocations. A rule portable across a declared
   parity boundary records its sibling obligation per
   [Related Repositories](../../conventions/structure/related-repositories.md), or records none with why. A repository
   adopting from a shared catalog proposes a rule that holds beyond itself to that catalog, through the catalog's own
   delivery, published only after the catalog's outbound-safety screen passes.

## Exit

Every rule ends with no change, landed, recorded under `dry-run`, or halted, and nothing is written but unaccounted for.

Outputs: a placement record (`file`, in the scratch location per
[Temporary Files](../../conventions/structure/temporary-files.md)) and `status` (`enum`: `no-change`, `landed`,
`recorded`, `partial`, `halted`, `blocked`). Partial outcome: some rules landed while others halted, each named with its
blocker. A pass alone authorizes no commit or push, and a rerun on unchanged inputs changes nothing.

## Example Usage

```text
Run rules-propagation with rules "Every script that deletes files offers a dry run, because deletion cannot be undone."
```

## Related Workflows

- [Rules Grooming](rules-grooming.md) hands over reductions.
- [Rules Quality Gate](rules-quality-gate.md) hands over findings.

## Modules

1. [Statement and Conflict](rules-propagation/001-statement-and-conflict.md)
2. [Placement](rules-propagation/002-placement.md)
3. [Enforcement and Verification](rules-propagation/003-enforcement-and-verification.md)

## Adopter Decision: How Entry Becomes Automatic

- **Root instruction file:** a route before any rule edit; it needs no tooling but relies on being read.
- **Commit-time notice:** names this workflow whenever a staged path carries rules, reaching every editor; it reports
  without blocking, since a hook cannot judge semantic decisions.
- **Editor pre-edit trigger:** the same notice earlier, in one harness; a convenience that can be switched off.

Record the routes taken and the delivery route. Every trigger reads one recorded list of rule-bearing paths.

## One Writer

Grooming and the quality gate find; only propagation writes, so placement, conflict, and enforcement are decided in one
place. This workflow implements [One Source Per Fact](../../principles/one-source-per-fact.md),
[Minimal Sufficiency](../../principles/minimal-sufficiency.md), and
[Governance Continuity](../../principles/governance-continuity.md).
