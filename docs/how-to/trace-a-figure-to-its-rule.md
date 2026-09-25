# Trace a Figure to Its Rule

Use this when someone points at a number in the report and asks why it is that number. Each figure leads, in four hops,
to the arithmetic that produces it, the decision behind it, the test that proves it, and the code that computes it:

```text
OUTPUT_TARGET          MOVEMENT                    AMBIGUITIES             the test               the code
the printed figure --> the day's tables and the --> the entry that decides --> named in the entry --> the function
                       "Why the Fixed Figures        the rule, with its        and in MOVEMENT's       the test calls,
                       Hold" arithmetic              options and reason        criteria                in src/
```

Run the commands from the repository root. On a fresh clone, run `npm install` and then
`npx nx run account-ledger-cli:install` once first, so the `uv run --no-sync` command in step 4 has its environment.

## Steps

1. **Find the figure in the report.** Open [OUTPUT_TARGET](../../OUTPUT_TARGET.md) and note the day and the table it is
   in: Events processed, EOD applied, or Closing summary. A figure in a `restated` row belongs to an earlier day,
   changed by a late event on the day it is printed under.

2. **Find its arithmetic in MOVEMENT.** Search [MOVEMENT](../../MOVEMENT.md) for the figure:

   ```bash
   grep -n "285.76" MOVEMENT.md
   ```

   The day's section has the same three tables with the rules named beside them, and
   [Why the Fixed Figures Hold](../../MOVEMENT.md#why-the-fixed-figures-hold) states the sum. A criterion that names the
   figure, C1 to C8, is in [Acceptance Criteria](../../MOVEMENT.md#acceptance-criteria) with its verdict.

3. **Read the entry that decides it.** Each bullet and criterion names its `AMB-` entries. Open each in
   [AMBIGUITIES](../../AMBIGUITIES.md): **Options** gives the other readings with the figures they would print, and
   **Rationale** says why this one was chosen. If the figure depends on a constant, such as the rate or the fee,
   [NUMBERS](../../NUMBERS.md) says where it comes from; if a criterion is refused, [REJECTED](../../REJECTED.md) says
   why.

4. **Find the test.** The entry's **Resolution** ends with the tests that prove it. Find the file:

   ```bash
   grep -rn "def test_c6_day_6_closes_at_285_76_not_285_79" apps/account-ledger-cli/tests
   ```

   Run that test alone, from the application's folder:

   ```bash
   cd apps/account-ledger-cli
   uv run --no-sync pytest tests/unit/application/test_stream.py -k 285_76 -q
   cd ../..
   ```

5. **Find the code.** The test builds a stream, processes it, and asserts on the result. The method that computes the
   figure is named in the [reading order](../../specs/apps/account-ledger/cli/architecture.md#reading-the-code); find
   its definition:

   ```bash
   grep -rn "def capitalize_interest" apps/account-ledger-cli/src
   ```

   The [code walkthrough](../explanation/code-walkthrough.md) and
   [fees and interest](../explanation/fees-and-interest.md) explain what each method does with the log.

## Worked Case: 285.76

ACC-001's Day 6 closing.

| Hop        | Where                                                   | What it says                                 |
| ---------- | ------------------------------------------------------- | -------------------------------------------- |
| report     | OUTPUT_TARGET, Day 6, Closing summary                   | Closing ledger balance 285.76                |
| arithmetic | MOVEMENT, "Day 6 closes at 285.76 and 10.008"           | refunds before interest, capitalization last |
| decision   | AMB-004, AMB-005, AMB-023; C6 refused in REJECTED       | refunds dated Day 6, so interest is 0.76     |
| test       | `test_c6_day_6_closes_at_285_76_not_285_79`             | Day 5 at 210.00, Day 6 at 285.76             |
| code       | `assess_fees`, `accrue_interest`, `capitalize_interest` | the three steps of `Ledger.close_day`        |

The answer in one breath: Day 5 closes at 210.00 because its three fees are value-dated Day 5 and their refunds Day 6;
the refunds bring Day 6 to 285.00; the twelve rounded interest events sum to 0.76; and capitalizing last adds it, so
285.76, not the 285.79 a ledger without E7 would print.

## Worked Case: FEE-001-D2@D5

The first overdraft fee on Day 5's EOD applied.

| Hop        | Where                                                | What it says                              |
| ---------- | ---------------------------------------------------- | ----------------------------------------- |
| report     | OUTPUT_TARGET, Day 5, EOD step 1                     | AED 25.00, for Day 2, value date Day 5    |
| arithmetic | MOVEMENT, "Fees for Days 2, 4, and 5"                | Day 2 closes at −370.00 once E7 arrives   |
| decision   | AMB-002, AMB-003                                     | each day re-judged, dated the day it runs |
| test       | `test_c2_e7_causes_three_fees_all_value_dated_day_5` | three fees, each value-dated Day 5        |
| code       | `AccountIn.assess_fees`, `FeeId`                     | the walk over Days 1 to 5                 |

## Worked Case: Auth-B Declined

Day 5's Authorizations row: `Auth-B declined, 90.00`.

| Hop        | Where                                       | What it says                              |
| ---------- | ------------------------------------------- | ----------------------------------------- |
| report     | OUTPUT_TARGET, Day 5, Closing summary       | Auth-B declined; Errors none              |
| arithmetic | MOVEMENT, "Auth-B"                          | 285.00 − 620.00 − 90.00 = −425.00         |
| decision   | AMB-008, AMB-009, AMB-016, AMB-019, AMB-021 | decided on arrival; a state, not an error |
| test       | `test_c5_auth_b_is_declined`                | Auth-B's state is declined                |
| code       | `_decide_authorization_entry`               | `compute_available`: −335.00 < 90.00      |
