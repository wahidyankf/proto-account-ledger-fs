# Restructure Around the Domain

Restructure `account-ledger-cli` so that every operation lives on the type it is about, in DDD and hexagonal layers,
with no inheritance, no `assert`, and immutable values throughout, while its output, its tests, and every assessment
doc's figure stay exactly as they are.

## Status

In progress. The owner asked for this plan on 2026-09-25 as "the last big push before our submission", settled R1 to R14
one question each at the pre-write gate, and then set the goal: finish the plan, commit and push it, run its quality
gate, commit and push, execute every phase with a commit and push each, and check the result instead of running the
quality gate again. That goal is the execution authorization; the [Execution Record](delivery.md) logs each step.

## Context

The ledger is built and every figure is proven. The code grew by topic: the rules about one account sit in nine modules
reached through forwarding methods, seven base classes share fields, the stream processing and the report sit in the
domain, and five `assert`s carry proofs. The owner's example of the scatter: `list_records` takes only an account's
history but lives in `authorizations.py`. [The business case](brd.md) states why that matters for the live defense.

## Scope

In scope, as [brd](brd.md) and [prd](prd.md) state:

- every source and test module of `apps/account-ledger-cli`, moved, merged, or reshaped as
  [the target layout](tech-docs/001-target-layout.md) draws it;
- the import bans, the no-inheritance lint gate, and the Python rules on operations and inheritance;
- the as-built architecture, the application and root READMEs, the trade-offs document, and `WORKLOG.md`.

Out of scope: any behaviour a user or a test can observe, the assessment docs other than `WORKLOG.md`, and the Part 2
PDF, which is written beside this plan.

## Approach

Bottom-up, one layer per phase, each phase landing as build-valid commits pushed at its gate: a baseline and a recorded
behaviour corpus, the values, the Account aggregate, the Ledger, the application with its ports and adapters, the
no-inheritance gate and its rule, a line-by-line polish, the documents, and a final verification against the baseline
([delivery](delivery.md)). Behaviour is proven unchanged at every gate by the corpus, the test inventory, and the
cited-name check ([004](tech-docs/004-behaviour-preservation-and-tests.md)).

## Dependencies

- Commit `83dfd58`, the baseline every comparison reads.
- The toolchain the repository pins: Python 3.14, uv, pytest, ruff, pyright, pylint, vulture, Nx, Rhino, and Prettier.
- The owner, only to reopen a decision; R17, R18, and R20 were settled on the recommendation under the owner's goal.

## Directory Map

- [brd.md](brd.md) — why the restructure is worth doing, for whom, and its risks.
- [prd.md](prd.md) — personas, stories, and acceptance criteria AC-01 to AC-16.
- [tech-docs/](tech-docs/README.md) — the final layout, the design, the proofs, the decisions, and the file impact.
- [delivery.md](delivery.md) — the execution record, the phases, and their gates.
- [learnings.md](learnings.md) — what execution discovers, held until it is routed.
