# Fees and Interest

This page explains how the ledger's day close charges and refunds overdraft fees, accrues and adjusts interest, and
capitalizes it, as the code does it, with the brief's stream as the worked case. The rules are decided in
[AMBIGUITIES](../../AMBIGUITIES.md), and the arithmetic behind every fixed figure is stated once, in
[MOVEMENT's "Why the Fixed Figures Hold"](../../MOVEMENT.md#why-the-fixed-figures-hold); every figure here is quoted
from there or from [OUTPUT_TARGET](../../OUTPUT_TARGET.md). The [code walkthrough](code-walkthrough.md#a-days-close)
shows where the close sits in a run.

## Booked Day and Value Date

Every event carries two days. The **booked** day is when the ledger receives it, and decides which day's processing it
belongs to; the **value date** is the day its money counts from, and decides which closings it moves. Three events in
the brief's stream have a value date earlier than the day they are processed on:

```text
value day ->          1        2        3        4        5        6
                      |        |        |        |        |        |
E7   debit 620.00              o<-------------------------*               value Day 2, processed Day 5
E9   reverses E7               o<----------------------------------*      value Day 2, processed Day 6
E10  credit 10.000                                        o<-------*      value Day 5, processed Day 6
fees for Days 2, 4, 5                                     *               generated and value-dated Day 5
refunds of those fees                                              *      generated and value-dated Day 6

o = the value date: the day its money counts from       * = the day it is processed, or generated at close
```

A closing for day N sums every event whose value date is N or earlier, whenever it arrived. So E7, arriving on Day 5,
changes the closings of Days 2, 3, and 4, which had already been printed, and E9, arriving on Day 6, changes them back.
The fees and refunds the ledger generates are value-dated the day they are generated, never an earlier day (AMB-003,
AMB-004), so they reach only closings from that day on.

## Each Day's Closing, as Known at Each Day's End

Because a late event changes earlier closings, the question "what was Day 2's closing?" has a different answer at the
end of each day. For ACC-001, in AED, with each value day down the side and each day's end across the top:

```text
value day   end of Day 1   end of Day 2   end of Day 3   end of Day 4   end of Day 5   end of Day 6
---------   ------------   ------------   ------------   ------------   ------------   ------------
Day 1       250.00         250.00         250.00         250.00         250.00         250.00
Day 2                      250.00         250.00         250.00         −370.00 r      250.00 r
Day 3                                     650.00         650.00         30.00 r        650.00 r
Day 4                                                    285.00         −335.00 r      285.00 r
Day 5                                                                   −410.00        210.00 r
Day 6                                                                                  285.76

r = printed as restated in that day's report (AMB-022)
```

Each report prints the diagonal as its closing and the cells marked `r` as restated rows; a cell not marked is the
closing already printed, unchanged. ACC-002, in BHD, closes at 0.000 through the end of Day 5, since E10 arrives late;
at the end of Day 6 its Day 5 is restated to 10.000 and Day 6 closes at 10.008 (AMB-015).

Day 5's closing is −410.00 at the end of Day 5 and 210.00 at the end of Day 6, not 285.00: the three fees are
value-dated Day 5 and their refunds Day 6, so the fees still count on Day 5. That is why criterion 6 is refused
([REJECTED](../../REJECTED.md#c6--everything-returning-to-its-pre-e7-value-after-e9)).

## Step 1: Fee Re-Evaluation

`AccountIn.assess_fees(today, first_day)` in [`account.py`][account] runs at every close and walks every day of the
window so far, from the first to today, oldest first (AMB-002). For each day it reads two things:

- **the fee in force for that day**, from `_map_fees_in_force`: a fee charged for the day, until a refund names it or a
  reversal undoes it, and again once a reversal undoes that refund (AMB-035);
- **whether the day closes below zero**, from `_is_closing_below_zero`, on the account as this close has grown it so
  far, so a fee generated for an earlier day in the same walk counts in the later days' closings (AMB-011).

Then one of four things happens:

| The day closes | A fee is in force for it | The step                                         |
| -------------- | ------------------------ | ------------------------------------------------ |
| below zero     | no                       | charges a `Fee`, value-dated today, for that day |
| below zero     | yes                      | nothing: once per day per account                |
| at or above 0  | yes                      | refunds it with a `FeeRefund`, value-dated today |
| at or above 0  | no                       | nothing                                          |

Each day of an account moves between two states, and the fee step is what moves it at a close:

```text
                     charge a Fee: a close finds day N below zero
                     or a reversal undoes the refund, putting the fee back
          +-----------------------------------------------------------------+
          |                                                                 v
  +-----------------+                                              +-----------------+
  | no fee in force |                                              | a fee in force  |--+ a close finds day N
  |    for day N    |                                              |   for day N     |  | still below zero:
  +-----------------+                                              +-----------------+<-+ nothing
          ^                                                                 |
          +-----------------------------------------------------------------+
                     refund it with a FeeRefund: a close finds day N at or above zero
                     or a reversal undoes the fee; the next close judges day N again
```

A fee's ID names its kind, account, the day it is for, and the day it is generated: `FEE-001-D2@D5` is ACC-001's fee for
Day 2, generated at the close of Day 5 (AMB-024). The amount comes from the account's own currency:
`compute_overdraft_fee` gives AED 25.00, or for a BHD account BHD 2.560, which is AED 25.00 converted at AMB-027's fixed
rate.

**The close of Day 5**, after E7 and E8:

```text
day   closing it reads                        fee in force   result
---   -------------------------------------   ------------   ---------------------------------
1     250.00                                  no             nothing
2     −370.00                                 no             FEE-001-D2@D5, value-dated Day 5
3     30.00                                   no             nothing: the new fee is dated Day 5
4     −335.00                                 no             FEE-001-D4@D5
5     −385.00, the two new fees included      no             FEE-001-D5@D5; Day 5 closes −410.00
```

Day 5 reads −385.00 because the fees for Days 2 and 4, value-dated Day 5, count in Day 5's closing (AMB-011); it is
negative either way, −335.00 without them.

**The close of Day 6**, after E9:

```text
day   closing it reads                        fee in force   result
---   -------------------------------------   ------------   ---------------------------------
1     250.00                                  no             nothing
2     250.00                                  yes            REFUND-001-D2@D6, value-dated Day 6
3     650.00                                  no             nothing
4     285.00                                  yes            REFUND-001-D4@D6
5     210.00, the three fees included         yes            REFUND-001-D5@D6
6     285.00, the three refunds included      no             nothing
```

No new fee is charged, so the report prints "no new fee assessed". Day 5's refund is judged on a closing that still
includes Day 5's own fee, since nothing removes a fee from the closing it is judged on. Here it makes no difference,
210.00 is well above zero, but a day whose events alone would close between zero and the fee would keep its fee: that is
the cost AMB-011 accepts, a fee that can keep an account negative that its own events lifted. Run on the real ledger: a
debit of 10.00 on Day 5 closes it at −10.00, and the close charges `FEE-001-D5@D5`, so −35.00. A credit of 20.00 booked
Day 6 and value-dated Day 5 brings the day's events to +10.00, but the closing with its fee to −15.00, so no refund is
generated; Day 6 closes at −15.00 too and is charged its own fee.

A fee is never deleted. When E9 makes Days 2, 4, and 5 non-negative, each fee stays in the log and a refund event undoes
it (AMB-004). A fee reversed directly, rather than refunded, is out of force at once, and the next close judges its day
again: a day still negative is charged again under a new ID, and a day no longer negative is left alone (AMB-035); the
[tutorial](../tutorials/change-the-stream-and-watch.md) runs one.

## Step 2: Interest

`AccountIn.accrue_interest(today, first_day)` walks the same days. For each day it works out one number, in
`_compute_interest_change`:

```text
change = daily interest on the day's base  -  interest already generated for that day

daily interest   = base x 0.0004, rounded half-even to the currency's places, or 0 if the base is not positive
the day's base   = its closing, less any capitalization value-dated that day (AMB-023)
already generated = the day's accruals and adjustments, signed, less any reversed
```

A change of zero generates nothing. Otherwise it is recorded as an `InterestAccrual` when the day is today, or as an
`InterestAdjustment` for an earlier day, up or down, value-dated today (AMB-005). Interest never joins the ledger
balance until it is capitalized (AMB-007), so no closing in the table above includes it before Day 6.

Every interest event ACC-001 generates, by the day it is for and the close that generated it, as OUTPUT_TARGET prints
them:

```text
for day   close 1   close 2   close 3   close 4   close 5   close 6   net
-------   -------   -------   -------   -------   -------   -------   ----
Day 1     +0.10                                                        0.10
Day 2               +0.10                         −0.10     +0.10      0.10
Day 3                         +0.26               −0.25     +0.25      0.26
Day 4                                   +0.11     −0.11     +0.11      0.11
Day 5                                             none      +0.08      0.08
Day 6                                                       +0.11      0.11
                                                                      -----
                                                            capitalized 0.76
```

- The first entry in each row is that day's own accrual, on the closing as known then.
- At the close of Day 5, E7 has lowered Days 2 to 4: Day 2's due interest is 0.00 and Day 3's 0.01 on 30.00, so each
  gets the difference as an adjustment, and Day 5 itself, closing at −410.00, accrues nothing.
- At the close of Day 6, E9 has restored them, so each gets the difference back, and Day 5, now 210.00, earns 0.08,
  recorded as an adjustment because Day 5 is no longer today.

ACC-002 generates two events at the close of Day 6, when E10 arrives: an adjustment of 0.004 for Day 5 and an accrual of
0.004 for Day 6, each on 10.000.

Correcting with new events, rather than recomputing the total at the end, keeps each day's printed accrual final while
the total still follows the balances the ledger finally holds: 0.68 as known, less 0.46 on Day 5, plus 0.54 on Day 6, is
0.76 (AMB-005). The rounding mode is half-even, and no unrounded amount in this stream is a tie (AMB-006).

## Step 3: Capitalization

`AccountIn.capitalize_interest(today)` runs only on a capitalization day, Day 6 here. `_compute_accrued` sums the
account's interest events, net of their directions and of any reversed, less any earlier capitalization, and a total
above zero is credited as one `Capitalization`, value-dated today: `CAP-001@D6` for AED 0.76 and `CAP-002@D6` for BHD
0.008.

The capitalized amount is the sum of the rounded events in the log, so the rounded dailies sum exactly to it by
construction, as the brief requires, and no remainder can exist to discard (criterion 8, refused in
[REJECTED](../../REJECTED.md#c8--discarding-a-rounding-remainder)). The report's "accrued Days 1 to 6" comes from
`list_accrued_days`, the days whose interest events since the previous capitalization do not net to zero.

Capitalization runs last so it pays every accrual in the window, and a day's interest never counts its own
capitalization (AMB-023): ACC-001's Day 6 closes at 210.00, plus the three refunds of 25.00, plus 0.76, which is 285.76.

## Where the Tests Pin This

| Behaviour                                    | Test                                                               |
| -------------------------------------------- | ------------------------------------------------------------------ |
| E7's three fees, all value-dated Day 5       | `test_c2_e7_causes_three_fees_all_value_dated_day_5`               |
| E9 restores Days 2 to 4, refunds the fees    | `test_c6_e9_restores_days_2_to_4_and_refunds_the_fees`             |
| a day still negative is not charged again    | `test_amb_011_a_day_still_negative_is_not_charged_again`           |
| a fee counts in the closings after it        | `test_amb_011_a_fee_counts_in_the_closings_after_it`               |
| a reversed fee is charged again if still due | `test_amb_035_a_fee_reversed_on_a_negative_day_is_charged_again`   |
| a changed closing adjusts its interest       | `test_amb_005_a_changed_closing_adjusts_its_interest`              |
| half-even rounding                           | `test_amb_006_daily_interest_rounds_half_even`                     |
| a day's interest skips its capitalization    | `test_amb_023_a_days_interest_never_counts_its_own_capitalization` |
| capitalization sums the interest events      | `test_c8_capitalization_equals_the_sum_of_interest_events`         |
| Day 6 closes at 285.76, not 285.79           | `test_c6_day_6_closes_at_285_76_not_285_79`                        |
| a BHD account is charged BHD 2.560           | `test_amb_027_a_bhd_account_is_charged_bhd_2_560`                  |

The fee and interest tests are in [`test_account.py`][test-account], the criteria in [`test_stream.py`][test-stream],
and the rounding in [`test_money.py`][test-money].

[account]: ../../apps/account-ledger-cli/src/account_ledger/domain/account/account.py
[test-account]: ../../apps/account-ledger-cli/tests/unit/domain/account/test_account.py
[test-stream]: ../../apps/account-ledger-cli/tests/unit/application/test_stream.py
[test-money]: ../../apps/account-ledger-cli/tests/unit/domain/model/test_money.py
