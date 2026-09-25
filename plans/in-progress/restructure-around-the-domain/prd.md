# Product Requirements

What the restructured application must be, stated so each criterion can be checked by a command or a reading. The design
that meets them is in [the technical design](tech-docs/README.md).

## Personas

- **The candidate** defends the code live. Opens a type to learn what it can do, and must never have to search the tree
  for a rule.
- **The assessor** runs the program and reads the documents. Expects the report, the refusals, and the figures the
  assessment docs defend, unchanged.
- **The maintainer** changes the code later. Relies on the tools to refuse a wrong import, an inherited class, or an
  unchecked type.

## User Stories

- As the candidate, I open `AccountIn` and find every rule about one account as its method, so that I can answer "where
  is the fee rule" with one file.
- As the candidate, I call `ledger.process_event(event, day)` and `account.compute_closing(day)`, so that the code reads
  as the domain speaks.
- As the assessor, I run the program on the brief's stream and on any faulty input, and see exactly what I saw before
  the restructure.
- As the assessor, I read the architecture and find it matches the tree, file by file.
- As the maintainer, I add a base class or an upward import, and lint refuses it.

## Acceptance Criteria

Each criterion names its proof; `delivery.md` cites each by its identifier.

- **AC-01.** The program's standard output on `streams/challenge.csv` equals `OUTPUT_TARGET.md`'s fence, and the fence
  equals its text at `83dfd58`.
- **AC-02.** The behaviour corpus run on the result equals its run on the baseline, input by input: exit code, standard
  error, and standard output's hash.
- **AC-03.** Every test function collected at the baseline is collected on the result with the same number of cases; the
  only names added are the five new tests; exactly one strict xfail remains, and nothing is skipped.
- **AC-04.** Every test name cited in `AMBIGUITIES.md`, `MOVEMENT.md`, `REJECTED.md`, `NUMBERS.md`, and
  `OUTPUT_TARGET.md` is defined under `tests/`.
- **AC-05.** `git diff 83dfd58 -- AMBIGUITIES.md NUMBERS.md REJECTED.md MOVEMENT.md OUTPUT_TARGET.md challenge-raw.md`
  is empty, and `WORKLOG.md` only gains entries.
- **AC-06.** pyright strict reports 0 errors; `src/` holds no `assert`, `Any`, `cast`, `# type: ignore`, or `# noqa`.
- **AC-07.** pylint `too-many-ancestors` with `max-parents = 0` passes on `src` and `tests`, and fails on the baseline.
- **AC-08.** Every public module-level function in `src/` is one of `parse_event_id`, `is_aed`, `apply_settlement`,
  `read_file`, `run_cli`, and `main`; every other operation is a method.
- **AC-09.** Every rule about one account is a method of `AccountIn` in `domain/account/account.py`; no other module
  takes an `AccountIn` as its subject.
- **AC-10.** `Ledger` and `EventLog` are frozen classes; the `Log` alias, `process_event`, `close_day`, and
  `find_history_of` functions do not exist.
- **AC-11.** `application/ports.py` declares `EventSource`, `ReportSink`, and `RunLedger`; `CsvFileSource` and
  `TextReportSink` satisfy them; each package's `ruff.toml` refuses the imports 001 lists, and ruff passes.
- **AC-12.** Every class in `src/` is frozen and slotted, save `Ok`, `Err`, the `Enum`s, and the `Protocol`s; no module
  holds a mutable container at module level.
- **AC-13.** The `.py` files under `src/account_ledger/` and `tests/` are exactly those 001's trees list.
- **AC-14.** The architecture, the application README, the root README, and the trade-offs document name only modules,
  types, and functions that exist; the doc sweep reports no removed name outside `plans/`.
- **AC-15.** `003-operations.md` states four cases and No Inheritance, `python-standards.md` summarizes it within 750
  words, and the word-budget, directory-map, and rules gates pass.
- **AC-16.** Each phase ends with its gate passing, one commit or more pushed to `origin/main`, a `WORKLOG.md` entry,
  and an Execution Record line.

Two examples, written as scenarios for readability only; the repository binds no Gherkin:

```gherkin
Scenario: An unconfigured account is an internal fault, never a user-visible one
  Given the ledger opened on the brief's configuration
  When it processes a credit on ACC-003
  Then it returns UnknownAccount for ACC-003
  And the stream reader, given the same credit as a row, refuses it with today's message

Scenario: A settlement reaching its hold settles it
  Given an authorization approved with a hold of AED 200.00
  When a partial settlement of AED 200.00 arrives
  Then take leaves nothing of the hold
  And the authorization is Settled for AED 200.00, as today
```

## Product Scope

In scope: every module under `apps/account-ledger-cli/src/` and `tests/`, the per-package `ruff.toml` files,
`pyproject.toml`'s lint settings, the as-built architecture, the application and root READMEs, the trade-offs document,
the Python operations and naming rules, and `WORKLOG.md`.

Out of scope: any rule, figure, message a user can reach, or exit status; the assessment docs other than `WORKLOG.md`;
the Part 2 PDF; the Rhino gates and the hooks, which stay as they are.

## Product Risks

- **A test's case changes while its name stays.** AC-03 counts cases, and a moved test's expected values are read
  against the baseline in review; a changed expectation is a behaviour change and stops the phase.
- **The long aggregate module becomes hard to read.** Its methods are grouped by topic under one heading comment each,
  in the order the architecture's reading order lists them.
- **An internal line is mistaken for a new user-facing error.** The application README states that no input reaches it,
  and the unit test proves it through a fake run only.
