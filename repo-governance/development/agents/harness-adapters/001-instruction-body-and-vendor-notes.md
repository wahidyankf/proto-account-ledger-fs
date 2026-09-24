---
description: >-
  Gives always-on repository instructions one canonical body that every harness reads or imports, refuses competing
  instruction sources, and records where vendor-specific operational notes may live.
when_to_use: >-
  Use when a harness needs its own instruction file, when a nested or override instruction source appears, or when a
  harness needs an operational note.
---

# Instruction Body and Vendor Notes

## One Instruction Body

Always-on repository instructions have one canonical, vendor-neutral body: the root `AGENTS.md`. A harness that reads it
natively needs no further file. A harness that reads another instruction file gets an adapter that imports or routes to
that body and restates none of it.

Instruction adapters are generated like every other adapter, and every rule in the [entrypoint](../harness-adapters.md)
applies to them unchanged.

Every competing always-on source is refused: a nested or override instruction file, a harness rules directory, or an
instruction field in harness settings. A harness preferring its own file over the canonical body follows that file
silently, and contributors on other harnesses never see the divergence. Personal and user-global configuration stays
outside this rule.

An adopter enforces this through its declared adapter-validation gate: validate every instruction adapter, its catalog,
and provenance, then refuse every competing source.

## Where Vendor-Specific Notes Live

A harness sometimes needs an operational note no other harness needs, such as where its generated files sit. The adopter
chooses where such notes may live and records the choice:

- **Import only.** The adapter is the import and nothing else. Validation is one exact comparison; the notes move to
  harness settings or documentation, away from the instructions.
- **Marked section.** One clearly headed vendor-specific section, kept only in a declared renderer input, which the
  profile adds to that harness's adapter and the adapter-validation gate verifies; never in the canonical body, and
  never hand-written into the output. A harness reading the canonical body natively takes notes through the import-only
  route. The section is one more input the renderer and gate must recognize, and it is where rules creep in.

Under either option a vendor-specific note is operational only. Anything that changes behaviour belongs in the canonical
body, where every harness receives it.
