---
description: >-
  States that the rules, authority, and state governing work survive context loss, so a resumed or handed-off reader
  acts under exactly the rules and permissions the original reader had.
when_to_use: >-
  Use when work spans a context compaction, a handoff, or an interrupted session, or when deciding where a rule, a
  decision, or an authorization must be written.
---

# Governance Continuity

A rule held only in someone's working memory stops applying when that memory is lost. Work that resumes after
compaction, handoff, or interruption follows the same rules, holds the same authority, and continues the same state as
the work that stopped — no more and no less.

## Context Loss Is Routine

A long task is summarized, a session ends, a reviewer picks up where an author stopped, an agent's context is compacted.
None of these is an accident. They are the ordinary lifecycle of work, and they arrive at moments nobody chooses.

A summary is shorter than what it summarizes, and what it drops is decided by what looked unimportant at the time. Rules
and obligations look unimportant exactly until they apply. The question is never whether a reader will lose context; it
is whether anything governing the work was stored only there.

## What It Requires

- **Every rule lives in a file**, reachable from the repository's instruction entry point. A rule stated only in a
  prompt, a chat, a review comment, or a change description is not a rule of the repository.
- **Reload rather than reconstruct.** After context loss, re-read the governing documents and check the repository's
  current state against the recorded state before the next action. Where a summary and the canonical source disagree,
  the source wins. A reconstruction is plausible, which is worse than knowing that something is missing.
- **Record the state, not only the rules.** Authorization, decisions, frozen inputs, open findings, pending
  verification, and uncommitted changes live somewhere durable, so a summary can point at them instead of paraphrasing
  them. A summary or handoff names where the governing rules live and what is still owed.
- **Missing detail is not permission.** A rule absent from a shortened context is recovered from its source, never
  treated as relaxed.
- **No authority is inferred.** Recorded authorization survives context loss, and a resumed reader holds exactly that:
  it never assumes a permission because it cannot see a refusal. Tracking where work stands grants nothing.
- **Bounded work stays bounded.** A resumed bounded operation continues from its recorded position, never from zero, and
  never reopens a finding its record marks resolved — see
  [Bounded Convergence](../development/workflow/bounded-convergence.md).
- **Unfamiliar is not wrong.** In-progress changes a resumed reader does not recognize are kept and understood before
  anything reverts them; they are more often unread than mistaken.
- **Rules change by their own act.** A rule that does not fit the work is changed in its document, with its own
  authorization — never weakened silently or worked around.

## Where It Is Already Load-Bearing

| Applied in                                                                                  | As                                                                    |
| ------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| [Plan Execution](../workflows/plan/plan-execution.md)                                       | a resumed session continues a budget; it does not reset one           |
| [Delivery Contract](../conventions/structure/plans/004-delivery-contract.md)                | an executor with no memory of the plan can tell what to do next       |
| [Decision Gates](../development/agents/planning-capabilities/003-decision-gates.md)         | a choice is traceable from the plan, without conversation history     |
| [Executor Authority](../development/agents/planning-capabilities/004-executor-authority.md) | authorization is recorded once, so it never moves into memory         |
| [Quality Gate](../workflows/plan/plan-quality-gate.md)                                      | the draft is frozen at a named commit, so the gate knows what it read |

## Why a Principle

It constrains how every other artifact is written rather than what any of them says. A convention that assumed its
reader remembered the previous session would fail the first time a session ended, and no care inside that convention
could prevent it.
