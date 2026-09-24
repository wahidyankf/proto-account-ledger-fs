# In-Memory Account Ledger Init

Build the in-memory account ledger the [challenge brief](../../../challenge-raw.md) asks for, test-first, with its
deliverable documents and the architecture trade-offs document that feeds the Part 2 PDF.

## Status

In progress. On 2026-09-24 the owner asked for the complete six-document plan, which replaces this folder's earlier
decision to run as a live iteration without the usual plan documents or decision gates. Both decision gates are closed
and recorded in the [decision records](tech-docs/005-decision-records.md). The same day the owner ordered execution: the
quality gate runs once on the committed plan, repairing within its budget, and execution follows it phase by phase;
archival then needs the execution check only (D11).

## Context

The assessment docs at the repository root already resolve every ambiguity, fix every figure, and decide every criterion
verdict. No ledger code exists yet: `apps/account-ledger-cli` is a scaffold that prints `Hello, world!` and binds one
Gherkin scenario at three test layers. This plan builds the ledger those documents describe, and changes the
repository's rules where the build needs them to change.

## Scope

In scope, as [brd](brd.md) and [prd](prd.md) state:

- the ledger core, its CSV stream reader, its report renderer, and its command-line shell;
- a plain-pytest suite at three layers proving every criterion verdict and every resolved rule, and the one strict
  expected failure the brief asks for;
- the as-built C4 architecture, and the README, NUMBERS, AMBIGUITIES, MOVEMENT, REJECTED, and WORKLOG updates the code
  makes necessary;
- the rule changes that retire Gherkin and record the repository's own choices; and
- `docs/explanation/architecture-trade-offs.md`.

Out of scope: the Part 2 PDF itself, any hold lifetime, a machine-readable output mode, and any change to a figure
[MOVEMENT](../../../MOVEMENT.md) fixes.

## Approach

A functional core over an event-sourced, append-only log, with every balance recomputed from the log, inside a thin
shell that reads the stream file and prints the report (see [the technical design](tech-docs/README.md)). Governance
changes land first, then the core bottom-up, one red, green, and refactor cycle per behaviour, then the shell, the known
weakness, partial capture last, and the documents. Each phase ends at a gate, commits its theme, and pushes to
`origin/main` ([delivery](delivery.md)).

## Dependencies

- The figures in [MOVEMENT](../../../MOVEMENT.md) and the text in [OUTPUT_TARGET](../../../OUTPUT_TARGET.md), which the
  code must reproduce and never edits.
- The toolchain the repository pins: Python 3.14, uv, pytest, ruff, pyright, Nx, and Rhino.
- The owner, for the two decisions only the owner can take during execution: a figure the code disagrees with (RC1), and
  falling back from partial capture (RC2). Directing the quality gate and ordering execution were given on 2026-09-24.

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

## Directory Map

- [brd.md](brd.md) — why the work is worth doing, for whom, and its risks.
- [prd.md](prd.md) — personas, stories, and acceptance criteria AC-01 to AC-37.
- [tech-docs/](tech-docs/README.md) — the technical design, decision records, and file impact.
- [delivery.md](delivery.md) — the phased checklist, its gates, and its execution record.
- [learnings.md](learnings.md) — what execution discovers, held until it is routed.
