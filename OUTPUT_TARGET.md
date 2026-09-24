# Output Target

The text the command-line program prints when it replays the stream from the [challenge brief](challenge-raw.md): the
clean view of [MOVEMENT](MOVEMENT.md), which holds the full analysis. Every figure below repeats MOVEMENT unchanged,
because this is the text a test will compare the program's output against; where the two ever disagree, MOVEMENT is
right and this file is corrected.

A value in brackets is pending: `[4b]` is key (a) under MOVEMENT's Day 4, which names the entries in
[AMBIGUITIES](AMBIGUITIES.md) it waits on; `[6l]` also decides whether its line is printed. The layout itself follows
the current recommendations of AMB-001 (Day 0 is the opening state, printed before the window), AMB-019 (a declined
authorization is a state), AMB-022 (one report per day, with restated closings), AMB-025 (every account every day, every
known authorization), and AMB-033 (available balance and capitalized interest are printed); it changes if any of them is
resolved otherwise. How the program is invoked is AMB-026.

```text
Day 0
  ACC-001 (AED)
    Closing ledger balance   0.00
    Available balance        0.00
    Fees assessed            none
    Authorizations           none
    Errors                   none
  ACC-002 (BHD)
    Closing ledger balance   0.000
    Available balance        0.000
    Fees assessed            none
    Authorizations           none
    Errors                   none

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
    Authorizations           Auth-A  APPROVED  hold 200.00
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
    Authorizations           Auth-A  APPROVED  hold 200.00
    Errors                   none
  ACC-002 (BHD)
    Closing ledger balance   0.000
    Available balance        0.000
    Fees assessed            none
    Authorizations           none
    Errors                   none

Day 4
  ACC-001 (AED)
    Closing ledger balance   [4b]
    Available balance        [4c]
    Fees assessed            none
    Authorizations           Auth-A  SETTLED   185.00
    Errors                   [4b]
  ACC-002 (BHD)
    Closing ledger balance   0.000
    Available balance        0.000
    Fees assessed            none
    Authorizations           none
    Errors                   none

Day 5
  ACC-001 (AED)
    Restated closings        Day 2  [5f]
                             Day 3  [5g]
                             Day 4  [5h]
    Closing ledger balance   [5i]
    Available balance        [5k]
    Fees assessed            [5b] for Day 2
                             [5c] for Day 4
                             25.00 for Day 5
    Authorizations           Auth-A  SETTLED   185.00
                             Auth-B  DECLINED  90.00
    Errors                   [5l]
  ACC-002 (BHD)
    Closing ledger balance   [5j]
    Available balance        [5j]
    Fees assessed            none
    Authorizations           none
    Errors                   none

Day 6
  ACC-001 (AED)
    Restated closings        Day 2  [6h]
                             Day 3  [6i]
                             Day 4  [6j]
                             Day 5  [6k]
    Closing ledger balance   [6m]
    Available balance        [6o]
    Fees assessed            none
    Fee reversals            [6b] for Day 2
                             [6b] for Day 4
                             [6c] for Day 5
    Interest capitalized     [6f]
    Authorizations           Auth-A  SETTLED   185.00
                             Auth-B  DECLINED  90.00
    Errors                   none
  ACC-002 (BHD)
    Restated closings        Day 5  [6l]
    Closing ledger balance   [6n]
    Available balance        [6n]
    Fees assessed            none
    Interest capitalized     [6g]
    Authorizations           none
    Errors                   [6p]
```
