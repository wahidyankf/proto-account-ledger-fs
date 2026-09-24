---
description: >-
  Adds the keep test and the sanitization and relevance gates every learnings.md entry passes before promotion, the
  explicit record that closes an empty log, and the guardrails that keep triage from becoming theater.
when_to_use: >-
  Use when triaging learnings.md before archival, or when a finished plan has nothing recorded in its learnings.
---

# Learning Triage

[Knowledge Capture and Archival](008-knowledge-capture-and-archival.md) sends each entry to one durable owner or to a
reasoned discard. This module adds what an entry must pass on the way, and what a plan writes when nothing needs
routing.

## A Keep Test, Then Two Gates

Before either gate, each entry answers one question: would routing it make the repository catch this issue next time,
when it does not already? An entry is kept only on yes. Any other entry, including one an existing rule already catches,
changes nothing durable and is discarded with a one-line reason, before anyone spends effort cleaning or placing it.

Every entry that is kept passes both gates, in this order, before it reaches an owner:

| Gate         | Asks                                                                                     | An entry that fails                                                                                                                                                                                                                                     |
| ------------ | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| sanitization | does its text hold a secret, a credential, a personal value, or an internal address?     | is rewritten with placeholders such as `<api-token>` first, and the value never travels — see [No Secrets](../../security/no-secrets-in-tracked-files.md); an entry that cannot lose the value without losing its meaning is discarded with that reason |
| relevance    | does the subject belong to this repository, rather than to a tool or repository it uses? | goes to the repository that owns the subject, per [Related Repositories](../related-repositories.md), or is discarded with that reason                                                                                                                  |

Sanitization comes first because promotion copies text into places that outlive the plan, and a durable owner is far
harder to clean than a transient log. Relevance comes second because a lesson about someone else's tool, filed here as a
rule, is a rule nobody here can keep true.

## An Empty Log Says So

A plan whose run produced nothing worth routing writes one line in `learnings.md`:

```markdown
No generalizable learnings — <reason>.
```

The reason is concrete: the change was a mechanical rename, or every surprise is already covered by a named rule. An
empty file is a finding, not this record, because silence looks identical to a triage nobody performed. A small plan may
use the record as readily as a large one; the triage stays, and only its output shrinks.

## Against Capture Theater

Capture fails in two directions, and both look diligent from outside.

| Failure       | Looks like                                                        | Guardrail                                                                                                                          |
| ------------- | ----------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| under-capture | a clean log after a run full of failed gates and course changes   | triage is mandatory, a plan with nothing to route records that with its reason, and a plan check reports a log left silently empty |
| over-capture  | every tick restated as a lesson, owners picked to look productive | the keep test discards an entry that would change nothing durable; results already in `delivery.md` stay there                     |

Three placement rules keep the triage honest:

- **The executor triages its own log.** Whoever ran the work holds context a later reader lacks, and a reader who did
  not run it discards whatever it cannot understand.
- **The log lives in the plan folder.** A tracker comment, a chat thread, or a review note is not archived with the plan
  and is checked by nothing.
- **Triage happens once, at a fixed point.** Entries are still written as discoveries happen; resolving them is the last
  substantive step, after every substantive delivery item is terminal and before the
  [Execution Check](../../../workflows/plan/plan-execution-check.md) runs. Its knowledge-capture step then confirms that
  every entry is resolved, and archival follows its verdict. Resolution spread across the run becomes commentary that
  nobody closes.

An adopter checks for the empty-log record in its own plan gate, and its execution check expects to find no unresolved
entry, blocking archival when it finds one.

## Principles

This module implements [Explicit Over Implicit](../../../principles/explicit-over-implicit.md), because an empty log is
stated with its reason rather than inferred from silence, and [Fail-Closed](../../../principles/fail-closed.md), because
a log with no entry and no record fails instead of passing as clean.
