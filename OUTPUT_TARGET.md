# Output Target

The text the command-line program prints when it replays the stream from the [challenge brief](challenge-raw.md): the
clean view of [MOVEMENT](MOVEMENT.md), which holds the full analysis. Every figure below repeats MOVEMENT unchanged,
because this is the text a test will compare the program's output against; where the two ever disagree, MOVEMENT is
right and this file is corrected.

Each day prints the same three blocks as a day in MOVEMENT: the events processed, the end-of-day steps applied, and the
closing summary. A value in brackets is pending: `[4b]` is key (b) under MOVEMENT's Day 4, which names the entries in
[AMBIGUITIES](AMBIGUITIES.md) it waits on; `[5a]` and `[6a]` also decide on which day E10's lines appear, and `[6l]`
whether its line is printed at all. The layout itself follows the current recommendations of AMB-001 (Day 0 is the
opening state, printed before the window), AMB-019 (a declined authorization is a state), AMB-022 (one report per day,
with restated closings), AMB-023 (the order of end-of-day steps), AMB-025 (every account every day, every known
authorization), and AMB-033 (events, end-of-day steps, and available balance are printed); it changes if any of them is
resolved otherwise. How the program is invoked is AMB-026.

```text
Day 0

Events processed
  none

EOD applied
  none

Closing summary
  Item                    ACC-001 (AED)  ACC-002 (BHD)
  Closing ledger balance  0.00           0.000
  Available balance       0.00           0.000
  Authorizations          none           none
  Errors                  none           none

Day 1

Events processed
  Event  Booked  Type    Account  Detail        Value date
  E1     Day 1   Credit  ACC-001  AED 1,200.00  Day 1
  E2     Day 1   Debit   ACC-001  AED 950.00    Day 1

EOD applied
  Step  Entry  Type               Account           Detail                       Value date
  1     -      Fee re-evaluation  ACC-001, ACC-002  no fee assessed or reversed  -
  2     -      Interest accrual   ACC-001           0.10                         Day 1
  2     -      Interest accrual   ACC-002           0.000                        Day 1

Closing summary
  Item                    ACC-001 (AED)  ACC-002 (BHD)
  Closing ledger balance  250.00         0.000
  Available balance       250.00         0.000
  Authorizations          none           none
  Errors                  none           none

Day 2

Events processed
  Event  Booked  Type           Account  Detail                   Value date
  E3     Day 2   Authorization  ACC-001  Auth-A, hold AED 200.00  Day 2

EOD applied
  Step  Entry  Type               Account           Detail                       Value date
  1     -      Fee re-evaluation  ACC-001, ACC-002  no fee assessed or reversed  -
  2     -      Interest accrual   ACC-001           [2a]                         Day 2
  2     -      Interest accrual   ACC-002           0.000                        Day 2

Closing summary
  Item                    ACC-001 (AED)                 ACC-002 (BHD)
  Closing ledger balance  250.00                        0.000
  Available balance       50.00                         0.000
  Authorizations          Auth-A approved, hold 200.00  none
  Errors                  none                          none

Day 3

Events processed
  Event  Booked  Type    Account  Detail      Value date
  E4     Day 3   Credit  ACC-001  AED 400.00  Day 3

EOD applied
  Step  Entry  Type               Account           Detail                       Value date
  1     -      Fee re-evaluation  ACC-001, ACC-002  no fee assessed or reversed  -
  2     -      Interest accrual   ACC-001           [3a]                         Day 3
  2     -      Interest accrual   ACC-002           0.000                        Day 3

Closing summary
  Item                    ACC-001 (AED)                 ACC-002 (BHD)
  Closing ledger balance  650.00                        0.000
  Available balance       450.00                        0.000
  Authorizations          Auth-A approved, hold 200.00  none
  Errors                  none                          none

Day 4

Events processed
  Event  Booked  Type        Account  Detail                         Value date
  E5     Day 4   Settlement  ACC-001  Auth-A settles for AED 185.00  Day 4
  E6     Day 4   Settlement  ACC-001  Auth-Z settles for AED 180.00  Day 4

EOD applied
  Step  Entry  Type               Account           Detail                       Value date
  1     -      Fee re-evaluation  ACC-001, ACC-002  no fee assessed or reversed  -
  2     -      Interest accrual   ACC-001           [4a]                         Day 4
  2     -      Interest accrual   ACC-002           0.000                        Day 4

Closing summary
  Item                    ACC-001 (AED)              ACC-002 (BHD)
  Closing ledger balance  [4b]                       0.000
  Available balance       [4c]                       0.000
  Authorizations          Auth-A settled for 185.00  none
  Errors                  [4b]                       none

Day 5

Events processed
  Event  Booked  Type           Account  Detail                                      Value date
  E7     Day 5   Debit          ACC-001  AED 620.00                                  Day 2
  E8     Day 5   Authorization  ACC-001  Auth-B, hold AED 90.00                      Day 5
  E10    Day 5   Credit         ACC-002  BHD 10.000 in three equal instalments [5a]  Day 5
  E10-1  Day 5   Credit         ACC-002  BHD instalment 1 of 3 [5a]                  [5a]
  E10-2  Day 5   Credit         ACC-002  BHD instalment 2 of 3 [5a]                  [5a]
  E10-3  Day 5   Credit         ACC-002  BHD instalment 3 of 3 [5a]                  [5a]

EOD applied
  Step  Entry   Type              Account  Detail          Value date
  1     FEE-D2  Overdraft fee     ACC-001  AED 25.00 [5b]  [5b]
  1     FEE-D4  Overdraft fee     ACC-001  AED 25.00 [5c]  [5c]
  1     FEE-D5  Overdraft fee     ACC-001  AED 25.00       Day 5
  2     -       Interest accrual  ACC-001  [5d]            Day 5
  2     -       Interest accrual  ACC-002  [5e]            Day 5

Closing summary
  Item                     ACC-001 (AED)                                      ACC-002 (BHD)
  Day 2 closing, restated  [5f]                                               -
  Day 3 closing, restated  [5g]                                               -
  Day 4 closing, restated  [5h]                                               -
  Closing ledger balance   [5i]                                               [5j]
  Available balance        [5k]                                               [5j]
  Authorizations           Auth-A settled for 185.00; Auth-B declined, 90.00  none
  Errors                   [5l]                                               none

Day 6

Events processed
  Event  Booked  Type      Account  Detail                                      Value date
  E9     Day 6   Reversal  ACC-001  reverses E7                                 Day 2
  E10    Day 5   Credit    ACC-002  BHD 10.000 in three equal instalments [6a]  Day 5
  E10-1  Day 5   Credit    ACC-002  BHD instalment 1 of 3 [6a]                  [6a]
  E10-2  Day 5   Credit    ACC-002  BHD instalment 2 of 3 [6a]                  [6a]
  E10-3  Day 5   Credit    ACC-002  BHD instalment 3 of 3 [6a]                  [6a]

EOD applied
  Step  Entry        Type                     Account           Detail               Value date
  1     FEE-REV-D2   Fee reversal             ACC-001           AED 25.00 [6b]       [6b]
  1     FEE-REV-D4   Fee reversal             ACC-001           AED 25.00 [6b]       [6b]
  1     FEE-REV-D5   Fee reversal             ACC-001           AED 25.00 [6c]       [6c]
  1     -            Fee re-evaluation        ACC-001, ACC-002  no new fee assessed  -
  2     -            Interest accrual         ACC-001           [6d]                 Day 6
  2     -            Interest accrual         ACC-002           [6e]                 Day 6
  3     CAP-ACC-001  Interest capitalization  ACC-001           [6f]                 Day 6
  3     CAP-ACC-002  Interest capitalization  ACC-002           [6g]                 Day 6

Closing summary
  Item                     ACC-001 (AED)                                      ACC-002 (BHD)
  Day 2 closing, restated  [6h]                                               -
  Day 3 closing, restated  [6i]                                               -
  Day 4 closing, restated  [6j]                                               -
  Day 5 closing, restated  [6k]                                               [6l]
  Closing ledger balance   [6m]                                               [6n]
  Available balance        [6o]                                               [6n]
  Authorizations           Auth-A settled for 185.00; Auth-B declined, 90.00  none
  Errors                   none                                               [6p]
```
