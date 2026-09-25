# Ambiguities

Every place the [challenge brief](challenge-raw.md) admits more than one reading, and how each is resolved.

Each entry has the same six parts:

- **Where** the brief is ambiguous, quoted where it can be.
- **Why it is problematic**: what the readings disagree on, and which figures or criteria that moves.
- **Options**: the readings, with the one recommended before the decision marked and its reason.
- **Status**: **Open** until the entry is settled, then **Resolved**.
- **Resolution**: the reading chosen, left blank while the entry is open.
- **Rationale**: why that reading was chosen over the others, left blank while the entry is open.

Entries are settled one at a time, each by an explicit decision; a recommendation is not a resolution. Entries were
numbered, when [MOVEMENT](MOVEMENT.md) was drafted, in the order they first bore on its days, from Day 0 onwards, then
on its other sections; an entry keeps its number when a later change cites it elsewhere, and entries added later, such
as AMB-034, come last. Figures were first taken from a scratch run of the event stream; the ledger's test suite under
`apps/account-ledger-cli/tests/` now re-derives every one, and each entry's resolution names the tests that prove it.

Every entry is resolved, and every figure follows the resolutions. Those that move figures most: fees re-evaluated for
every day (AMB-002), dated on the day the check runs (AMB-003), refunded on Day 6 once E9 makes their days non-negative
(AMB-004), interest accrued as known and corrected by later events (AMB-005), E6 honoured as a force-post (AMB-012),
fees generated at day close (AMB-016), and the end-of-day order that capitalizes last (AMB-023). [MOVEMENT](MOVEMENT.md)
holds every figure.

Reference balances for ACC-001 before E7 arrives, by value date:

| Day | Closing (AED) |
| --- | ------------- |
| 1   | 250.00        |
| 2   | 250.00        |
| 3   | 650.00        |
| 4   | 285.00        |

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

**Status.** Resolved.

**Resolution.** Days are plain integers, Day 1 to Day 6, with no calendar, time zone, or cut-off, and every day in the
window closes whether or not events arrive. Day 0 reports the opening state in the same shape as every other day, with
the opening balance as its closing, and sits outside the window, so it assesses no fee and accrues no interest. _Tests:_
`test_an_empty_stream_reports_the_opening_balances_for_day_0_to_6`, `test_amb_001_a_day_without_events_still_closes`,
and `test_amb_001_an_event_booked_after_the_window_reaches_no_day`.

**Rationale.** The brief names days only as "Day 1 through Day 6", and no rule consults a calendar, so dates, business
days, or a cut-off would add assumptions without changing a figure. Closing every day keeps "0.04% per day" and the fee
"assessed once per day per account" true on a day without events, which days close only on events would not. Day 0 shows
the opening balances Day 1 starts from, in the report's own shape; keeping it outside the window adds no fee or interest
the brief does not ask for.

## AMB-002 — Which days a backdated event makes liable for an overdraft fee

**Where.** The fee is assessed when "that day's closing ledger balance (all entries with value_date ≤ that day) is
negative". E7 arrives on Day 5 with value date Day 2.

**Why it is problematic.** E7 turns Days 2, 4, and 5 negative after Days 2 and 4 have already closed. A check that looks
only at today misses days that became negative in the past; a check that looks back changes both the number of fees and
every later closing. Criterion 2 ("exactly one overdraft fee … on Day 2") turns on this.

**Options.**

| Option                                       | Fees caused by E7 | ACC-001 Day 5 closing |
| -------------------------------------------- | ----------------- | --------------------- |
| Re-evaluate every day up to today, in order  | Day 2, 4, 5       | −410.00               |
| Evaluate the backdated value date plus today | Day 2, 5          | −385.00               |
| Evaluate today only                          | Day 5             | −360.00               |

Each fee is value-dated on the day the check runs (AMB-003), so before any fee Day 2 closes at −370.00, Day 3 at +30.00,
and Days 4 and 5 at −335.00.

**Recommended**: re-evaluate every day. It is the only option under which no day ends with a negative value-dated
closing balance and no fee, which is what the rule defines.

**Status.** Resolved.

**Resolution.** Every end of day re-evaluates each day of the window up to today, in value-date order, and assesses one
AED 25.00 fee for each day whose closing ledger balance is negative and that has no fee yet; a day at or above zero is
skipped. E7 makes Days 2, 4, and 5 liable, three fees in all, and leaves Day 3 without one. Each fee names the day it is
for, such as "for Day 2", so a retroactive fee reads as a past day's charge recognised when the ledger learns of it.
_Test:_ `test_c2_e7_causes_three_fees_all_value_dated_day_5`.

**Rationale.** The rule makes a day liable by "that day's closing ledger balance (all entries with value_date ≤ that
day)", so a backdated event that turns a past day negative makes that day liable however late it arrives. Checking only
today, or only the value date and today, leaves Day 2 or Day 4 negative with no fee, which the rule does not allow.
"Once per day per account" keeps a day from being charged twice when it is re-evaluated again, and naming the day each
fee is for keeps that visible though AMB-003 dates all three on Day 5. Day 5 is negative at its own close under every
option, so none gives criterion 2's "exactly one overdraft fee", which [REJECTED](REJECTED.md) refuses.

## AMB-003 — The value date of a retroactive fee

**Where.** "Booked with value_date equal to the day assessed."

**Why it is problematic.** The phrase "the day assessed" can mean the day whose closing is negative (Day 2) or the day
the check runs (Day 5). The fees for Days 2 and 4 are charged either way (AMB-002); the choice moves them between value
dates. Dated Day 2 and Day 4, they restate Day 2 to −395.00, Day 3 to +5.00, and Day 4 to −385.00; dated Day 5, those
days stay at −370.00, +30.00, and −335.00, and Day 5 carries three fees. Day 5's closing is −410.00 either way; if
interest is computed from final balances (AMB-005), Day 3's interest differs too.

**Options.**

- The day whose closing is negative. **Recommended**: the brief itself uses "assessed" this way. Criterion 2 speaks of a
  fee "assessed, on Day 2" that only E7, booked on Day 5, can cause, and criterion 1 evaluates Day 2's closing "before
  any fee is assessed", which matters only if a fee can land on Day 2. Dated Day 5, Day 2 would keep a negative
  value-dated closing with no fee against it.
- The day the assessment runs, each fee naming the day it is for, such as "for Day 2": a retroactive fee is a past day's
  charge recognised when the ledger learns of it, and a past day's value-dated closing moves only by the backdated event
  itself.

**Status.** Resolved.

**Resolution.** A fee is value-dated on the day the check that assesses it runs, and names the day it is for, such as
"for Day 2". The fees E7 makes due for Days 2, 4, and 5 are all value-dated Day 5, so a past day's value-dated closing
moves only by the backdated event itself. _Test:_ `test_c2_e7_causes_three_fees_all_value_dated_day_5`.

**Rationale.** "The day assessed" reads as the day the assessment runs as readily as the day it looks at. On that
reading a retroactive fee is a past day's charge recognised when the ledger learns of it, and a restated day shows only
what the backdated event did to it: Day 2 stays at −370.00, Day 3 at +30.00, and Day 4 at −335.00, while Day 5 closes at
−410.00 under either reading. Naming the day each fee is for keeps "once per day per account" checkable, though three
fees share Day 5's value date. The cost is accepted: criterion 1's "before any fee is assessed" and criterion 2's fee
"assessed, on Day 2" sit more naturally with the other reading, and Day 2 keeps a negative value-dated closing with no
fee dated on it.

## AMB-004 — What happens to fees once E9 reverses E7

**Where.** E9 "reverses E7 — value_date Day 2"; "The ledger is append-only. No event record is ever mutated or deleted."

**Why it is problematic.** After E9, the days that earned fees are no longer negative, so the fees no longer match the
rule that charged them, yet the ledger cannot delete them. Criterion 6 ("all balances and fees return to their pre-E7
values") turns on this, and a refund's own value date moves the interest.

**Options.** Figures are ACC-001, in AED, with interest on the hindsight basis (AMB-005).

| Option                                        | Day 6 before interest | Interest | Day 6 after capitalization |
| --------------------------------------------- | --------------------- | -------- | -------------------------- |
| Refund, dated on the fee's value date (Day 5) | 285.00                | 0.79     | 285.79                     |
| Refund, dated the day it is generated (Day 6) | 285.00                | 0.76     | 285.76                     |
| Keep the fees                                 | 210.00                | 0.73     | 210.73                     |

Dated on the fee's value date, Day 5 (AMB-003), a refund and its fee cancel in every closing they touch; dated Day 6,
Day 5's value-dated closing keeps its fees at 210.00, and accrues 0.08 instead of 0.11.

**Recommended**: refund each fee on Day 6, value-dated on the value date of the fee it cancels. The fee rule is defined
on the value-dated closing balance, which after E9 is non-negative on Days 2, 4, and 5; keeping the fees contradicts the
rule as the ledger now states it. Refunds are new records, so nothing is mutated.

**Status.** Resolved.

**Resolution.** The ledger is event-sourced: an append-only log of events, including the fees and refunds it generates
at end of day, and balances that are aggregations over the log by value date, recomputed when a late event arrives.
After E9, Day 6's end-of-day check finds Days 2, 4, and 5 no longer negative and generates one AED 25.00 fee refund for
each, naming the day it is for and value-dated Day 6; the fees stay in the log. A later correction to interest follows
the same rule: a new event, dated the day it is recognised. _Test:_
`test_c6_e9_restores_days_2_to_4_and_refunds_the_fees`.

**Rationale.** It is the principle of AMB-002 and AMB-003 applied to undoing a charge: the log is never edited, and what
the ledger generates never reaches back into a past day, so a correction is a new event on the day it is recognised, as
a production ledger generates it at end of day. E9 still restates Days 2 to 5, because the brief value-dates it Day 2.
The fee rule reads value-dated closings, which after E9 are non-negative, so keeping the fees would leave charges the
rule no longer supports. The cost is accepted: Day 5's value-dated closing stays at 210.00, with its fees on Day 5 and
their refunds on Day 6, and interest (AMB-005) totals 0.76 instead of 0.79, so criterion 6's "all balances and fees
return to their pre-E7 values" holds for Day 6's closing and the net fees but not for Day 5 or the interest, so
[REJECTED](REJECTED.md) refuses it.

## AMB-005 — Which balance daily interest accrues on

**Where.** "Daily interest: 0.04% per day on the closing ledger balance, positive balances only."

**Why it is problematic.** E7 and E9 change past closings after those days' interest was worked out. The brief does not
say whether an accrual follows the closing as it was known that day or as the ledger finally holds it, and the two give
different totals.

**Options.**

| Option                                                                 | ACC-001 total | ACC-002 total |
| ---------------------------------------------------------------------- | ------------- | ------------- |
| Hindsight: at capitalization, from final value-dated closings          | 0.76          | 0.008         |
| As known: each day's accrual fixed at that day's close, never restated | 0.68          | 0.008         |
| As known, corrected: a late event generates an adjusting accrual       | 0.76          | 0.008         |

The as-known figure is 0.10 + 0.10 + 0.26 + 0.11 + 0.00 (Day 5 as known was −410.00) + 0.11. Corrected, E7 generates
−0.46 on Day 5 for Days 2 to 4, and E9 generates +0.54 on Day 6 for Days 2 to 5, each dated the day it is recognised, as
AMB-004's resolution does for fees; the total then matches hindsight.

**Recommended**: as known, corrected. It follows AMB-004's resolution: each accrual printed on a day is final, and a
late event corrects interest with a new event instead of restating an old one, while the total still reflects the
balances the ledger finally holds.

**Status.** Resolved.

**Resolution.** Each day's accrual is an event generated at that day's close, on the closing ledger balance as known
then. When a late event changes a past day's closing, the end-of-day check that sees it generates an adjusting accrual
for that day, value-dated the day it is recognised and naming the day it is for. ACC-001 accrues 0.68 as known, adjusted
by −0.46 on Day 5 for E7 and +0.54 on Day 6 for E9, 0.76 in all; ACC-002 accrues 0.008. _Tests:_
`test_amb_005_interest_accrues_on_a_positive_closing` and `test_amb_005_a_changed_closing_adjusts_its_interest`.

**Rationale.** It is AMB-004's principle applied to interest: an accrual is generated when its day closes, on what the
ledger knew, so the accrual printed that day is final, and a correction is a new event rather than a restatement. The
corrections bring the total to what the final value-dated closings earn, as hindsight would, so interest still follows
"the closing ledger balance" once the ledger knows it; never correcting would leave 0.68 and ignore balances the ledger
later knows to be true. Every daily accrual and adjustment is a rounded event, so together they sum exactly to the
capitalized total.

## AMB-006 — Rounding mode

**Where.** "Amounts stored and rounded to their own precision."

**Why it is problematic.** No rounding mode is named, and every accrual is rounded. A value that falls exactly halfway
rounds differently under half-up and half-even. No figure in this stream is a tie (the unrounded accruals are 0.1, 0.26,
0.114, 0.012, 0.084, and 0.004), so both give identical results here, but a different stream would not.

**Options.**

- Half-even. **Recommended**: it carries no upward bias across many small accruals.
- Half-up.

**Status.** Resolved.

**Resolution.** Every amount the ledger computes is rounded to its currency's precision half-even: a value exactly
halfway goes to the even digit, and any other value to the nearer one. A split into instalments rounds down instead, as
AMB-020 resolves. An amount the stream gives is already stored at its currency's precision, as every amount in the brief
is; one given with more places is not rounded but refused as a fault in the input (AMB-014), since rounding it would
post money its sender never sent. _Tests:_ `test_amb_006_daily_interest_rounds_half_even` and
`test_aed_refuses_more_than_two_places`.

**Rationale.** The brief names no mode, and daily accruals are rounded many times. Half-up pushes every halfway value
up, a small bias that grows with the number of accruals; half-even sends half of them each way, so the rounded accruals
carry no bias. It is also the default of Python's Decimal. The cost is accepted: rounding each daily accrual leaves an
account's capitalized total slightly off the interest on unrounded amounts, by at most half a minor unit a day (0.03 AED
over this six-day window, 0.15 AED over a thirty-day month), because the brief makes the capitalized total the sum of
the rounded dailies. Under half-even each of those differences is as likely down as up, so across many accounts and days
they cancel: their expected sum is zero, and their spread grows only with the square root of the number of accruals
while the interest grows with the number itself, so the relative difference shrinks as the book grows. Half-up adds a
small upward bias on every halfway value that never cancels. No unrounded accrual in this stream is a tie, so no figure
moves; a test with a halfway value pins the mode.

## AMB-007 — Whether daily interest compounds before capitalization

**Where.** "Accruals capitalize as a single credit at end of Day 6."

**Why it is problematic.** The brief does not say whether a day's accrual joins the next day's interest base. Every
accrual is an event (AMB-005), so the question is whether it joins the ledger balance before Day 6. Compounding changes
no rounded accrual in this stream (ACC-001 still totals 0.76), but it would in a longer or larger one.

**Options.**

- No compounding: accrual events accumulate apart from the ledger balance until they capitalize, so they are part of no
  closing before Day 6. **Recommended**: it follows the brief's single credit at end of Day 6.
- Daily compounding: each accrual joins the next day's base.

**Status.** Resolved.

**Resolution.** No compounding. Accrual events build up in a separate accrued-interest total, apart from the ledger
balance, and join it only when the capitalization event is generated at the end of Day 6; each day's interest is on that
day's closing ledger balance alone. _Tests:_ `test_c6_day_6_closes_at_285_76_not_285_79` and
`test_the_brief_stream_prints_output_target`.

**Rationale.** The brief puts interest on "the closing ledger balance" and has accruals "capitalize as a single credit
at end of Day 6", so until then they are not part of the balance interest is computed on. It is also how banking usually
works: daily interest is simple, an absolute amount accrued on each day's balance, not a rate compounded on interest
already earned. Compounding would change no rounded accrual in this stream, but it would in a longer or larger one.

## AMB-008 — The ledger balance an authorization is checked against

**Where.** "available balance — ledger balance minus active holds".

**Why it is problematic.** With value-dated events, the ledger balance at an authorization could mean the events
value-dated up to that day, or every event booked so far, including any value-dated in the future. No event in this
stream is future-dated, so both give the same figures, but the model has to pick one.

**Options.**

- Events value-dated on or before the current day, which includes E7 when E8 is checked. **Recommended**: it is the same
  balance the fee rule reads.
- Every booked event, whatever its value date.

**Status.** Resolved.

**Resolution.** An authorization is checked against the ledger balance as the aggregation of events value-dated on or
before the current day, minus active holds; E8 therefore sees E7. An event value-dated in the future counts from its
value date only. _Test:_ `test_amb_008_a_future_dated_credit_does_not_count_for_an_authorization`.

**Rationale.** It is the same aggregation the fee rule and the closing summary read, so the ledger has one definition of
"ledger balance". A future-dated event, such as a scheduled debit, is dealt with when its day comes: it is rejected, or
it goes through and the fee rule charges the overdraft, if the funds are not there then. How a scheduled event is
refused is left for later, since the stream holds none.

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

**Status.** Resolved.

**Resolution.** An authorization is decided the moment it arrives, against the ledger balance (AMB-008) and the active
holds as they stand then, before any later event of that day. The decision is final, and an approved hold is active from
that moment. _Test:_ `test_amb_009_a_later_credit_the_same_day_does_not_change_a_decline`.

**Rationale.** A card network needs the answer when the card is presented, not at the end of the day, so the ledger can
only weigh what preceded the request. A credit arriving later that day cannot rescue a decline, which is how card
authorization works. In this stream Auth-A is approved against 250.00, leaving 50.00 available, and Auth-B declined,
since it would leave −425.00.

## AMB-010 — What a value date means on an authorization

**Where.** "E3 — Day 2 — AUTHORIZATION — ACC-001 Auth-A hold AED 200.00 — value_date Day 2", and E8 likewise.

**Why it is problematic.** A hold is an event that moves no ledger balance (AMB-024), so a value date on it has no
defined effect: it could date the hold, start its lifetime, or mean nothing. Both authorizations are value-dated on
their booked day, so no figure depends on this here.

**Options.**

- Record it and use it for nothing: a hold takes effect when approved, and a settlement's own value date dates the
  debit. **Recommended**: no rule reads it.
- The hold takes effect from its value date.

**Status.** Resolved.

**Resolution.** An approved hold reduces the available balance from the authorization's value date onwards, in the
aggregation by value date that every other event follows. The decision itself is still made on arrival (AMB-009). E3 and
E8 are value-dated on the day they are booked, so Auth-A's hold counts from Day 2, and Auth-B, declined, holds nothing.
_Test:_ `test_amb_010_a_hold_counts_from_its_value_date`.

**Rationale.** The value date is on the event, and in an event-sourced ledger every event's effect lands on its value
date; holds then follow the same rule as debits, credits, and fees, rather than being the one event whose value date
means nothing. The cost is accepted: a backdated authorization reserves funds in past days' available balances, and a
future-dated one reserves nothing until its day although the merchant already has an approval; neither occurs in this
stream.

## AMB-011 — Whether a fee counts towards later days' closings

**Where.** The fee is assessed on "all entries with value_date ≤ that day".

**Why it is problematic.** A fee can itself turn a later day negative and earn another fee, a cascade the brief neither
allows nor forbids. This stream is unaffected: every fee is value-dated Day 5 (AMB-003), so the fees for Days 2 and 4
reach no closing before Day 5's, which is negative with or without them (−385.00 or −335.00).

**Options.**

- A fee is an event like any other and counts. **Recommended**: the rule reads "all entries".
- Fees are left out of the closing the fee rule reads.

**Status.** Resolved.

**Resolution.** A fee counts. It is an event in the log like any other, so it is part of every later closing the fee
rule reads, and a day that a fee leaves negative is charged again, once, as long as its closing stays below zero.
_Tests:_ `test_amb_011_a_day_still_negative_is_not_charged_again` and
`test_amb_011_a_fee_counts_in_the_closings_after_it`.

**Rationale.** The rule reads "all entries with value_date ≤ that day", and a fee is one of them; the fee is charged
"once per day per account" for as long as a day's closing is negative, and counting fees keeps that closing the one the
report prints, so the ledger has a single aggregation. The cost is accepted: a fee can keep an account negative that its
own events would have lifted above zero, so fees can follow one another, at most one a day. No figure in this stream
moves, since Day 5 is negative with or without the fees for Days 2 and 4, and Day 5 is non-negative after E9 either way.

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

**Status.** Resolved.

**Resolution.** E6 is honoured as a force-post: it debits AED 180.00 from ACC-001, value-dated Day 4, although Auth-Z
was never authorized, and releases no hold. Day 4 closes at 285.00, and no error is reported for E6. _Test:_
`test_c4_e6_is_force_posted_for_180`.

**Rationale.** In production a settlement can arrive with no authorization in the ledger, such as an offline purchase on
a flight, a toll, or a settlement after its authorization lapsed, and card scheme rules have the issuer post it and
pursue any dispute through a chargeback rather than refuse it; the model follows production. The cost is accepted:
criterion 4's "must be rejected and the funds must not leave the account" cannot hold, so [REJECTED](REJECTED.md)
refuses it, and the model has no chargeback, so a force-post that should not have been honoured stays until a later
event reverses it.

## AMB-013 — A settlement smaller than its hold

**Where.** E3 holds AED 200.00 for Auth-A; E5: "Auth-A settles for AED 185.00".

**Why it is problematic.** The brief does not say what becomes of the unused 15.00: released at settlement, or kept on
hold. The choice changes ACC-001's available balance from Day 4 onwards.

**Options.**

- The settlement debits 185.00 and releases the whole hold. **Recommended**: keeping 15.00 on hold would reserve funds
  no merchant can still claim.
- The unused 15.00 stays on hold until it lapses (AMB-018).
- The settlement says whether it is final: a final one releases the whole hold, and one marked as followed by more
  settlements keeps the rest on hold.

**Status.** Resolved.

**Resolution.** A settlement carries whether it is final. A final settlement debits its amount and releases the whole
hold; a settlement marked as followed by more settlements debits its amount and keeps the rest on hold until a later
settlement or its lapse (AMB-018). A settlement that carries no `final` flag, as every one in the brief, is final, so E5
debits 185.00 and releases all 200.00 of Auth-A's hold. _Tests:_
`test_c3_auth_a_settlement_is_accepted_and_releases_the_hold`,
`test_amb_013_a_non_final_settlement_keeps_the_rest_of_the_hold`, and
`test_amb_013_partial_settlements_reaching_the_hold_settle`.

**Rationale.** It is how card networks settle: most transactions settle once, such as a fuel pump or a hotel bill below
its deposit, and the unused hold goes back to the customer at once, while a merchant shipping an order in parts marks
the earlier settlements as partial so the rest stays reserved for it. Releasing always would drop a later settlement's
reservation, and keeping always would lock funds no merchant claims, behind a lifetime the brief never gives. The
brief's events carry no `final` flag, so the model adds the field and treats its absence as final, which gives every
figure in this stream the same value as releasing the whole hold.

## AMB-014 — Whether rejected and declined events are recorded

**Where.** "The ledger is append-only. No event record is ever mutated or deleted." E8 is declined, and a refused event,
such as a conflicting reversal (AMB-028) or a clashing ID (AMB-034), is rejected.

**Why it is problematic.** The brief does not say whether a refused event becomes a record at all. That decides whether
the report's errors have anything to point at, and whether "append-only" covers refusals.

**Options.**

- Every incoming event is appended to the log with its outcome, and only accepted events move a balance.
  **Recommended**: discarding refused events would leave the errors with nothing to point at, and an auditor with no
  trace of what was refused.
- Refused events are discarded.

**Status.** Resolved.

**Resolution.** Every incoming event is appended to the one log with its outcome, accepted, approved, declined,
rejected, or duplicate (AMB-034), and the aggregations count only the events that were accepted or approved. E8 is in
the log as declined and moves no balance and holds nothing. A row that cannot be an event at all, such as one naming an
account that is not configured, an amount that is not positive, has more places than its currency (AMB-006), or is not
below the limit in [NUMBERS](NUMBERS.md), a day outside the window, or more instalments than its amount has minor units
(AMB-020) or than the limit in NUMBERS, is a fault in the input, not a refusal: it never reaches the log, and processing
stops with an error naming its line. _Tests:_ `test_c5_auth_b_is_declined`,
`test_amb_014_a_rejected_event_is_that_days_error`, and `test_amb_014_a_rejected_event_prints_its_refusal`.

**Rationale.** Discarding a refused event deletes an event record in all but name, which "No event record is ever
mutated or deleted" forbids. With the outcome in the log, a report line such as "Auth-B declined" points at the event
behind it, processing the log again rebuilds every report exactly, and an auditor can see what was refused, when, and
why. A second log for refusals would keep the ledger's log to money-moving events, at the cost of two sources that must
agree. A refusal is the ledger's decision against what it already holds, so it belongs in the log; a row naming an
account the ledger does not have, or an amount no event can carry, is refused by nothing the ledger holds, and logging
it would put a record in the log that no account, balance, or rule can read.

## AMB-015 — Processing order when booked days are out of sequence

**Where.** "Event stream, replayed in this order", but E10 (booked Day 5) is listed after E9 (booked Day 6).

**Why it is problematic.** Following the list literally processes a Day 5 event on Day 6, which is either a late,
backdated arrival or an error; following the booked days departs from "in this order". E9 touches only ACC-001 and E10
only ACC-002, so the two commute: ACC-001 is identical under every option, and only ACC-002's day-by-day view and
possibly its interest change.

**Options.** Figures are ACC-002, in BHD, with interest as AMB-005 resolves it.

| Option                             | Day 5 report | Day 6 report           | Interest |
| ---------------------------------- | ------------ | ---------------------- | -------- |
| Sort by booked day (E10 before E9) | 10.000       | 10.008                 | 0.008    |
| Listed order; E10 late, backdated  | 0.000        | 10.008; Day 5 restated | 0.008    |
| Listed order; E10 rejected         | 0.000        | 0.000, plus an error   | 0.000    |

In the late-arrival option, E10 is processed on Day 6 with value date Day 5, so Day 6's report restates Day 5 to 10.000
and generates an interest adjustment of 0.004 for Day 5.

**Recommended**, held loosely: sort by booked day. The booked day is a business fact about when the bank recorded the
event, while list position is presentation; because the events commute, the deviation from "in this order" changes no
account balance. The late-arrival reading is the strongest alternative: it honours the wording literally and reuses the
backdating machinery E7 and E9 already need.

**Status.** Resolved.

**Resolution.** The stream is processed in the order it is listed. E10, booked Day 5, arrives after E9 and after Day 5
has closed, so it is processed on Day 6 as a late event value-dated Day 5: Day 5's report shows ACC-002 at 0.000, and
Day 6's restates its Day 5 to the instalments value-dated Day 5 and generates Day 5's interest as an adjustment. A day
closes on time and never waits for an event that may still come. _Test:_
`test_amb_015_a_late_event_is_processed_on_the_current_day`.

**Rationale.** The listed order is the order the ledger receives events, and in production that order is guaranteed only
within a partition, typically per account: E9 on ACC-001 and E10 on ACC-002 can arrive in either order, and a lagging
consumer delivers E10 after E9. Waiting for a partition to catch up before closing a day needs a sign that it has, and
ACC-002 sends no later event to give one, so a close would wait forever or time out and still meet late events. Closing
on time and handling a late event as backdated reuses the machinery E7 and E9 already need, and follows the rule that an
event is recognised when it arrives. Rejecting E10 would take a customer's credit for an ordering fault that is not
theirs. ACC-001 is identical under every option, since E9 and E10 touch different accounts.

## AMB-016 — When a retroactive fee is booked

**Where.** Criterion 1: "evaluated at end of Day 5 and before any fee is assessed". Nothing says whether a fee is
assessed the moment a backdated event arrives or at the close of the day it arrives on.

**Why it is problematic.** Assessed on arrival, retroactive fees land mid-day, before later events such as E8; assessed
at day close, they come after. That changes the available balance Auth-B is checked against (−425.00 without the fees,
−475.00 with the Day 2 and Day 4 fees; declined either way, AMB-021), and what "before any fee" in criterion 1 means.

**Options.**

- At day close. **Recommended**: criterion 1's "at end of Day 5 and before any fee is assessed" only makes sense if
  assessment is a day-close step.
- The moment the backdated event arrives.

**Status.** Resolved.

**Resolution.** Fees and their refunds are generated only in the end-of-day fee step, as events in the log, after every
event booked that day; a backdated event that arrives mid-day assesses nothing until its day closes. E7's fees are
generated at the close of Day 5, after E8. _Test:_ `test_c2_e7_causes_three_fees_all_value_dated_day_5`.

**Rationale.** A fee is an event the ledger generates at the end of the day, as a production ledger runs its fee job at
day close, not a side effect of whichever event happens to arrive. Criterion 1's "evaluated at end of Day 5 and before
any fee is assessed" describes exactly that moment. Auth-B is then checked against −425.00, without the fees, and is
declined either way (AMB-021).

## AMB-017 — Whether the E10 instalments are spread over days

**Where.** E10: "BHD 10.000, posted as three equal instalments — value_date Day 5".

**Why it is problematic.** The word "instalments" usually means payments over time, but E10 gives one value date.
Spreading them over Days 5, 6, and 7 would put the third outside the window and change ACC-002's interest from 0.008 to
0.004 (0.001 on 3.333, then 0.003 on 6.666).

**Options.**

- All three instalments value-dated Day 5. **Recommended**: it is the value date E10 states.
- One instalment on each of Days 5, 6, and 7.

**Status.** Resolved.

**Resolution.** All three instalments are value-dated Day 5, the value date E10 states: E10 is posted as three credit
events of 3.333, 3.333, and 3.334 (AMB-020), each value-dated Day 5. _Test:_ `test_c7_e10_posts_3_333_3_333_3_334`.

**Rationale.** The brief does not say what unit the instalments are spread over, days, weeks, or months, so any schedule
would be invented, and it would contradict the one value date E10 does give. Reading "instalments" as how the credit is
posted, three events rather than one, takes the brief at its word without concluding anything it does not say.

## AMB-018 — How long a hold lives

**Where.** "Auth-B is never settled inside the window." No hold lifetime is given.

**Why it is problematic.** An unsettled hold would reduce available balance indefinitely. In this stream no hold is left
open: Auth-B is declined, and Auth-A is settled finally, so AMB-013 keeps none of its hold.

**Options.**

- No expiry inside the window, and this is the design limitation the deliberately failing test exposes: a hold that
  should lapse never does. **Recommended**: the brief gives no lifetime to model.
- A fixed lifetime after which an unsettled hold lapses.

**Status.** Resolved.

**Resolution.** No hold expires: an approved hold stays active until a settlement releases it. This is the design
limitation the deliberately failing test exposes: it processes a hold left unsettled past a card network's usual
lifetime and asserts that the hold has lapsed, which it never does. The fix, a lifetime after which the ledger generates
a hold-expiry event, is described in the architecture document. _Test:_
`test_known_weakness_an_unsettled_hold_never_expires`.

**Rationale.** The brief gives no hold lifetime, and any number would be invented and would need its own defence in
NUMBERS; a lifetime of six days or more would change nothing in this window anyway. The brief also asks for "One failing
test against your own design", and a hold that never lapses is a real, easily explained weakness: in production it locks
a customer's funds for as long as a merchant never claims them. No figure in this stream moves, since Auth-A is settled
finally and Auth-B holds nothing.

## AMB-019 — Whether a declined authorization is an "authorization state" or an "error"

**Where.** The report "prints, per day: closing ledger balance, fee assessments, authorization states, and errors".

**Why it is problematic.** A declined authorization fits either heading, and where it goes changes Day 5's errors line.

**Options.**

- A state (`DECLINED`), while an event the ledger cannot carry out, such as a rejected settlement, is an error.
  **Recommended**: declining is the rule working as intended; a rejected settlement is an instruction the ledger could
  not carry out.
- An error.

**Status.** Resolved.

**Resolution.** A declined authorization is an authorization state, printed with the others, and Auth-B shows as
declined from Day 5. The errors line is kept for events the ledger cannot carry out, and no event in this stream is one,
so every day's errors line reads none. _Test:_ `test_amb_019_every_known_authorization_is_listed_with_its_state`.

**Rationale.** The brief lists "authorization states" apart from "errors", and declined is one of an authorization's
states, beside approved and settled. A decline is the approval rule working as intended, since Auth-B would leave the
available balance at −425.00; reporting it as an error would mix a business outcome with a failure to process, and hide
real failures among routine declines.

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

**Status.** Resolved.

**Resolution.** An amount posted as N equal instalments gives each instalment the amount divided by N, rounded down to
the currency's precision, and adds what remains to the last one. E10's BHD 10.000 is 3.333, 3.333, and 3.334. Every
instalment must be at least one minor unit, so a credit split into more instalments than its amount has minor units,
such as BHD 0.002 in three, is refused as a fault in the input (AMB-014). _Tests:_
`test_amb_020_ten_bhd_splits_3_333_3_333_3_334` and `test_more_instalments_than_minor_units_are_refused`.

**Rationale.** No three-decimal amount divides 10.000 into three, so exact instalments need one to differ. Rounding down
and giving the last the remainder keeps the sum at exactly 10.000, invents no money, and works for any N and precision
that leaves each instalment at least one minor unit; rounding down, rather than half-even (AMB-006), keeps the remainder
from ever being negative. Criterion 7's 3.334 each sums to 10.002, crediting 0.002 BHD that E10 never posted, so it
cannot hold, and [REJECTED](REJECTED.md) refuses it.

## AMB-021 — Auth-B: declined, yet "never settled"

**Where.** "Auth-B is never settled inside the window"; criterion 5: "If Auth-B is approved, its hold reduces available
balance but not ledger balance."

**Why it is problematic.** The wording suggests Auth-B was approved, but the ledger declines it: E7 lands earlier on Day
5 than E8, so available balance at E8 is −335.00 − 90.00 = −425.00. Without E7 it would have been 195.00 and approved.
Criterion 5 is a conditional whose premise is false here, and this entry decides it.

**Options.**

- Accept criterion 5 as a statement of hold semantics, prove those semantics with Auth-A (ledger 250.00, available 50.00
  on Day 2), and state that Auth-B never holds anything: the criterion is vacuously true.
- Reject criterion 5, because its premise never holds.
- Reject criterion 5 as a claim about this stream, and still test the hold semantics it describes with Auth-A.
  **Recommended**: accepting it vacuously passes over the trap, and rejecting it outright reads as rejecting a hold rule
  the ledger does follow.

**Status.** Resolved.

**Resolution.** Criterion 5 is refused as a claim about this stream, and the hold semantics it describes are tested with
Auth-A instead: on Day 2 Auth-A's hold of 200.00 leaves the ledger balance at 250.00 and the available balance at 50.00.
The refusal and its reason are recorded in [REJECTED](REJECTED.md). _Tests:_ `test_c5_auth_b_is_declined` and
`test_c5_a_hold_reduces_available_balance_but_not_ledger_balance`.

**Rationale.** The criterion describes Auth-B approved, and the ledger declines it, since E7 lands before E8 on Day 5
and leaves an available balance of −425.00; a criterion about an event that never happens cannot be checked against this
stream, and accepting it as vacuously true would pass over what the brief is testing. The rule it states, that a hold
reduces available balance and not ledger balance, is still the ledger's rule, so a test pins it with the one hold that
does exist.

## AMB-022 — What a day's report shows once backdated events exist

**Where.** The report "prints, per day: closing ledger balance …", alongside value-dated events that arrive days late
(E7, E9).

**Why it is problematic.** Once E7 and E9 rewrite past days, the closing for Day N can mean what was known at the end of
Day N or what the ledger holds for Day N later. After E7, Day 2 reads 250.00 as known on Day 2 but −370.00 as restated
on Day 5, and an authorization decision can look inconsistent with the balance printed beside it.

**Options.**

| Option                          | What Day N's report shows                                                    |
| ------------------------------- | ---------------------------------------------------------------------------- |
| Point-in-time, with restatement | what was known at end of Day N, plus restated closings a backdated event hit |
| Hindsight only                  | one final table by value date, printed after the whole stream                |
| Point-in-time, plus final table | what was known at end of Day N; one hindsight table after Day 6              |

**Recommended**: point-in-time with restatement. Each authorization decision stays explainable from the balance it
actually saw, it matches criterion 1's framing ("evaluated at end of Day 5"), and each restatement appears on the day it
happened. Hindsight only makes Auth-A's Day 2 approval look inconsistent with a restated Day 2 of −370.00; a final table
alone hides each restatement from the day it happened.

**Status.** Resolved.

**Resolution.** Point-in-time, with restatement. Each day's report shows the ledger as known at the end of that day, and
when a backdated event changes an earlier closing, that day's report adds a restated closing for each earlier day it
changed. Day 5 prints Day 2 restated to −370.00, Day 3 to 30.00, and Day 4 to −335.00; Day 6 prints them back at 250.00,
650.00, and 285.00, and Day 5 at 210.00. No earlier report is reprinted, and no final table is added. _Test:_
`test_amb_022_a_day_restates_each_earlier_closing_it_changed`.

**Rationale.** The ledger is an append-only log, and a day's report is the aggregation over that log at the end of the
day (AMB-024): what was printed on Day 2 stays what was known on Day 2, and a late event shows up on the day it arrives,
as a restatement. Every authorization decision then stays explainable from the balance it actually saw, Auth-A's Day 2
approval against 250.00 among them, and criterion 1's "evaluated at end of Day 5" reads straight off Day 5's report.

## AMB-023 — End-of-day ordering and the Day 6 capitalization

**Where.** "Accruals capitalize as a single credit at end of Day 6", while fees are assessed on each day's closing. No
order is given for what happens at the end of a day.

**Why it is problematic.** Fees, fee refunds, interest, and capitalization all happen at the end of a day. Their order
decides whether interest accrues on the closing before or after that day's fees, and whether Day 6's accrual includes
the capitalization credit.

**Options.**

- Fee re-evaluation, which generates new fees and refunds any whose day is no longer negative (AMB-004); then the
  interest step, which generates the day's accrual on the resulting closing and any adjustment (AMB-005); then, on Day 6
  only, capitalization as one credit value-dated Day 6. **Recommended**: interest then accrues on the closing the fee
  rule leaves, and never on itself; the printed Day 6 closing includes the credit.
- Interest accrual before fee re-evaluation.
- Capitalization before Day 6's accrual.

**Status.** Resolved.

**Resolution.** Every day closes in three steps: fee re-evaluation, then interest, then, on Day 6 only, capitalization.
On Day 6 the refunds for Days 2, 4, and 5 are generated first and bring ACC-001 to 285.00; interest then accrues 0.11
for Day 6 and generates the adjustments E9 makes due; capitalization last credits every accrual, AED 0.76 as
`CAP-001@D6` and BHD 0.008 as `CAP-002@D6`, both value-dated Day 6. Day 6 closes at 285.76 and 10.008. _Tests:_
`test_amb_023_a_days_interest_never_counts_its_own_capitalization` and `test_c6_day_6_closes_at_285_76_not_285_79`.

**Rationale.** Accrual is interest earned and recorded, capitalization is that interest paid into the balance, as a day
worker's wages are recorded daily and paid on payday. Interest then accrues on the closing the fee rule leaves: accruing
first would earn on 210.00, a balance still carrying three fees the same day's step refunds, and pay 0.73. Capitalizing
last pays everything accrued in the window, as "Accruals capitalize as a single credit at end of Day 6" asks; before Day
6's interest step it would pay AED 0.11 and BHD 0.000, and leave AED 0.65 and BHD 0.008 accrued but never credited. The
rounded accruals then sum exactly to each capitalized total.

## AMB-024 — What "append-only" covers

**Where.** "The ledger is append-only. No event record is ever mutated or deleted."

**Why it is problematic.** Authorizations change state, holds are released, and balances change daily. If those are
stored as fields updated in place, the ledger mutates records in spirit while keeping every event record intact; the
brief does not say how far "record" reaches.

**Options.**

- Every event, from the brief or generated by the ledger, is immutable; balances, holds, and authorization states are
  derived by folding over them and never stored as mutable fields; every state change, such as a hold settled or a fee
  refunded, is a new record. **Recommended**: nothing the ledger holds can then be edited.
- Only event records are immutable; derived state is stored and updated in place.

**Status.** Resolved.

**Resolution.** The ledger is event-sourced, as AMB-004 records: every event, from the brief or generated by the ledger,
is appended to a log and never mutated or deleted; balances, holds, and authorization states are aggregations over the
log, never stored as mutable fields; and every change, such as a hold settled, a fee refunded, or interest corrected, is
a new event. An event the ledger generates is named by kind, account, the day it is for, and the day it is generated,
such as `FEE-001-D2@D5`, and a step that would move nothing generates no event. _Test:_
`test_a_generated_id_prints_its_kind_account_and_days`.

**Rationale.** "No event record is ever mutated or deleted" then holds in spirit as well as in letter, because nothing
the ledger holds is edited in place, and any day's view can be rebuilt by processing the log again. A backdated event, a
refund, or an interest correction is a new event that every aggregation picks up. The generated ID keeps the ledger's
own events apart from E1 to E10 and stays stable when a late event adds or removes a generated event, where a running
number would shift; generating nothing when nothing moves keeps the log to events that change a balance, as interest
accrues on "positive balances only".

## AMB-025 — What each day's report lists

**Where.** The report "prints, per day: closing ledger balance, fee assessments, authorization states, and errors".

**Why it is problematic.** The sentence fixes the categories but not their scope: per account or overall, on days with
no activity, and whether an authorization appears only on the day it changes or on every day it is known.

**Options.**

- Per account, every day, even with no activity; fees listed on the day they are assessed, each with its own value date,
  so Day 5 lists the Day 2, 4, and 5 fees; every known authorization with its state at end of day (so Auth-A shows its
  active hold on Day 3); and that day's errors. **Recommended**: every figure can be checked on every day.
- Only what changed that day. Shorter, but it hides an active hold on days it does nothing.

**Status.** Resolved.

**Resolution.** Every day's report lists both accounts, each in its own currency, even on a day with no activity; every
authorization known by the end of that day, with its state then; the fees and refunds generated that day, each naming
the day it is for; and that day's errors, or none. Day 3 therefore shows Auth-A approved with its hold of 200.00, and
ACC-002 prints 0.000 on Days 1 to 4. _Tests:_ `test_amb_019_every_known_authorization_is_listed_with_its_state` and
`test_the_brief_stream_prints_output_target`.

**Rationale.** Each day's report then stands on its own: Day 3's available balance of 450.00 is explained by the hold
printed beside it, and no figure needs an earlier report to be checked. ACC-001 and ACC-002 hold different currencies,
so their balances cannot be combined into one line. Printing only what changed would be shorter, but it would drop
Auth-A from Day 3 and leave the 200.00 gap between closing and available unexplained.

## AMB-026 — Test suite or script

**Where.** "It must be exercised by a runnable test suite or script that replays the event stream and prints, per day".

**Why it is problematic.** The "or" allows either. A script alone asserts nothing, and a test suite that prints mixes
assertion with presentation.

**Options.**

- Both: the command-line program processes the stream and prints the daily report, and the test suite processes the same
  stream and asserts every figure. **Recommended**: each does one job.
- A test suite that prints.
- A script only.

**Status.** Resolved.

**Resolution.** Both. The command-line program, `account-ledger-cli`, processes the stream and prints the daily report
exactly as [OUTPUT_TARGET](OUTPUT_TARGET.md) shows it. The test suite processes the same stream and asserts every
figure: plain pytest unit and integration tests assert each criterion and each resolved rule, each by at least one named
test, and an end-to-end test runs the program through its process boundary and compares its output with OUTPUT_TARGET.
_Test:_ `test_the_brief_stream_prints_output_target`.

**Rationale.** Each does one job: the program shows the report, and the tests prove it. A script alone asserts nothing,
so a Day 6 closing of 285.73 instead of 285.76 would fail nothing; a test suite that prints buries the report in test
output and leaves nothing a reader can run to see it. The repository already holds both, a runnable app and three test
levels, and the failing test the brief asks for needs a suite to live in. The tests are plain pytest, not Gherkin: each
criterion has at least one named test whose docstring quotes it, so step bindings would add a second language without
adding a reader ([REJECTED](REJECTED.md)).

## AMB-027 — An overdraft fee on a BHD account

**Where.** "Overdraft fee: AED 25.00, assessed once per day per account", while ACC-002 is in BHD.

**Why it is problematic.** The fee has no BHD amount, and converting it needs an exchange rate the brief does not give.
ACC-002 never goes negative in this stream, so this is not triggered.

**Options.**

- Define the fee for AED only, convert nothing, and report a negative BHD closing as an error saying that no overdraft
  fee is configured for BHD. **Recommended**: it invents neither an amount nor a rate.
- Convert AED 25.00 at a chosen rate.
- Charge BHD 25.000.

**Status.** Resolved.

**Resolution.** Convert AED 25.00 at a fixed rate of 1 AED = 0.10238257 BHD, the mid-market rate XE showed on 2026-09-24
at 12:32 UTC: 25.00 × 0.10238257 = 2.55956425, rounded half-even to BHD 2.560 (AMB-006). A BHD account is charged BHD
2.560 on each negative day, under the same rules as an AED account. The rate and the fee are recorded in
[NUMBERS](NUMBERS.md) as chosen constants. ACC-002 never goes negative in this stream, so no figure moves. _Tests:_
`test_amb_027_the_bhd_fee_is_2_560` and `test_amb_027_a_bhd_account_is_charged_bhd_2_560`.

**Rationale.** "Assessed once per day per account" reaches every account, so a BHD account is charged too, and the fee's
value is kept in the currency it is charged in. Charging BHD 25.000 would cost about ten times as much. The rate is
taken once and fixed, not read daily, because the ledger is in-memory and never reaches the network. It matches the
cross rate of the two US dollar pegs, 0.376 BHD and 3.6725 AED, to seven decimal places, so it is unlikely to drift.

## AMB-028 — Reversing a reversal

**Where.** E9 "reverses E7"; the brief does not say what a reversal may target. Not in this stream.

**Why it is problematic.** Reversing a reversal, or reversing the same event twice, would let a debit be undone more
than once.

**Options.**

- Idempotent, with conflicts refused: the same reversal arriving again, under the same event ID, is recognised as
  already processed and has no effect and no error; a different reversal of an event already reversed is refused and
  reported as an error; a reversal of a reversal is refused, and a mistaken reversal is corrected by a new event.
  **Recommended**: a debit can then be undone at most once, a retry raises no false alarm, and a conflict stays visible.
- Refuse every second reversal alike, repeated or new, as an error, and refuse a reversal of a reversal.
- Allow a reversal only of an event still in effect, so a reversal of a reversal reinstates the original.
- Allow everything, so a debit can be undone more than once.

**Status.** Resolved.

**Resolution.** Idempotent, with conflicts refused. A reversal arriving again under an event ID already processed, with
the same content, such as E9 delivered twice, is the same event (AMB-034): it has no effect and is not an error. A new
reversal of an event already reversed, such as an E12 that reverses E7 after E9, is refused, recorded in the log with
its outcome (AMB-014), and printed as that day's error. A reversal whose target is itself a reversal is refused the same
way; a mistaken reversal is corrected by a new debit or credit that names what it corrects. Neither case occurs in this
stream, so no figure moves. _Tests:_ `test_amb_028_a_reversal_of_a_reversal_is_refused`,
`test_amb_028_a_second_reversal_of_the_same_event_is_refused`, and
`test_amb_034_a_repeated_reversal_or_settlement_is_a_duplicate`.

**Rationale.** In production a reversal names the event it undoes, and each event is undone at most once. A reversal
sent again after a timeout is routine, so treating it as an error would raise false alarms, while a second, different
reversal of the same event is a conflict someone must see. Correcting a mistaken reversal with a new event, rather than
reversing the reversal, keeps the log readable: each event has one purpose, and no chain of reversals has to be followed
to know what is in effect. AMB-034 extends the same rule to every kind of event.

## AMB-029 — A settlement against a declined or already-settled authorization

**Where.** Criterion 4 covers "an authorization ID not present in the ledger". Not in this stream.

**Why it is problematic.** An ID that is present but declined or already settled has no active hold, and criterion 4 is
silent on it.

**Options.**

- Accept, as a force-post, as AMB-012 resolves for an unknown ID. **Recommended**: a merchant claiming against an
  authorization the ledger knows has at least as good a claim as one the ledger has never seen, as with a second
  settlement for a split shipment; rejecting it while honouring E6 would treat the stronger claim worse.
- Reject, and debit nothing: without an active hold there are no reserved funds to settle against.

**Status.** Resolved.

**Resolution.** Accept, as a force-post. A new settlement against an authorization that was declined, or whose hold a
final settlement already released, posts its debit and releases no hold, as E6 does (AMB-012). The same settlement
delivered again is a retry and has no effect (AMB-034), and one after a settlement marked partial meets the hold that
remains (AMB-013). Neither case occurs in this stream, so no figure moves. _Tests:_
`test_amb_029_a_settlement_after_a_final_one_is_force_posted`,
`test_amb_029_a_settlement_against_a_declined_authorization_is_force_posted`, and
`test_amb_034_a_repeated_reversal_or_settlement_is_a_duplicate`.

**Rationale.** E6 is honoured though the ledger has never seen its authorization, so a merchant whose authorization the
ledger does know cannot be treated worse; refusing it would give the weaker claim the better outcome. Second settlements
occur in production, as with a split shipment or an offline transaction. The debit can take the balance negative and
incur the overdraft fee, exactly as E6 could.

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

**Status.** Resolved.

**Resolution.** Accept and debit the full amount. A settlement above its hold posts its whole amount and releases the
hold, as AMB-013 resolves; the balance may go negative, and the fee rule then applies as for any negative day. Nothing
settles above its hold in this stream, so no figure moves. _Test:_
`test_amb_030_a_settlement_above_its_hold_debits_in_full`.

**Rationale.** In production the authorization reserves funds and the settlement moves them: by the time a settlement
reaches the bank, the card network has already paid the merchant, so the ledger records the full amount or stops
matching the money that moved. Settling above the hold is routine, as with a restaurant tip, a fuel pump, or a hotel
minibar, and card schemes allow it within limits; an excess beyond them is disputed through a chargeback, outside the
ledger core, not refused at posting. A settlement with no hold at all is honoured (AMB-012, AMB-029), so one with a
smaller hold cannot be refused. The cost is that a customer can be charged above what was approved, and the bank carries
the risk of a negative balance.

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

**Status.** Resolved.

**Resolution.** Mark it as an expected failure in the regular suite, with `@pytest.mark.xfail(strict=True, reason=…)`,
the reason naming the weakness AMB-018 records: holds never expire. The test runs on every push, its assertion fails,
and pytest reports it as `XFAIL`, so the run stays green; once the weakness is fixed the test passes, pytest reports
`XPASS(strict)`, and the run turns red until the marker is removed. Through Rules Propagation, the guard on every test
target no longer refuses `mark.xfail` but refuses `strict=False`, so every expected failure is strict, and the
test-driven development rule that a deliberately failing test is "never a finished state" carries an exception for a
strict expected failure that records a known design weakness. _Test:_
`test_known_weakness_an_unsettled_hold_never_expires`.

**Rationale.** An expected failure is the idiomatic pytest form for a known weakness: the test is still run, its failure
is still observed, and its `reason` is the inline annotation the brief asks for. Strict mode keeps the marker honest,
since a fix cannot go unnoticed. The cost is that the run is green, where the brief says "One failing test", so the
report must point the reader to the `XFAIL` line. The repository forbids marking an intermittent test as an expected
failure; this one fails deterministically, by design, so that rule does not reach it.

## AMB-032 — Which constants belong in NUMBERS

**Where.** "NUMBERS.md — every constant you chose, why that value and not half it".

**Why it is problematic.** Most constants are given by the brief, and halving a given constant breaks a rule, so asking
why not half of it does not apply to them; listing only chosen constants hides the values that drive most figures.

**Options.**

- List both, marked given or chosen: a given constant's entry says what the value drives, and only chosen constants
  argue why that value and not half it. **Recommended**: every value a figure rests on is then in one place.
- List chosen constants only.

**Status.** Resolved.

**Resolution.** List both, marked given or chosen, as [NUMBERS](NUMBERS.md) already does: a given constant's entry says
what its value drives, and every chosen constant argues why that value and not half it.

**Rationale.** The brief's question, why that value and not half it, is answered for every constant chosen here, as it
asks. The given constants, the fee, the rate, the precisions, and the capitalization day, drive most figures in
[MOVEMENT](MOVEMENT.md); listing them beside the chosen ones, clearly marked, lets a reader derive any figure from one
file without going back to the brief.

## AMB-033 — What the report prints beyond the four named items

**Where.** The report "prints, per day: closing ledger balance, fee assessments, authorization states, and errors".

**Why it is problematic.** The brief does not say whether the report may print more. Without the available balance,
Auth-A's approval and Auth-B's decline cannot be checked from the output, and without the events and end-of-day steps no
closing can be traced to what moved it.

**Options.**

- Also print, for each day, the events processed, every end-of-day step with the events it generates (fees, fee refunds,
  interest accruals and adjustments, and the capitalization), and each account's available balance. **Recommended**:
  every printed figure can then be verified from the output alone.
- Exactly the four items.

**Status.** Resolved.

**Resolution.** The report prints the four named items and more. Each day prints three tables: the events processed;
every end-of-day step with the events it generates, fees, fee refunds, interest accruals and adjustments, and the
capitalization; and a closing summary with the closing ledger balance, the available balance, any restated earlier
closings (AMB-022), authorization states, and errors, for both accounts (AMB-025). Each day opens with a banner, its
name between two full-width lines of `=`, and every table is drawn as a plain-text box, with `+`, `-`, and `|` borders,
as [OUTPUT_TARGET](OUTPUT_TARGET.md) shows; a block with nothing in it prints none. _Tests:_
`test_amb_033_a_step_that_generates_nothing_reports_its_row` and `test_the_brief_stream_prints_output_target`.

**Rationale.** The brief's "prints, per day" names what the report must hold, not everything it may. With only the four
items, Auth-B's decline could not be checked without the available balance, and Day 5's −410.00 and its fee for Day 2
could not be traced to E7; with the events and steps printed, every figure can be verified from the output alone. The
banners mark where one day ends and the next begins, and drawing each table as a box keeps its columns readable in a
terminal while staying plain text.

## AMB-034 — An event whose ID arrives twice

**Where.** Every event in the stream carries an ID, such as "E4 — Day 3 — CREDIT — ACC-001 AED 400.00 — value_date Day
3", and "The ledger is append-only. No event record is ever mutated or deleted." Not in this stream.

**Why it is problematic.** The brief does not say whether an event ID can arrive twice, as a retry after a timeout would
send it. Appending E4 a second time would credit 400.00 twice; refusing it as an error would raise an alarm for a
routine retry. AMB-028 settles this for a reversal only.

**Options.**

- Idempotent by event ID: an ID already in the log, with the same content, is recognised as already processed and has no
  effect and no error; the same ID with different content is refused and reported as an error. **Recommended**: it
  extends AMB-028's rule to every kind of event, so a retry never moves a balance twice and a clash stays visible.
- Refuse every repeated ID as an error, whatever its content.
- Append every event as it arrives, so a repeated ID moves the balance again.

**Status.** Resolved.

**Resolution.** Idempotent by event ID. The event ID is the idempotency key: an event whose ID is already in the log,
with the same content in every field, is appended with the outcome duplicate (AMB-014), has no effect, and is not an
error; one whose ID is already in the log with different content, the booked day included, is refused, recorded with its
outcome (AMB-014), and printed as that day's error. The rule covers every event, from the brief or generated by the
ledger, and AMB-028's rule for a repeated reversal is this rule applied to a reversal. Nothing repeats in this stream,
so no figure moves. _Tests:_ `test_amb_034_a_repeated_event_is_logged_as_a_duplicate_with_no_effect`,
`test_amb_034_a_repeated_reversal_or_settlement_is_a_duplicate`,
`test_amb_034_a_reused_id_with_different_content_is_refused`, and
`test_amb_034_the_same_event_booked_another_day_is_refused`.

**Rationale.** An event already carries an ID, so it is the natural key: a retry after a timeout delivers the same ID
and content and must not move a balance twice, and an alarm for it would be false. The same ID with different content
cannot be a retry, so dropping it silently could lose a real transaction; it is a clash someone must see. The ledger's
own generated IDs, such as `FEE-001-D2@D5`, are built from kind, account, and days (AMB-024), so re-running a day's
close generates the same IDs and cannot charge a fee twice. Appending the retry as a duplicate keeps every delivery in
the log, so an auditor sees that a retry arrived and when, and processing the log again shows it moved nothing. The rule
relies on the sender keeping IDs unique, which the brief does not state; a sender that reuses an ID for a new event sees
it refused, not applied.

## AMB-035 — What a reversal may target

**Where.** "E9 — Day 6 — REVERSAL — ACC-001 reverses E7 — value_date Day 2", with "No event record is ever mutated or
deleted." E7 is a debit, and nothing else is reversed in this stream.

**Why it is problematic.** The brief does not say which events a reversal may undo: an unknown ID, a declined or refused
event, an authorization, or an event the ledger generates itself, such as a fee, an interest event, an instalment, or a
capitalization. Reversing a fee whose day is still negative also meets the fee rule, which would charge that day again.

**Options.**

- Only an accepted incoming credit, debit, or settlement, anything else refused. **Recommended**: the ledger corrects
  its own events by re-evaluating them, so reversing one would fight the rule that generated it.
- Any accepted incoming posting, plus an approved authorization, whose reversal releases its hold, as a card void does.
- Any accepted event, incoming or generated; after a generated end-of-day event is reversed, the next close generates
  again whatever the rules still require.
- Any accepted event, with a reversed generated event waived and never generated again.

**Status.** Resolved.

**Resolution.** Any accepted event, incoming or generated, may be reversed. A reversal of an unknown ID, or of an event
that moved no money, declined or rejected, is refused, recorded with its outcome (AMB-014), and printed as that day's
error; an authorization is approved, never accepted, so a reversal of one is refused the same way, a reversal of a
reversal stays refused (AMB-028), and so does one whose target is on another account (AMB-036). Each event's money is
undone at most once, whichever event undoes it: a reversal is refused when its target is an instalment of a credit
already reversed, a credit one of whose instalments is already reversed, or a fee already refunded. A refund may itself
be reversed, which puts its fee back in force for the next close to judge again. A reversal undoes only what its target
moved, so a reversed settlement leaves its authorization's state and hold as they are, and reversing a credit posted in
instalments undoes every instalment. After a fee, an interest event, or a capitalization is reversed, the next close
re-evaluates as always and generates again whatever the rules still require, under a new generated ID for that close: a
fee reversed while its day is still negative is charged again. An instalment is generated when its credit is processed,
not at a close, so a reversed instalment stays reversed. None of this occurs in this stream, so no figure moves.
_Tests:_ `test_amb_035_a_capitalization_reversed_on_its_own_day_leaves_that_days_interest`,
`test_amb_035_a_fee_reversed_on_a_negative_day_is_charged_again`,
`test_amb_035_a_reversal_of_an_event_that_moved_no_money_is_refused`,
`test_amb_035_a_reversal_of_an_unknown_event_is_refused`, `test_amb_035_a_reversal_undoes_what_its_target_moved`,
`test_amb_035_a_reversed_capitalization_returns_its_interest_to_accrued`,
`test_amb_035_a_reversed_instalment_stays_reversed`, `test_amb_035_a_reversed_interest_event_is_generated_again`,
`test_amb_035_a_reversed_refund_puts_its_fee_back_in_force`,
`test_amb_035_a_reversed_settlement_leaves_its_authorization_settled`,
`test_amb_035_money_already_undone_cannot_be_undone_again`, and
`test_amb_035_reversing_a_credit_in_instalments_undoes_every_instalment`.

**Rationale.** In production an operations team corrects any posted entry, whether a customer sent it or the bank
generated it, through the same reversal path, so one rule for every accepted event keeps the log uniform: each
correction is an event that names what it undoes. Letting the end-of-day rules re-evaluate afterwards keeps them the
only source of fees and interest, so no balance is left that the rules disagree with; waiving a fee for good is a
separate decision the ledger does not model, and the architecture trade-offs record it as a simplification. Refusing a
reversal of something that moved no money keeps a mistake visible instead of logging an undo of nothing.

## AMB-036 — A reversal whose target is on another account

**Where.** "E9 — Day 6 — REVERSAL — ACC-001 reverses E7 — value_date Day 2". Every event row names an account, a
reversal's included, and E9 and its target E7 are both on ACC-001. Not otherwise in this stream.

**Why it is problematic.** The brief does not say whether a reversal may name an event on another account. An event ID
is unique across the ledger (AMB-034), so the target can be found wherever it is, but the reversal's own row names an
account too. Undoing the money on the reversal's account moves a balance that never held it, and in another currency it
cannot be summed at all; undoing it on the target's account overrides what the row says.

**Options.**

- Refuse it, with its own reason naming both accounts. **Recommended**: a correction belongs on the account that holds
  the entry it corrects, and a row naming the wrong account is an input error best shown as one.
- Refuse it as an unknown target, since the reversal's account does not hold the event.
- Apply it to the target's account, whatever account the reversal's row names.

**Status.** Resolved.

**Resolution.** Refused with its own reason. A reversal whose target is in the log but on another account is refused
once the target is found, before the other checks of AMB-028 and AMB-035; it is recorded with its outcome (AMB-014),
moves neither account's balance, and prints as that day's error, `E12 refused: E7 is on ACC-001, not ACC-002`. The
target stays reversible by a reversal on its own account. None of this occurs in this stream, so no figure moves.
_Tests:_ `test_amb_036_a_reversal_of_another_accounts_event_is_refused`.

**Rationale.** Each account's balance, holds, fees, and interest are its own, so an entry that undoes money has to sit
on the account that holds that money, or the account's own history no longer explains its balance. Refusing as an
unknown target would tell the operator that E7 is missing when it is not, and applying the reversal elsewhere would let
a row's account column be wrong without anyone seeing it; a named refusal points at the one field to correct.

## AMB-037 — A reversal value-dated apart from its target

**Where.** "E9 — Day 6 — REVERSAL — ACC-001 reverses E7 — value_date Day 2". E9 carries its own value date, and it is
E7's, so the two coincide in this stream.

**Why it is problematic.** The brief does not say what a reversal's value date does when it differs from its target's.
Counted from its own value date, a reversal dated before its target credits the money back on days the target never
debited: a reversal dated Day 2 of a debit dated Day 3 would restate Day 2 above anything the account ever held. Dated
after it, the target's effect stands on the days between. Ignoring the reversal's date always undoes the target in full,
but leaves a column of the row meaning nothing.

**Options.**

- Refuse a reversal dated before its target; one on or after its target's value date undoes it from its own date.
  **Recommended**: no day is ever credited with money its target never moved, and a later-dated correction stays
  possible, as when a bank corrects an entry only from the day the error is found.
- Count every reversal from its target's value date, whatever its own row says.
- Count every reversal from its own value date, as the row gives it.

**Status.** Resolved.

**Resolution.** A reversal value-dated before its target is refused. It is checked once the target is known to be in the
log, to have moved money, and to be neither a reversal nor already reversed (AMB-028, AMB-035), and before any part of
it is found already undone. The refusal is recorded with its outcome (AMB-014), moves no balance, and prints as that
day's error, `E12 refused: E7 is value-dated later, Day 3`. A reversal dated on or after its target's value date is
posted and undoes the target from its own value date, so the days between keep the target's effect. E9 is dated Day 2,
as E7 is, so no figure in this stream moves. _Tests:_ `test_amb_037_a_reversal_value_dated_before_its_target_is_refused`
and `test_amb_037_a_reversal_value_dated_after_its_target_undoes_it_from_its_own_date`.

**Rationale.** A reversal undoes what its target moved, so it cannot take effect before the target moved anything;
counted from an earlier date, it would put money into closings, fees, and interest that no event explains. Taking the
target's date for every reversal would hide a mistyped value date instead of showing it, and would take away a
correction dated from the day an error is found, which leaves the past days as they were reported. A named refusal
points at the one field to correct.

## AMB-038 — An authorization ID used twice

**Where.** "E3 — Day 2 — AUTHORIZATION — ACC-001 Auth-A hold AED 200.00", and "E5 — Day 4 — SETTLEMENT — ACC-001 Auth-A
settles for AED 185.00". A settlement names the authorization it settles by that ID alone. Not otherwise in this stream.

**Why it is problematic.** The brief does not say whether an authorization ID may arrive on a second authorization
event. If both are approved, a settlement naming the ID matches both: one settlement of 100.00 would settle a hold of
100.00 and a second hold of 50.00 together, releasing the 50.00 with nothing debited for it and printing two settlements
where there was one.

**Options.**

- Refuse an authorization whose ID an authorization already decided on any account holds. **Recommended**: a settlement
  finds its hold by this ID, so the ID must name one hold, as an event ID names one event (AMB-034).
- Accept both, and let a settlement move the first open authorization with the ID only.
- Accept both, as the settlement lookup does without a check.

**Status.** Resolved.

**Resolution.** Refused. An authorization whose authorization ID is held by an authorization already approved or
declined, on any account, is refused once its event ID is found new (AMB-034); it is recorded with its outcome
(AMB-014), holds nothing, and prints as that day's error, `E3 refused: Auth-A is already used by E2`. A settlement
naming the ID then moves the first authorization alone. The same authorization event delivered again is still a
duplicate (AMB-034), not a refusal. Auth-A and Auth-B each arrive once in this stream, so no figure moves. _Tests:_
`test_amb_038_an_authorization_id_already_used_is_refused` and
`test_amb_038_an_authorization_id_is_refused_on_another_account_too`.

**Rationale.** The ID is the only link between a hold and its settlement, so a second holder of it makes every later
settlement ambiguous; moving the first open one only would settle the wrong hold whenever settlements arrive out of
order. Refusing it keeps each hold settled by what names it and shows the clash to someone who can correct it. In
production the link is the card network's transaction identifier, which is unique; a short authorization code, which is
not, would be only part of the key.
