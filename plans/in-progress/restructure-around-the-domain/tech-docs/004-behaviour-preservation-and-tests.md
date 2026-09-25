# Behaviour Preservation and Tests

How the plan proves that nothing a user, a reader of the assessment docs, or a test can observe changes, while every
file of the application moves (R10, R11). The owner's constraint, in their words: "hasil akhir gak boleh berubah. cuman
struktur yang boleh."

## What Must Not Change

| Surface              | What stays identical                                 | Proof                       |
| -------------------- | ---------------------------------------------------- | --------------------------- |
| the program's output | stdout, stderr, and exit code, for every input       | the behaviour corpus        |
| the brief's report   | `OUTPUT_TARGET.md`'s fenced block, byte for byte     | the golden e2e test         |
| the assessment docs  | every figure, verdict, reading, and cited test name  | `git diff`, the cited names |
| the tests            | every test, its cases, expected values, and xfail    | the test inventory          |
| the rules' outcomes  | every refusal, fee, interest figure, hold, and order | the three suites, unchanged |

The assessment docs change in one place only: `WORKLOG.md` gains one entry per session of work, newest first, as the
[assessment docs convention](../../../../repo-governance/conventions/structure/assessment-docs.md) requires. No other
assessment doc cites a module or a function, so none goes stale; `AMBIGUITIES.md` cites the path
`apps/account-ledger-cli/tests/` and `MOVEMENT.md` the path `apps/account-ledger-cli/tests/unit/`, and both stay.

## The Behaviour Corpus

Phase 0 writes `local-tmp/restructure/corpus.py`, a scratch script that runs the program as a process, the way a user
does, over a fixed set of inputs, and prints for each its exit code, its standard error in full, and its standard
output's SHA-256 and line count. It takes the application directory as its argument, so the same inputs run against a
baseline copy of the application and against the working tree. The script is scratch and never committed, as
[evidence files](../../../../repo-governance/conventions/structure/plans/016-evidence-files.md) require; what it prints
is the evidence, each file headed by `#` lines naming the command, the commit, and the time it ran, which the comparison
ignores:

```bash
mkdir -p local-tmp/restructure/baseline
/usr/bin/git archive 83dfd58 apps/account-ledger-cli | tar -x -C local-tmp/restructure/baseline
python3 local-tmp/restructure/corpus.py local-tmp/restructure/baseline/apps/account-ledger-cli \
  > plans/in-progress/restructure-around-the-domain/evidence/phase-0-corpus.txt
python3 local-tmp/restructure/corpus.py apps/account-ledger-cli \
  | diff -I '^#' plans/in-progress/restructure-around-the-domain/evidence/phase-0-corpus.txt -
```

The baseline copy shares the working tree's `.venv` through `uv run --no-sync` from the application directory, and runs
with `PYTHONPATH` set to its own `src`, so it runs the baseline code on the same interpreter.

The inputs, each written by the script into a temporary directory and named by a relative path, so no absolute path
reaches standard error:

| Group            | Inputs                                                                                      |
| ---------------- | ------------------------------------------------------------------------------------------- |
| the brief        | `streams/challenge.csv`, copied from the application                                        |
| the refusals     | one stream per refusal reason, the seven `Rejection` kinds and a duplicate                  |
| cross-account    | a reversal naming another account's event (AMB-036)                                         |
| settlements      | a partial below the hold, one reaching it, one past it, a final, one against a decline      |
| instalments      | a credit split in 3, a BHD split, a split too fine to make (`TooManyInstalments`)           |
| end of day       | a negative close charging a fee, a refund, an interest adjustment, a capitalization         |
| late and outside | an event booked after the window, one listed after a later day                              |
| volume           | the brief's events a hundred times under new IDs, 1,000 events, as the trade-offs doc times |
| stream faults    | a wrong header, a short row, each money fault, a bad day, each ID fault, an unknown account |
|                  | and kind, a missing and an unexpected cell, a bad `final`, a cell past the CSV field limit  |
| file faults      | a missing file, a file that is not UTF-8, a directory given as the file                     |
| arguments        | no argument, two arguments                                                                  |

Every phase gate runs the corpus against the working tree and compares it with the Phase 0 record; any difference fails
the gate. Phase 8 writes `evidence/phase-8-corpus.txt` and proves it equal (AC-02).

Two effects cannot run in the corpus, because they depend on the terminal: the closed pipe (exit 141) and the interrupt
(exit 130). The unit tests that prove both today keep proving them, and the integration test that runs `main` on the
real descriptors keeps running it.

## The Test Inventory

Phase 0 records `evidence/phase-0-tests.txt`: for every test function, its name and the number of cases pytest collects
for it, read from `uv run --no-sync pytest --collect-only -q` over the three suites, sorted by name. Today: 157 cases
collected, 115 test functions; the unit suite passes 147 with 1 strict xfail, the integration suite 3, the e2e suite 6.

A test is identified by its function name and its number of cases, not its file or node ID, because every file moves and
a parametrized case's ID may follow a renamed argument. Phase 8 records `evidence/phase-8-tests.txt` and proves:

- every Phase 0 name is present with the same number of cases (AC-03);
- the only names added are the new tests listed below;
- the known weakness is still the one strict xfail, and nothing is skipped.

What a moved test may change, and what it may not:

| May change                                                     | May not change                                |
| -------------------------------------------------------------- | --------------------------------------------- |
| its file, as [the target layout](001-target-layout.md) maps it | its name                                      |
| the calls it makes: `account.compute_closing(day)` for         | its docstring's AC and AMB identifiers        |
| `compute_closing(history, day)`, `Ledger(…).process_event(…)`  | its cases: the inputs each builds, in values  |
| the types it builds a case from: `AccountOpeningIn` for        | its expected values and its assertions' sense |
| `AccountIn`, `(SettlementKind.FINAL, amount)` for              | its xfail, strictness, and reason             |
| `FinalSettlement(amount)`                                      |                                               |
| a fake port where it patched `cli.process_stream`              |                                               |

## Cited Test Names

`local-tmp/restructure/cited_names.py` reads every `test_…` name in `AMBIGUITIES.md`, `MOVEMENT.md`, `REJECTED.md`,
`NUMBERS.md`, and `OUTPUT_TARGET.md`, and every `def test_…` under `tests/`, and fails if a cited name is not defined.
Today it reports 60 cited, 115 defined, none missing. It runs at every phase gate (AC-04); the table tests
`test_every_state_and_settlement_input_pair_follows_the_table` and
`test_an_unconfigured_transition_leaves_the_state_unchanged` are not cited, and keep their names anyway.

## New Tests

Each is written first and seen to fail for the stated reason before the code that passes it, one behaviour per cycle,
per [test-driven development](../../../../repo-governance/development/quality/testing/test-driven-development.md):

| Test, in the file it lands in                                                        | Fails first because        |
| ------------------------------------------------------------------------------------ | -------------------------- |
| `domain/ledger/test_ledger.py`: `test_an_event_on_an_unconfigured_account_is_an_…`   | today's `assert` raises    |
| `unit/test_cli.py`: `test_an_unknown_account_exits_2_naming_it`                      | `run_cli` has no such line |
| `domain/model/test_money.py`: `test_taking_all_of_a_hold_or_more_leaves_nothing`     | `AmountIn` has no `take`   |
| `domain/model/test_money.py`: `test_a_zero_change_has_no_direction`                  | no `make_directed_amount`  |
| `domain/model/test_events.py`: `test_instalments_refuse_parts_whose_number_is_not_…` | `Instalments` has no parts |

The two shortened names are `test_an_event_on_an_unconfigured_account_is_an_internal_fault` and
`test_instalments_refuse_parts_whose_number_is_not_the_count`.

None changes a user-visible line: the stream reader refuses an unconfigured account before the ledger sees it, a
settlement that reaches its hold is settled today as after, the interest step never records a zero change, and the
reader builds every split through `Instalments.make`.

## Every Other Proof

- **The golden run.** `test:e2e` compares the program's standard output on the brief with `OUTPUT_TARGET.md`'s fence;
  the fence itself is compared with `git show 83dfd58:OUTPUT_TARGET.md` at Phase 8 (AC-01).
- **Coverage.** `test:unit` keeps its 80% line gate; the plan records today's figure, about 95%, and Phase 8 reports it
  again, lower only with a named reason.
- **Mutation spot-checks.** At Phase 8, for each new module, one rule is broken by hand in a scratch copy and a test
  must fail: `take` returning the rest at zero, `Ledger.process_event` skipping the repeated-ID check, `EventLog.select`
  keeping another account's entries, `ReportedClosings.update` dropping a restatement, `CsvFileSource` reporting the
  wrong path, and `TextReportSink.publish` not flushing. Each result goes to `evidence/phase-8-mutations.txt`; the
  scratch copy is deleted, and nothing of it is committed.
- **Timings.** The trade-offs doc's timing table is re-measured with `local-tmp/restructure/scale.py`, rewritten against
  the new API, on 6, 30, 60, and 120 days, with the 1,000-event volume run beside it; the table takes the new figures if
  any moves by more than a fifth, and its conclusion stays unless a figure contradicts it, which is then reported to the
  owner as a finding.
