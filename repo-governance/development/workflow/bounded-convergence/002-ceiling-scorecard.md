---
description: >-
  Defines how a loop resolves at its ceiling by scoring its two declared branches, selecting one without asking a human,
  and recording a terminal result.
when_to_use: >-
  Use when a registered loop reaches its ceiling or stops making progress.
---

# Resolving at the Ceiling

At the ceiling, or at the first cycle that makes no progress, the loop resolves. It does not extend, retry, or escalate.

## The Scorecard

1. **Remove ineligible branches.** A branch violating repository instructions, granted authority, confidentiality, or
   safety rules is out, regardless of how well it scores on anything else.
2. **Evaluate each branch under its own rules.** The target branch is judged against the rules it proposes; the existing
   branch against the repository's current rules. Judging the existing state by rules it predates measures the wrong
   thing.
3. **Compare eligible branches in this order:** rule compliance; safety and reversibility; preservation of verified
   behaviour and data; acceptance-criteria coverage; cross-repository coupling; change size.
4. **On an exact tie, keep the existing state.** The tie-break is not neutral, and should not be: the existing state is
   already verified, and a tie means the change has not shown itself to be better.
5. **Apply the selected branch once and verify it once.**
6. **Record `TARGET_PASS`, `EXISTING_PASS`, or `SAFE_FAIL`.**

## No Human Is Asked

The ceiling is not an escalation point. The branches were declared before the first cycle, and the criteria for choosing
between them were declared with them — so the decision is already made in every respect except which branch the evidence
selects.

Asking at the ceiling converts a bounded operation into an unbounded wait, and the person asked has less context about
what the cycles actually showed than the executor does.

## A Ceiling Alone Is Not a Failure

Reaching a ceiling never produces `SAFE_FAIL` by itself. The executor selects whichever eligible branch wins, and that
selection is a successful outcome — often `EXISTING_PASS`, which means the change was tried, bounded, and judged not
better.

`SAFE_FAIL` is reserved for the case where both branches violate a hard eligibility rule, or where the selected branch
and its single restoration attempt both fail verification.

## Dependent Work Follows the Selection

Downstream work follows only the selected branch. The other branch's acceptance criteria are recorded as not applicable,
with the loop's row as the evidence.

Leaving both alive is how a repository ends up half-migrated with nothing recording which half is authoritative.

## Independent Work Continues

All three results close the loop and none of them stops unrelated work.

`SAFE_FAIL` is the exception in one respect only: it prevents declaring the containing effort complete, because
something was left unresolved and that fact has to survive to the end.
