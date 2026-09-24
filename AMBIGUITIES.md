# Ambiguities

Every place the [challenge brief](challenge-raw.md) admits more than one reading, and how each is resolved.

Each entry is **Resolved** (the choice is recorded with its reason) or **Open** (options and a recommendation are
listed, and nothing is built on it yet). Figures come from a scratch replay of the event stream, not from the ledger
code, which does not exist yet; every figure is re-derived by the test suite once it does.

Unless an entry says otherwise, figures assume the current recommendation of every other open entry. Those that move
figures most: fees re-evaluated for every day (AMB-003), dated on the day they are for (AMB-004), booked at day close
(AMB-005), reversed when E9 makes the day non-negative (AMB-006), interest computed from final value-dated balances
(AMB-007), and E6 rejected (AMB-014). [MOVEMENT](MOVEMENT.md) holds only the figures every open option agrees on.

Reference balances for ACC-001 before E7 arrives, by value date:

| Day | Closing (AED) |
| --- | ------------- |
| 1   | 250.00        |
| 2   | 250.00        |
| 3   | 650.00        |
| 4   | 465.00        |

## AMB-001 — Replay order when booked days are out of sequence

**Where.** The stream is "replayed in this order", but E10 (booked Day 5) is listed after E9 (booked Day 6).

**Status: Open.**

E9 touches only ACC-001 and E10 only ACC-002, so the two events commute: ACC-001 is identical under every option, and
only ACC-002's day-by-day view and possibly its interest change. All figures below are ACC-002, in BHD; the interest
columns follow the two bases in AMB-007.

| Option                             | Day 5 report | Day 6 report           | Hindsight interest | As-known interest |
| ---------------------------------- | ------------ | ---------------------- | ------------------ | ----------------- |
| Sort by booked day (E10 before E9) | 10.000       | 10.000                 | 0.008              | 0.008             |
| Listed order; E10 late, backdated  | 0.000        | 10.000; Day 5 restated | 0.008              | 0.004             |
| Listed order; E10 rejected         | 0.000        | 0.000, plus an error   | 0.000              | 0.000             |

In the late-arrival option, E10 is processed on Day 6 with value date Day 5, so Day 6's report restates Day 5 to 10.000.

Recommendation, held loosely: sort by booked day. The booked day is a business fact about when the bank recorded the
event, while list position is presentation; because the events commute, the deviation from "in this order" changes no
account balance. The late-arrival reading is the strongest alternative: it honours the wording literally and reuses the
backdating machinery E7 and E9 already need.

## AMB-002 — What a day's report shows once backdated entries exist

**Where.** "Prints, per day: closing ledger balance …" alongside value-dated entries that arrive days late (E7, E9).

**Status: Open.**

| Option                          | What Day N's report shows                                                    |
| ------------------------------- | ---------------------------------------------------------------------------- |
| Point-in-time, with restatement | what was known at end of Day N, plus restated closings a backdated entry hit |
| Hindsight only                  | one final table by value date, printed after the whole stream                |
| Point-in-time, plus final table | what was known at end of Day N; one hindsight table after Day 6              |

Recommendation: point-in-time with restatement. Each authorization decision stays explainable from the balance it
actually saw, it matches acceptance criterion 1's framing ("evaluated at end of Day 5"), and each restatement appears on
the day it happened. Hindsight only makes Auth-A's Day 2 approval look inconsistent with a restated Day 2 of −370.00; a
final table alone hides each restatement from the day it happened.

## AMB-003 — Which days a backdated entry makes liable for an overdraft fee

**Where.** The fee is assessed when "that day's closing ledger balance (all entries with value_date ≤ that day) is
negative". E7 arrives on Day 5 with value date Day 2.

**Status: Open.**

| Option                                       | Fees caused by E7 | ACC-001 Day 5 closing |
| -------------------------------------------- | ----------------- | --------------------- |
| Re-evaluate every day up to today, in order  | Day 2, 4, 5       | −230.00               |
| Evaluate the backdated value date plus today | Day 2, 5          | −205.00               |
| Evaluate today only                          | Day 5             | −180.00               |

Re-evaluating in order matters: Day 2's fee (−370.00 → −395.00) leaves Day 3 at +5.00, so Day 3 stays fee-free, while
Day 4 falls to −180.00 and Day 5 to −205.00 before their own fees.

Recommendation: re-evaluate every day. It is the only option under which no day ends with a negative value-dated closing
balance and no fee, which is what the rule defines.

## AMB-004 — The value date of a retroactive fee

**Where.** "Booked with value_date equal to the day assessed." The day assessed could be the day whose closing is
negative (Day 2) or the day the assessment runs (Day 5).

**Status: Open.** Recommendation: the day whose closing is negative. Dating Day 2's fee on Day 5 would leave Day 2's
value-dated closing at −370.00 with no fee against it, and would push Day 5 further negative for a Day 2 event.

## AMB-005 — When a retroactive fee is booked

**Where.** Nothing says whether fees are assessed the moment a backdated entry arrives or at the close of the day it
arrives on.

**Status: Open.** Recommendation: at day close. Criterion 1 evaluates Day 2 "at end of Day 5 and before any fee is
assessed", which only makes sense if assessment is a day-close step. The choice does not change Auth-B (AMB-015):
available balance at E8 is −245.00 without the fees and −295.00 with the Day 2 and Day 4 fees.

## AMB-006 — What happens to fees once E9 reverses E7

**Where.** The ledger is append-only, E9 reverses E7, and the fees E7 caused were correct when assessed.

**Status: Open.**

Figures are ACC-001, in AED, with interest on the hindsight basis (AMB-007).

| Option                                         | Day 6 before interest | Interest | Day 6 after capitalization |
| ---------------------------------------------- | --------------------- | -------- | -------------------------- |
| Reverse the fee of each day no longer negative | 465.00                | 1.03     | 466.03                     |
| Keep the fees                                  | 390.00                | 0.93     | 390.93                     |

Recommendation: book fee reversals. The fee rule is defined on the value-dated closing balance, which after E9 is
non-negative on Days 2, 4, and 5; keeping the fees contradicts the rule as the ledger now states it. Reversal entries
are new records, so nothing is mutated.

## AMB-007 — Which balance daily interest accrues on

**Where.** "0.04% per day on the closing ledger balance", with backdated entries changing past closings.

**Status: Open.**

| Option                                                                 | ACC-001 total | ACC-002 total |
| ---------------------------------------------------------------------- | ------------- | ------------- |
| Hindsight: at capitalization, from final value-dated closings          | 1.03          | 0.008         |
| As known: each day's accrual fixed at that day's close, never restated | 0.84          | 0.008         |

The as-known figure is 0.10 + 0.10 + 0.26 + 0.19 + 0.00 (Day 5 as known was −230.00) + 0.19. Recommendation: hindsight.
Accruals are not booked until capitalization, so there is no record to restate; the credit reflects the balances the
ledger finally holds, and the rounded dailies still sum exactly to it.

## AMB-008 — Rounding mode

**Where.** "Amounts stored and rounded to their own precision" names no mode.

**Status: Open.** No figure in this stream falls on a tie: the unrounded accruals are 0.1, 0.26, 0.186, and 0.004, so
half-even and half-up give identical results here. Recommendation: half-even, because it carries no upward bias across
many small accruals; the choice still has to be made because a different stream could hit a tie.

## AMB-009 — End-of-day ordering and the Day 6 capitalization

**Where.** Fees, interest, and capitalization all happen "at end of day", in no stated order.

**Status: Open.** Recommendation: fee assessment, then the day's interest accrual on the post-fee closing, then — on Day
6 only — capitalization as one credit value-dated Day 6. Day 6's accrual is computed before the capitalization credit,
so interest never accrues on itself, and the printed Day 6 closing includes the credit.

## AMB-010 — "Three equal instalments" of BHD 10.000

**Where.** 10.000 ÷ 3 = 3.3333…, which no three-decimal amount divides equally.

**Status: Open.** Three entries of 3.333, 3.333, and 3.334, all value-dated Day 5, summing exactly to 10.000.
Recommendation: the extra 0.001 goes on the last instalment, so the first two carry the plain quotient and the remainder
closes the total. Criterion 7 turns on the same arithmetic.

## AMB-011 — A settlement smaller than its hold

**Where.** Auth-A holds 200.00 and settles for 185.00.

**Status: Open.** Recommendation: the settlement debits 185.00 and releases the whole hold, so the unused 15.00 returns
to available balance at once. Keeping 15.00 on hold would reserve funds no merchant can still claim.

## AMB-012 — A settlement larger than its hold

**Where.** Not in this stream; the rules are silent.

**Status: Open.** Recommendation: accept and debit the full amount. The authorization check guards holds, not
settlements, and once the bank has authorized it is liable for the merchant's claim; any resulting negative balance is
what the fee rule already handles.

## AMB-013 — A settlement against a declined or already-settled authorization

**Where.** Not in this stream; criterion 4 covers only IDs "not present in the ledger".

**Status: Open.** Recommendation: reject, and debit nothing, exactly as for an unknown ID: without an active hold there
are no reserved funds to settle against.

## AMB-014 — Settlements with no authorization, in production

**Where.** E6 settles Auth-Z, which was never authorized; criterion 4 says such settlements are rejected.

**Status: Open.** This entry decides criterion 4. Within this model, rejecting is consistent: only an authorization
creates a right to settle. In production, card schemes deliver force-posted and offline settlements that the issuer must
still honour, so "funds must not leave the account" does not hold there. Recommendation: accept criterion 4 for the
model and record the production gap in the architecture document.

## AMB-015 — Auth-B: declined, yet "never settled"

**Where.** "Auth-B is never settled inside the window" suggests it was approved, and criterion 5 opens "If Auth-B is
approved".

**Status: Open.** This entry decides criterion 5. E7 lands earlier on Day 5 than E8, so available balance at E8 is
−155.00 − 90.00 = −245.00, and Auth-B is **declined**. Without E7 it would have been 375.00 and approved. The criterion
is a conditional whose premise is false, so it is vacuously true here. Recommendation: accept it as a statement of hold
semantics, prove those semantics with Auth-A (ledger 250.00, available 50.00 on Day 2), and state that Auth-B never
holds anything.

## AMB-016 — The ledger balance an authorization is checked against

**Where.** "Ledger balance minus active holds", where the ledger contains backdated entries.

**Status: Open.** Recommendation: all entries with value date on or before the current day, which includes E7 when E8 is
checked. No entry in this stream is value-dated in the future, so the alternative — every booked entry — gives the same
figures; the choice matters only for future-dated entries.

## AMB-017 — Whether a declined authorization is an "authorization state" or an "error"

**Where.** The report prints both "authorization states" and "errors".

**Status: Open.** Recommendation: a declined authorization is a state (`DECLINED`), because declining is the rule
working as intended; a rejected settlement (E6) is an error, because it is an instruction the ledger could not carry
out.

## AMB-018 — An overdraft fee on a BHD account

**Where.** The fee is AED 25.00, and ACC-002 is in BHD. ACC-002 never goes negative, so this is not triggered.

**Status: Open.** Recommendation: define the fee for AED only, convert nothing, and report a negative BHD closing as an
error ("no overdraft fee configured for BHD") rather than inventing an amount or an exchange rate.

## AMB-019 — Reversing a reversal

**Where.** Not in this stream.

**Status: Open.** Recommendation: reject a reversal of an entry that is itself a reversal, and a second reversal of the
same entry, so a debit can be undone at most once.

## AMB-020 — How long a hold lives

**Where.** No expiry is specified, and an unsettled hold would reduce available balance indefinitely.

**Status: Open.** Recommendation: model no expiry inside the window, and make this the design limitation the
deliberately failing test exposes: a hold that should lapse never does.

## AMB-021 — What each day's report lists

**Where.** "Prints, per day: closing ledger balance, fee assessments, authorization states, and errors" fixes the
categories but not their scope.

**Status: Open.** Recommendation: per account, every day, even with no activity; fees listed on the day they are
assessed, each with its own value date, so Day 5 lists the Day 2, 4, and 5 fees; every known authorization with its
state at end of day (so Auth-A shows its active hold on Day 3), not only that day's changes; and that day's errors. The
alternative, printing only what changed that day, is shorter but hides an active hold on days it does nothing.

## AMB-022 — Whether a fee counts towards later days' closings

**Where.** The fee is an entry like any other, but the rule does not say whether a fee-induced negative closing can
trigger the next day's fee.

**Status: Open.** Recommendation: a fee is an ordinary entry and counts, because the rule reads "all entries with
value_date ≤ that day". This stream is unaffected either way: without counting fees, Day 3 is +30.00 instead of +5.00
and Day 5 is −155.00 instead of −205.00, and the same days end negative.

## AMB-023 — Whether daily interest compounds before capitalization

**Where.** Interest accrues daily but capitalizes only at the end of Day 6.

**Status: Open.** Recommendation: no compounding. An accrual is not a ledger entry until it capitalizes, so it is not
part of any closing balance before Day 6. Compounding would not change a single rounded accrual in this stream (ACC-001
still totals 1.03), but it would in a longer or larger one.

## AMB-024 — What a value date means on an authorization

**Where.** E3 and E8 carry value dates, but a hold is not a ledger entry and moves no ledger balance.

**Status: Open.** Recommendation: record it and use it for nothing. A hold takes effect when it is approved, and a
settlement's own value date dates the debit. Both authorizations here are value-dated on their booked day, so no figure
depends on this.

## AMB-025 — Whether the E10 instalments are spread over days

**Where.** "Instalments" usually means payments over time, but E10 gives one value date, Day 5.

**Status: Open.** Recommendation: all three instalments are value-dated Day 5, as E10 states. Spreading them over Day 5,
6, and 7 would put the third instalment outside the window and change ACC-002's interest from 0.008 to 0.004 (0.001 on
3.333, then 0.003 on 6.666).

## AMB-026 — What "append-only" covers

**Where.** "No event record is ever mutated or deleted", while authorizations change state and balances change daily.

**Status: Open.** Recommendation: event records and ledger entries are immutable; balances, holds, and authorization
states are derived by folding over them and are never stored as mutable fields. A state change, such as a hold being
settled or a fee being reversed, is always a new record.

## AMB-027 — Whether rejected and declined events are recorded

**Where.** E6 is rejected and E8 is declined; the brief does not say whether such events enter the ledger.

**Status: Open.** Recommendation: every incoming event is recorded with its outcome, and only accepted events produce
ledger entries. Discarding rejected events would leave the report's errors with nothing to point at, and an auditor with
no trace of what was refused.

## AMB-028 — When an authorization is decided

**Where.** An authorization could be decided when it arrives or at the close of its day.

**Status: Open.** Recommendation: when it arrives, against the ledger and holds as they stand at that moment, because
that is when a card network needs the answer. In this stream E7 precedes E8 on Day 5, so both readings decline Auth-B.

## AMB-029 — How a deliberately failing test coexists with a runnable suite

**Where.** The brief wants "one failing test against your own design" and also a runnable test suite; this repository
runs every test on every push, and a failing test there would block all delivery.

**Status: Open.** Recommendation: the failing test lives in its own test target, excluded from the regular suites and
the push hooks, so it fails whenever it is run and nothing else is blocked. Marking it as an expected failure would make
the run green, which is not a failing test.

## AMB-030 — Test suite or script

**Where.** "It must be exercised by a runnable test suite or script that replays the event stream and prints, per day".

**Status: Open.** Recommendation: both. The command-line program replays the stream and prints the daily report; the
test suite replays the same stream and asserts every figure. The alternative, a test suite that prints, mixes assertion
and presentation.

## AMB-031 — Which constants belong in NUMBERS

**Where.** "Every constant you chose, why that value and not half it", while most constants are given by the brief.

**Status: Open.** Recommendation: list both, marked given or chosen. A given constant cannot be halved without breaking
a rule, so its entry says what the value drives; only chosen constants carry a "why not half" argument.

## AMB-032 — What a "day" is

**Where.** Days 1 to 6 have no calendar, time zone, or cut-off time.

**Status: Open.** Recommendation: days are plain integers, every day in the window closes whether or not events arrive,
and there is no business-day calendar, weekend, or cut-off. Day 0 names the opening state, reported before Day 1 in the
same shape, with the opening balance as its closing; it is outside the window, so it assesses no fee and accrues no
interest. Nothing in the rules consults a calendar, so inventing one would add assumptions without changing a figure.

## AMB-033 — What the report prints beyond the four named items

**Where.** The report prints "closing ledger balance, fee assessments, authorization states, and errors"; nothing says
whether it may print more.

**Status: Open.** Recommendation: also print each account's available balance every day and, on Day 6, the interest
capitalized. Every authorization is decided against the available balance, so without it Auth-A's approval and Auth-B's
decline cannot be checked from the output; the capitalized interest is the total the rounded daily accruals must sum to.
The alternative, exactly the four items, matches the brief's list but leaves both unverifiable from the output.
