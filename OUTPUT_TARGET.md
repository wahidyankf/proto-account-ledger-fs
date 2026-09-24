# Output Target

The text the command-line program prints when it replays the stream from the [challenge brief](challenge-raw.md): the
clean view of [MOVEMENT](MOVEMENT.md), which holds the full analysis. Every figure below repeats MOVEMENT unchanged,
because this is the text a test will compare the program's output against; where the two ever disagree, MOVEMENT is
right and this file is corrected.

A value in brackets is pending: `[4a]` is key (a) under MOVEMENT's Day 4, which names the entries in
[AMBIGUITIES](AMBIGUITIES.md) it waits on. The layout itself follows the current recommendations of AMB-002 (one report
per day, with restated closings), AMB-017 (a declined authorization is a state), AMB-021 (every account every day, every
known authorization), and AMB-033 (available balance and capitalized interest are printed); it changes if any of them is
resolved otherwise. How the program is invoked is AMB-030.

```text
Day 1
  ACC-001 (AED)
    Closing ledger balance   250.00
    Available balance        250.00
    Fees assessed            none
    Authorizations           none
    Errors                   none
  ACC-002 (BHD)
    Closing ledger balance   0.000
    Available balance        0.000
    Fees assessed            none
    Authorizations           none
    Errors                   none

Day 2
  ACC-001 (AED)
    Closing ledger balance   250.00
    Available balance        50.00
    Fees assessed            none
    Authorizations           Auth-A  APPROVED  hold 200.00, active
    Errors                   none
  ACC-002 (BHD)
    Closing ledger balance   0.000
    Available balance        0.000
    Fees assessed            none
    Authorizations           none
    Errors                   none

Day 3
  ACC-001 (AED)
    Closing ledger balance   650.00
    Available balance        450.00
    Fees assessed            none
    Authorizations           Auth-A  APPROVED  hold 200.00, active
    Errors                   none
  ACC-002 (BHD)
    Closing ledger balance   0.000
    Available balance        0.000
    Fees assessed            none
    Authorizations           none
    Errors                   none

Day 4
  ACC-001 (AED)
    Closing ledger balance   [4a]
    Available balance        [4b]
    Fees assessed            none
    Authorizations           Auth-A  SETTLED   185.00
    Errors                   [4a]
  ACC-002 (BHD)
    Closing ledger balance   0.000
    Available balance        0.000
    Fees assessed            none
    Authorizations           none
    Errors                   none

Day 5
  ACC-001 (AED)
    Day 2 closing, restated  -370.00 before fees
    Closing ledger balance   [5a]
    Available balance        [5c]
    Fees assessed            25.00 for Day 5
                             [5d] for other days
    Authorizations           Auth-A  SETTLED   185.00
                             Auth-B  DECLINED  hold 90.00
    Errors                   [5e]
  ACC-002 (BHD)
    Closing ledger balance   [5b]
    Available balance        [5b]
    Fees assessed            none
    Authorizations           none
    Errors                   none

Day 6
  ACC-001 (AED)
    Closing ledger balance   [6a]
    Available balance        [6a]
    Fees assessed            none
    Fee reversals            [6c]
    Interest capitalized     [6d]
    Authorizations           Auth-A  SETTLED   185.00
                             Auth-B  DECLINED  hold 90.00
    Errors                   none
  ACC-002 (BHD)
    Closing ledger balance   [6b]
    Available balance        [6b]
    Fees assessed            none
    Interest capitalized     [6e]
    Authorizations           none
    Errors                   [6f]
```
