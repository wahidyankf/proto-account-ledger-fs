---
name: rules-grooming
description: >-
  Sweeps the rule corpus on request for volume that carries no obligation, ranks the candidates for approval, and hands
  each approved group to Rules Propagation, proving that no obligation was lost.
when_to_use: >-
  Use on explicit request after a structural change to a repository, or when rules have grown by repetition rather than
  by new obligations.
---

# Rules Grooming

## Entry

Someone explicitly directs a grooming run. One document over its word budget is not a trigger; it is repaired by
relocation per [Document Word Budget](../../conventions/structure/document-word-budget.md).

- `scope` (`string`, optional, default the whole rule corpus): path prefixes to sweep.
- `classes` (`string`, optional, default every admitted class): the classes this run considers.
- `dry-run` (`boolean`, optional, default `false`): produce the inventory and manifest, handing nothing over.

## Sequence

1. **Inventory every obligation in `scope` first.** Record each distinct obligation with its audience, condition, and
   locations.
2. **Discover candidates in the admitted `classes` only,** each recording its class, paths, yield as measured, and
   evidence:
   - **duplication:** one obligation stated on several surfaces with no recorded reason to keep both. The home kept is
     chosen by level, then by the narrowest surface that binds, and must already cover every case the removed text
     covered; otherwise the candidate becomes completing that home first.
   - **scaffolding:** whole sentences stating no obligation, such as a preamble restating its heading. They are deleted,
     never rewritten.
   - **retirement:** a rule whose subject no longer exists, that a later rule supersedes in practice, or that nothing
     reaches. Missing inbound links alone are not evidence. Only this class removes an obligation.
3. **Rank by yield over risk,** retirement the riskiest, and group by subject. Drop a candidate whose yield would not
   repay a propagation run.
4. **Seek approval of the manifest.** Under `dry-run`, the run ends `no-change` here. Duplication and scaffolding may be
   approved as a batch, scaffolding against its listed sentences; each retirement is approved alone, with its evidence;
   an entry-point document needs approval naming it. Silence is not approval. Record each rejection and deferral with
   its reason, and keep deferrals for the next run.
5. **Hand each approved group to [Rules Propagation](rules-propagation.md) once,** in ranked order, with its surfaces,
   home, and evidence. A propagation blocker is recorded against its item and the run continues. An item is never
   restated more loosely to get it accepted.
6. **Prove preservation.** Inventory again and compare, leaving index entries and routing clauses out of both sides. The
   run passes only when every missing obligation was an approved retirement, none changed its audience, condition,
   qualifier, or exception, and each survivor stays reachable from a surface that binds its audience.
7. **Request an effective verdict** from the [Rules Quality Gate](rules-quality-gate.md) where the adopter chose one,
   then log the run, with its size change and each item's disposition.

## Exit

Outputs: the manifest and both obligation inventories (`file`, in the scratch location per
[Temporary Files](../../conventions/structure/temporary-files.md)), and `status` (`enum`: `no-change`, `groomed`,
`partial`, `halted`).

Partial outcome: an unanswered approval ends the run with nothing handed over. An unapproved obligation loss halts it;
its revert is itself a rule edit for propagation, and the class that caused the loss is recorded for tightening. A pass
authorizes no commit or push.

## Example Usage

```text
Run rules-grooming with scope "repo-governance/development/" and dry-run true.
```

## Related Workflows

- [Rules Propagation](rules-propagation.md) writes every approved reduction.
- [Rules Quality Gate](rules-quality-gate.md) can judge the state a run leaves.

## Never a Reduction

- Rewording text only to shorten it, or weakening a qualifier, boundary, exception, or pass condition.
- Cutting any safety guardrail the adopter lists, such as data safety or commit authorization.
- Raising a word budget, or deleting a rule to make room.

## Adopter Decisions

| Option            | Trade-off                                                                                                                                       |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| three classes     | split documents are judged by the same tests as any text; a heavily split corpus keeps its per-module overhead                                  |
| add fragmentation | an undersized companion module may merge back within the budget, carrying every link and index line; one more class that can lose an obligation |

Record the choice, and whether that class is approved per item or as a batch. Also record whether step 7 runs: a verdict
every run catches reductions that keep each obligation yet leave rules incoherent, costing a gate pass; otherwise the
gate needs its own direction.

## Principles

This workflow implements [Minimal Sufficiency](../../principles/minimal-sufficiency.md) and
[Governance Continuity](../../principles/governance-continuity.md).
