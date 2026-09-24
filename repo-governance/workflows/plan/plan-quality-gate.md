---
name: plan-quality-gate
description: >-
  Judges a complete plan draft against the specification and records one terminal verdict with sanitized findings.
when_to_use: >-
  Use after a complete six-document draft and its post-write gate, before execution begins.
---

# Quality Gate

## Entry

A complete draft, with both decision gates finished. The draft is frozen at a named commit for the duration of the gate.

## Sequence

1. **Freeze the snapshot.** Record the commit. A gate that re-reads a changing draft cannot state what it verified.
2. **Run structural validation** against the frozen snapshot. Structure is mechanical and is checked mechanically — see
   [Structural Validation](../../conventions/structure/plans/006-structural-validation.md).
3. **Review what validation cannot reach**: whether the acceptance criteria are testable and the right ones, whether
   `delivery.md` is genuinely executable by someone who was not present, whether the technical shape matches the work.
4. **Record one terminal verdict** — `PASS`, `PASS_WITH_FINDINGS`, or `FAIL` — with the command, the commit, the time,
   and the findings, sanitized.
5. **Repair within the budget.** At most two repair cycles. Each cycle repairs against the frozen finding list and
   re-verifies once.
6. **Decide at the ceiling.** If findings remain after the second cycle, choose between the repaired draft and the last
   known-good state on the criteria declared before the first cycle, and record the choice and its reasoning. Do not
   extend the budget because the next attempt looks close.

## Exit

A terminal verdict exists as a file, with its command, commit, timestamp, result, and sanitized findings.

## Why Bounded

An unbounded quality gate is a gate that always passes eventually. Each repair cycle costs judgement, and the third
cycle is usually spent defending the second rather than improving the plan.

The budget forces the more useful question: is this draft good enough to execute, or is the last known-good state better
than what two cycles produced? Either answer closes the gate.

## Adopter Decision: What Follows the Audit

Repositories genuinely disagree on what the gate does after it finds something, and the choice is recorded.

| Option                        | What happens                                                                                                                                                                                                                                                       | Trade-off                                                                                                       |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------- |
| repair within the budget      | the sequence above: up to two repair cycles, then a recorded choice at the ceiling                                                                                                                                                                                 | closes on a usable draft; the gate both judges and edits                                                        |
| audit, then one stabilization | a read-only audit freezes a ledger of material gaps only; its rows are repaired once, and one further cycle may add only gaps the repair caused; the result is a pass or a blocked verdict naming its cause: input changed, non-convergent, or tooling unavailable | never invents an answer or loops; a blocked plan needs new input and a fresh, explicitly directed run           |
| check-fix to zero findings    | validation and fixing at a criticality threshold repeat under a cycle ceiling until two consecutive validations are clean; a fixer that changes nothing, or a finding set repeating an earlier cycle's, ends it partial                                            | ends clean when it converges; costs repeated audits, and admits findings by severity rather than by materiality |

Under the audit-first option, the gate runs only when someone explicitly directs it or a workflow named as its caller
invokes it; creating, editing, or executing a plan never authorizes it. Each run serves one named checkpoint: before
execution, after a material change, or at completion. Its pass authorizes neither execution nor commit, no mandatory
finding is waived, and a not-applicable row carries evidence.

The second and third options replace steps 4 to 6, and a caller reads a `blocked` or `partial` result as `FAIL`, and a
clean end as `PASS`, or `PASS_WITH_FINDINGS` when findings are recorded.
