# Numbers

Every constant the ledger and its known-weakness test use, where it comes from, and why it has that value and not half
of it. A value marked open depends on an entry still open in [AMBIGUITIES](AMBIGUITIES.md), which holds its options and
reasoning; a value marked proposed is a chosen value no ambiguity covers, not yet confirmed; a value marked resolved
follows a settled entry there. Figures here follow the resolutions in AMBIGUITIES.

A **given** constant is fixed by the [challenge brief](challenge-raw.md); halving it would break a non-negotiable rule,
so its entry says what the value drives instead. A **chosen** constant is a design decision and carries its own reason.
Both are listed, as AMB-032 resolves.

## Given Constants

| Constant                | Value                    | What it drives                                                |
| ----------------------- | ------------------------ | ------------------------------------------------------------- |
| Window                  | Day 1 to Day 6           | six day-closes and accruals; capitalization on Day 6          |
| Opening balances        | 0.00 / 0.000             | every closing is the sum of its events alone                  |
| Overdraft fee           | AED 25.00                | 25.00 per fee day; at half, AMB-004's gap is 37.50, not 75.00 |
| Fee cap                 | once per day per account | re-evaluation (AMB-002) can never charge a day twice          |
| Daily interest rate     | 0.04% = 0.0004           | 285.00 accrues 0.114 → 0.11; at half, 0.057 → 0.06            |
| Interest floor          | positive balances only   | a zero or negative closing fires no accrual                   |
| Capitalization day      | Day 6                    | one credit per account, value-dated Day 6                     |
| AED precision           | 2 decimal places         | every AED amount is quantized to 0.01                         |
| BHD precision           | 3 decimal places         | every BHD amount is quantized to 0.001                        |
| Authorization threshold | available ≥ 0 after hold | Auth-A passes at 50.00; Auth-B fails at −425.00               |
| Instalment count        | 3                        | fixes the instalment split below                              |

## Chosen Constants

| Constant                    | Value                                | Status             |
| --------------------------- | ------------------------------------ | ------------------ |
| Rate literal                | `Decimal("0.0004")`                  | in place           |
| Decimal working precision   | 28 significant digits                | in place           |
| Rounding mode               | half-even                            | resolved, AMB-006  |
| Instalment split            | 3.333, 3.333, 3.334                  | resolved, AMB-020  |
| Hold released on settlement | the full hold, on a final settlement | resolved, AMB-013  |
| Day representation          | integers 1 to 6                      | resolved, AMB-001  |
| End-of-day order            | fees, interest, then capitalization  | resolved, AMB-023  |
| AED to BHD rate             | 1 AED = 0.10238257 BHD               | resolved, AMB-027  |
| BHD overdraft fee           | BHD 2.560                            | resolved, AMB-027  |
| Unit coverage floor         | 80% of lines                         | in place           |
| Report rule width           | 120 `=` characters                   | in place           |
| Spelled instalment counts   | two to ten                           | in place           |
| Hold time frame             | 30 calendar days                     | test only, AMB-018 |
| Known-weakness replay       | through Day 32                       | test only, AMB-018 |

### Rate literal

Written as the string `"0.0004"`, so the rate is exact; `0.04 / 100` in binary floating point is not. Halving is not a
choice here: this is the given rate, represented without error.

### Decimal working precision

Python's default context of 28 significant digits. A balance of 10¹² at three decimals is 16 digits, and multiplying it
by a four-digit rate needs 20. At 14 digits (half), intermediate products for large balances would be rounded silently
before the deliberate quantize step.

### Rounding mode

Resolved in AMB-006, which holds the options and the reason for half-even. A rounding mode has no half.

### Instalment split

Resolved in AMB-020: divide by three, round down, and add the remainder to the last. It sums to 10.000 with the parts as
equal as possible and the remainder on the last. 3.334 × 3 = 10.002 invents 0.002 BHD, and 3.333 × 3 = 9.999 loses
0.001.

### Hold released on settlement

Resolved in AMB-013: a final settlement, which is every settlement without a marker, releases the whole hold, and one
marked as followed by more captures keeps the rest. Releasing half of Auth-A's hold, 100.00, would still reserve funds
no merchant can claim.

### Day representation

Resolved in AMB-001, which holds the reason for plain integers. Halving does not apply: the window is given as six days.

### End-of-day order

Resolved in AMB-023: fee re-evaluation, then interest, then, on Day 6 only, capitalization. Interest accrues on the
closing the fee rule leaves, and capitalization pays every accrual in the window: AED 0.76 and BHD 0.008. An order has
no half.

### AED to BHD rate

Resolved in AMB-027: the mid-market rate
[XE](https://www.xe.com/en-us/currencyconverter/convert/?Amount=1&From=AED&To=BHD) showed on 2026-09-24 at 12:32 UTC,
taken once and fixed, since the ledger never reaches the network. It matches the cross rate of the two US dollar pegs
(0.376 BHD and 3.6725 AED to the dollar) to seven decimal places. At half the rate, a BHD account's fee would be worth
AED 12.50, not AED 25.00.

### BHD overdraft fee

Resolved in AMB-027: AED 25.00 × 0.10238257 = 2.55956425, rounded half-even to three decimals, is BHD 2.560. It is
charged under the same rules as the AED fee. ACC-002 never goes negative in this stream, so it is never charged.

### Unit coverage floor

Set in commit 199456f for this time-boxed assessment: it still guards the ledger core while leaving room to move fast.
At 40% (half), most of the core could go unexecuted by unit tests.

### Report rule width

The rule above and below each day's banner in [OUTPUT_TARGET](OUTPUT_TARGET.md) is 120 `=` characters. The widest table
the brief's report prints, Day 6's EOD applied, is 119 characters, so the rule spans every table, and 120 is the column
limit every Markdown line here keeps, so the fenced report fits it. At 60 (half), the rule would stop midway across most
of the report's tables.

### Spelled instalment counts

A credit in instalments prints its count as an English word from two to ten and as digits above, so the brief's "three
equal instalments" prints as the brief words it. Two is the least count a split allows. At five (half), a credit in six
to ten instalments would print its count in digits although a word is as short to read.

### Hold time frame

The known-weakness test's measure of how long a hold should live; the ledger itself gives a hold no lifetime (AMB-018).
Visa Business News AI13522, effective 13 April 2024, makes 30 calendar days its longest authorization-to-clearing time
frame, so no network would still honour an older hold. At 15 (half), Visa would still honour a lodging or cruise
authorization, so a lapse test would claim a weakness no network shows.

### Known-weakness replay

Through Day 32, the first day after Auth-A's thirty: the test's Auth-A is approved on Day 1, so Day 31 is the thirtieth
day after it and Day 32 the first on which no network would still honour it. At Day 16 (half), the hold is still
legitimately active, and the test would call a hold that ought to be kept a weakness.

## Derived Figures

Figures derived from these constants are not repeated here. [MOVEMENT](MOVEMENT.md) holds each day's figures, and
[AMBIGUITIES](AMBIGUITIES.md) holds the figures each option would give.
