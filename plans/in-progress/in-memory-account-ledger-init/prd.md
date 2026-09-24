# Product Requirements

What the finished ledger must do, stated as criteria a test can fail. The criteria accept this plan; they are written in
Gherkin for readability only and are never executed as Gherkin, since the suite is plain pytest (D12). Each names the
pytest test that proves it once the plan is executed, and [delivery](delivery.md) cites them by identifier.

## Personas

- **The assessor**, who clones the public repository, runs one command, reads the printed report beside
  [OUTPUT_TARGET](../../../OUTPUT_TARGET.md), and asks for the test behind any figure.
- **The candidate**, who must point at that test and explain it without AI during a 45-minute defense.
- **A maintainer**, who later changes a rule and relies on the suite to say what broke.

## User Stories

- As the assessor, I run the command-line program on the brief's stream and see each day's closing ledger balance, fee
  assessments, authorization states, and errors, so that I can check the replay against the brief.
- As the assessor, I run the test suite and see every criterion verdict and every stated rule proven, and one strict
  expected failure that names the design's weakness.
- As the candidate, I open the test for any criterion and read, in one function, the stream it replays and the figures
  it asserts.
- As a maintainer, I feed the program a stream of my own and get either the report or a diagnostic naming the line at
  fault, never a traceback.

## Acceptance Criteria

Figures are those [MOVEMENT](../../../MOVEMENT.md) fixes. "The brief's stream" is E1 to E10 as
[challenge-raw.md](../../../challenge-raw.md) lists them, held in `apps/account-ledger-cli/streams/challenge.csv`.

### The Replay and the Program

#### AC-01 — The replay prints the target report

```gherkin
Scenario: Replaying the brief's stream prints OUTPUT_TARGET exactly
  Given the file "streams/challenge.csv"
  When the program runs as its own process with that file as its only argument
  Then standard output equals the fenced block in OUTPUT_TARGET.md, byte for byte
  And standard error is empty
  And the exit status is 0
```

Test: `test_the_brief_replay_prints_output_target`, in `tests/e2e/test_program.py`.

#### AC-02 — A missing stream file is a failure to complete

```gherkin
Scenario: The stream file does not exist
  Given no file at "streams/missing.csv"
  When the program runs with "streams/missing.csv" as its only argument
  Then standard error reads "error: cannot read streams/missing.csv: no such file"
  And standard output is empty
  And the exit status is 2
```

Tests: `test_a_missing_stream_file_exits_2` end to end, `test_main_reads_a_real_file_and_reports_a_missing_one` at the
integration layer, and `test_an_unreadable_file_exits_2` through `run`.

#### AC-03 — A malformed stream names the line at fault

```gherkin
Scenario: An amount that is not a decimal
  Given a stream whose second data row, on line 3, has the amount "12.00x"
  When the program runs with that stream
  Then standard error reads "error: line 3: amount '12.00x' is not a decimal number"
  And standard output is empty
  And the exit status is 2

Scenario: A row naming an account the ledger does not hold
  Given a stream whose first data row, on line 2, names the account "ACC-009"
  When the program runs with that stream
  Then standard error reads "error: line 2: account 'ACC-009' is not held by this ledger"
  And standard output is empty
  And the exit status is 2
```

The second scenario is AMB-014's input fault (D21): the row never becomes an event, so nothing is logged.

Tests: `test_a_malformed_amount_names_its_line` and `test_an_unheld_account_names_its_line` end to end, and each fault
of tech-docs 003 through its `tests/unit/test_stream_csv.py` test.

#### AC-04 — Wrong usage is a failure to complete

```gherkin
Scenario: The program runs with no argument
  When the program runs with no arguments
  Then standard error reads "usage: account-ledger-cli <stream.csv>"
  And the exit status is 2
```

Tests: `test_no_argument_prints_usage_and_exits_2` end to end, and `test_no_argument_is_a_usage_error_exiting_2` through
`run`.

#### AC-05 — The stream file holds the brief's events

```gherkin
Scenario: The shipped stream matches the brief
  When "streams/challenge.csv" is read from disk and parsed
  Then it yields E1 to E10 in the brief's order, each with the brief's booked day, type, account, amount, value day,
    and reference, and E10 carries 3 instalments
```

Tests: `test_the_shipped_stream_is_the_brief`, in `tests/integration/test_stream_file.py`, and
`test_a_valid_stream_parses_to_its_events`.

### The Brief's Criteria

Each criterion keeps its brief identifier. A refused criterion is proven by a test of what the ledger does instead.

#### AC-06 — C1, accepted: Day 2 closes at −370.00 at the end of Day 5, before the fees

```gherkin
Scenario: The Day 2 closing as known at the end of Day 5
  Given the brief's stream
  When it is replayed through the end of Day 5
  Then the Day 2 closing ledger balance of ACC-001, counting no fee event, is AED −370.00
```

Test: `test_c1_day_2_closes_at_minus_370_at_end_of_day_5_before_fees`.

#### AC-07 — C2, refused: E7 causes three fees, all value-dated Day 5

```gherkin
Scenario: The fees E7 causes
  Given the brief's stream
  When it is replayed through the end of Day 5
  Then ACC-001 carries FEE-001-D2@D5, FEE-001-D4@D5, and FEE-001-D5@D5, each AED 25.00 and value-dated Day 5
  And no fee is value-dated Day 2
```

Test: `test_c2_e7_causes_three_fees_all_value_dated_day_5`.

#### AC-08 — C3, accepted: Auth-A's settlement is accepted

```gherkin
Scenario: E5 settles Auth-A
  Given the brief's stream
  When it is replayed through E5
  Then E5 is accepted, ACC-001 is debited AED 185.00 value-dated Day 4, and Auth-A is settled with no hold left
```

Test: `test_c3_auth_a_settlement_is_accepted_and_releases_the_hold`.

#### AC-09 — C4, refused: E6 is honoured as a force-post

```gherkin
Scenario: A settlement with no authorization
  Given the brief's stream
  When it is replayed through E6
  Then E6 is accepted as a force-post, ACC-001 is debited AED 180.00 value-dated Day 4, and no hold is released
  And Day 4 closes at AED 285.00
```

Test: `test_c4_e6_is_force_posted_for_180`.

#### AC-10 — C5, refused: Auth-B is declined; a hold reduces available balance only

```gherkin
Scenario: Auth-B is declined
  Given the brief's stream
  When it is replayed through E8
  Then Auth-B is declined, holds nothing, and moves no balance

Scenario: Auth-A's hold on Day 2
  Given the brief's stream
  When it is replayed through the end of Day 2
  Then ACC-001's ledger balance is AED 250.00 and its available balance is AED 50.00
```

Tests: `test_c5_auth_b_is_declined`, `test_c5_a_hold_reduces_available_balance_but_not_ledger_balance`.

#### AC-11 — C6, refused: E9 restores Days 2 to 4 but not everything

```gherkin
Scenario: E9 restores Days 2 to 4 and refunds the fees
  Given the brief's stream
  When it is replayed through the end of Day 6
  Then Days 2, 3, and 4 restate to AED 250.00, 650.00, and 285.00
  And the three fees stay in the log, each undone by REFUND-001-D2@D6, REFUND-001-D4@D6, or REFUND-001-D5@D6

Scenario: Day 5 keeps its fees, so Day 6 does not return to its pre-E7 value
  Given the brief's stream
  When it is replayed through the end of Day 6
  Then Day 5 restates to AED 210.00 and ACC-001 closes Day 6 at AED 285.76, not 285.79
```

Tests: `test_c6_e9_restores_days_2_to_4_and_refunds_the_fees`, `test_c6_day_6_closes_at_285_76_not_285_79`.

#### AC-12 — C7, refused: E10 posts 3.333, 3.333, and 3.334

```gherkin
Scenario: The E10 instalments
  Given the brief's stream
  When E10 is processed
  Then ACC-002 is credited E10-1 BHD 3.333, E10-2 BHD 3.333, and E10-3 BHD 3.334, each value-dated Day 5
  And the three sum to BHD 10.000
```

Test: `test_c7_e10_posts_3_333_3_333_3_334`.

#### AC-13 — C8, refused: capitalization equals the sum of the interest events

```gherkin
Scenario: The Day 6 capitalization
  Given the brief's stream
  When it is replayed through the end of Day 6
  Then CAP-001@D6 is AED 0.76 and CAP-002@D6 is BHD 0.008
  And each equals the sum of that account's interest accrual and adjustment events, leaving no remainder
```

Test: `test_c8_capitalization_equals_the_sum_of_interest_events`.

### Rules the Brief's Stream Never Triggers

Each rule is a resolution in [AMBIGUITIES](../../../AMBIGUITIES.md) that this stream does not exercise (D3). Each test
replays a short stream of its own, built in the test. AC-31 to AC-37 were added after the others and keep their numbers.
Where a criterion states an error text, its named test asserts the log entry, and
`test_amb_014_a_rejected_event_prints_as_that_days_error`, one case per rejection, asserts the text the day prints.

#### AC-14 — AMB-034: the same event twice is logged as a duplicate with no effect

```gherkin
Scenario: A credit delivered twice
  Given a stream with E1, a credit of AED 100.00 to ACC-001 value-dated Day 1, listed twice with identical content
  When it is replayed through the end of Day 1
  Then the log holds E1 accepted and E1 again as a duplicate
  And ACC-001 closes Day 1 at AED 100.00
  And Day 1's errors read none
```

Test: `test_amb_034_a_repeated_event_is_logged_as_a_duplicate_with_no_effect`.

#### AC-15 — AMB-034: the same ID with different content is refused

```gherkin
Scenario: A second E1 with another amount
  Given a stream with E1, a credit of AED 100.00, then E1 again as a credit of AED 90.00
  When it is replayed through the end of Day 1
  Then ACC-001 closes Day 1 at AED 100.00
  And Day 1's errors for ACC-001 read "E1 refused: ID already used with different content"
```

Test: `test_amb_034_a_reused_id_with_different_content_is_refused`.

#### AC-16 — AMB-028: a second reversal of the same event is refused

```gherkin
Scenario: E7 reversed twice
  Given a stream with a debit E7, its reversal E9, and a later reversal E12 of E7
  When it is replayed
  Then E12 is refused and moves no balance
  And that day's errors for ACC-001 read "E12 refused: E7 is already reversed by E9"
```

Test: `test_amb_028_a_second_reversal_of_the_same_event_is_refused`.

#### AC-17 — AMB-028: a reversal of a reversal is refused

```gherkin
Scenario: Reversing E9
  Given a stream with a debit E7, its reversal E9, and a reversal E12 of E9
  When it is replayed
  Then E12 is refused and moves no balance
  And that day's errors for ACC-001 read "E12 refused: E9 is a reversal"
```

Test: `test_amb_028_a_reversal_of_a_reversal_is_refused`.

#### AC-18 — AMB-029: a settlement against a declined authorization is a force-post

```gherkin
Scenario: Settling a declined authorization
  Given ACC-001 at AED 50.00 and an authorization Auth-X of AED 90.00 that is declined
  When a settlement of Auth-X for AED 40.00 arrives
  Then it is accepted as a force-post, debits AED 40.00, and Auth-X stays declined
```

Test: `test_amb_029_a_settlement_against_a_declined_authorization_is_force_posted`.

#### AC-19 — AMB-029: a second settlement after a final one is a force-post

```gherkin
Scenario: Settling an already-settled authorization
  Given Auth-A settled finally for AED 185.00
  When a new settlement of Auth-A for AED 10.00 arrives under a new event ID
  Then it is accepted as a force-post, debits AED 10.00, and releases no hold
```

Test: `test_amb_029_a_settlement_after_a_final_one_is_force_posted`.

#### AC-20 — AMB-030: a settlement above its hold debits in full

```gherkin
Scenario: Settling above the hold
  Given ACC-001 at AED 250.00 with Auth-A approved for a hold of AED 200.00
  When Auth-A settles for AED 260.00
  Then ACC-001 is debited AED 260.00, the hold is released, and the ledger balance is AED −10.00
  And that day's close assesses an overdraft fee for it
```

Test: `test_amb_030_a_settlement_above_its_hold_debits_in_full`.

#### AC-21 — AMB-013: a non-final settlement keeps the rest of the hold

```gherkin
Scenario: A partial capture
  Given Auth-A approved for a hold of AED 200.00
  When Auth-A settles for AED 120.00, marked as not final
  Then ACC-001 is debited AED 120.00, Auth-A is partially settled, and AED 80.00 stays on hold
  And a later final settlement of AED 80.00 settles Auth-A for AED 200.00 and releases the rest

Scenario: A partial capture that reaches the hold
  Given Auth-A partially settled for AED 120.00 with AED 80.00 on hold
  When Auth-A settles for AED 80.00, marked as not final
  Then Auth-A is settled, and no hold is left
```

Tests: `test_amb_013_a_non_final_settlement_keeps_the_rest_of_the_hold`,
`test_amb_013_a_partial_capture_reaching_the_hold_settles`. Built last, under the fallback in [delivery](delivery.md).

#### AC-22 — AMB-027: a BHD account is charged BHD 2.560

```gherkin
Scenario: ACC-002 goes negative
  Given ACC-002 at BHD 0.000
  When a debit of BHD 1.000 value-dated Day 1 is replayed through the end of Day 1
  Then ACC-002 is charged FEE-002-D1@D1 of BHD 2.560 and closes Day 1 at BHD −3.560
```

Test: `test_amb_027_a_bhd_account_is_charged_bhd_2_560`.

#### AC-31 — AMB-035: a fee reversed on a day still negative is charged again

```gherkin
Scenario: Reversing a fee
  Given ACC-001 debited AED 100.00 value-dated Day 1, so the close of Day 1 fires FEE-001-D1@D1
  When E2, booked Day 2 and value-dated Day 2, reverses FEE-001-D1@D1
  Then E2 is accepted, and the close of Day 2 fires FEE-001-D1@D2, since Day 1 still closes below zero
```

Test: `test_amb_035_a_fee_reversed_on_a_negative_day_is_charged_again`.

#### AC-32 — AMB-035: a reversal of an unknown event or one that moved no money is refused

```gherkin
Scenario Outline: Reversing what cannot be reversed
  Given a stream in which <target> is <what>
  When E12 reverses <target>
  Then E12 is refused and moves no balance
  And that day's errors for ACC-001 read "<text>"

  Examples:
    | target | what                       | text                                 |
    | E99    | not in the log             | E12 refused: E99 is not in the log   |
    | E8     | a declined authorization   | E12 refused: E8 moved no money       |
    | E3     | an approved authorization  | E12 refused: E3 moved no money       |
```

Tests: `test_amb_035_a_reversal_of_an_unknown_event_is_refused`,
`test_amb_035_a_reversal_of_an_event_that_moved_no_money_is_refused`.

#### AC-33 — AMB-035: reversing a credit in instalments undoes every instalment

```gherkin
Scenario: Reversing E10
  Given the brief's E10, credited to ACC-002 in three instalments value-dated Day 5
  When a reversal of E10 value-dated Day 5 is replayed
  Then ACC-002's Day 5 closing is BHD 0.000
```

Test: `test_amb_035_reversing_a_credit_in_instalments_undoes_every_instalment`.

#### AC-35 — AMB-035: money already undone cannot be undone again

```gherkin
Scenario Outline: Reversing what is already undone
  Given a stream in which <undoer> <how>
  When E12 reverses <target>
  Then E12 is refused and moves no balance
  And that day's errors for the account read "E12 refused: <part> is already undone by <undoer>"

  Examples:
    | undoer           | how                   | target        | part          |
    | E11              | reverses E10          | E10-1         | E10-1         |
    | E11              | reverses E10-1        | E10           | E10-1         |
    | REFUND-001-D2@D6 | refunds FEE-001-D2@D5 | FEE-001-D2@D5 | FEE-001-D2@D5 |
```

Test: `test_amb_035_money_already_undone_cannot_be_undone_again`.

#### AC-37 — AMB-008, AMB-009, AMB-010: how an authorization is decided

```gherkin
Scenario: A credit value-dated in the future does not count
  Given ACC-001 holds AED 0.00, and a credit of AED 100.00 booked Day 2 and value-dated Day 3
  When an authorization of AED 50.00 is booked and value-dated Day 2
  Then it is declined

Scenario: A later credit the same day does not rescue a decline
  Given ACC-001 holds AED 0.00 and an authorization of AED 50.00 on Day 2 is declined
  When a credit of AED 100.00 value-dated Day 2 follows it on Day 2
  Then the authorization stays declined at the end of Day 2

Scenario: A hold counts from its authorization's value date
  Given ACC-001 holds AED 100.00, and an authorization of AED 40.00 booked Day 2 and value-dated Day 3
  When the day reports are read
  Then the available balance is AED 100.00 at the end of Day 2, and AED 60.00 at the end of Day 3
```

Tests: `test_amb_008_a_future_dated_credit_does_not_count_for_an_authorization`,
`test_amb_009_a_later_credit_the_same_day_does_not_rescue_a_decline`, `test_amb_010_a_hold_counts_from_its_value_date`.

### The Command Line

#### AC-36 — A failure inside the program, a closed pipe, and an interrupt

```gherkin
Scenario: The core raises an unexpected exception
  When run is called with a stream whose replay raises
  Then standard error reads "error: internal failure: " and the exception's type, with no traceback
  And the exit status is 2

Scenario: Standard output closes early
  When the report is written to a stream that raises BrokenPipeError
  Then standard error is empty and the exit status is 141

Scenario: The program is interrupted
  When the replay raises KeyboardInterrupt
  Then the exit status is 130
```

Tests: `test_an_internal_failure_exits_2_without_a_traceback`, `test_a_closed_pipe_exits_141_quietly`,
`test_an_interrupt_exits_130`.

### The Domain Types

#### AC-34 — No illegal value can be built (D14 to D18)

```gherkin
Scenario: The constructors refuse illegal values
  When an AED value with three places, an amount of zero, a day of −1, an account ID "ACC-1", or an instalment count of
    1 is constructed
  Then each constructor refuses it, and each parse returns its typed fault

Scenario: The type checker refuses mixed currencies
  When strict pyright checks a line adding an Aed to a Bhd
  Then it reports an error, and the typecheck target fails
```

Tests: `test_aed_refuses_more_than_two_places`, `test_an_amount_must_be_above_zero`,
`test_aed_and_bhd_values_never_combine`, `test_ledger_config_refuses_an_inverted_window`, and one
`test_<type>_refuses_a_malformed_value` per type in `test_ids.py`; the second scenario is the type-gate proof in
tech-docs 004.

### The Known Weakness

#### AC-23 — AMB-018, AMB-031: holds never expire, recorded as a strict expected failure

```gherkin
Scenario: The suite carries exactly one strict expected failure
  When the unit suite runs
  Then test_known_weakness_an_unsettled_hold_never_lapses reports XFAIL, and the run passes
  And the test replays Auth-A approved on Day 1, never settled, through Day 32, and asserts the hold has lapsed
  And its inline annotation names the weakness and cites Visa's 30-calendar-day maximum
```

### Documents and Governance

#### AC-24 — The deliverable documents agree with the code

```gherkin
Scenario: Every criterion and rule names its test
  When MOVEMENT, REJECTED, and AMBIGUITIES are read
  Then each criterion names a test function that exists in the suite
  And each AMBIGUITIES entry that states what the ledger does names one, as tech-docs 004 maps them
  And ACCEPTANCE_CRITERIA.feature no longer exists
  And WORKLOG.md holds an entry, stamped with its real times, for each phase of this plan
```

#### AC-25 — The README says how to run the suite and read the output

```gherkin
Scenario: The brief's README deliverable
  When the root README is read
  Then it gives the command that prints the report, the commands that run each test layer, and how to read each of the
    three tables a day prints
```

#### AC-26 — The architecture is an as-built C4 model

```gherkin
Scenario: The architecture document
  When specs/apps/account-ledger/cli/architecture.md is read
  Then it holds a system context, containers, components, code, and a dynamic view of one day, each as a plain-text
    diagram, and every component it names exists in the code
```

#### AC-27 — The trade-offs document covers the brief's four sections

```gherkin
Scenario: The architecture trade-offs document
  When docs/explanation/architecture-trade-offs.md is read
  Then it has the sections "Append-only at scale", "Value-dated entries in production", "Authorization lifecycle", and
    "What you cut and why"
  And it restates neither the event stream nor the rule text of Part 1
```

#### AC-28 — No live rule requires Gherkin

```gherkin
Scenario: The retired behaviour-driven rules
  When the live governance, AGENTS.md, and project configuration are searched for a requirement to write or bind Gherkin
  Then none remains, and each adopted behaviour-driven module records its status and reason
```

#### AC-29 — The repository's own choices are recorded

```gherkin
Scenario: Adopter decisions this plan made
  When the governance is read
  Then it records typed result values (S3), the hand-written state machine (D8), the money, value-object, and state
    shapes (D14 to D18), the split test-first cycle (D9a), the baseline phase (D9b), phase gates (D9c), reopening an
    archived plan (D9d), and the completion gate (D11)
  And the application README records the command-line tier (D13)
```

#### AC-30 — Every gate passes

```gherkin
Scenario: The finished suite
  When test:quick, test:integration, test:e2e, and check:hygiene run
  Then each exits 0, and unit line coverage is at least 80%
```

## Product Scope

In scope: the ledger core, its CSV reader, its report renderer, and its command-line shell in `apps/account-ledger-cli`;
the plain-pytest suite at three layers; the as-built architecture; the assessment docs and README updates the code makes
necessary; the governance changes S3, D8, D9a to D9d, D11, D12, D12b, D12c, and D14 to D18 require; and the trade-offs
document at `docs/explanation/architecture-trade-offs.md`.

Out of scope: the Part 2 PDF, any hold lifetime (AMB-018), a machine-readable output mode (D13), and any change to a
figure MOVEMENT fixes. A figure the code disagrees with is a decision for the owner, never a silent edit.

## Product Risks

- **The golden test is brittle.** One changed space fails AC-01. That is intended: OUTPUT_TARGET is the exact text, and
  a failure prints a diff naming the line.
- **Error texts are new product surface.** AC-02, AC-03, AC-15 to AC-17, and AC-32 fix wording no brief states; the
  wording is chosen here (D22) so the executor does not invent it.
- **The Unicode minus.** OUTPUT_TARGET prints negative amounts with `−` (U+2212), not `-`; the renderer and the golden
  test must agree, and a terminal without UTF-8 would print it wrongly.
