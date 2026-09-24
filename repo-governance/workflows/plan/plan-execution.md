---
name: plan-execution
description: >-
  Works through a plan's delivery checklist, recording the result of each item as it resolves.
when_to_use: >-
  Use when a plan has passed its quality gate and its checklist is ready to be executed.
---

# Execution

## Entry

A plan in `plans/in-progress/` whose quality gate returned a terminal verdict permitting execution.

The verdict is current and comes from an explicitly directed gate run; without one, execution stops and says so. A
queued plan is moved into `plans/in-progress/` first, never copied. Input: `plan` (`directory`, required).

## Sequence

1. **Read the plan before the checklist.** `delivery.md` is written to be executable, not to be self-explanatory. The
   other five documents hold why each item exists.
2. **Confirm the execution checkout.** Which working copy, which branch or worktree, which delivery mode. Executing in
   the wrong checkout is recoverable; noticing late is expensive. Enter it, synced per
   [Integration Path](../../development/workflow/integration-path.md), before any change; every delivery unit reuses the
   plan's one worktree when its route uses one.
3. **Mirror the checklist, disk first.** On every start and resume, rebuild the task list from `delivery.md`: one task
   per unchecked action checkbox, in order, and none without one. A tick whose change is absent is removed and its item
   re-run. Dormant recovery items wait for their trigger. See
   [Task Tracking](../../development/agents/task-tracking.md).
4. **Work items in order.** An item blocked by something outside the plan is recorded as blocked, with what would
   unblock it, rather than skipped silently. A `[HUMAN]` item is prepared as far as possible, then handed over; it is
   never performed or ticked on that person's behalf.
5. **Resolve each item atomically.** Tick the checkbox, record the result, and move on — in that order, as one step. A
   batch of ticks applied at the end of a session cannot say which item produced which result. Tick only once the item's
   outcome and its proof both hold.
6. **Record results, not only ticks.** What was produced, what changed, what was surprising. A tick says an action
   happened; it does not say what it found. See
   [Verification Routing](../../development/agents/planning-capabilities/006-verification-routing.md).
7. **Pass each phase gate before the next phase.** Per
   [Phase Boundaries and Delivery Choices](../../conventions/structure/plans/011-phase-boundaries-and-delivery-choices.md),
   run each gate check as written against the phase's combined state, and repair a failure inside the phase before its
   delivery or the next phase starts.
8. **Land each delivery unit** by the route Integration Path records. A unit is complete once it reaches the trunk.
9. **Fix what fails, including what was already failing.** A check that was red before the plan started is still red
   because of this plan's work by the time it ships. Pre-existing is an explanation, not an exemption.
10. **Route discoveries to `learnings.md`** as they happen, not from memory afterwards. Discovered work becomes a new
    checkbox only when it serves an outcome the plan already has.
11. **Run [Execution Check](plan-execution-check.md)** once every substantive item is terminal.
12. **Close out on a permitting verdict.** Give each dormant recovery item a dated `Not triggered` disposition with its
    evidence, run [Dev Artifact Clean-Up](../maintenance/dev-artifact-clean-up.md) once every delivery unit has landed,
    and archive per
    [Knowledge Capture and Archival](../../conventions/structure/plans/008-knowledge-capture-and-archival.md).

## Exit

Every substantive checklist item is terminal, `learnings.md` holds what execution discovered, and the execution check
has recorded a verdict.

Partial outcome: only blocked items remain, each recording what would unblock it; the plan stays in `plans/in-progress/`
and the execution check waits. A failed run keeps any worktree and records why.

## Adopter Decision: Completion Gate

| Option                        | Archival also requires                                    | Trade-off                                            |
| ----------------------------- | --------------------------------------------------------- | ---------------------------------------------------- |
| execution check only          | nothing beyond the execution check's permitting verdict   | one review closes the plan                           |
| fresh quality gate on the end | a new, explicitly directed quality-gate `PASS` on the end | the whole delivered plan is judged again, at one run |

Record the option. The fresh-gate option also requires a fresh `PASS` before interrupted work resumes. Execution never
starts that gate run itself.

## Pause Safety

Execution stops at arbitrary moments. At any pause the plan itself must carry enough state to resume: the current
checkout, the last terminal gate, the next unresolved item, and any bounded budget already partly consumed.

A resumed session continues a budget; it does not reset one.
