# Numbers

Every constant the ledger uses, where it comes from, and why it has that value and not half of it. A value marked open
depends on an entry still open in [AMBIGUITIES](AMBIGUITIES.md), which holds its options and reasoning; a value marked
proposed is a chosen value no ambiguity covers, not yet confirmed. Figures here assume the current recommendations in
AMBIGUITIES, as that file's own figures do.

A **given** constant is fixed by the [challenge brief](challenge-raw.md); halving it would break a non-negotiable rule,
so its entry says what the value drives instead. A **chosen** constant is a design decision and carries its own reason.

## Given Constants

| Constant                | Value                    | What it drives                                                |
| ----------------------- | ------------------------ | ------------------------------------------------------------- |
| Window                  | Day 1 to Day 6           | six day-closes and accruals; capitalization on Day 6          |
| Opening balances        | 0.00 / 0.000             | every closing is the sum of entries alone                     |
| Overdraft fee           | AED 25.00                | 25.00 per fee day; at half, AMB-004's gap is 37.50, not 75.00 |
| Fee cap                 | once per day per account | re-evaluation (AMB-002) can never charge a day twice          |
| Daily interest rate     | 0.04% = 0.0004           | 465.00 accrues 0.186 → 0.19; at half, 0.093 → 0.09            |
| Interest floor          | positive balances only   | a zero or negative closing accrues exactly 0                  |
| Capitalization day      | Day 6                    | one credit per account, value-dated Day 6                     |
| AED precision           | 2 decimal places         | every AED amount is quantized to 0.01                         |
| BHD precision           | 3 decimal places         | every BHD amount is quantized to 0.001                        |
| Authorization threshold | available ≥ 0 after hold | Auth-A passes at 50.00; Auth-B fails at −245.00               |
| Instalment count        | 3                        | fixes the instalment split below                              |

## Chosen Constants

| Constant                    | Value                 | Status        |
| --------------------------- | --------------------- | ------------- |
| Rate literal                | `Decimal("0.0004")`   | proposed      |
| Decimal working precision   | 28 significant digits | proposed      |
| Rounding mode               | half-even             | open, AMB-006 |
| Instalment split            | 3.333, 3.333, 3.334   | open, AMB-020 |
| Hold released on settlement | the full hold         | open, AMB-013 |
| Day representation          | integers 1 to 6       | open, AMB-001 |
| Unit coverage floor         | 80% of lines          | in place      |

### Rate literal

Written as the string `"0.0004"`, so the rate is exact; `0.04 / 100` in binary floating point is not. Halving is not a
choice here: this is the given rate, represented without error.

### Decimal working precision

Python's default context of 28 significant digits. A balance of 10¹² at three decimals is 16 digits, and multiplying it
by a four-digit rate needs 20. At 14 digits (half), intermediate products for large balances would be rounded silently
before the deliberate quantize step.

### Rounding mode

Open in AMB-006, which holds the options and the reason for half-even. A rounding mode has no half.

### Instalment split

The only three-decimal split that sums to 10.000 with the parts as equal as possible. 3.334 × 3 = 10.002 invents 0.002
BHD, and 3.333 × 3 = 9.999 loses 0.001.

### Hold released on settlement

Open in AMB-013, which holds the reason for releasing the whole hold. Releasing half of it, 100.00, would still reserve
funds no merchant can claim.

### Day representation

Open in AMB-001, which holds the reason for plain integers. Halving does not apply: the window is given as six days.

### Unit coverage floor

Set in commit 199456f for this time-boxed assessment: it still guards the ledger core while leaving room to move fast.
At 40% (half), most of the core could go unexecuted by unit tests.

## Derived Figures

Figures derived from these constants are not repeated here. [MOVEMENT](MOVEMENT.md) holds each day's figures where every
open option agrees, and [AMBIGUITIES](AMBIGUITIES.md) holds the figures each option gives.
