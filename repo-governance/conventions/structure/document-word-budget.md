---
description: >-
  Caps instruction files and governance documents at a declared word ceiling measured over the whole file, and repairs a
  breach by relocating detail rather than cutting or compressing it.
when_to_use: >-
  Use whenever a governed document nears or exceeds its word ceiling, or when setting the ceiling a repository enforces.
---

# Document Word Budget

Instruction files and governance documents are read whole, by people looking for one rule and by coding-agent harnesses
that load them into every session and may not read past their own limits. A word ceiling keeps that read affordable.
[Progressive Disclosure](../../principles/progressive-disclosure.md) argues why; this convention fixes the mechanics.

## What Is Measured

| Surface                                                                            | Budgeted        |
| ---------------------------------------------------------------------------------- | --------------- |
| the root instruction file and each harness counterpart, alone and with its imports | always          |
| every document in the governance tree, index files included                        | always          |
| each harness's agent-definition directory                                          | adopter decides |
| plans, behaviour specifications, and product documentation                         | adopter decides |

The count covers the entire file, metadata and code included, because any carve-out becomes room for words to grow
unmeasured; a root file's imports count with it, because a harness loads them together.

Repository configuration declares the ceiling and the counting rule, and the gate's verdict is the measurement; a quick
shell count is only an estimate.

## What an Adopter Decides

| Decision          | Options                                                                 | Trade-off                                                                                                |
| ----------------- | ----------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| the ceiling       | one number, or one per class of surface                                 | one number is simpler; classes fit files with different jobs, and overlapping classes then need an order |
| the count         | whitespace-separated tokens, or runs of letters and digits              | whitespace is reproducible with standard tools; letter runs weigh links and tables more as a reader does |
| agent definitions | measure them, or leave them unmeasured                                  | measuring catches a definition a harness stops reading; leaving them out sizes each by its task          |
| a warning band    | none; closed only by relocation; or prompting a simplification or split | relocation-only blocks trimming back under the band; a prompt trusts the author; no band fails first     |
| excluded trees    | exclude records sized by what they must say, or include them            | exclusion keeps a delivery record whole; inclusion catches a plan grown too large to follow              |

When two surface classes match one file, the later declaration decides, so a narrower class is declared after any
broader one it overlaps, and reordering the declarations is a change of policy. An excluded tree is outside the gate,
not outside [Minimal Sufficiency](../../principles/minimal-sufficiency.md).

## Repair by Relocation

A breach closes by moving detail, whole, into the document that owns it, leaving a one-line summary and a link. The rule
stays reachable; it is no longer inline.

These do not close a breach:

1. **Deleting a rule.** Coverage is lost.
2. **Compressing, or moving text into another always-loaded file.** Neither lowers what a reader pays, as
   [Progressive Disclosure](../../principles/progressive-disclosure.md#a-budget-is-the-usual-mechanical-form) explains.
3. **Linking to an incomplete target.** A link replacing a list that lacks cases the inline text covered quietly removes
   them. Complete the target first, or state the rule as a pattern instead of a list.
4. **Evading the gate.** Cutting a file off mid-rule, parking the excess in a file the gate never sees, or renaming an
   extension so the file drops out of measurement.

Rules that protect safety, such as secret handling and branch protection, move last, and only into a target that already
holds them completely.

A document split for its budget becomes an entrypoint and a companion directory named per [File Naming](file-naming.md),
split along reader tasks. Nothing is split merely to use or avoid the budget. An index at its ceiling follows
[Directory Indexes](directory-indexes.md).

## Changing the Ceiling

A file over its ceiling keeps failing until relocation fixes it; Progressive Disclosure argues why. The ceiling moves
only in a class-wide recalibration that records evidence the signal is broadly unactionable or that the harness's
capacity or the repository's policy has changed, states its reasoning, and validates every file in the class.

The adopter enforces the ceiling in its own gate, run in pre-commit or CI wherever its other checks run.

## Principles

This convention implements [Progressive Disclosure](../../principles/progressive-disclosure.md) and
[Minimal Sufficiency](../../principles/minimal-sufficiency.md): a reader pays only for the rule in hand, and a ceiling
bounds a document without becoming a length to fill.
