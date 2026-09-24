---
description: >-
  Requires an agent to exhaust safe, in-scope ways of proceeding before asking the user anything, then to ask the fewest
  questions carrying the context needed to answer them, without waiving any reserved authorization.
when_to_use: >-
  Use before asking the user for information, confirmation, a preference, or a decision during repository work.
---

# Last-Resort Questions

A question spends the user's attention. That is the right spend when only the user holds the answer, and the wrong one
when the repository already records it.

## Before Asking

1. **Read what governs the work** — the instruction file, the applicable conventions, the specification, the files
   involved, and their history.
2. **Run safe diagnostics** — a read-only command, a help text, a probe. Evidence answers most questions about behaviour
   faster than a reply does, and answers them with proof.
3. **Reuse what is already known** — evidence gathered earlier in the task or returned by a delegated agent. Never ask
   the user to repeat something they already said or something the repository already records.
4. **Check whether the ambiguity changes anything** — where every reading leads to the same work, pick one, say which,
   and continue.
5. **Take a bounded assumption** — when it is reversible, low in risk, and unlikely to diverge from the user's intent.
   State it where the user will see it.
6. **Finish the independent work** — everything the answer does not block, including viable in-scope alternatives, so
   the question arrives with the rest of the work already done.

## When Asking Is Necessary

Ask only when the missing information or authority exists nowhere the agent can reach, and proceeding on any assumption
would materially risk incorrect work, harm, an irreversible or externally visible effect, a rule violation, or an
outcome meaningfully different from the one intended.

Never ask for a discoverable path, a current implementation fact, a documented default, or which validation to run.

## How to Ask

Raise the open questions together, at one moment, rather than interrupting the work each time one surfaces. Ask the
fewest questions that unblock it, and make each one state:

- the blocker;
- what was read, run, or attempted;
- the viable options and what each would produce; and
- the recommended option, and why no safe default remains.

A question with that context is a decision the user can make in one pass. A question without it is a request to redo the
investigation. Where a choice has several defensible answers, offer mutually exclusive options with exactly one marked
as recommended; [Grill Me](../../../.agents/skills/grill-me/SKILL.md) is the fuller form.

## What This Does Not Waive

Exhausting the repository never substitutes for an authorization a rule reserves to the user — to commit, publish,
deploy, destroy, or create a durable artifact, or to act on an item a plan assigns to a person under
[Executor Authority](planning-capabilities/004-executor-authority.md). Complete every independent prerequisite first,
then obtain that authorization explicitly. Silence is not authorization, and neither is the inconvenience of asking.

Security boundaries, destructive scope, and product preference are never settled by assumption, however bounded.

Equally, never manufacture work to avoid a question that genuinely has to be asked. The rule minimizes questions; it
does not forbid them.

## Why Review Enforces It

Whether a question was necessary depends on the context of the task, which no validator can read. Contextual review
judges it, and a mechanical gate would only count questions.
