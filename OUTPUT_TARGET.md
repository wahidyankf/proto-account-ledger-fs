# Output Target

The text the command-line program prints when it processes the stream from the [challenge brief](challenge-raw.md): the
clean view of [MOVEMENT](MOVEMENT.md), which holds the full analysis. Every figure below repeats MOVEMENT unchanged,
because this is the text a test will compare the program's output against; where the two ever disagree, MOVEMENT is
right and this file is corrected.

Each day opens with a banner between two lines of `=`, then prints the same three blocks as a day in MOVEMENT, each
drawn as a plain-text table: the events processed, the end-of-day steps applied, and the closing summary (AMB-033).
Every figure is fixed, since no entry in [AMBIGUITIES](AMBIGUITIES.md) is open. A Detail cell prints MOVEMENT's text up
to its first semicolon, leaving out the notes after it, and a block with nothing in it prints `none`. Every event the
ledger fires is printed with its marker, such as `FEE-001-D2@D5`, and a step that fires none prints `-` (AMB-024). Day 0
is the opening state, printed before the window (AMB-001); a declined authorization is a state (AMB-019); each day
prints one report as known that day, with the earlier closings it restated (AMB-022); and every day lists both accounts
and every known authorization (AMB-025). The program prints it, and an end-to-end test compares the two (AMB-026).

```text
========================================================================================================================
Day 0
========================================================================================================================

Events processed
  none

EOD applied
  none

Closing summary
+------------------------+---------------+---------------+
| Item                   | ACC-001 (AED) | ACC-002 (BHD) |
+------------------------+---------------+---------------+
| Closing ledger balance | 0.00          | 0.000         |
| Available balance      | 0.00          | 0.000         |
| Authorizations         | none          | none          |
| Errors                 | none          | none          |
+------------------------+---------------+---------------+

========================================================================================================================
Day 1
========================================================================================================================

Events processed
+-------+--------+--------+---------+--------------+------------+
| Event | Booked | Type   | Account | Detail       | Value date |
+-------+--------+--------+---------+--------------+------------+
| E1    | Day 1  | Credit | ACC-001 | AED 1,200.00 | Day 1      |
| E2    | Day 1  | Debit  | ACC-001 | AED 950.00   | Day 1      |
+-------+--------+--------+---------+--------------+------------+

EOD applied
+------+---------------+-------------------+------------------+-----------------------------+------------+
| Step | Event         | Type              | Account          | Detail                      | Value date |
+------+---------------+-------------------+------------------+-----------------------------+------------+
| 1    | -             | Fee re-evaluation | ACC-001, ACC-002 | no fee assessed or refunded | -          |
| 2    | INT-001-D1@D1 | Interest accrual  | ACC-001          | 0.10, for Day 1             | Day 1      |
| 2    | -             | Interest accrual  | ACC-002          | no interest accrued         | -          |
+------+---------------+-------------------+------------------+-----------------------------+------------+

Closing summary
+------------------------+---------------+---------------+
| Item                   | ACC-001 (AED) | ACC-002 (BHD) |
+------------------------+---------------+---------------+
| Closing ledger balance | 250.00        | 0.000         |
| Available balance      | 250.00        | 0.000         |
| Authorizations         | none          | none          |
| Errors                 | none          | none          |
+------------------------+---------------+---------------+

========================================================================================================================
Day 2
========================================================================================================================

Events processed
+-------+--------+---------------+---------+-------------------------+------------+
| Event | Booked | Type          | Account | Detail                  | Value date |
+-------+--------+---------------+---------+-------------------------+------------+
| E3    | Day 2  | Authorization | ACC-001 | Auth-A, hold AED 200.00 | Day 2      |
+-------+--------+---------------+---------+-------------------------+------------+

EOD applied
+------+---------------+-------------------+------------------+-----------------------------+------------+
| Step | Event         | Type              | Account          | Detail                      | Value date |
+------+---------------+-------------------+------------------+-----------------------------+------------+
| 1    | -             | Fee re-evaluation | ACC-001, ACC-002 | no fee assessed or refunded | -          |
| 2    | INT-001-D2@D2 | Interest accrual  | ACC-001          | 0.10, for Day 2             | Day 2      |
| 2    | -             | Interest accrual  | ACC-002          | no interest accrued         | -          |
+------+---------------+-------------------+------------------+-----------------------------+------------+

Closing summary
+------------------------+------------------------------+---------------+
| Item                   | ACC-001 (AED)                | ACC-002 (BHD) |
+------------------------+------------------------------+---------------+
| Closing ledger balance | 250.00                       | 0.000         |
| Available balance      | 50.00                        | 0.000         |
| Authorizations         | Auth-A approved, hold 200.00 | none          |
| Errors                 | none                         | none          |
+------------------------+------------------------------+---------------+

========================================================================================================================
Day 3
========================================================================================================================

Events processed
+-------+--------+--------+---------+------------+------------+
| Event | Booked | Type   | Account | Detail     | Value date |
+-------+--------+--------+---------+------------+------------+
| E4    | Day 3  | Credit | ACC-001 | AED 400.00 | Day 3      |
+-------+--------+--------+---------+------------+------------+

EOD applied
+------+---------------+-------------------+------------------+-----------------------------+------------+
| Step | Event         | Type              | Account          | Detail                      | Value date |
+------+---------------+-------------------+------------------+-----------------------------+------------+
| 1    | -             | Fee re-evaluation | ACC-001, ACC-002 | no fee assessed or refunded | -          |
| 2    | INT-001-D3@D3 | Interest accrual  | ACC-001          | 0.26, for Day 3             | Day 3      |
| 2    | -             | Interest accrual  | ACC-002          | no interest accrued         | -          |
+------+---------------+-------------------+------------------+-----------------------------+------------+

Closing summary
+------------------------+------------------------------+---------------+
| Item                   | ACC-001 (AED)                | ACC-002 (BHD) |
+------------------------+------------------------------+---------------+
| Closing ledger balance | 650.00                       | 0.000         |
| Available balance      | 450.00                       | 0.000         |
| Authorizations         | Auth-A approved, hold 200.00 | none          |
| Errors                 | none                         | none          |
+------------------------+------------------------------+---------------+

========================================================================================================================
Day 4
========================================================================================================================

Events processed
+-------+--------+------------+---------+-------------------------------+------------+
| Event | Booked | Type       | Account | Detail                        | Value date |
+-------+--------+------------+---------+-------------------------------+------------+
| E5    | Day 4  | Settlement | ACC-001 | Auth-A settles for AED 185.00 | Day 4      |
| E6    | Day 4  | Settlement | ACC-001 | Auth-Z force-posts AED 180.00 | Day 4      |
+-------+--------+------------+---------+-------------------------------+------------+

EOD applied
+------+---------------+-------------------+------------------+-----------------------------+------------+
| Step | Event         | Type              | Account          | Detail                      | Value date |
+------+---------------+-------------------+------------------+-----------------------------+------------+
| 1    | -             | Fee re-evaluation | ACC-001, ACC-002 | no fee assessed or refunded | -          |
| 2    | INT-001-D4@D4 | Interest accrual  | ACC-001          | 0.11, for Day 4             | Day 4      |
| 2    | -             | Interest accrual  | ACC-002          | no interest accrued         | -          |
+------+---------------+-------------------+------------------+-----------------------------+------------+

Closing summary
+------------------------+---------------------------+---------------+
| Item                   | ACC-001 (AED)             | ACC-002 (BHD) |
+------------------------+---------------------------+---------------+
| Closing ledger balance | 285.00                    | 0.000         |
| Available balance      | 285.00                    | 0.000         |
| Authorizations         | Auth-A settled for 185.00 | none          |
| Errors                 | none                      | none          |
+------------------------+---------------------------+---------------+

========================================================================================================================
Day 5
========================================================================================================================

Events processed
+-------+--------+---------------+---------+------------------------+------------+
| Event | Booked | Type          | Account | Detail                 | Value date |
+-------+--------+---------------+---------+------------------------+------------+
| E7    | Day 5  | Debit         | ACC-001 | AED 620.00             | Day 2      |
| E8    | Day 5  | Authorization | ACC-001 | Auth-B, hold AED 90.00 | Day 5      |
+-------+--------+---------------+---------+------------------------+------------+

EOD applied
+------+---------------+---------------------+---------+----------------------+------------+
| Step | Event         | Type                | Account | Detail               | Value date |
+------+---------------+---------------------+---------+----------------------+------------+
| 1    | FEE-001-D2@D5 | Overdraft fee       | ACC-001 | AED 25.00, for Day 2 | Day 5      |
| 1    | FEE-001-D4@D5 | Overdraft fee       | ACC-001 | AED 25.00, for Day 4 | Day 5      |
| 1    | FEE-001-D5@D5 | Overdraft fee       | ACC-001 | AED 25.00, for Day 5 | Day 5      |
| 2    | INT-001-D2@D5 | Interest adjustment | ACC-001 | −0.10, for Day 2     | Day 5      |
| 2    | INT-001-D3@D5 | Interest adjustment | ACC-001 | −0.25, for Day 3     | Day 5      |
| 2    | INT-001-D4@D5 | Interest adjustment | ACC-001 | −0.11, for Day 4     | Day 5      |
| 2    | -             | Interest accrual    | ACC-001 | no interest accrued  | -          |
| 2    | -             | Interest accrual    | ACC-002 | no interest accrued  | -          |
+------+---------------+---------------------+---------+----------------------+------------+

Closing summary
+-------------------------+---------------------------------------------------+---------------+
| Item                    | ACC-001 (AED)                                     | ACC-002 (BHD) |
+-------------------------+---------------------------------------------------+---------------+
| Day 2 closing, restated | −370.00                                           | -             |
| Day 3 closing, restated | 30.00                                             | -             |
| Day 4 closing, restated | −335.00                                           | -             |
| Closing ledger balance  | −410.00                                           | 0.000         |
| Available balance       | −410.00                                           | 0.000         |
| Authorizations          | Auth-A settled for 185.00; Auth-B declined, 90.00 | none          |
| Errors                  | none                                              | none          |
+-------------------------+---------------------------------------------------+---------------+

========================================================================================================================
Day 6
========================================================================================================================

Events processed
+-------+--------+----------+---------+---------------------------------------+------------+
| Event | Booked | Type     | Account | Detail                                | Value date |
+-------+--------+----------+---------+---------------------------------------+------------+
| E9    | Day 6  | Reversal | ACC-001 | reverses E7                           | Day 2      |
| E10   | Day 5  | Credit   | ACC-002 | BHD 10.000 in three equal instalments | Day 5      |
| E10-1 | Day 5  | Credit   | ACC-002 | BHD 3.333, instalment 1 of 3          | Day 5      |
| E10-2 | Day 5  | Credit   | ACC-002 | BHD 3.333, instalment 2 of 3          | Day 5      |
| E10-3 | Day 5  | Credit   | ACC-002 | BHD 3.334, instalment 3 of 3          | Day 5      |
+-------+--------+----------+---------+---------------------------------------+------------+

EOD applied
+------+------------------+-------------------------+------------------+---------------------------------+------------+
| Step | Event            | Type                    | Account          | Detail                          | Value date |
+------+------------------+-------------------------+------------------+---------------------------------+------------+
| 1    | REFUND-001-D2@D6 | Fee refund              | ACC-001          | AED 25.00, for Day 2            | Day 6      |
| 1    | REFUND-001-D4@D6 | Fee refund              | ACC-001          | AED 25.00, for Day 4            | Day 6      |
| 1    | REFUND-001-D5@D6 | Fee refund              | ACC-001          | AED 25.00, for Day 5            | Day 6      |
| 1    | -                | Fee re-evaluation       | ACC-001, ACC-002 | no new fee assessed             | -          |
| 2    | INT-001-D2@D6    | Interest adjustment     | ACC-001          | 0.10, for Day 2                 | Day 6      |
| 2    | INT-001-D3@D6    | Interest adjustment     | ACC-001          | 0.25, for Day 3                 | Day 6      |
| 2    | INT-001-D4@D6    | Interest adjustment     | ACC-001          | 0.11, for Day 4                 | Day 6      |
| 2    | INT-001-D5@D6    | Interest adjustment     | ACC-001          | 0.08, for Day 5                 | Day 6      |
| 2    | INT-001-D6@D6    | Interest accrual        | ACC-001          | 0.11, for Day 6                 | Day 6      |
| 2    | INT-002-D5@D6    | Interest adjustment     | ACC-002          | 0.004, for Day 5                | Day 6      |
| 2    | INT-002-D6@D6    | Interest accrual        | ACC-002          | 0.004, for Day 6                | Day 6      |
| 3    | CAP-001@D6       | Interest capitalization | ACC-001          | AED 0.76, accrued Days 1 to 6   | Day 6      |
| 3    | CAP-002@D6       | Interest capitalization | ACC-002          | BHD 0.008, accrued Days 5 and 6 | Day 6      |
+------+------------------+-------------------------+------------------+---------------------------------+------------+

Closing summary
+-------------------------+---------------------------------------------------+---------------+
| Item                    | ACC-001 (AED)                                     | ACC-002 (BHD) |
+-------------------------+---------------------------------------------------+---------------+
| Day 2 closing, restated | 250.00                                            | -             |
| Day 3 closing, restated | 650.00                                            | -             |
| Day 4 closing, restated | 285.00                                            | -             |
| Day 5 closing, restated | 210.00                                            | 10.000        |
| Closing ledger balance  | 285.76                                            | 10.008        |
| Available balance       | 285.76                                            | 10.008        |
| Authorizations          | Auth-A settled for 185.00; Auth-B declined, 90.00 | none          |
| Errors                  | none                                              | none          |
+-------------------------+---------------------------------------------------+---------------+
```
