---
description: >-
  Orders a migration as expand, migrate, verify, contract, states what proves a switch of authoritative source, and
  keeps input the migration cannot interpret instead of discarding it.
when_to_use: >-
  Use when ordering a migration's delivery steps, proving a switch to a new source of truth, or planning rollback.
---

# Transition and Recovery

## Transition Order

1. **Expand** — introduce the new schema, location, reader, or writer while the old one stays in place.
2. **Migrate** — copy idempotently from a source that no longer changes, validate what was copied, and report an outcome
   someone can observe. Running the step twice neither duplicates nor damages what it already copied.
3. **Verify** — consume the migrated result the way real consumers do, never through the migration's own tooling, and
   practise a restore from the recovery source that has already been checked.
4. **Contract** — keep the old path compatible for a stated period. Archiving or deleting the old source destructively
   is left to a later plan with its own authorization, under
   [Deletion With Proof](../../../development/quality/deletion-with-proof.md).

Each step is the fallback position for the one after it. A step that fills the new location and removes the old one at
once leaves nothing to fall back to if verification then fails.

Verification uses the real consumer path because migration tooling reads back what it wrote, in the form it already
expects, and so agrees with itself. When documents move, the checks that must pass on the moved tree are that every
internal link resolves and every directory index lists its entries. When configuration changes, the command its users
run must succeed.

## Authority Cutover

When the target takes over as the source of truth, or the old source is retired, verification:

1. starts a new process that reads only the saved target configuration;
2. removes access to the old source, inside an isolated fixture; and
3. drives every critical reader and writer the change touches through its ordinary interfaces.

The result must show that the target stays in charge, and that a missing dependency makes it stop rather than reach back
to the old source.

Row counts, the presence of a schema, the migration's own summary, calls that exercise only an adapter, and state held
inside one process do not count as proof. Any of them can pass while some consumer still quietly depends on the old
source, and that consumer fails on the day the old source finally goes.

## Preservation and Recovery

The plan states:

- how each affected reader and writer behaves on rollback;
- the mixed-version boundary: what the system looks like part-way through, and which consumers cope with that;
- how a retry behaves;
- the recovery source, and the manifest describing it; and
- the manual check to be performed.

Input that is unknown or malformed is kept untouched as an opaque record, and what happened to it is reported. It is
never forced into shape, dropped, or overwritten so that the migration can look successful. A migration that claims
success after silently discarding what it could not parse has turned a visible failure into a hidden loss.
