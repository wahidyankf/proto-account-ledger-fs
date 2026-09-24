---
name: plan-ideas-grooming
description: >-
  Reviews every brief in the ideas root and drives each one to promotion, deliberate retention, or retirement.
when_to_use: >-
  Use when the ideas root has accumulated briefs, or before choosing what to plan next.
---

# Ideas Grooming

## Entry

`plans/ideas/` holds at least one brief, and someone needs to know which of them are still worth anything.

Inputs: `repositories` (`string`, optional, default the current repository), groomed together; `dry-run` (`boolean`,
optional, default `false`), recording decisions without writing.

## Sequence

1. **Freeze the list.** Enumerate every brief in `plans/ideas/` before judging any of them. A brief added during
   grooming belongs to the next pass, not this one — otherwise the list never closes.
2. **Read each brief once.** A brief that cannot be understood in one reading has a defect worth recording; that is
   itself a grooming outcome.
3. **Settle residency** across repositories before merging, first match winning: a brief needing secrets or
   infrastructure state resides where private infrastructure work is designated; one naming something that exists in
   only one groomed repository resides there; any other resides where generalizable work is designated. Record the rule,
   even when nothing moves.
4. **Merge duplicates and split mixed briefs.** Overlapping briefs merge into the more complete one, keeping unique
   content; a brief joining unrelated concerns splits in two.
5. **Assign exactly one disposition** per brief:

   | Disposition | Means                                                           |
   | ----------- | --------------------------------------------------------------- |
   | promote     | worth planning now; it becomes a formal plan in the backlog     |
   | keep        | still worth doing eventually, and here is what would trigger it |
   | retire      | not worth doing, and here is why                                |

6. **Record the reason** for every `keep` and every `retire`. A `keep` without a trigger is indistinguishable from
   indecision, and it will be re-read at every future grooming pass at the same cost.
7. **Relocate toward duplication, never loss.** Land the brief in its resident repository, verify it arrived, then
   delete the source copy; an interruption leaves a recorded duplicate.
8. **Keep names and links true.** Rename a brief whose name no longer fits its title, deferring on a name collision;
   rewrite links into and out of each moved or renamed brief in the same change, and log each merge, split, move, and
   rename in each repository's ideas index.
9. **Promote by authoring, not by moving.** A promoted brief is the input to [Planning](plan-planning.md); the brief
   itself does not become the plan. Move the brief only after the plan exists.

   First confirm the brief is ripe: every
   [Idea Brief Template](../../conventions/structure/plans/015-idea-brief-template.md) section holds a real answer, open
   questions allowed, stubs not; an unripe brief stays, with a report naming each stub. Then run the deferred prior-art
   study and get the owner's explicit approval. The brief leaves the ideas root in the change adding its plan.

10. **Delete retired briefs.** Version control is the archive. A retired brief left in place will be reconsidered by
    someone who does not know it was already rejected.

## Exit

Every brief on the frozen list carries a disposition, and every `keep` and `retire` carries a reason.

No unresolved duplicate remains and each brief sits, truthfully named, in its resident repository. Partial outcome:
deferred renames or interrupted relocations remain, recorded.

## Adopter Decision: Layout, Cadence, and Residency

| Decision  | Option                                                                               | Trade-off                                                  |
| --------- | ------------------------------------------------------------------------------------ | ---------------------------------------------------------- |
| layout    | one flat ideas root                                                                  | nothing to re-file; urgency shows only through grooming    |
|           | four folders, urgent or not by important                                             | every pass re-files briefs; the pressing ones sit apart    |
| cadence   | on request only                                                                      | no idle passes; the root can grow unread                   |
|           | a brief-count or elapsed-time trigger, first wins                                    | the root is never left long unread; a pass may find little |
| residency | name the repositories designated for private infrastructure and generalizable briefs | one record read by every pass                              |

Folders need a falsifiable test per axis, such as urgent only when a live plan waits on it; a trigger needs each pass
dated in the ideas index.

## What This Does Not Do

It does not size, schedule, or sequence work. A promoted brief has been judged worth planning; whether it is planned
next is [Backlog Grooming](plan-backlog-grooming.md)'s question.

It does not improve briefs. A brief too vague to judge is retired or rewritten, and rewriting it is authoring — the same
work as writing it the first time.
