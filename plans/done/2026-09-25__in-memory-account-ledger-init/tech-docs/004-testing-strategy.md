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
- `tests/support/streams.py` also holds `ACC_001: Account[Aed]` and `ACC_002: Account[Bhd]`, the configured accounts,
  whose `.id` keys every per-account field of a `DayReport`; `through(stream, event_id)`, the stream up to and including
  one event; `fee_markers(log)` and `interest_amounts(log, account)`, readers that turn log entries into plain tuples
  for an assertion; and `csv_text(rows)`, which writes rows under the header of the current stream version, so the
  header's ninth column in Phase 8 changes one helper, not every fixture.
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
  [the domain model](001-domain-model.md), each unconfigured one leaving the state unchanged, and the three decision
  rules: a future-dated credit does not count, a later credit the same day does not rescue a decline, and a hold counts
  from its value date (AC-18, AC-19, AC-21, AC-37).
- `tests/unit/test_processing.py` — duplicates, reused IDs, reversals and their targets, force-posts, and instalments
  (AC-14 to AC-17, AC-32, AC-33, AC-35).
- `tests/unit/test_end_of_day.py` — fees, refunds, interest, and capitalization, a test per step rule (AC-13, AC-20,
  AC-22, AC-31).
- `tests/unit/test_criteria.py` — one test per brief criterion, C1 to C8 (AC-06 to AC-13).
- `tests/unit/test_replay.py` — the driver: opening reports, days closing as booked days advance, late events, and the
  log at each day (AC-01).
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

## Every Resolution and Its Test

Each AMBIGUITIES entry that states what the ledger does names at least one test once Phase 9 runs (AMB-026, AC-24):

| Entry   | Test                                                                                                  |
| ------- | ----------------------------------------------------------------------------------------------------- |
| AMB-001 | `test_an_empty_stream_reports_the_opening_balances_for_day_0_to_6`                                    |
| AMB-002 | `test_c2_e7_causes_three_fees_all_value_dated_day_5`                                                  |
| AMB-003 | `test_c2_e7_causes_three_fees_all_value_dated_day_5`                                                  |
| AMB-004 | `test_c6_e9_restores_days_2_to_4_and_refunds_the_fees`                                                |
| AMB-005 | the two `test_amb_005_` tests                                                                         |
| AMB-006 | `test_amb_006_daily_interest_rounds_half_even`, `test_aed_refuses_more_than_two_places`               |
| AMB-007 | `test_c6_day_6_closes_at_285_76_not_285_79`, the golden run                                           |
| AMB-008 | `test_amb_008_a_future_dated_credit_does_not_count_for_an_authorization`                              |
| AMB-009 | `test_amb_009_a_later_credit_the_same_day_does_not_rescue_a_decline`                                  |
| AMB-010 | `test_amb_010_a_hold_counts_from_its_value_date`                                                      |
| AMB-011 | the two `test_amb_011_` tests                                                                         |
| AMB-012 | `test_c4_e6_is_force_posted_for_180`                                                                  |
| AMB-013 | `test_c3_…`, `test_amb_013_a_non_final_settlement_keeps_the_rest_of_the_hold`, and its reaching case  |
| AMB-014 | `test_c5_auth_b_is_declined`, `test_amb_014_a_rejected_event_prints_as_that_days_error`               |
| AMB-015 | `test_amb_015_a_late_event_is_processed_on_the_open_day`                                              |
| AMB-016 | `test_c2_e7_causes_three_fees_all_value_dated_day_5`                                                  |
| AMB-017 | `test_c7_e10_posts_3_333_3_333_3_334`                                                                 |
| AMB-018 | `test_known_weakness_an_unsettled_hold_never_lapses`                                                  |
| AMB-019 | `test_amb_019_every_known_authorization_is_listed_with_its_state`                                     |
| AMB-020 | `test_amb_020_ten_bhd_splits_3_333_3_333_3_334`, `test_more_instalments_than_minor_units_are_refused` |
| AMB-021 | `test_c5_auth_b_is_declined`, `test_c5_a_hold_reduces_available_balance_but_not_ledger_balance`       |
| AMB-022 | `test_amb_022_a_day_restates_each_earlier_closing_it_changed`                                         |
| AMB-023 | `test_amb_023_a_days_interest_never_counts_its_own_capitalization`, `test_c6_day_6_…`                 |
| AMB-024 | `test_a_marker_prints_its_kind_account_and_days`                                                      |
| AMB-025 | `test_amb_019_every_known_authorization_is_listed_with_its_state`, the golden run                     |
| AMB-026 | `test_the_brief_replay_prints_output_target`                                                          |
| AMB-027 | `test_amb_027_the_bhd_fee_is_2_560`, `test_amb_027_a_bhd_account_is_charged_bhd_2_560`                |
| AMB-028 | the two `test_amb_028_` tests                                                                         |
| AMB-029 | the two `test_amb_029_` tests                                                                         |
| AMB-030 | `test_amb_030_a_settlement_above_its_hold_debits_in_full`                                             |
| AMB-031 | `test_known_weakness_an_unsettled_hold_never_lapses`                                                  |
| AMB-033 | `test_amb_033_a_step_that_fires_nothing_reports_its_row`, the golden run                              |
| AMB-034 | the two `test_amb_034_` tests                                                                         |
| AMB-035 | the `test_amb_035_` tests                                                                             |

AMB-032 states how NUMBERS lists its constants, not what the ledger does, so no test covers it.

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
    log = replay(brief_stream(), CHALLENGE).log_at(Day(5))

    assert fee_markers(log) == ("FEE-001-D2@D5", "FEE-001-D4@D5", "FEE-001-D5@D5")
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
    day_32 = replay(auth_a_never_settled(), replace(CHALLENGE, last_day=Day(32))).report(Day(32))

    assert day_32.available[ACC_001.id] == day_32.closing[ACC_001.id]
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
