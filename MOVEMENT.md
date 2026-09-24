# Movement

The full analysis behind [OUTPUT_TARGET](OUTPUT_TARGET.md): the constraints and criteria from the
[challenge brief](challenge-raw.md), every event, and what each day moves on each account. A figure appears here only
when every option still open in [AMBIGUITIES](AMBIGUITIES.md) gives the same value; a cell marked pending carries no
figure, and its key points to the entries it waits on, listed under its table.

Each day has three tables. **Events processed** lists the day's events from the brief, with E10's instalments under E10.
**EOD applied** lists the end-of-day steps in the order AMB-023 recommends: 1, fee re-evaluation, which assesses and
reverses overdraft fees; 2, interest accrual, which is not an entry until it capitalizes (AMB-007); 3, on Day 6 only,
capitalization. **Closing Summary** is the state OUTPUT_TARGET prints. A generated entry is named by kind and day, such
as `FEE-D2` for the fee on Day 2, so its name holds under every option of AMB-002; a hold is not an entry (AMB-010), and
shows under authorizations.

Balances are the state as known at the end of each day. How the report lays that state out, and whether it adds restated
or final views, is itself open (AMB-022, AMB-025); OUTPUT_TARGET shows the printed text, and repeats these figures
unchanged.

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
  AMB-014._
- An authorization is approved only if the account's available balance — ledger balance minus active holds — remains at
  or above zero after the hold is applied. _Ambiguities: AMB-008, AMB-009, AMB-010, AMB-013, AMB-018._

## Acceptance Criteria

Quoted from the brief, numbered in its order. The brief states that some of them are wrong; each verdict belongs in
[REJECTED](REJECTED.md), and none is assumed right or wrong here. The same criteria as draft Gherkin are in
[ACCEPTANCE_CRITERIA.feature](ACCEPTANCE_CRITERIA.feature). No figure below rests on a criterion alone.

- **C1.** The Day 2 closing ledger balance, evaluated at end of Day 5 and before any fee is assessed, is AED −370.00.
  _Ambiguities: AMB-016, AMB-022._
- **C2.** E7 causes exactly one overdraft fee to be assessed, on Day 2. _Ambiguities: AMB-002, AMB-003, AMB-016._
- **C3.** The Day 4 settlement of Auth-A must be accepted. _Ambiguities: AMB-013._
- **C4.** Any settlement referencing an authorization ID not present in the ledger must be rejected and the funds must
  not leave the account. _Ambiguities: AMB-012, AMB-029._
- **C5.** If Auth-B is approved, its hold reduces available balance but not ledger balance. _Ambiguities: AMB-021._
- **C6.** After E9, all balances and fees return to their pre-E7 values. _Ambiguities: AMB-004, AMB-005._
- **C7.** The three BHD instalments in E10 must each be BHD 3.334. _Ambiguities: AMB-020._
- **C8.** If the rounded daily interest accruals do not sum to the capitalized total, the remainder is discarded.

## Accounts

| Account | Currency | Opening balance |
| ------- | -------- | --------------- |
| ACC-001 | AED      | 0.00            |
| ACC-002 | BHD      | 0.000           |

## Events

Listed in the brief's order; the order they are replayed in is AMB-015, and E10's split and timing are AMB-020 and
AMB-017.

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

| Step | Entry | Type | Account | Detail                            | Value date |
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

| Step | Entry | Type              | Account          | Detail                      | Value date |
| ---- | ----- | ----------------- | ---------------- | --------------------------- | ---------- |
| 1    | —     | Fee re-evaluation | ACC-001, ACC-002 | no fee assessed or reversed | —          |
| 2    | —     | Interest accrual  | ACC-001          | 0.10; not an entry          | Day 1      |
| 2    | —     | Interest accrual  | ACC-002          | 0.000; not an entry         | Day 1      |

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

| Step | Entry | Type              | Account          | Detail                      | Value date |
| ---- | ----- | ----------------- | ---------------- | --------------------------- | ---------- |
| 1    | —     | Fee re-evaluation | ACC-001, ACC-002 | no fee assessed or reversed | —          |
| 2    | —     | Interest accrual  | ACC-001          | pending (a); not an entry   | Day 2      |
| 2    | —     | Interest accrual  | ACC-002          | 0.000; not an entry         | Day 2      |

Closing Summary:

| Item                   | ACC-001 (AED)                | ACC-002 (BHD) |
| ---------------------- | ---------------------------- | ------------- |
| Closing ledger balance | 250.00                       | 0.000         |
| Available balance      | 50.00                        | 0.000         |
| Authorizations         | Auth-A approved, hold 200.00 | none          |
| Errors                 | none                         | none          |

Pending cells wait on:

- (a) AMB-002, AMB-003, AMB-004, AMB-005, AMB-006, AMB-007

Readings that touch this day without changing a figure: AMB-008 and AMB-009, on when and against what Auth-A is checked,
and AMB-010, on what E3's value date means.

## Day 3

Events processed:

| Event | Booked | Type   | Account | Detail     | Value date |
| ----- | ------ | ------ | ------- | ---------- | ---------- |
| E4    | Day 3  | Credit | ACC-001 | AED 400.00 | Day 3      |

EOD applied:

| Step | Entry | Type              | Account          | Detail                      | Value date |
| ---- | ----- | ----------------- | ---------------- | --------------------------- | ---------- |
| 1    | —     | Fee re-evaluation | ACC-001, ACC-002 | no fee assessed or reversed | —          |
| 2    | —     | Interest accrual  | ACC-001          | pending (a); not an entry   | Day 3      |
| 2    | —     | Interest accrual  | ACC-002          | 0.000; not an entry         | Day 3      |

Closing Summary:

| Item                   | ACC-001 (AED)                | ACC-002 (BHD) |
| ---------------------- | ---------------------------- | ------------- |
| Closing ledger balance | 650.00                       | 0.000         |
| Available balance      | 450.00                       | 0.000         |
| Authorizations         | Auth-A approved, hold 200.00 | none          |
| Errors                 | none                         | none          |

Pending cells wait on:

- (a) AMB-002, AMB-003, AMB-004, AMB-005, AMB-006, AMB-007, AMB-011

## Day 4

Events processed:

| Event | Booked | Type       | Account | Detail                                                | Value date |
| ----- | ------ | ---------- | ------- | ----------------------------------------------------- | ---------- |
| E5    | Day 4  | Settlement | ACC-001 | Auth-A settles for AED 185.00                         | Day 4      |
| E6    | Day 4  | Settlement | ACC-001 | Auth-Z settles for AED 180.00; no prior authorization | Day 4      |

EOD applied:

| Step | Entry | Type              | Account          | Detail                      | Value date |
| ---- | ----- | ----------------- | ---------------- | --------------------------- | ---------- |
| 1    | —     | Fee re-evaluation | ACC-001, ACC-002 | no fee assessed or reversed | —          |
| 2    | —     | Interest accrual  | ACC-001          | pending (a); not an entry   | Day 4      |
| 2    | —     | Interest accrual  | ACC-002          | 0.000; not an entry         | Day 4      |

Closing Summary:

| Item                   | ACC-001 (AED)             | ACC-002 (BHD) |
| ---------------------- | ------------------------- | ------------- |
| Closing ledger balance | pending (b)               | 0.000         |
| Available balance      | pending (c)               | 0.000         |
| Authorizations         | Auth-A settled for 185.00 | none          |
| Errors                 | pending (b)               | none          |

Pending cells wait on:

- (a) AMB-002, AMB-003, AMB-004, AMB-005, AMB-006, AMB-007, AMB-011, AMB-012
- (b) AMB-012
- (c) AMB-012, AMB-013

Readings that touch this day without changing a figure: AMB-014, on whether E6 is recorded once rejected.

## Day 5

Events processed:

| Event | Booked | Type          | Account | Detail                                                   | Value date  |
| ----- | ------ | ------------- | ------- | -------------------------------------------------------- | ----------- |
| E7    | Day 5  | Debit         | ACC-001 | AED 620.00                                               | Day 2       |
| E8    | Day 5  | Authorization | ACC-001 | Auth-B, hold AED 90.00; never settled in window          | Day 5       |
| E10   | Day 5  | Credit        | ACC-002 | BHD 10.000 in three equal instalments; pending (AMB-015) | Day 5       |
| E10-1 | Day 5  | Credit        | ACC-002 | BHD instalment 1 of 3; pending (a)                       | pending (a) |
| E10-2 | Day 5  | Credit        | ACC-002 | BHD instalment 2 of 3; pending (a)                       | pending (a) |
| E10-3 | Day 5  | Credit        | ACC-002 | BHD instalment 3 of 3; pending (a)                       | pending (a) |

EOD applied:

| Step | Entry  | Type             | Account | Detail                              | Value date  |
| ---- | ------ | ---------------- | ------- | ----------------------------------- | ----------- |
| 1    | FEE-D2 | Overdraft fee    | ACC-001 | AED 25.00, if assessed; pending (b) | pending (b) |
| 1    | FEE-D4 | Overdraft fee    | ACC-001 | AED 25.00, if assessed; pending (c) | pending (c) |
| 1    | FEE-D5 | Overdraft fee    | ACC-001 | AED 25.00                           | Day 5       |
| 2    | —      | Interest accrual | ACC-001 | pending (d); not an entry           | Day 5       |
| 2    | —      | Interest accrual | ACC-002 | pending (e); not an entry           | Day 5       |

Closing Summary:

| Item                    | ACC-001 (AED)                                     | ACC-002 (BHD) |
| ----------------------- | ------------------------------------------------- | ------------- |
| Day 2 closing, restated | pending (f)                                       | —             |
| Day 3 closing, restated | pending (g)                                       | —             |
| Day 4 closing, restated | pending (h)                                       | —             |
| Closing ledger balance  | pending (i)                                       | pending (j)   |
| Available balance       | pending (k)                                       | pending (j)   |
| Authorizations          | Auth-A settled for 185.00; Auth-B declined, 90.00 | none          |
| Errors                  | pending (l)                                       | none          |

Before any fee, E7 restates Day 2 to −370.00 under every option (criterion 1); the printed restatement is the closing
after that day's fees, so it waits on them.

Pending cells wait on:

- (a) AMB-015, AMB-017, AMB-020; listed on Day 5 unless E10 is processed late
- (b) AMB-002, AMB-003
- (c) AMB-002, AMB-003
- (d) AMB-002, AMB-003, AMB-004, AMB-005, AMB-006, AMB-007, AMB-011, AMB-012
- (e) AMB-005, AMB-015, AMB-017
- (f) AMB-002, AMB-003
- (g) AMB-002, AMB-003, AMB-011
- (h) AMB-002, AMB-003, AMB-011, AMB-012
- (i) AMB-002, AMB-003, AMB-011, AMB-012, AMB-016
- (j) AMB-015, AMB-017
- (k) AMB-002, AMB-012, AMB-013, AMB-016, AMB-018
- (l) AMB-019

Readings that touch this day without changing a figure: AMB-008, AMB-009, AMB-010, and AMB-021, on Auth-B's decline, and
AMB-014, on recording it; whether restated closings are reported at all is AMB-022.

## Day 6

Events processed:

| Event | Booked | Type     | Account | Detail                                                   | Value date  |
| ----- | ------ | -------- | ------- | -------------------------------------------------------- | ----------- |
| E9    | Day 6  | Reversal | ACC-001 | reverses E7                                              | Day 2       |
| E10   | Day 5  | Credit   | ACC-002 | BHD 10.000 in three equal instalments; pending (AMB-015) | Day 5       |
| E10-1 | Day 5  | Credit   | ACC-002 | BHD instalment 1 of 3; pending (a)                       | pending (a) |
| E10-2 | Day 5  | Credit   | ACC-002 | BHD instalment 2 of 3; pending (a)                       | pending (a) |
| E10-3 | Day 5  | Credit   | ACC-002 | BHD instalment 3 of 3; pending (a)                       | pending (a) |

EOD applied:

| Step | Entry       | Type                    | Account          | Detail                            | Value date  |
| ---- | ----------- | ----------------------- | ---------------- | --------------------------------- | ----------- |
| 1    | FEE-REV-D2  | Fee reversal            | ACC-001          | AED 25.00, if booked; pending (b) | pending (b) |
| 1    | FEE-REV-D4  | Fee reversal            | ACC-001          | AED 25.00, if booked; pending (b) | pending (b) |
| 1    | FEE-REV-D5  | Fee reversal            | ACC-001          | AED 25.00, if booked; pending (c) | pending (c) |
| 1    | —           | Fee re-evaluation       | ACC-001, ACC-002 | no new fee assessed               | —           |
| 2    | —           | Interest accrual        | ACC-001          | pending (d); not an entry         | Day 6       |
| 2    | —           | Interest accrual        | ACC-002          | pending (e); not an entry         | Day 6       |
| 3    | CAP-ACC-001 | Interest capitalization | ACC-001          | pending (f)                       | Day 6       |
| 3    | CAP-ACC-002 | Interest capitalization | ACC-002          | pending (g)                       | Day 6       |

Closing Summary:

| Item                    | ACC-001 (AED)                                     | ACC-002 (BHD) |
| ----------------------- | ------------------------------------------------- | ------------- |
| Day 2 closing, restated | pending (h)                                       | —             |
| Day 3 closing, restated | pending (i)                                       | —             |
| Day 4 closing, restated | pending (j)                                       | —             |
| Day 5 closing, restated | pending (k)                                       | pending (l)   |
| Closing ledger balance  | pending (m)                                       | pending (n)   |
| Available balance       | pending (o)                                       | pending (n)   |
| Authorizations          | Auth-A settled for 185.00; Auth-B declined, 90.00 | none          |
| Errors                  | none                                              | pending (p)   |

Pending cells wait on:

- (a) AMB-015, AMB-017, AMB-020; listed on Day 6 only if E10 is processed late
- (b) AMB-002, AMB-003, AMB-004
- (c) AMB-004
- (d) AMB-002, AMB-003, AMB-004, AMB-005, AMB-006, AMB-007, AMB-011, AMB-012, AMB-023
- (e) AMB-005, AMB-007, AMB-015, AMB-017, AMB-023
- (f) AMB-002, AMB-003, AMB-004, AMB-005, AMB-006, AMB-007, AMB-011, AMB-012, AMB-023
- (g) AMB-005, AMB-007, AMB-015, AMB-017, AMB-023
- (h) AMB-002, AMB-003, AMB-004
- (i) AMB-002, AMB-003, AMB-004, AMB-011
- (j) AMB-002, AMB-003, AMB-004, AMB-011, AMB-012
- (k) AMB-002, AMB-003, AMB-004, AMB-011, AMB-012
- (l) AMB-015, which also decides whether the line is printed at all
- (m) AMB-002, AMB-003, AMB-004, AMB-005, AMB-006, AMB-007, AMB-011, AMB-012, AMB-023
- (n) AMB-005, AMB-007, AMB-015, AMB-017, AMB-023
- (o) AMB-002, AMB-003, AMB-004, AMB-005, AMB-006, AMB-007, AMB-011, AMB-012, AMB-013, AMB-018, AMB-023
- (p) AMB-015

Readings that touch this day without changing a figure: AMB-024, on E9 being a new record rather than an edit to E7.

## Why the Fixed Figures Hold

- **Day 0** is the opening balances the brief gives, before any event.
- **Day 1 to 3 balances** involve no backdated entry, no negative balance, and no settlement, so no open entry changes
  them; only the interest accrued from Day 2 onwards waits on open entries.
- **Auth-A** is approved against 250.00 − 200.00 = 50.00 under every reading of when and against what it is checked
  (AMB-008, AMB-009), and its settlement is accepted because no open entry rejects a settlement within its hold.
- **Day 4 fees** are none because ACC-001 stays positive whether E6 is rejected (465.00) or honoured (285.00).
- **Day 2's restated closing before fees** is 1,200.00 − 950.00 − 620.00 = −370.00; E6 is value-dated Day 4 and cannot
  reach it.
- **Day 5's own fee** (`FEE-D5`) is assessed under every option in AMB-002, because Day 5 closes at −155.00 or lower
  before any fee; it is booked and value-dated Day 5 whichever day AMB-003 or AMB-016 picks.
- **Day 1's interest** is 250.00 × 0.0004 = 0.10 exactly: no backdated entry reaches Day 1, and there is nothing to
  round or compound.
- **ACC-002 accrues 0.000 on Days 1 to 4**, because its balance is zero until E10.
- **Auth-B** is declined whether E6 was rejected (available −245.00) or honoured (−425.00), and whether retroactive fees
  land before it (AMB-016).
- **Day 6** brings no new fee: after E9 every day closes at or above zero under every option.
- **ACC-002** never goes negative, so it never has a fee, and its Days 1 to 4 hold no events under any replay order.
