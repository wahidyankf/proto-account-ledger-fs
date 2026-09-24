# Ambiguities

Every place the [challenge brief](challenge-raw.md) admits more than one reading, and how each is resolved.

Each entry has the same six parts:

- **Where** the brief is ambiguous, quoted where it can be.
- **Why it is problematic**: what the readings disagree on, and which figures or criteria that moves.
- **Options**: the readings, with the one currently recommended marked and its reason.
- **Status**: **Open** until the entry is settled, then **Resolved**.
- **Resolution**: the reading chosen, left blank while the entry is open.
- **Rationale**: why that reading was chosen over the others, left blank while the entry is open.

Every entry is open, and entries are settled one at a time; a recommendation is not a resolution. Entries are numbered
in the order they first bear on [MOVEMENT](MOVEMENT.md)'s days, from Day 0 onwards, then on its other sections; entries
MOVEMENT never cites come last. Figures come from a scratch replay of the event stream, not from the ledger code, which
does not exist yet; every figure is re-derived by the test suite once it does.

Unless an entry says otherwise, figures assume the current recommendation of every other open entry. Those that move
figures most: fees re-evaluated for every day (AMB-002), dated on the day they are for (AMB-003), reversed when E9 makes
the day non-negative (AMB-004), interest computed from final value-dated balances (AMB-005), E6 rejected (AMB-012), and
fees booked at day close (AMB-016). [MOVEMENT](MOVEMENT.md) holds only the figures every open option agrees on.

Reference balances for ACC-001 before E7 arrives, by value date:

| Day | Closing (AED) |
| --- | ------------- |
| 1   | 250.00        |
| 2   | 250.00        |
| 3   | 650.00        |
| 4   | 465.00        |

## AMB-001 — What a "day" is

**Where.** "The window is six days, Day 1 through Day 6." The brief gives no calendar, time zone, or cut-off time, and
says nothing about the state before Day 1.

**Why it is problematic.** Every rule is keyed to a day: fees are assessed on "that day's closing", interest accrues
"per day", and capitalization happens "at end of Day 6". The ledger has to know when a day closes, whether a day with no
events closes at all, and where the report starts from.

**Options.**

- Plain integers 1 to 6; every day in the window closes whether or not events arrive; no calendar, weekend, or cut-off.
  Day 0 reports the opening state in the same shape as every other day, with the opening balance as its closing, and
  sits outside the window, so it assesses no fee and accrues no interest. **Recommended**: nothing in the rules consults
  a calendar, so inventing one would add assumptions without changing a figure.
- Calendar dates, with business days and a cut-off time.
- Days close only when an event arrives on them.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-002 — Which days a backdated entry makes liable for an overdraft fee

**Where.** The fee is assessed when "that day's closing ledger balance (all entries with value_date ≤ that day) is
negative". E7 arrives on Day 5 with value date Day 2.

**Why it is problematic.** E7 turns Days 2, 4, and 5 negative after Days 2 and 4 have already closed. A check that looks
only at today misses days that became negative in the past; a check that looks back changes both the number of fees and
every later closing. Criterion 2 ("exactly one overdraft fee … on Day 2") turns on this.

**Options.**

| Option                                       | Fees caused by E7 | ACC-001 Day 5 closing |
| -------------------------------------------- | ----------------- | --------------------- |
| Re-evaluate every day up to today, in order  | Day 2, 4, 5       | −230.00               |
| Evaluate the backdated value date plus today | Day 2, 5          | −205.00               |
| Evaluate today only                          | Day 5             | −180.00               |

Re-evaluating in order matters: Day 2's fee (−370.00 → −395.00) leaves Day 3 at +5.00, so Day 3 stays fee-free, while
Day 4 falls to −180.00 and Day 5 to −205.00 before their own fees.

**Recommended**: re-evaluate every day. It is the only option under which no day ends with a negative value-dated
closing balance and no fee, which is what the rule defines.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-003 — The value date of a retroactive fee

**Where.** "Booked with value_date equal to the day assessed."

**Why it is problematic.** The phrase "the day assessed" can mean the day whose closing is negative (Day 2) or the day
the check runs (Day 5). The choice moves the fee between days, which changes the Day 2 to Day 5 closings, which later
days end negative, and the interest they accrue.

**Options.**

- The day whose closing is negative. **Recommended**: dating Day 2's fee on Day 5 would leave Day 2's value-dated
  closing at −370.00 with no fee against it, and would push Day 5 further negative for a Day 2 event.
- The day the assessment runs.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-004 — What happens to fees once E9 reverses E7

**Where.** E9 "reverses E7 — value_date Day 2"; "The ledger is append-only. No event record is ever mutated or deleted."

**Why it is problematic.** After E9, the days that earned fees are no longer negative, so the fees no longer match the
rule that charged them, yet the ledger cannot delete them. Criterion 6 ("all balances and fees return to their pre-E7
values") turns on this, and a reversal's own value date moves the interest.

**Options.** Figures are ACC-001, in AED, with interest on the hindsight basis (AMB-005).

| Option                                         | Day 6 before interest | Interest | Day 6 after capitalization |
| ---------------------------------------------- | --------------------- | -------- | -------------------------- |
| Reverse the fee of each day no longer negative | 465.00                | 1.03     | 466.03                     |
| Keep the fees                                  | 390.00                | 0.93     | 390.93                     |

**Recommended**: book fee reversals, each booked on Day 6 and value-dated on the day of the fee it reverses, so the fee
and its reversal cancel in every closing they touch; the figures above assume that dating. The fee rule is defined on
the value-dated closing balance, which after E9 is non-negative on Days 2, 4, and 5; keeping the fees contradicts the
rule as the ledger now states it. Reversal entries are new records, so nothing is mutated.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-005 — Which balance daily interest accrues on

**Where.** "Daily interest: 0.04% per day on the closing ledger balance, positive balances only."

**Why it is problematic.** E7 and E9 change past closings after those days' interest was worked out. The brief does not
say whether an accrual follows the closing as it was known that day or as the ledger finally holds it, and the two give
different totals.

**Options.**

| Option                                                                 | ACC-001 total | ACC-002 total |
| ---------------------------------------------------------------------- | ------------- | ------------- |
| Hindsight: at capitalization, from final value-dated closings          | 1.03          | 0.008         |
| As known: each day's accrual fixed at that day's close, never restated | 0.84          | 0.008         |

The as-known figure is 0.10 + 0.10 + 0.26 + 0.19 + 0.00 (Day 5 as known was −230.00) + 0.19.

**Recommended**: hindsight. Accruals are not booked until capitalization, so there is no record to restate; the credit
reflects the balances the ledger finally holds, and the rounded dailies still sum exactly to it.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-006 — Rounding mode

**Where.** "Amounts stored and rounded to their own precision."

**Why it is problematic.** No rounding mode is named, and every accrual is rounded. A value that falls exactly halfway
rounds differently under half-up and half-even. No figure in this stream is a tie (the unrounded accruals are 0.1, 0.26,
0.186, and 0.004), so both give identical results here, but a different stream would not.

**Options.**

- Half-even. **Recommended**: it carries no upward bias across many small accruals.
- Half-up.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-007 — Whether daily interest compounds before capitalization

**Where.** "Accruals capitalize as a single credit at end of Day 6."

**Why it is problematic.** The brief does not say whether a day's accrual joins the next day's interest base, which also
decides whether an accrual is a ledger entry before Day 6. Compounding changes no rounded accrual in this stream
(ACC-001 still totals 1.03), but it would in a longer or larger one.

**Options.**

- No compounding: an accrual is not a ledger entry until it capitalizes, so it is part of no closing before Day 6.
  **Recommended**: it follows the brief's single credit at end of Day 6.
- Daily compounding: each accrual joins the next day's base.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-008 — The ledger balance an authorization is checked against

**Where.** "available balance — ledger balance minus active holds".

**Why it is problematic.** With value-dated entries, the ledger balance at an authorization could mean the entries
value-dated up to that day, or every entry booked so far, including any value-dated in the future. No entry in this
stream is future-dated, so both give the same figures, but the model has to pick one.

**Options.**

- Entries value-dated on or before the current day, which includes E7 when E8 is checked. **Recommended**: it is the
  same balance the fee rule reads.
- Every booked entry, whatever its value date.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-009 — When an authorization is decided

**Where.** "An authorization is approved only if the account's available balance … remains at or above zero after the
hold is applied", with no moment named.

**Why it is problematic.** Decided on arrival, an authorization sees only what came before it that day; decided at day
close, it sees every event of the day, including later credits and debits. In this stream E7 precedes E8 on Day 5, so
both readings decline Auth-B.

**Options.**

- On arrival, against the ledger and holds as they stand at that moment. **Recommended**: that is when a card network
  needs the answer.
- At the close of the day it arrives on.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-010 — What a value date means on an authorization

**Where.** "E3 — Day 2 — AUTHORIZATION — ACC-001 Auth-A hold AED 200.00 — value_date Day 2", and E8 likewise.

**Why it is problematic.** A hold is not a ledger entry and moves no ledger balance, so a value date on it has no
defined effect: it could date the hold, start its lifetime, or mean nothing. Both authorizations are value-dated on
their booked day, so no figure depends on this here.

**Options.**

- Record it and use it for nothing: a hold takes effect when approved, and a settlement's own value date dates the
  debit. **Recommended**: no rule reads it.
- The hold takes effect from its value date.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-011 — Whether a fee counts towards later days' closings

**Where.** The fee is assessed on "all entries with value_date ≤ that day".

**Why it is problematic.** A fee can itself turn a later day negative and earn another fee, a cascade the brief neither
allows nor forbids. This stream is unaffected: without counting fees, Day 3 is +30.00 instead of +5.00 and Day 5 is
−155.00 instead of −205.00, and the same days end negative.

**Options.**

- A fee is an ordinary entry and counts. **Recommended**: the rule reads "all entries".
- Fees are left out of the closing the fee rule reads.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-012 — Settlements with no authorization, in production

**Where.** E6: "Auth-Z settles for AED 180.00 … (Auth-Z has no preceding authorization event)"; criterion 4: "must be
rejected and the funds must not leave the account."

**Why it is problematic.** Within the model, rejecting is consistent: only an authorization creates a right to settle.
In production, card schemes deliver force-posted and offline settlements the issuer must honour, so "funds must not
leave the account" does not hold there. The choice moves ACC-001's Day 4 closing (465.00 rejected, 285.00 honoured) and
decides criterion 4.

**Options.**

- Reject E6 as an error and debit nothing. **Recommended**: accept criterion 4 for the model, and record the production
  gap in the architecture document.
- Honour E6 as a force-post and debit 180.00.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-013 — A settlement smaller than its hold

**Where.** E3 holds AED 200.00 for Auth-A; E5: "Auth-A settles for AED 185.00".

**Why it is problematic.** The brief does not say what becomes of the unused 15.00: released at settlement, or kept on
hold. The choice changes ACC-001's available balance from Day 4 onwards.

**Options.**

- The settlement debits 185.00 and releases the whole hold. **Recommended**: keeping 15.00 on hold would reserve funds
  no merchant can still claim.
- The unused 15.00 stays on hold until it lapses (AMB-018).

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-014 — Whether rejected and declined events are recorded

**Where.** "The ledger is append-only. No event record is ever mutated or deleted." E6 is rejected and E8 declined.

**Why it is problematic.** The brief does not say whether a refused event becomes a record at all. That decides whether
the report's errors have anything to point at, and whether "append-only" covers refusals.

**Options.**

- Every incoming event is recorded with its outcome, and only accepted events produce ledger entries. **Recommended**:
  discarding refused events would leave the errors with nothing to point at, and an auditor with no trace of what was
  refused.
- Refused events are discarded.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-015 — Replay order when booked days are out of sequence

**Where.** "Event stream, replayed in this order", but E10 (booked Day 5) is listed after E9 (booked Day 6).

**Why it is problematic.** Following the list literally processes a Day 5 event on Day 6, which is either a late,
backdated arrival or an error; following the booked days departs from "in this order". E9 touches only ACC-001 and E10
only ACC-002, so the two commute: ACC-001 is identical under every option, and only ACC-002's day-by-day view and
possibly its interest change.

**Options.** Figures are ACC-002, in BHD; the interest columns follow the two bases in AMB-005.

| Option                             | Day 5 report | Day 6 report           | Hindsight interest | As-known interest |
| ---------------------------------- | ------------ | ---------------------- | ------------------ | ----------------- |
| Sort by booked day (E10 before E9) | 10.000       | 10.000                 | 0.008              | 0.008             |
| Listed order; E10 late, backdated  | 0.000        | 10.000; Day 5 restated | 0.008              | 0.004             |
| Listed order; E10 rejected         | 0.000        | 0.000, plus an error   | 0.000              | 0.000             |

In the late-arrival option, E10 is processed on Day 6 with value date Day 5, so Day 6's report restates Day 5 to 10.000.

**Recommended**, held loosely: sort by booked day. The booked day is a business fact about when the bank recorded the
event, while list position is presentation; because the events commute, the deviation from "in this order" changes no
account balance. The late-arrival reading is the strongest alternative: it honours the wording literally and reuses the
backdating machinery E7 and E9 already need.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-016 — When a retroactive fee is booked

**Where.** Criterion 1: "evaluated at end of Day 5 and before any fee is assessed". Nothing says whether a fee is
assessed the moment a backdated entry arrives or at the close of the day it arrives on.

**Why it is problematic.** Assessed on arrival, retroactive fees land mid-day, before later events such as E8; assessed
at day close, they come after. That changes the available balance Auth-B is checked against (−245.00 without the fees,
−295.00 with the Day 2 and Day 4 fees; declined either way, AMB-021), and what "before any fee" in criterion 1 means.

**Options.**

- At day close. **Recommended**: criterion 1's "at end of Day 5 and before any fee is assessed" only makes sense if
  assessment is a day-close step.
- The moment the backdated entry arrives.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-017 — Whether the E10 instalments are spread over days

**Where.** E10: "BHD 10.000, posted as three equal instalments — value_date Day 5".

**Why it is problematic.** The word "instalments" usually means payments over time, but E10 gives one value date.
Spreading them over Days 5, 6, and 7 would put the third outside the window and change ACC-002's interest from 0.008 to
0.004 (0.001 on 3.333, then 0.003 on 6.666).

**Options.**

- All three instalments value-dated Day 5. **Recommended**: it is the value date E10 states.
- One instalment on each of Days 5, 6, and 7.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-018 — How long a hold lives

**Where.** "Auth-B is never settled inside the window." No hold lifetime is given.

**Why it is problematic.** An unsettled hold would reduce available balance indefinitely. In this stream no hold is left
open (Auth-B is declined, and Auth-A is settled), so it matters only if AMB-013 keeps part of a hold.

**Options.**

- No expiry inside the window, and this is the design limitation the deliberately failing test exposes: a hold that
  should lapse never does. **Recommended**: the brief gives no lifetime to model.
- A fixed lifetime after which an unsettled hold lapses.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-019 — Whether a declined authorization is an "authorization state" or an "error"

**Where.** The report "prints, per day: closing ledger balance, fee assessments, authorization states, and errors".

**Why it is problematic.** A declined authorization fits either heading, and where it goes changes Day 5's errors line.

**Options.**

- A state (`DECLINED`), while a rejected settlement such as E6 is an error. **Recommended**: declining is the rule
  working as intended; a rejected settlement is an instruction the ledger could not carry out.
- An error.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-020 — How BHD 10.000 splits into "three equal instalments"

**Where.** E10: "BHD 10.000, posted as three equal instalments"; criterion 7: "The three BHD instalments in E10 must
each be BHD 3.334."

**Why it is problematic.** 10.000 ÷ 3 = 3.3333…, which no three-decimal amount divides equally, so the instalments
cannot all be equal and still sum to 10.000. Criterion 7's 3.334 × 3 = 10.002 invents 0.002 BHD.

**Options.**

- 3.333, 3.333, and 3.334, all value-dated Day 5. **Recommended**: the first two carry the plain quotient and the last
  closes the total, which sums exactly to 10.000.
- 3.334, 3.333, and 3.333, with the extra 0.001 first.
- 3.334 each, as criterion 7 states, summing to 10.002.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-021 — Auth-B: declined, yet "never settled"

**Where.** "Auth-B is never settled inside the window"; criterion 5: "If Auth-B is approved, its hold reduces available
balance but not ledger balance."

**Why it is problematic.** The wording suggests Auth-B was approved, but the replay declines it: E7 lands earlier on Day
5 than E8, so available balance at E8 is −155.00 − 90.00 = −245.00. Without E7 it would have been 375.00 and approved.
Criterion 5 is a conditional whose premise is false here, and this entry decides it.

**Options.**

- Accept criterion 5 as a statement of hold semantics, prove those semantics with Auth-A (ledger 250.00, available 50.00
  on Day 2), and state that Auth-B never holds anything. **Recommended**: the criterion is vacuously true, and its
  semantics are still testable.
- Reject criterion 5, because its premise never holds.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-022 — What a day's report shows once backdated entries exist

**Where.** The report "prints, per day: closing ledger balance …", alongside value-dated entries that arrive days late
(E7, E9).

**Why it is problematic.** Once E7 and E9 rewrite past days, the closing for Day N can mean what was known at the end of
Day N or what the ledger holds for Day N later. After E7, Day 2 reads 250.00 as known on Day 2 but −370.00 before fees
as restated on Day 5, and an authorization decision can look inconsistent with the balance printed beside it.

**Options.**

| Option                          | What Day N's report shows                                                    |
| ------------------------------- | ---------------------------------------------------------------------------- |
| Point-in-time, with restatement | what was known at end of Day N, plus restated closings a backdated entry hit |
| Hindsight only                  | one final table by value date, printed after the whole stream                |
| Point-in-time, plus final table | what was known at end of Day N; one hindsight table after Day 6              |

**Recommended**: point-in-time with restatement. Each authorization decision stays explainable from the balance it
actually saw, it matches criterion 1's framing ("evaluated at end of Day 5"), and each restatement appears on the day it
happened. Hindsight only makes Auth-A's Day 2 approval look inconsistent with a restated Day 2 of −370.00; a final table
alone hides each restatement from the day it happened.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-023 — End-of-day ordering and the Day 6 capitalization

**Where.** "Accruals capitalize as a single credit at end of Day 6", while fees are assessed on each day's closing. No
order is given for what happens at the end of a day.

**Why it is problematic.** Fees, fee reversals, interest, and capitalization all happen at the end of a day. Their order
decides whether interest accrues on the closing before or after that day's fees, and whether Day 6's accrual includes
the capitalization credit.

**Options.**

- Fee re-evaluation, which assesses new fees and reverses any whose day is no longer negative (AMB-004); then the day's
  interest accrual on the resulting closing; then, on Day 6 only, capitalization as one credit value-dated Day 6.
  **Recommended**: interest then accrues on the closing the fee rule leaves, and never on itself; the printed Day 6
  closing includes the credit.
- Interest accrual before fee re-evaluation.
- Capitalization before Day 6's accrual.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-024 — What "append-only" covers

**Where.** "The ledger is append-only. No event record is ever mutated or deleted."

**Why it is problematic.** Authorizations change state, holds are released, and balances change daily. If those are
stored as fields updated in place, the ledger mutates records in spirit while keeping every event record intact; the
brief does not say how far "record" reaches.

**Options.**

- Event records and ledger entries are immutable; balances, holds, and authorization states are derived by folding over
  them and never stored as mutable fields; every state change, such as a hold settled or a fee reversed, is a new
  record. **Recommended**: nothing the ledger holds can then be edited.
- Only event records are immutable; derived state is stored and updated in place.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-025 — What each day's report lists

**Where.** The report "prints, per day: closing ledger balance, fee assessments, authorization states, and errors".

**Why it is problematic.** The sentence fixes the categories but not their scope: per account or overall, on days with
no activity, and whether an authorization appears only on the day it changes or on every day it is known.

**Options.**

- Per account, every day, even with no activity; fees listed on the day they are assessed, each with its own value date,
  so Day 5 lists the Day 2, 4, and 5 fees; every known authorization with its state at end of day (so Auth-A shows its
  active hold on Day 3); and that day's errors. **Recommended**: every figure can be checked on every day.
- Only what changed that day. Shorter, but it hides an active hold on days it does nothing.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-026 — Test suite or script

**Where.** "It must be exercised by a runnable test suite or script that replays the event stream and prints, per day".

**Why it is problematic.** The "or" allows either. A script alone asserts nothing, and a test suite that prints mixes
assertion with presentation.

**Options.**

- Both: the command-line program replays the stream and prints the daily report, and the test suite replays the same
  stream and asserts every figure. **Recommended**: each does one job.
- A test suite that prints.
- A script only.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-027 — An overdraft fee on a BHD account

**Where.** "Overdraft fee: AED 25.00, assessed once per day per account", while ACC-002 is in BHD.

**Why it is problematic.** The fee has no BHD amount, and converting it needs an exchange rate the brief does not give.
ACC-002 never goes negative in this stream, so this is not triggered.

**Options.**

- Define the fee for AED only, convert nothing, and report a negative BHD closing as an error saying that no overdraft
  fee is configured for BHD. **Recommended**: it invents neither an amount nor a rate.
- Convert AED 25.00 at a chosen rate.
- Charge BHD 25.000.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-028 — Reversing a reversal

**Where.** E9 "reverses E7"; the brief does not say what a reversal may target. Not in this stream.

**Why it is problematic.** Reversing a reversal, or reversing the same entry twice, would let a debit be undone more
than once.

**Options.**

- Reject a reversal of an entry that is itself a reversal, and a second reversal of the same entry. **Recommended**: a
  debit can then be undone at most once.
- Allow both.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-029 — A settlement against a declined or already-settled authorization

**Where.** Criterion 4 covers "an authorization ID not present in the ledger". Not in this stream.

**Why it is problematic.** An ID that is present but declined or already settled has no active hold, and criterion 4 is
silent on it.

**Options.**

- Reject, and debit nothing, exactly as for an unknown ID. **Recommended**: without an active hold there are no reserved
  funds to settle against.
- Accept, as for a force-post.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-030 — A settlement larger than its hold

**Where.** "An authorization is approved only if the account's available balance … remains at or above zero after the
hold is applied"; nothing is said of a settlement above its hold. Not in this stream.

**Why it is problematic.** The amount above the hold was never checked against the available balance, so accepting it
can drive the balance negative.

**Options.**

- Accept and debit the full amount. **Recommended**: the authorization check guards holds, not settlements; once the
  bank has authorized it is liable for the merchant's claim, and any negative balance is what the fee rule handles.
- Reject it.
- Accept up to the hold and reject the rest.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-031 — How a deliberately failing test coexists with a runnable suite

**Where.** "One failing test against your own design, inline-annotated with what it reveals", alongside "a runnable test
suite".

**Why it is problematic.** This repository runs every test on every push, so a failing test in the regular suites would
block all delivery; marking it as an expected failure would turn the run green, which is not a failing test.

**Options.**

- The failing test lives in its own test target, excluded from the regular suites and the push hooks, so it fails
  whenever it is run and nothing else is blocked. **Recommended**: it stays a real failure without blocking delivery.
- Mark it as an expected failure in the regular suite.
- Keep it failing in the regular suite.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-032 — Which constants belong in NUMBERS

**Where.** "NUMBERS.md — every constant you chose, why that value and not half it".

**Why it is problematic.** Most constants are given by the brief, and halving a given constant breaks a rule, so asking
why not half of it does not apply to them; listing only chosen constants hides the values that drive most figures.

**Options.**

- List both, marked given or chosen: a given constant's entry says what the value drives, and only chosen constants
  argue why that value and not half it. **Recommended**: every value a figure rests on is then in one place.
- List chosen constants only.

**Status.** Open.

**Resolution.**

**Rationale.**

## AMB-033 — What the report prints beyond the four named items

**Where.** The report "prints, per day: closing ledger balance, fee assessments, authorization states, and errors".

**Why it is problematic.** The brief does not say whether the report may print more. Without the available balance,
Auth-A's approval and Auth-B's decline cannot be checked from the output, and without the events and end-of-day steps no
closing can be traced to what moved it.

**Options.**

- Also print, for each day, the events processed, every end-of-day step with the entry it books (fees, fee reversals,
  interest accruals, and the capitalization), and each account's available balance. **Recommended**: every printed
  figure can then be verified from the output alone.
- Exactly the four items.

**Status.** Open.

**Resolution.**

**Rationale.**
