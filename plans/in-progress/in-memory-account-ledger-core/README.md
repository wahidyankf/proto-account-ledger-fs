# In-Memory Account Ledger Core

Build the in-memory account ledger the [challenge brief](../../../challenge-raw.md) asks for, with its deliverable
documents.

## Status

In progress, as a live iteration. By decision, this plan does not follow the usual planning rules — no six-document set
and no decision gates; documents are added here only as they are needed.

## Where Things Live

The assessment docs sit at the repository root, because the brief names most of them there, and are kept in agreement
per [Assessment Docs](../../../repo-governance/conventions/structure/assessment-docs.md):

- [challenge-raw.md](../../../challenge-raw.md) — the brief, verbatim
- [AMBIGUITIES.md](../../../AMBIGUITIES.md) — every ambiguity and its resolution
- [NUMBERS.md](../../../NUMBERS.md) — every constant and why it has that value
- [REJECTED.md](../../../REJECTED.md) — refused criteria and abandoned approaches
- [WORKLOG.md](../../../WORKLOG.md) — timestamped record of the work
- [MOVEMENT.md](../../../MOVEMENT.md) — each day's movement per account, fully analysed
- [OUTPUT_TARGET.md](../../../OUTPUT_TARGET.md) — the exact text the CLI must print
- [ACCEPTANCE_CRITERIA.feature](../../../ACCEPTANCE_CRITERIA.feature) — the brief's acceptance criteria as draft Gherkin

## Decisions So Far

- Scope: all of Part 1, plus an architecture trade-offs document at `docs/explanation/architecture-trade-offs.md` that
  feeds the Part 2 PDF; the PDF itself is out of scope.
- The deliberately failing test runs under its own Nx target, outside `test:quick`, `test:integration`, `test:e2e`, and
  the pre-push hook.
- Expected domain failures are typed result values, not exceptions.
- The agent appends to `WORKLOG.md` with real timestamps as work happens; entries may also be added by hand.

- `ACCEPTANCE_CRITERIA.feature` stays at the root, unexecuted, so it cannot break the test suite. It moves under
  `specs/` only once no ambiguity blocks it, and only after the plan documents exist.

Open design questions are tracked in [AMBIGUITIES.md](../../../AMBIGUITIES.md) and settled one at a time.

## Directory Map

No subdirectories yet.
