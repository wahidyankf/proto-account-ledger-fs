# Movement

The full analysis behind [OUTPUT_TARGET](OUTPUT_TARGET.md): the constraints and criteria from the
[challenge brief](challenge-raw.md), every event, and what each day moves on each account. A figure appears here only
when every option still open in [AMBIGUITIES](AMBIGUITIES.md) gives the same value; a cell marked pending carries no
figure, and its key points to the entries it waits on, listed under its table.

Balances are the state as known at the end of each day. How the report lays that state out, and whether it adds restated
or final views, is itself open (AMB-002, AMB-021); OUTPUT_TARGET shows the printed text, and repeats these figures
unchanged.

## Constraints

Quoted from the brief, split where its sentences run together. Each item names the entries in
[AMBIGUITIES](AMBIGUITIES.md) that bear on it; an item naming none is read as written.

What is built:

- An in-memory account ledger core. Any language. No web layer, no persistence, no UI, no database.
- It must be exercised by a runnable test suite or script that replays the event stream and prints, per day: closing
  ledger balance, fee assessments, authorization states, and errors. _Ambiguities: AMB-002, AMB-021, AMB-030._
- The window is six days, Day 1 through Day 6. _Ambiguities: AMB-032._

Non-negotiable rules:

- Overdraft fee: AED 25.00, assessed once per day per account when that day's closing ledger balance (all entries with
  value_date ≤ that day) is negative. Booked with value_date equal to the day assessed. _Ambiguities: AMB-003, AMB-004,
  AMB-005, AMB-006, AMB-018, AMB-022._
- Daily interest: 0.04% per day on the closing ledger balance, positive balances only. Accruals capitalize as a single
  credit at end of Day 6. The rounded daily accruals must sum exactly to the capitalized total. _Ambiguities: AMB-007,
  AMB-008, AMB-009, AMB-023._
- AED is 2 decimal places, BHD is 3. Amounts stored and rounded to their own precision. _Ambiguities: AMB-008, AMB-010._
- The ledger is append-only. No event record is ever mutated or deleted. _Ambiguities: AMB-006, AMB-019, AMB-026,
  AMB-027._
- An authorization is approved only if the account's available balance — ledger balance minus active holds — remains at
  or above zero after the hold is applied. _Ambiguities: AMB-011, AMB-016, AMB-020, AMB-024, AMB-028._

## Acceptance Criteria

Quoted from the brief, numbered in its order. The brief states that some of them are wrong; each verdict belongs in
[REJECTED](REJECTED.md), and none is assumed right or wrong here. The same criteria as draft Gherkin are in
[ACCEPTANCE_CRITERIA.feature](ACCEPTANCE_CRITERIA.feature). No figure below rests on a criterion alone.

- **C1.** The Day 2 closing ledger balance, evaluated at end of Day 5 and before any fee is assessed, is AED −370.00.
  _Ambiguities: AMB-002, AMB-005._
- **C2.** E7 causes exactly one overdraft fee to be assessed, on Day 2. _Ambiguities: AMB-003, AMB-004, AMB-005._
- **C3.** The Day 4 settlement of Auth-A must be accepted. _Ambiguities: AMB-011._
- **C4.** Any settlement referencing an authorization ID not present in the ledger must be rejected and the funds must
  not leave the account. _Ambiguities: AMB-013, AMB-014._
- **C5.** If Auth-B is approved, its hold reduces available balance but not ledger balance. _Ambiguities: AMB-015._
- **C6.** After E9, all balances and fees return to their pre-E7 values. _Ambiguities: AMB-006, AMB-007._
- **C7.** The three BHD instalments in E10 must each be BHD 3.334. _Ambiguities: AMB-010._
- **C8.** If the rounded daily interest accruals do not sum to the capitalized total, the remainder is discarded.

## Accounts

| Account | Currency | Opening balance |
| ------- | -------- | --------------- |
| ACC-001 | AED      | 0.00            |
| ACC-002 | BHD      | 0.000           |

## Events

Listed in the brief's order; the order they are replayed in is AMB-001, and E10's split and timing are AMB-010 and
AMB-025.

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

## Day 1

Events processed:

| Event | Booked | Type   | Account | Detail       | Value date |
| ----- | ------ | ------ | ------- | ------------ | ---------- |
| E1    | Day 1  | Credit | ACC-001 | AED 1,200.00 | Day 1      |
| E2    | Day 1  | Debit  | ACC-001 | AED 950.00   | Day 1      |

| Item                   | ACC-001 (AED) | ACC-002 (BHD) |
| ---------------------- | ------------- | ------------- |
| Closing ledger balance | 250.00        | 0.000         |
| Available balance      | 250.00        | 0.000         |
| Fees assessed          | none          | none          |
| Authorizations         | none          | none          |
| Errors                 | none          | none          |

## Day 2

Events processed:

| Event | Booked | Type          | Account | Detail                  | Value date |
| ----- | ------ | ------------- | ------- | ----------------------- | ---------- |
| E3    | Day 2  | Authorization | ACC-001 | Auth-A, hold AED 200.00 | Day 2      |

| Item                   | ACC-001 (AED)                       | ACC-002 (BHD) |
| ---------------------- | ----------------------------------- | ------------- |
| Closing ledger balance | 250.00                              | 0.000         |
| Available balance      | 50.00                               | 0.000         |
| Fees assessed          | none                                | none          |
| Authorizations         | Auth-A approved, hold 200.00 active | none          |
| Errors                 | none                                | none          |

## Day 3

Events processed:

| Event | Booked | Type   | Account | Detail     | Value date |
| ----- | ------ | ------ | ------- | ---------- | ---------- |
| E4    | Day 3  | Credit | ACC-001 | AED 400.00 | Day 3      |

| Item                   | ACC-001 (AED)                       | ACC-002 (BHD) |
| ---------------------- | ----------------------------------- | ------------- |
| Closing ledger balance | 650.00                              | 0.000         |
| Available balance      | 450.00                              | 0.000         |
| Fees assessed          | none                                | none          |
| Authorizations         | Auth-A approved, hold 200.00 active | none          |
| Errors                 | none                                | none          |

## Day 4

Events processed:

| Event | Booked | Type       | Account | Detail                                                | Value date |
| ----- | ------ | ---------- | ------- | ----------------------------------------------------- | ---------- |
| E5    | Day 4  | Settlement | ACC-001 | Auth-A settles for AED 185.00                         | Day 4      |
| E6    | Day 4  | Settlement | ACC-001 | Auth-Z settles for AED 180.00; no prior authorization | Day 4      |

| Item                   | ACC-001 (AED)             | ACC-002 (BHD) |
| ---------------------- | ------------------------- | ------------- |
| Closing ledger balance | pending (a)               | 0.000         |
| Available balance      | pending (b)               | 0.000         |
| Fees assessed          | none                      | none          |
| Authorizations         | Auth-A settled for 185.00 | none          |
| Errors                 | pending (a)               | none          |

Pending cells wait on:

- (a) AMB-014
- (b) AMB-011, AMB-014

## Day 5

Events processed:

| Event | Booked | Type          | Account | Detail                                                   | Value date |
| ----- | ------ | ------------- | ------- | -------------------------------------------------------- | ---------- |
| E7    | Day 5  | Debit         | ACC-001 | AED 620.00                                               | Day 2      |
| E8    | Day 5  | Authorization | ACC-001 | Auth-B, hold AED 90.00; never settled in window          | Day 5      |
| E10   | Day 5  | Credit        | ACC-002 | BHD 10.000 in three equal instalments; pending (AMB-001) | Day 5      |

| Item                             | ACC-001 (AED)                       | ACC-002 (BHD) |
| -------------------------------- | ----------------------------------- | ------------- |
| Day 2 closing, restated, pre-fee | −370.00                             | —             |
| Closing ledger balance           | pending (a)                         | pending (b)   |
| Available balance                | pending (c)                         | pending (b)   |
| Fees assessed                    | 25.00 for Day 5; others pending (d) | none          |
| Authorizations                   | Auth-A settled; Auth-B declined     | none          |
| Errors                           | pending (e)                         | none          |

Pending cells wait on:

- (a) AMB-003, AMB-004, AMB-005, AMB-014, AMB-022
- (b) AMB-001, AMB-025
- (c) AMB-003, AMB-005, AMB-014
- (d) AMB-003, AMB-004, AMB-005
- (e) AMB-017

## Day 6

Events processed:

| Event | Booked | Type     | Account | Detail                                                   | Value date |
| ----- | ------ | -------- | ------- | -------------------------------------------------------- | ---------- |
| E9    | Day 6  | Reversal | ACC-001 | reverses E7                                              | Day 2      |
| E10   | Day 5  | Credit   | ACC-002 | BHD 10.000 in three equal instalments; pending (AMB-001) | Day 5      |

| Item                   | ACC-001 (AED)                     | ACC-002 (BHD) |
| ---------------------- | --------------------------------- | ------------- |
| Closing ledger balance | pending (a)                       | pending (b)   |
| Available balance      | pending (a)                       | pending (b)   |
| Fees assessed          | no new fee; reversals pending (c) | none          |
| Interest capitalized   | pending (d)                       | pending (e)   |
| Authorizations         | Auth-A settled; Auth-B declined   | none          |
| Errors                 | none                              | pending (f)   |

Pending cells wait on:

- (a) AMB-006, AMB-007, AMB-009, AMB-014
- (b) AMB-001, AMB-007, AMB-009, AMB-025
- (c) AMB-006
- (d) AMB-006, AMB-007, AMB-008, AMB-009, AMB-014, AMB-023
- (e) AMB-001, AMB-007, AMB-023, AMB-025
- (f) AMB-001

## Why the Fixed Figures Hold

- **Day 1 to 3** involve no backdated entry, no negative balance, and no settlement, so no open entry touches them.
- **Auth-A** is approved against 250.00 − 200.00 = 50.00 under every reading of when and against what it is checked
  (AMB-016, AMB-028), and its settlement is accepted because no open entry rejects a settlement within its hold.
- **Day 4 fees** are none because ACC-001 stays positive whether E6 is rejected (465.00) or honoured (285.00).
- **Day 2's restated pre-fee closing** is 1,200.00 − 950.00 − 620.00 = −370.00; E6 is value-dated Day 4 and cannot reach
  it.
- **Day 5's own fee** is assessed under every option in AMB-003, because Day 5 closes at −155.00 or lower before any
  fee.
- **Auth-B** is declined whether E6 was rejected (available −245.00) or honoured (−425.00), and whether retroactive fees
  land before it (AMB-005).
- **Day 6** brings no new fee: after E9 every day closes at or above zero under every option.
- **ACC-002** never goes negative, so it never has a fee, and its Days 1 to 4 hold no events under any replay order.
