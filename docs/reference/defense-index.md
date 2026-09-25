# Defense Index

The questions a reviewer is likely to ask about this ledger, each with the short answer and the document that owns the
full one. The answers quote the owning documents and add nothing to them; where a short answer and its owner seem to
differ, the owner is right. The documents it points to are the [brief](../../challenge-raw.md),
[AMBIGUITIES](../../AMBIGUITIES.md), [NUMBERS](../../NUMBERS.md), [REJECTED](../../REJECTED.md),
[MOVEMENT](../../MOVEMENT.md), [OUTPUT_TARGET](../../OUTPUT_TARGET.md), the
[architecture](../../specs/apps/account-ledger/cli/architecture.md), and the
[trade-offs](../explanation/architecture-trade-offs.md).

## The Eight Criteria

The brief's acceptance criteria, as [MOVEMENT](../../MOVEMENT.md#acceptance-criteria) numbers them and gives their
verdicts; each refusal is argued in [REJECTED](../../REJECTED.md). Each test is in
`apps/account-ledger-cli/tests/unit/`.

- **C1, accepted.** Day 2 closes at −370.00 at the end of Day 5, before any fee: 1,200.00 − 950.00 − 620.00. The fees
  are value-dated Day 5, so the figure is the same after them.
  `test_c1_day_2_closes_at_minus_370_at_end_of_day_5_before_fees`.
- **C2, refused.** E7 causes three fees, for Days 2, 4, and 5, all value-dated Day 5, not one on Day 2.
  `test_c2_e7_causes_three_fees_all_value_dated_day_5`.
- **C3, accepted.** Auth-A is approved on arrival against 250.00, and E5's 185.00 settles within its 200.00 hold and
  releases all of it; E7 restates Day 2 but never reopens a decision.
  `test_c3_auth_a_settlement_is_accepted_and_releases_the_hold`.
- **C4, refused.** E6 is honoured as a force-post of 180.00, not rejected. `test_c4_e6_is_force_posted_for_180`.
- **C5, refused as a claim about this stream.** Auth-B is never approved, so the criterion describes an event that does
  not happen; its rule, a hold reduces the available balance but not the ledger balance, is the ledger's rule and is
  tested on Auth-A. `test_c5_auth_b_is_declined`, `test_c5_a_hold_reduces_available_balance_but_not_ledger_balance`.
- **C6, refused.** Days 2 to 4 and the net fees return, but Day 5 closes at 210.00, interest is 0.76, not 0.79, and Day
  6 closes at 285.76, not 285.79. `test_c6_e9_restores_days_2_to_4_and_refunds_the_fees`,
  `test_c6_day_6_closes_at_285_76_not_285_79`.
- **C7, refused.** 3 × 3.334 = 10.002; the ledger posts 3.333, 3.333, and 3.334. `test_c7_e10_posts_3_333_3_333_3_334`.
- **C8, refused.** Each capitalization is the sum of its rounded interest events, so no remainder exists.
  `test_c8_capitalization_equals_the_sum_of_interest_events`.

## The Figures

- **Walk ACC-001 through the six days.** 250.00, 250.00 with 50.00 available, 650.00, 285.00, then −410.00 on Day 5 with
  Days 2 to 4 restated to −370.00, 30.00, and −335.00, then 285.76 on Day 6 with Days 2 to 5 restated to 250.00, 650.00,
  285.00, and 210.00. MOVEMENT's [Day 1](../../MOVEMENT.md#day-1) to [Day 6](../../MOVEMENT.md#day-6), and [each day's
  closing as known][closings].
- **Why 285.76 and not 285.79?** The refunds are value-dated Day 6, so Day 5 keeps its fees at 210.00 and earns 0.08,
  not 0.11; interest is 0.76, not 0.79. AMB-004, AMB-005; C6 in
  [REJECTED](../../REJECTED.md#c6--everything-returning-to-its-pre-e7-value-after-e9).
- **Why −410.00 on Day 5?** 285.00 − 620.00 = −335.00, less three fees of 25.00, all value-dated Day 5. MOVEMENT,
  [Why the Fixed Figures Hold](../../MOVEMENT.md#why-the-fixed-figures-hold); AMB-002, AMB-003.
- **Why is Day 3 restated to 30.00, not below zero?** E4's 400.00 lands on Day 3: −370.00 + 400.00. E6 is value-dated
  Day 4 and every fee Day 5, so neither reaches Day 3. MOVEMENT, Why the Fixed Figures Hold.
- **Why is Day 3's adjustment −0.25, not −0.26?** At 30.00, Day 3 still earns 0.012 → 0.01, and 0.26 was accrued, so the
  difference is −0.25. MOVEMENT, Why the Fixed Figures Hold; AMB-005.
- **Why 10.008 for ACC-002?** 3.333 + 3.333 + 3.334 = 10.000, value-dated Day 5, earning 0.004 for Day 5 and 0.004 for
  Day 6. AMB-015, AMB-017, AMB-020.
- **Why is ACC-002 at 0.000 on Day 5's report?** E10 is listed after E9, which opened Day 6, so E10 is processed on Day
  6 as a late event and Day 6 restates Day 5. AMB-015.

## Fees

- **Why three fees and not one?** A fee is judged on each day's value-dated closing, and E7 makes Days 2, 4, and 5
  negative. AMB-002; C2 in [REJECTED](../../REJECTED.md#c2--exactly-one-fee-from-e7-on-day-2).
- **Why are they all dated Day 5, when the brief says "the day assessed"?** "The day assessed" is read as the day the
  check runs; a fee names the day it is for, such as `FEE-001-D2@D5`, and a past day's closing moves only by the
  backdated event itself. AMB-003, whose Rationale states the cost.
- **Why are the refunds dated Day 6, not Day 5?** A correction is a new event on the day it is recognised; the ledger
  never reaches back into a closed day. AMB-004.
- **When is a fee generated: when E7 arrives, or at close?** At close, after E8. AMB-016.
- **Can a fee cause another fee?** Yes: a fee counts in later closings, at most one a day. AMB-011.
- **Is a fee refunded on a closing that includes itself?** Yes: the fee step reads each day's closing with every fee
  value-dated by then, its own included; that is AMB-011's accepted cost. Example, run on the ledger: Day 5 at −10.00 is
  charged 25.00, so −35.00; a late credit of 20.00 for Day 5 lifts its events to +10.00 but its closing only to −15.00,
  so the fee stays. It never arises in the brief's stream, where Day 5 recovers to 210.00.
  [Fees and interest](../explanation/fees-and-interest.md#step-1-fee-re-evaluation).
- **What is the BHD fee?** AED 25.00 at a fixed 0.10238257: BHD 2.560. AMB-027;
  [NUMBERS](../../NUMBERS.md#bhd-overdraft-fee).

## Interest

- **Which balance does interest accrue on?** The closing as known that day; a late event generates an adjustment, dated
  the day it is recognised. 0.68 as known, −0.46 on Day 5, +0.54 on Day 6: 0.76. AMB-005.
- **Why half-even, and does it matter here?** No upward bias across many roundings; no figure in this stream is a tie,
  so half-up would print the same. AMB-006; [NUMBERS](../../NUMBERS.md#rounding-mode).
- **Why no compounding?** Interest capitalizes as a single credit at the end of Day 6, so until then it is not part of
  the balance it accrues on. AMB-007.
- **What order does a close run in?** Fees, then interest, then capitalization on Day 6 only. AMB-023;
  [NUMBERS](../../NUMBERS.md#end-of-day-order).
- **How do the rounded dailies sum exactly to the capitalized total?** The capitalization is the sum of the rounded
  events in the log, so no remainder can exist; C8's remainder never arises.
  [REJECTED](../../REJECTED.md#c8--discarding-a-rounding-remainder).
- **Why `Decimal("0.0004")` and 28 digits?** A string literal is exact; 28 significant digits hold every product below
  the amount limit. [NUMBERS](../../NUMBERS.md#rate-literal),
  [Decimal working precision](../../NUMBERS.md#decimal-working-precision).

## Authorizations and Settlements

- **Why is Auth-A approved, when Day 2 later reads −370.00?** It is decided on arrival against 250.00, and a decision is
  final; the report is point-in-time, so the approval stays explainable. AMB-009, AMB-022; C3 in MOVEMENT.
- **Why is Auth-B declined?** E7 lands before E8: −335.00 − 90.00 = −425.00. AMB-008, AMB-009, AMB-016; C5 in
  [REJECTED](../../REJECTED.md#c5--an-approved-auth-b-hold).
- **Is a decline an error?** No, an authorization state; errors are for events the ledger cannot carry out. AMB-019.
- **Why honour E6? Criterion 4 says reject it.** In production a settlement with no authorization is posted, and a
  dispute goes through a chargeback. AMB-012, AMB-029; C4 in
  [REJECTED](../../REJECTED.md#c4--rejecting-a-settlement-with-an-unknown-authorization).
- **What happens to Auth-A's unused 15.00?** Released: a settlement with no `final` flag is final and releases the whole
  hold. AMB-013; [NUMBERS](../../NUMBERS.md#hold-released-on-settlement).
- **What about a settlement above its hold?** It debits the full amount. AMB-030.
- **What does an authorization's value date do?** The hold counts from it. AMB-010.
- **How long does a hold live?** Forever: the known weakness and the failing test. AMB-018; the fix in
  [fix the known weakness](../how-to/fix-the-known-weakness.md).
- **The same authorization ID twice?** The second is refused, on any account. AMB-038.

## Reversals, Retries, and Refusals

- **What can a reversal target?** Any accepted event, generated ones included; each event's money is undone at most
  once. AMB-035.
- **A second reversal of E7, or a reversal of E9?** Both refused. AMB-028.
- **A reversal on the wrong account?** Refused with a reason naming both accounts. AMB-036.
- **A reversal dated before its target?** Refused; one dated after undoes the target from its own date. AMB-037.
- **The same event twice?** The same content is a duplicate with no effect; different content is refused. AMB-034.
- **Where do refused events go? What stops a run?** Every event is logged with its outcome; only a row that cannot be an
  event, such as a bad amount, stops the run, with exit status 2. AMB-014;
  [exit statuses](../../apps/account-ledger-cli/README.md#exit-statuses).
- **Every refusal and the order checked.** [Code walkthrough](../explanation/code-walkthrough.md#a-reversal).

## Days, Order, and the Report

- **What is a day? Why Day 0?** Integers 1 to 6 with no calendar; Day 0 is the opening, outside the window. AMB-001.
- **Why process in listed order, not by booked day?** The listed order is the order received; a day closes on time and a
  late event is backdated. AMB-015.
- **Why do reports restate earlier days?** Point-in-time with restatement keeps every decision explainable from the
  balance it saw. AMB-022.
- **Why does the report print more than the four items the brief names?** So every figure can be checked from the output
  alone. AMB-033, AMB-025.
- **A test suite or a script?** Both: the CLI prints the report; the tests assert every figure. AMB-026.

## Design and Code

- **What does append-only mean in your code?** One log of immutable entries; every balance, hold, and state is worked
  out from it on demand. AMB-024;
  [architecture, Domain Model](../../specs/apps/account-ledger/cli/architecture.md#domain-model).
- **Show one day's path through the code.** [Code walkthrough](../explanation/code-walkthrough.md);
  [reading order](../../specs/apps/account-ledger/cli/architecture.md#reading-the-code).
- **Why `Result` rather than exceptions? Why no inheritance? Why methods, not dispatchers?**
  [REJECTED, Abandoned Approaches](../../REJECTED.md#abandoned-approaches);
  [Python crash course](../explanation/python-crash-course.md).
- **Why one type per currency?** AED and BHD must never be summed: pyright refuses `Aed + Bhd` and keeps each account's
  figures in its own currency, and a sum that meets both at run time returns `CurrencyMismatch`.
  [Python crash course, Generics](../explanation/python-crash-course.md#generics).
- **Why plain pytest, not Gherkin?** [REJECTED](../../REJECTED.md#gherkin-acceptance-tests); AMB-026.
- **Your failing test: why a strict xfail?** It runs and fails on every push without blocking delivery, and turns the
  run red once fixed. AMB-031; [known weakness](../../apps/account-ledger-cli/README.md#known-weakness).
- **Show me the failing test.** `test_known_weakness_an_unsettled_hold_never_expires` in `test_stream.py`: run with
  `-k known_weakness` it reports `1 xfailed`, and with `--runxfail` its assertion fails, 802.40 available against a
  1,002.40 closing. [Fix the known weakness, step 1](../how-to/fix-the-known-weakness.md#steps).
- **How would you fix it?** A fifth authorization state, `Expired`; a `HoldExpired` entry the close generates, before
  fees, for every hold kept more than 30 days after its value date; and a clearing after expiry force-posted. The marker
  then reports `XPASS(strict)` and is removed. No figure in the brief's stream moves.
  [Fix the known weakness](../how-to/fix-the-known-weakness.md), built and run on a scratch copy.
- **Why Day 32 and 30 days in that test?** Visa's longest authorization-to-clearing time frame is 30 calendar days.
  [NUMBERS](../../NUMBERS.md#hold-time-frame), [known-weakness run](../../NUMBERS.md#known-weakness-run).
- **Why that value and not half?** The brief asks it of every constant; [NUMBERS](../../NUMBERS.md#chosen-constants)
  answers each. In short:
  - rate `Decimal("0.0004")`: the given rate, written exactly; halving is not a choice.
  - 28 digits: an amount just below 10¹² times the rate keeps 16 digits; at 14, large products would round silently.
  - amount limit below 10¹²: keeps every sum inside 28 digits; halving it refuses more amounts and makes no sum safer.
  - 360 instalments: a monthly plan over thirty years; at 180, a thirty-year plan would be refused.
  - BHD 2.560 at 0.10238257: at half the rate, a BHD account's fee would be worth AED 12.50, not AED 25.00.
  - 80% unit coverage: guards the core while leaving room to move fast; at 40%, most of it could go unexecuted.
  - 120 `=` in the report's rule: the widest table is 119; at 60, the rule stops midway across most tables.
  - words for two to ten instalments: at five, six to ten would print as digits although a word is as short.
  - 30 days and Day 32 in the failing test: at 15, Visa would still honour a lodging or cruise authorization, and at Day
    16 the hold is still legitimately active.
  - half-even, the day integers, and the close's order have no half; the full hold released at 100.00 would still
    reserve funds no merchant can claim.
- **Where would hold expiry, a third currency, or a new refusal go?**
  [Code walkthrough, Where a Change Would Go](../explanation/code-walkthrough.md#where-a-change-would-go); a new refusal
  step by step in [add a refusal, test first](../how-to/add-a-refusal-test-first.md).

## Part 2: Trade-Offs

- **What breaks first at 100× volume?** The day's close, in processing time, well before memory: a close re-evaluates
  every day from the first against every entry, so D days cost about D³. A hundred times the daily volume took 10.1 s
  over 30 days and 69.2 s over 60, at 31 MB and 41 MB.
  [Append-only at scale](../explanation/architecture-trade-offs.md#append-only-at-scale).
- **Where does unbounded state accumulate, and what is the cheapest fix?** The log, the window, and the snapshots; a
  projection of running totals by value day. Same section.
- **The one control for value-dated entries in a UAE bank?** Maker-checker approval for any value date earlier than the
  booking day. [Value-dated entries](../explanation/architecture-trade-offs.md#value-dated-entries-in-production).
- **Every way an authorization ends?**
  [Authorization lifecycle](../explanation/architecture-trade-offs.md#authorization-lifecycle).
- **What did you cut?** [What you cut and why](../explanation/architecture-trade-offs.md#what-you-cut-and-why).

## How It Was Built

- **Who wrote the code, and how?** [How this was built](../explanation/how-this-was-built.md).
- **Isn't OUTPUT_TARGET only what your code printed?** No: git shows MOVEMENT and OUTPUT_TARGET added in `72e338c`, at
  15:39 on 2026-09-24, and last given a figure in `43ed1ae`, at 21:33, before the first ledger code, `bd5722b`, at 04:42
  on 2026-09-25; the two later changes to OUTPUT_TARGET are wording. The golden test holds the code to it.
- **The brief budgets three to four hours of design and building; why so much more?** [WORKLOG](../../WORKLOG.md)
  records every section of work with its real times; [how this was built](../explanation/how-this-was-built.md) says
  what they add up to.

## Decisions Against the First Recommendation

Each entry in AMBIGUITIES marks the option recommended before the decision. Nine were decided another way, and each
entry's Rationale says why; a reviewer checking the documents' honesty may ask about them.

| Entry   | Recommended first                                  | Decided                                             |
| ------- | -------------------------------------------------- | --------------------------------------------------- |
| AMB-003 | date a fee on the day whose closing is negative    | date it the day the check runs, naming its day      |
| AMB-004 | refund on Day 6, value-dated Day 5, the fee's date | refund value-dated Day 6, the day generated         |
| AMB-010 | record a hold's value date and use it for nothing  | the hold counts from its value date                 |
| AMB-012 | reject E6 and accept criterion 4                   | honour E6 as a force-post                           |
| AMB-013 | a settlement always releases the whole hold        | a `final` flag; without it, the settlement is final |
| AMB-015 | sort by booked day, held loosely                   | the listed order; E10 is late                       |
| AMB-027 | no BHD fee; a negative BHD closing is an error     | convert AED 25.00 at a fixed rate: BHD 2.560        |
| AMB-031 | the failing test in its own target, outside suites | a strict expected failure in the regular suite      |
| AMB-035 | reverse only an incoming credit, debit, settlement | reverse any accepted event, generated included      |

[closings]: ../explanation/fees-and-interest.md#each-days-closing-as-known-at-each-days-end
