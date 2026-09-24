# Testing Strategy

Plain pytest at three layers (D12), each in its own tree and Nx target, classified by the strongest boundary it touches,
per [Test Boundaries and Gates](../../../../repo-governance/development/quality/testing/test-boundaries-and-gates.md).
Every test is written before the code it proves, one red, green, and refactor cycle at a time (D9a).

## The Layers

- **Unit, `test:unit`.** Touches nothing outside the process: `run` receives a reader function and `StringIO` streams.
  Proves every type's constructor, rule, criterion, parse fault, rendering rule, and exit status.
- **Integration, `test:integration`.** Touches real files it creates under `tmp_path`, the shipped stream file, and the
  process's real standard streams. Proves that `main` reads a real file and writes the real standard output, and that
  the shipped stream is the brief's.
- **End-to-end, `test:e2e`.** Runs the program as its own process. Proves the public contract, byte for byte.

The unit run measures coverage and fails below 80% of lines, as it does today; `__main__.py` stays excluded. Strict
pyright runs in `test:quick` beside the tests, so a line mixing AED and BHD, or passing an `int` where a `Day` belongs,
fails the gate before any test runs (D14, D15).

## Support Shared by the Layers

- `tests/support/brief_stream.py` builds the brief's stream as `IncomingEvent` values in code, so a unit test never
  reads `challenge.csv`. The integration test for AC-05 proves the file and this builder agree.
- `tests/support/streams.py` has small builders, such as `credit("E1", day=1, amount="100.00")`, for the short streams
  the rule tests replay; each builds its values through the domain constructors, so a test cannot build an illegal one
  either.
- `tests/support/output_target.py` extracts the fenced `text` block from `OUTPUT_TARGET.md` at the repository root. Only
  the end-to-end layer calls it, since reading a file is a real boundary.

## Test Files

- `tests/unit/test_money.py` — places, positive amounts, one currency per sum, half-even rounding, the split and its
  floor, and the BHD fee (AC-12, AC-22, AC-34).
- `tests/unit/test_ids.py` — each identifier, day, and instalment count refusing a malformed value, and each marker's
  text (AC-34).
- `tests/unit/test_config.py` — the configuration refusing an illegal window or account list (AC-34).
- `tests/unit/test_stream_csv.py` — each parse fault with its message, and a valid stream (AC-03).
- `tests/unit/test_authorizations.py` — every pair of state and trigger against the table in
  [the domain model](001-domain-model.md), each unconfigured one leaving the state unchanged (AC-18, AC-19, AC-21).
- `tests/unit/test_processing.py` — duplicates, reused IDs, reversals and their targets, force-posts, and instalments
  (AC-14 to AC-17, AC-32, AC-33, AC-35).
- `tests/unit/test_end_of_day.py` — fees, refunds, interest, and capitalization, a test per step rule (AC-13, AC-20,
  AC-22, AC-31).
- `tests/unit/test_criteria.py` — one test per brief criterion, C1 to C8 (AC-06 to AC-13).
- `tests/unit/test_replay.py` — the driver: opening reports, days closing as booked days advance, late events.
- `tests/unit/test_report.py` — restated closings, authorization states, each rejection's error text, and the rows for
  steps that fire nothing (AC-10, AC-11, AC-15 to AC-17, AC-32, AC-35).
- `tests/unit/test_render.py` — each rendering rule on a small report; never the whole brief report, which would be a
  second copy of OUTPUT_TARGET.
- `tests/unit/test_cli.py` — every exit status in the contract, through `run` (AC-02 to AC-04, AC-36).
- `tests/unit/test_known_weakness.py` — the one strict expected failure (AC-23).
- `tests/integration/test_stream_file.py` — the shipped stream parses to the brief (AC-05).
- `tests/integration/test_main.py` — `main` on a real file, and on a missing one (AC-02).
- `tests/e2e/test_program.py` — the golden run against OUTPUT_TARGET, and the error paths (AC-01 to AC-04).

Each criterion test is named `test_c<N>_` and each rule test `test_amb_<nnn>_`, so MOVEMENT, REJECTED, and AMBIGUITIES
can cite one function by name (D12b), and a reader of the suite finds them with `pytest -k c2` or `-k amb_034`.

## A Test That Passes on Arrival

Some rules follow from code an earlier cycle wrote, such as a settlement above its hold once final settlements release
the whole hold. A test for such a rule can pass the first time it runs, and a pass before the change proves nothing.
Delivery handles it the same way every time: the RED item is left unticked with the disposition "passes on arrival"; the
executor breaks the code path the test names, watches the test fail on its assertion, restores it, and records that run
in place of the red; the GREEN item closes as "no production change". The Execution Record gets a line for each.

## The Criterion Tests

Each replays the brief's stream once and asserts only the figures its criterion is about. Its docstring quotes the
criterion from [challenge-raw.md](../../../../challenge-raw.md), states the verdict, and cites the AMB entries, so the
test reads as the proof of one REJECTED paragraph:

```python
def test_c2_e7_causes_three_fees_all_value_dated_day_5() -> None:
    """C2, refused: "E7 causes exactly one overdraft fee to be assessed, on Day 2."

    E7 makes Days 2, 4, and 5 negative, so three fees fire at the close of Day 5, each value-dated Day 5 (AMB-002,
    AMB-003, AMB-016).
    """
    day_5 = replay(brief_stream(), CHALLENGE)[5]

    assert fee_markers(day_5) == ("FEE-001-D2@D5", "FEE-001-D4@D5", "FEE-001-D5@D5")
```

## The Known Weakness

`tests/unit/test_known_weakness.py` holds the brief's "One failing test against your own design, inline-annotated with
what it reveals" (AMB-018, AMB-031, D6). It stays outside the criterion and rule tests because the behaviour it asks for
does not exist.

```python
# KNOWN WEAKNESS (AMB-018): a hold never expires.
# What it reveals: an approved authorization that is never settled keeps its hold, and so keeps reducing the
# available balance, for as long as the ledger runs. Visa's longest authorization-to-clearing time frame is 30
# calendar days (Visa Business News AI13522, effective 13 April 2024), so by Day 32 no network would still honour
# Auth-A, yet this ledger still reserves its AED 200.00.
# The fix: a hold lifetime after which the end of day fires a hold-expiry event that releases the hold.
@pytest.mark.xfail(strict=True, reason="AMB-018: holds never expire, so an unsettled hold is never released")
def test_known_weakness_an_unsettled_hold_never_lapses() -> None:
    day_32 = replay(auth_a_never_settled(), replace(CHALLENGE, last_day=Day(32)))[32]

    assert day_32.available[ACC_001] == day_32.closing[ACC_001]
```

Auth-A is approved on Day 1, so Day 31 is the thirtieth day after it and Day 32 the first on which no network would
still honour it. The suite reports the test as `XFAIL` and passes. Once a hold-expiry event exists it passes, pytest
reports `XPASS(strict)`, and the run fails until the marker is removed. The guard on every test target already refuses a
non-strict expected failure, and no other test is ever marked this way.

## Proving Each Harness Can Fail

Per [Cycle and Evidence][cycle], a new harness proves it can fail before it is trusted:

- **The golden test.** Change one character in a copy of the expected text, run it, watch it fail with a diff, restore.
- **The integration reader.** Point `main` at a file missing a column, watch the test's assertion on exit 2 fail when
  the parser is stubbed to succeed, restore.
- **The strict expected failure.** Temporarily make holds lapse after 30 days in the working tree, never committed, run
  `test:unit`, watch `XPASS(strict)` fail the run, restore.
- **The type gate.** Add a line summing an `Aed` and a `Bhd` to a scratch test, watch `typecheck` fail, remove it.

Each record goes into the item's evidence in [delivery](../delivery.md).

[cycle]: ../../../../repo-governance/development/quality/testing/test-driven-development/001-cycle-and-evidence.md
