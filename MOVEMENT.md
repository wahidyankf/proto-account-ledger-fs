# Movement

The full analysis behind [OUTPUT_TARGET](OUTPUT_TARGET.md): the constraints and criteria from the
[challenge brief](challenge-raw.md), every event, and what each day moves on each account. Every entry in
[AMBIGUITIES](AMBIGUITIES.md) is resolved, so every figure here is fixed; a figure that waited on an open entry would be
marked pending, with a key under its table naming the entries it waits on.

Each day has three tables. **Events processed** lists the day's events from the brief, with E10's instalments under E10.
**EOD applied** lists the end-of-day steps and the events each fires: 1, fee re-evaluation, which fires overdraft fees
and refunds those no longer due; 2, interest, which fires the day's accrual and any adjustment a late event makes due
(AMB-005); 3, on Day 6 only, capitalization, in that order (AMB-023); an accrual stays out of the ledger balance until
it capitalizes (AMB-007). A step that moves nothing fires no event and shows —. **Closing Summary** is the state
OUTPUT_TARGET prints.

An event the ledger fires is named by kind, account, the day it is for, and the day it fires (AMB-024): `FEE-001-D2@D5`
is ACC-001's overdraft fee for Day 2, fired on Day 5 and value-dated that day (AMB-003); `REFUND-001-D2@D6` refunds it
(AMB-004); `INT-001-D2@D5` adjusts Day 2's interest; `CAP-001@D6` capitalizes it. A hold moves no ledger balance and
shows under authorizations; it reduces the available balance from its value date (AMB-010).

The ledger is an append-only log of events, the brief's and those it fires itself, and every balance here is an
aggregation over that log by value date, recomputed when a late event arrives (AMB-004, AMB-024). Balances are the state
as known at the end of each day, and a day a late event reaches adds the earlier closings it restated (AMB-022). Every
day lists both accounts and every known authorization (AMB-025); OUTPUT_TARGET shows the printed text, and repeats these
figures unchanged.

## Constraints

Quoted from the brief, split where its sentences run together. Each item names the entries in
[AMBIGUITIES](AMBIGUITIES.md) that bear on it; an item naming none is read as written.

What is built:

- An in-memory account ledger core. Any language. No web layer, no persistence, no UI, no database.
- It must be exercised by a runnable test suite or script that replays the event stream and prints, per day: closing
  ledger balance, fee assessments, authorization states, and errors. _Ambiguities: AMB-022, AMB-025, AMB-026._
- The window is six days, Day 1 through Day 6. _Ambiguities: AMB-001._

Non-negotiable rules:

- Overdraft fee: AED 25.00, assessed once per day per account when that day's closing ledger balance (all entries with
  value_date ≤ that day) is negative. Booked with value_date equal to the day assessed. _Ambiguities: AMB-002, AMB-003,
  AMB-004, AMB-011, AMB-016, AMB-027._
- Daily interest: 0.04% per day on the closing ledger balance, positive balances only. Accruals capitalize as a single
  credit at end of Day 6. The rounded daily accruals must sum exactly to the capitalized total. _Ambiguities: AMB-005,
  AMB-006, AMB-007, AMB-023._
- AED is 2 decimal places, BHD is 3. Amounts stored and rounded to their own precision. _Ambiguities: AMB-006, AMB-020._
- The ledger is append-only. No event record is ever mutated or deleted. _Ambiguities: AMB-004, AMB-024, AMB-028,
  AMB-014, AMB-035._
- An authorization is approved only if the account's available balance — ledger balance minus active holds — remains at
  or above zero after the hold is applied. _Ambiguities: AMB-008, AMB-009, AMB-010, AMB-013, AMB-018._

## Acceptance Criteria

Quoted from the brief, numbered in its order. The brief states that some of them are wrong; a refused criterion is
recorded in [REJECTED](REJECTED.md), and each criterion below states its verdict. The same criteria as draft Gherkin are
in [ACCEPTANCE_CRITERIA.feature](ACCEPTANCE_CRITERIA.feature). No figure below rests on a criterion alone.

- **C1.** The Day 2 closing ledger balance, evaluated at end of Day 5 and before any fee is assessed, is AED −370.00.
  _Ambiguities: AMB-016, AMB-022._ **Accepted:** 1,200.00 − 950.00 − 620.00 = −370.00, as Day 5 restates it; the fees
  are value-dated Day 5 (AMB-003) and interest joins no balance before capitalization (AMB-007), so the figure is the
  same before or after the fees.
- **C2.** E7 causes exactly one overdraft fee to be assessed, on Day 2. _Ambiguities: AMB-002, AMB-003, AMB-016._
  **Refused**, in [REJECTED](REJECTED.md): E7 causes three fees, for Days 2, 4, and 5, all value-dated Day 5.
- **C3.** The Day 4 settlement of Auth-A must be accepted. _Ambiguities: AMB-013._ **Accepted:** Auth-A is approved on
  arrival on Day 2 against 250.00 (AMB-009), and E5's 185.00 settles within its hold of 200.00, releasing all of it
  (AMB-013); E7, arriving on Day 5, restates Day 2 but never reopens a decision already in the log (AMB-024).
- **C4.** Any settlement referencing an authorization ID not present in the ledger must be rejected and the funds must
  not leave the account. _Ambiguities: AMB-012, AMB-029._ **Refused**, in [REJECTED](REJECTED.md): E6 is honoured as a
  force-post.
- **C5.** If Auth-B is approved, its hold reduces available balance but not ledger balance. _Ambiguities: AMB-021._
  **Refused**, in [REJECTED](REJECTED.md).
- **C6.** After E9, all balances and fees return to their pre-E7 values. _Ambiguities: AMB-004, AMB-005._ **Refused**,
  in [REJECTED](REJECTED.md): Days 2 to 4 and the net fees return, but Day 5 closes at 210.00, interest totals 0.76, not
  0.79, and Day 6 closes at 285.76, not 285.79.
- **C7.** The three BHD instalments in E10 must each be BHD 3.334. _Ambiguities: AMB-020._ **Refused**, in
  [REJECTED](REJECTED.md): 3 × 3.334 = 10.002; the ledger posts 3.333, 3.333, and 3.334.
- **C8.** If the rounded daily interest accruals do not sum to the capitalized total, the remainder is discarded.
  _Ambiguities: AMB-006, AMB-023._ **Refused**, in [REJECTED](REJECTED.md): each capitalization is the sum of its
  rounded interest events, so no remainder exists.

## Accounts

| Account | Currency | Opening balance |
| ------- | -------- | --------------- |
| ACC-001 | AED      | 0.00            |
| ACC-002 | BHD      | 0.000           |

## Events

Listed and replayed in the brief's order, so E10, booked Day 5, arrives after E9 and is processed on Day 6 as a late
event (AMB-015); E10 is split as AMB-020 resolves, all on Day 5 (AMB-017).

| Event | Booked | Type          | Account | Detail                                                | Value date |
| ----- | ------ | ------------- | ------- | ----------------------------------------------------- | ---------- |
| E1    | Day 1  | Credit        | ACC-001 | AED 1,200.00                                          | Day 1      |
| E2    | Day 1  | Debit         | ACC-001 | AED 950.00                                            | Day 1      |
| E3    | Day 2  | Authorization | ACC-001 | Auth-A, hold AED 200.00                               | Day 2      |
| E4    | Day 3  | Credit        | ACC-001 | AED 400.00                                            | Day 3      |
| E5    | Day 4  | Settlement    | ACC-001 | Auth-A settles for AED 185.00                         | Day 4      |
| E6    | Day 4  | Settlement    | ACC-001 | Auth-Z settles for AED 180.00; no prior authorization | Day 4      |
| E7    | Day 5  | Debit         | ACC-001 | AED 620.00                                            | Day 2      |
| E8    | Day 5  | Authorization | ACC-001 | Auth-B, hold AED 90.00; never settled in window       | Day 5      |
| E9    | Day 6  | Reversal      | ACC-001 | reverses E7                                           | Day 2      |
| E10   | Day 5  | Credit        | ACC-002 | BHD 10.000 in three equal instalments                 | Day 5      |

## Day 0

The opening state, before any event, in the same shape as every other day: its closing balance is the opening balance.
Day 0 is not in the window, so no fee is assessed and no interest accrues (AMB-001).

Events processed:

| Event | Booked | Type | Account | Detail | Value date |
| ----- | ------ | ---- | ------- | ------ | ---------- |
| —     | —      | —    | —       | none   | —          |

EOD applied:

| Step | Event | Type | Account | Detail                            | Value date |
| ---- | ----- | ---- | ------- | --------------------------------- | ---------- |
| —    | —     | —    | —       | none; Day 0 is outside the window | —          |

Closing Summary:

| Item                   | ACC-001 (AED) | ACC-002 (BHD) |
| ---------------------- | ------------- | ------------- |
| Closing ledger balance | 0.00          | 0.000         |
| Available balance      | 0.00          | 0.000         |
| Authorizations         | none          | none          |
| Errors                 | none          | none          |

## Day 1

Events processed:

| Event | Booked | Type   | Account | Detail       | Value date |
| ----- | ------ | ------ | ------- | ------------ | ---------- |
| E1    | Day 1  | Credit | ACC-001 | AED 1,200.00 | Day 1      |
| E2    | Day 1  | Debit  | ACC-001 | AED 950.00   | Day 1      |

EOD applied:

| Step | Event         | Type              | Account          | Detail                                    | Value date |
| ---- | ------------- | ----------------- | ---------------- | ----------------------------------------- | ---------- |
| 1    | —             | Fee re-evaluation | ACC-001, ACC-002 | no fee assessed or refunded               | —          |
| 2    | INT-001-D1@D1 | Interest accrual  | ACC-001          | 0.10, for Day 1                           | Day 1      |
| 2    | —             | Interest accrual  | ACC-002          | no interest accrued; balance not positive | —          |

Closing Summary:

| Item                   | ACC-001 (AED) | ACC-002 (BHD) |
| ---------------------- | ------------- | ------------- |
| Closing ledger balance | 250.00        | 0.000         |
| Available balance      | 250.00        | 0.000         |
| Authorizations         | none          | none          |
| Errors                 | none          | none          |

## Day 2

Events processed:

| Event | Booked | Type          | Account | Detail                  | Value date |
| ----- | ------ | ------------- | ------- | ----------------------- | ---------- |
| E3    | Day 2  | Authorization | ACC-001 | Auth-A, hold AED 200.00 | Day 2      |

EOD applied:

| Step | Event         | Type              | Account          | Detail                                    | Value date |
| ---- | ------------- | ----------------- | ---------------- | ----------------------------------------- | ---------- |
| 1    | —             | Fee re-evaluation | ACC-001, ACC-002 | no fee assessed or refunded               | —          |
| 2    | INT-001-D2@D2 | Interest accrual  | ACC-001          | 0.10, for Day 2                           | Day 2      |
| 2    | —             | Interest accrual  | ACC-002          | no interest accrued; balance not positive | —          |

Closing Summary:

| Item                   | ACC-001 (AED)                | ACC-002 (BHD) |
| ---------------------- | ---------------------------- | ------------- |
| Closing ledger balance | 250.00                       | 0.000         |
| Available balance      | 50.00                        | 0.000         |
| Authorizations         | Auth-A approved, hold 200.00 | none          |
| Errors                 | none                         | none          |

Readings that touch this day without changing a figure: AMB-008 and AMB-009, on when and against what Auth-A is checked,
and AMB-010, on what E3's value date means.

## Day 3

Events processed:

| Event | Booked | Type   | Account | Detail     | Value date |
| ----- | ------ | ------ | ------- | ---------- | ---------- |
| E4    | Day 3  | Credit | ACC-001 | AED 400.00 | Day 3      |

EOD applied:

| Step | Event         | Type              | Account          | Detail                                    | Value date |
| ---- | ------------- | ----------------- | ---------------- | ----------------------------------------- | ---------- |
| 1    | —             | Fee re-evaluation | ACC-001, ACC-002 | no fee assessed or refunded               | —          |
| 2    | INT-001-D3@D3 | Interest accrual  | ACC-001          | 0.26, for Day 3                           | Day 3      |
| 2    | —             | Interest accrual  | ACC-002          | no interest accrued; balance not positive | —          |

Closing Summary:

| Item                   | ACC-001 (AED)                | ACC-002 (BHD) |
| ---------------------- | ---------------------------- | ------------- |
| Closing ledger balance | 650.00                       | 0.000         |
| Available balance      | 450.00                       | 0.000         |
| Authorizations         | Auth-A approved, hold 200.00 | none          |
| Errors                 | none                         | none          |

## Day 4

Events processed:

| Event | Booked | Type       | Account | Detail                                                | Value date |
| ----- | ------ | ---------- | ------- | ----------------------------------------------------- | ---------- |
| E5    | Day 4  | Settlement | ACC-001 | Auth-A settles for AED 185.00                         | Day 4      |
| E6    | Day 4  | Settlement | ACC-001 | Auth-Z force-posts AED 180.00; no prior authorization | Day 4      |

EOD applied:

| Step | Event         | Type              | Account          | Detail                                    | Value date |
| ---- | ------------- | ----------------- | ---------------- | ----------------------------------------- | ---------- |
| 1    | —             | Fee re-evaluation | ACC-001, ACC-002 | no fee assessed or refunded               | —          |
| 2    | INT-001-D4@D4 | Interest accrual  | ACC-001          | 0.11, for Day 4                           | Day 4      |
| 2    | —             | Interest accrual  | ACC-002          | no interest accrued; balance not positive | —          |

Closing Summary:

| Item                   | ACC-001 (AED)             | ACC-002 (BHD) |
| ---------------------- | ------------------------- | ------------- |
| Closing ledger balance | 285.00                    | 0.000         |
| Available balance      | 285.00                    | 0.000         |
| Authorizations         | Auth-A settled for 185.00 | none          |
| Errors                 | none                      | none          |

E6 has no authorization to settle, so it is honoured as a force-post (AMB-012): it debits 180.00 and releases no hold.

Readings that touch this day without changing a figure: AMB-029 and AMB-030, on settlements against other
authorizations.

## Day 5

Events processed:

| Event | Booked | Type          | Account | Detail                                          | Value date |
| ----- | ------ | ------------- | ------- | ----------------------------------------------- | ---------- |
| E7    | Day 5  | Debit         | ACC-001 | AED 620.00                                      | Day 2      |
| E8    | Day 5  | Authorization | ACC-001 | Auth-B, hold AED 90.00; never settled in window | Day 5      |

EOD applied:

| Step | Event         | Type                | Account | Detail                                    | Value date |
| ---- | ------------- | ------------------- | ------- | ----------------------------------------- | ---------- |
| 1    | FEE-001-D2@D5 | Overdraft fee       | ACC-001 | AED 25.00, for Day 2                      | Day 5      |
| 1    | FEE-001-D4@D5 | Overdraft fee       | ACC-001 | AED 25.00, for Day 4                      | Day 5      |
| 1    | FEE-001-D5@D5 | Overdraft fee       | ACC-001 | AED 25.00, for Day 5                      | Day 5      |
| 2    | INT-001-D2@D5 | Interest adjustment | ACC-001 | −0.10, for Day 2                          | Day 5      |
| 2    | INT-001-D3@D5 | Interest adjustment | ACC-001 | −0.25, for Day 3                          | Day 5      |
| 2    | INT-001-D4@D5 | Interest adjustment | ACC-001 | −0.11, for Day 4                          | Day 5      |
| 2    | —             | Interest accrual    | ACC-001 | no interest accrued; balance not positive | —          |
| 2    | —             | Interest accrual    | ACC-002 | no interest accrued; balance not positive | —          |

Closing Summary:

| Item                    | ACC-001 (AED)                                     | ACC-002 (BHD) |
| ----------------------- | ------------------------------------------------- | ------------- |
| Day 2 closing, restated | −370.00                                           | —             |
| Day 3 closing, restated | 30.00                                             | —             |
| Day 4 closing, restated | −335.00                                           | —             |
| Closing ledger balance  | −410.00                                           | 0.000         |
| Available balance       | −410.00                                           | 0.000         |
| Authorizations          | Auth-A settled for 185.00; Auth-B declined, 90.00 | none          |
| Errors                  | none                                              | none          |

E7 restates Day 2 to −370.00 (criterion 1) and Day 3 to +30.00; every fee is value-dated Day 5 (AMB-003), so those are
also the printed restatements.

Readings that touch this day without changing a figure: AMB-008, AMB-009, AMB-010, and AMB-021, on Auth-B's decline,
AMB-014, on recording it, and AMB-019, on printing it as a state; AMB-011, since the fees for Days 2 and 4 reach no
closing before Day 5's, which is negative either way; the restated closings are reported as AMB-022 resolves.

## Day 6

Events processed:

| Event | Booked | Type     | Account | Detail                                                | Value date |
| ----- | ------ | -------- | ------- | ----------------------------------------------------- | ---------- |
| E9    | Day 6  | Reversal | ACC-001 | reverses E7                                           | Day 2      |
| E10   | Day 5  | Credit   | ACC-002 | BHD 10.000 in three equal instalments; late (AMB-015) | Day 5      |
| E10-1 | Day 5  | Credit   | ACC-002 | BHD 3.333, instalment 1 of 3                          | Day 5      |
| E10-2 | Day 5  | Credit   | ACC-002 | BHD 3.333, instalment 2 of 3                          | Day 5      |
| E10-3 | Day 5  | Credit   | ACC-002 | BHD 3.334, instalment 3 of 3                          | Day 5      |

EOD applied:

| Step | Event            | Type                    | Account          | Detail                          | Value date |
| ---- | ---------------- | ----------------------- | ---------------- | ------------------------------- | ---------- |
| 1    | REFUND-001-D2@D6 | Fee refund              | ACC-001          | AED 25.00, for Day 2            | Day 6      |
| 1    | REFUND-001-D4@D6 | Fee refund              | ACC-001          | AED 25.00, for Day 4            | Day 6      |
| 1    | REFUND-001-D5@D6 | Fee refund              | ACC-001          | AED 25.00, for Day 5            | Day 6      |
| 1    | —                | Fee re-evaluation       | ACC-001, ACC-002 | no new fee assessed             | —          |
| 2    | INT-001-D2@D6    | Interest adjustment     | ACC-001          | 0.10, for Day 2                 | Day 6      |
| 2    | INT-001-D3@D6    | Interest adjustment     | ACC-001          | 0.25, for Day 3                 | Day 6      |
| 2    | INT-001-D4@D6    | Interest adjustment     | ACC-001          | 0.11, for Day 4                 | Day 6      |
| 2    | INT-001-D5@D6    | Interest adjustment     | ACC-001          | 0.08, for Day 5                 | Day 6      |
| 2    | INT-001-D6@D6    | Interest accrual        | ACC-001          | 0.11, for Day 6                 | Day 6      |
| 2    | INT-002-D5@D6    | Interest adjustment     | ACC-002          | 0.004, for Day 5                | Day 6      |
| 2    | INT-002-D6@D6    | Interest accrual        | ACC-002          | 0.004, for Day 6                | Day 6      |
| 3    | CAP-001@D6       | Interest capitalization | ACC-001          | AED 0.76, accrued Days 1 to 6   | Day 6      |
| 3    | CAP-002@D6       | Interest capitalization | ACC-002          | BHD 0.008, accrued Days 5 and 6 | Day 6      |

Closing Summary:

| Item                    | ACC-001 (AED)                                     | ACC-002 (BHD) |
| ----------------------- | ------------------------------------------------- | ------------- |
| Day 2 closing, restated | 250.00                                            | —             |
| Day 3 closing, restated | 650.00                                            | —             |
| Day 4 closing, restated | 285.00                                            | —             |
| Day 5 closing, restated | 210.00                                            | 10.000        |
| Closing ledger balance  | 285.76                                            | 10.008        |
| Available balance       | 285.76                                            | 10.008        |
| Authorizations          | Auth-A settled for 185.00; Auth-B declined, 90.00 | none          |
| Errors                  | none                                              | none          |

E10 is booked Day 5 but arrives after E9, so it is processed on Day 6 as a late event value-dated Day 5 (AMB-015): Day 6
restates ACC-002's Day 5 and fires its interest for Day 5 as an adjustment.

Readings that touch this day without changing a figure: AMB-028, on reversing a reversal, and AMB-035, on what a
reversal such as E9 may target.

## Why the Fixed Figures Hold

- **Day 0** is the opening balances the brief gives, before any event.
- **Day 1 to 3 balances** involve no backdated event, no negative balance, and no settlement, so no ambiguity bears on
  them.
- **Auth-A** is approved against 250.00 − 200.00 = 50.00 under every reading of when and against what it is checked
  (AMB-008, AMB-009), and its settlement, within its hold, is accepted (AMB-013).
- **Day 4** closes at 250.00 + 400.00 − 185.00 − 180.00 = 285.00, with E6 honoured (AMB-012), so it has no fee.
- **Days 2 and 3 restated on Day 5** are 1,200.00 − 950.00 − 620.00 = −370.00 and −370.00 + 400.00 = +30.00: E6 is
  value-dated Day 4 and cannot reach them, and every fee is value-dated Day 5 (AMB-003). After E9 on Day 6 they return
  to 250.00 and 650.00, because no fee is value-dated before Day 5 (AMB-003) and no refund before Day 6 (AMB-004).
- **Fees for Days 2, 4, and 5** are assessed under AMB-002's resolution, because before any fee Day 2 closes at −370.00,
  Days 4 and 5 at −335.00, and Day 3 at +30.00; all three fire at the close of Day 5 (AMB-016) and are value-dated Day 5
  (AMB-003).
- **Day 4 restated on Day 5** is 285.00 − 620.00 = −335.00, and Day 5 closes at −335.00 − 3 × 25.00 = −410.00; after E9,
  Day 4 is 285.00 again and Day 5 is 285.00 − 75.00 = 210.00, its fees still in and their refunds on Day 6.
- **Interest on Days 1 to 3** is fired as known (AMB-005): 250.00 × 0.0004 = 0.10 on Days 1 and 2, and 650.00 × 0.0004 =
  0.26 on Day 3. On Day 5, E7 makes Day 2's due interest 0.00 and Day 3's 0.01 (on 30.00), so adjustments of −0.10 and
  −0.25 fire; on Day 6, E9 restores 250.00 and 650.00, so +0.10 and +0.25 fire. Day 4 accrues 285.00 × 0.0004 = 0.114 →
  0.11, adjusted by −0.11 on Day 5 and +0.11 on Day 6, and Day 5 earns 210.00 × 0.0004 = 0.084 → 0.08 on Day 6. No
  unrounded accrual here is a tie, so half-even (AMB-006) and half-up agree, and no accrual joins the base before it
  capitalizes (AMB-007).
- **ACC-001 accrues nothing on Day 5**, because its Day 5 closing as known is negative under every option, before or
  after the day's fees.
- **ACC-002 fires no accrual on Days 1 to 4**, because its balance is zero until E10 and interest accrues on positive
  balances only.
- **Available balance** equals the closing from Day 4 onwards: E5 carries no marker, so it is final and releases all of
  Auth-A's hold (AMB-013), and Auth-B, declined, holds nothing.
- **Auth-B** is declined against an available balance of 285.00 − 620.00 − 90.00 = −425.00, and fees fire only at the
  close of Day 5, after it (AMB-016).
- **Day 6** brings no new fee: after E9 every day closes at or above zero under every option. It refunds the fees for
  Days 2, 4, and 5, because their value-dated closings are then 250.00, 285.00, and 210.00, all at or above zero; each
  refund is value-dated Day 6 under AMB-004's resolution.
- **Day 6 closes at 285.76 and 10.008**, because the refunds fire before interest and capitalization fires last
  (AMB-023): ACC-001 accrues 285.00 × 0.0004 = 0.114 → 0.11 for Day 6 and capitalizes 0.10 + 0.10 + 0.26 + 0.11 − 0.10 −
  0.25 − 0.11 + 0.10 + 0.25 + 0.11 + 0.08 + 0.11 = 0.76; ACC-002 accrues 10.000 × 0.0004 = 0.004 for Days 5 and 6 and
  capitalizes 0.008. Neither account holds anything, so available equals closing.

- **ACC-002** never goes negative, so it never has a fee. It holds no event until E10, which arrives late and is
  processed on Day 6 (AMB-015), so ACC-002 closes Days 1 to 5 at 0.000 as known and accrues nothing on them until Day 6.
