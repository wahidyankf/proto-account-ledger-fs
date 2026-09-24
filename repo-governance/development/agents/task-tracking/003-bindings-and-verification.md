---
description: >-
  Fixes how the task-list obligation reaches delegated agents and harnesses without a second copy of the rules, and how
  compliance is verified.
when_to_use: >-
  Use when binding the obligation to a delegated agent or a harness, or when reviewing whether a session kept its list.
---

# Bindings and Verification

## Delegated Agents

A delegated agent does not inherit the main thread's instruction file, so the obligation has to reach it another way:
typically a skill every delegated agent loads, or a clause in the delegation prompt.

That binding says only what is specific to reaching the agent: that the obligation applies to it exactly as it applies
to the main thread, that it covers every task with no size threshold, and how the agent's harness exposes a task list.
It cites this standard for everything else. It does not restate the rules, soften them, or add to them.

This standard owns the rules completely. A binding that paraphrases them is a second copy that will drift, and nothing
would decide which copy a delegated agent should have believed; see
[One Source Per Fact](../../../principles/one-source-per-fact.md) and [Capability Forms](../capability-forms.md).

## Harnesses

Use the harness's native task mechanism. Where a harness exposes task creation and status-update tools, those tools are
the list. Where it has none, keep a visible written checklist and update it the same way. Harnesses call the feature a
task list or a todo list; the obligation is identical under either name.

## Plans

Inside plan-mediated work, the plan's delivery checklist is the authoritative progress record, updated in the same
change as the work it describes. The live list tracks in-session state during that execution. Both stay in sync, and
neither exempts the other.

It is also the only written one. A scratch or report directory holds what an execution needs and then discards —
scripts, assets, logs, intermediate data, the touched-path ledger — and never a copy of the checklist, its ticks, or its
status. Two written records drift apart, and nothing decides which one was true. Outside plan-mediated work there is no
checklist, and a scratch file may carry working notes that have to survive a context boundary.

## What Does Not Satisfy This

- a list written after the work, describing what already happened;
- prose narration of progress in place of list entries;
- a list created at the start and never updated;
- one item covering a whole deliverable, in progress from start to finish, which gives no signal of how far the work got
  or where to resume.

## Verification

No gate can see a harness task list. The list lives in the session rather than in the repository, and a commit looks the
same whether or not a list was kept, so a gate declared for this standard would always pass.

Review verifies compliance by setting the list beside the change and the commands actually run. A session that produced
work with no corresponding entries is the violating observation. An adopter that wants the check earlier enforces it in
its own session-review checklist.
