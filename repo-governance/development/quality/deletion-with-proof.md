---
description: >-
  Requires anything being deleted or retired to have an inventory, a named successor for each responsibility, and a test
  that fails without it.
when_to_use: >-
  Use before deleting a command, workflow, agent, script, or module, or before retiring a name.
---

# Deletion With Proof

Deleting something that is genuinely unused is one of the most valuable changes anyone makes. Deleting something that
turned out to be load-bearing is one of the worst.

The difference is not confidence. It is evidence, and the evidence is cheap to gather compared to what it prevents.

## Before Deleting

1. **Inventory every live responsibility.** Every command, hook, script, continuous-integration use, specification,
   reference, and caller. Not what it was for — what currently depends on it.
2. **Name a successor for each responsibility.** Explicitly, by path. A responsibility with no named successor is not
   redundant; it is about to be lost.
3. **Prove the behaviour is missed.** Disable the thing and demonstrate that something fails. A test that passes with it
   disabled was never testing it.
4. **Prove the successor provides it.** The same demonstration against the new owner.
5. **Compare on recorded inputs.** Both paths agree on the same inputs, recorded, before one of them goes away.
6. **Run the repository's full gate.**

Only then delete, and update every reference in the same change.

## Step 3 Is the One That Gets Skipped

It is the least convenient step and the only one that can contradict the plan. Everything else confirms what was already
believed; disabling the thing is the only step that can show the belief was wrong.

Skipping it is usually rationalized as obvious. If it is obvious, the demonstration takes minutes.

## No Compatibility Shim

Deletion is complete. A forwarding stub, an alias, or a deprecated wrapper left behind means the thing was not deleted —
it was renamed, and now there are two names, one of which nobody maintains.

Where a shim is genuinely needed, that is evidence the deletion was premature.

## Record the Destination

Every removed responsibility records where it went. This survives the change and is what a future reader needs when they
find a reference to something that no longer exists.

"Removed as obsolete" is not a destination. "Removed; check aggregation now lives in the ordered gate registry" is.

## If Something Fails Afterwards

Restore the previous implementation once, reinstate its invocation, and record that the retirement did not hold.

Do not attempt the deletion a second time in the same change, and do not paper over the gap with a shim. The inventory
missed something, and finding out what it missed is the work — not getting the deletion through.
