# Change the Stream and Watch the Ledger

In this tutorial you run the ledger on the brief's stream, then change a copy of the stream one way at a time and watch
which figures move. By the end you will have seen, in the program's own output, why E9 does not bring everything back
(criterion 6), what a partial settlement keeps on hold, how a retry differs from a clash, what reversing a fee does,
eight of the nine reasons the ledger refuses an event, and what stops a run.

You need the repository installed, as the [README](../../README.md#getting-started) describes: `npm install` once, then
`npx nx run account-ledger-cli:install` once from the repository root, which creates the Python environment every
`uv run --no-sync` command below uses. Every output below was produced by the command above it, on this repository, and
every file you create goes in `local-tmp/`, which git ignores.

## How the Stream Is Written

Every step edits a copy of `apps/account-ledger-cli/streams/challenge.csv`, the brief's ten events, one row each, under
this header:

```text
event,booked,type,account,amount,value_date,reference,instalments,final
E1,1,CREDIT,ACC-001,1200.00,1,,,
E3,2,AUTHORIZATION,ACC-001,200.00,2,Auth-A,,
E9,6,REVERSAL,ACC-001,,2,E7,,
E10,5,CREDIT,ACC-002,10.000,5,,3,
```

- `event`: the event's ID, which a retry repeats (AMB-034).
- `booked` and `value_date`: the day the bank recorded the event and the day its money counts from, as integers.
- `type`: `CREDIT`, `DEBIT`, `AUTHORIZATION`, `SETTLEMENT`, or `REVERSAL`.
- `account`: `ACC-001`, in AED with two places, or `ACC-002`, in BHD with three.
- `amount`: positive, in the account's places; a reversal has none, since it undoes what its target moved.
- `reference`: an authorization's or a settlement's authorization ID, such as `Auth-A`, or a reversal's target, such as
  `E7`.
- `instalments`: a credit only; blank posts it whole, and a count from 2 to 360 splits it (AMB-017, AMB-020).
- `final`: a settlement only; blank or `yes` is final, and `no` keeps the rest of the hold (AMB-013).

A cell a type does not take must be blank, and a row that breaks any of this stops the run with its line number, as step
8 shows.

## 1. Run the Brief's Stream

From the repository root, move into the application and make a folder for your copies:

```bash
cd apps/account-ledger-cli
mkdir -p ../../local-tmp/tutorial
```

Run the brief's stream and look at the last table, Day 6's closing summary:

```bash
PYTHONPATH=src uv run --no-sync python -m account_ledger streams/challenge.csv | tail -n 12
```

```text
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

These are the figures in [OUTPUT_TARGET](../../OUTPUT_TARGET.md). Keep 285.76 and the restated Day 5 of 210.00 in mind;
every step below changes one thing and compares with them. Run the command without `| tail -n 12` to read all seven
days.

## 2. Drop the Reversal

Make a copy of the stream without E9, the reversal of E7, and run it:

```bash
grep -v '^E9,' streams/challenge.csv > ../../local-tmp/tutorial/no-e9.csv
PYTHONPATH=src uv run --no-sync python -m account_ledger ../../local-tmp/tutorial/no-e9.csv | tail -n 21
```

```text

EOD applied
+------+---------------+-------------------------+---------+---------------------------------+------------+
| Step | Event         | Type                    | Account | Detail                          | Value date |
+------+---------------+-------------------------+---------+---------------------------------+------------+
| 1    | FEE-001-D6@D6 | Overdraft fee           | ACC-001 | AED 25.00, for Day 6            | Day 6      |
| 2    | -             | Interest accrual        | ACC-001 | no interest accrued             | -          |
| 2    | INT-002-D6@D6 | Interest accrual        | ACC-002 | 0.004, for Day 6                | Day 6      |
| 3    | CAP-001@D6    | Interest capitalization | ACC-001 | AED 0.11, accrued Days 1 and 3  | Day 6      |
| 3    | CAP-002@D6    | Interest capitalization | ACC-002 | BHD 0.008, accrued Days 5 and 6 | Day 6      |
+------+---------------+-------------------------+---------+---------------------------------+------------+

Closing summary
+------------------------+---------------------------------------------------+---------------+
| Item                   | ACC-001 (AED)                                     | ACC-002 (BHD) |
+------------------------+---------------------------------------------------+---------------+
| Closing ledger balance | −434.89                                           | 10.008        |
| Available balance      | −434.89                                           | 10.008        |
| Authorizations         | Auth-A settled for 185.00; Auth-B declined, 90.00 | none          |
| Errors                 | none                                              | none          |
+------------------------+---------------------------------------------------+---------------+
```

Notice three things:

- Day 6 is still negative, so it is charged a fourth fee, and nothing is refunded: the fees for Days 2, 4, and 5 stay in
  force (AMB-002).
- ACC-001 capitalizes only 0.11. Its interest for Days 2 and 4 was accrued and then adjusted back to zero once E7
  arrived, so only Days 1 and 3 still net to something (AMB-005).
- ACC-002 has no restated Day 5 and only one interest event on Day 6. Without E9, nothing is booked on Day 6 before E10,
  so E10 is processed on Day 5, its own booked day, and is not late at all. In the brief's stream it is E9 that opens
  Day 6 first and makes E10 late (AMB-015).

## 3. Drop E7 as Well

Remove E7 too, so the account never goes negative:

```bash
grep -v -e '^E7,' -e '^E9,' streams/challenge.csv > ../../local-tmp/tutorial/no-e7.csv
PYTHONPATH=src uv run --no-sync python -m account_ledger ../../local-tmp/tutorial/no-e7.csv | tail -n 21
```

```text

EOD applied
+------+---------------+-------------------------+------------------+---------------------------------+------------+
| Step | Event         | Type                    | Account          | Detail                          | Value date |
+------+---------------+-------------------------+------------------+---------------------------------+------------+
| 1    | -             | Fee re-evaluation       | ACC-001, ACC-002 | no fee assessed or refunded     | -          |
| 2    | INT-001-D6@D6 | Interest accrual        | ACC-001          | 0.11, for Day 6                 | Day 6      |
| 2    | INT-002-D6@D6 | Interest accrual        | ACC-002          | 0.004, for Day 6                | Day 6      |
| 3    | CAP-001@D6    | Interest capitalization | ACC-001          | AED 0.79, accrued Days 1 to 6   | Day 6      |
| 3    | CAP-002@D6    | Interest capitalization | ACC-002          | BHD 0.008, accrued Days 5 and 6 | Day 6      |
+------+---------------+-------------------------+------------------+---------------------------------+------------+

Closing summary
+------------------------+--------------------------------------------------------+---------------+
| Item                   | ACC-001 (AED)                                          | ACC-002 (BHD) |
+------------------------+--------------------------------------------------------+---------------+
| Closing ledger balance | 285.79                                                 | 10.008        |
| Available balance      | 195.79                                                 | 10.008        |
| Authorizations         | Auth-A settled for 185.00; Auth-B approved, hold 90.00 | none          |
| Errors                 | none                                                   | none          |
+------------------------+--------------------------------------------------------+---------------+
```

This is the ledger as if E7 had never happened: 0.79 of interest and a closing of 285.79. Criterion 6 says that after E9
everything returns to these pre-E7 values, and step 1 shows it does not: 285.76, not 285.79. The difference is Day 5.
With E7 and E9, Day 5 keeps its three fees, refunded only on Day 6, so it closes at 210.00 and earns 0.08 instead of
0.11 (AMB-004, [REJECTED](../../REJECTED.md#c6--everything-returning-to-its-pre-e7-value-after-e9)).

Without E7, Auth-B is also approved: E8 meets an available balance of 285.00, and its hold of 90.00 leaves 195.00, the
available balance you see less the 0.79. With E7, the same E8 meets −335.00 and is declined (AMB-021).

## 4. Settle Auth-A in Part

The brief's settlements carry no `final` flag, so each is final and releases the whole hold. Mark E5 as partial by
putting `no` in its last cell:

```bash
sed 's/^E5,\(.*\),$/E5,\1,no/' streams/challenge.csv > ../../local-tmp/tutorial/partial.csv
grep '^E5,' ../../local-tmp/tutorial/partial.csv
PYTHONPATH=src uv run --no-sync python -m account_ledger ../../local-tmp/tutorial/partial.csv \
  | sed -n '/^Day 4$/,/^Day 5$/p' | grep -e '^| E5 ' -e '^| Available' -e '^| Authorizations'
```

```text
E5,4,SETTLEMENT,ACC-001,185.00,4,Auth-A,,no
| E5    | Day 4  | Settlement | ACC-001 | Auth-A settles for AED 185.00, hold kept | Day 4      |
| Available balance      | 270.00                                          | 0.000         |
| Authorizations         | Auth-A partially settled for 185.00, hold 15.00 | none          |
```

A partial settlement debits its 185.00 and keeps the rest of the hold, 15.00, for a later settlement, so Day 4's
available balance is 270.00 instead of 285.00 (AMB-013). Nothing settles the 15.00, so it stays held through Day 6,
which is right inside the window: a network may still clear it. The weakness is that it would still be held past 30
days, when no network would; that is the brief's failing test (AMB-018), and
[fix the known weakness](../how-to/fix-the-known-weakness.md) shows it.

## 5. Send an Event Twice

Add two rows to a copy: E1 again, exactly as it was, and a new credit that reuses E4's ID:

```bash
cp streams/challenge.csv ../../local-tmp/tutorial/repeat.csv
echo 'E1,1,CREDIT,ACC-001,1200.00,1,,,' >> ../../local-tmp/tutorial/repeat.csv
echo 'E4,6,CREDIT,ACC-001,5.00,6,,,' >> ../../local-tmp/tutorial/repeat.csv
PYTHONPATH=src uv run --no-sync python -m account_ledger ../../local-tmp/tutorial/repeat.csv \
  | sed -n '/^Day 6$/,$p' | grep -e '^| E1 ' -e '^| E4 ' -e '^| Closing ledger' -e '^| Errors'
```

```text
| E1    | Day 1  | Credit   | ACC-001 | duplicate of E1, no effect            | Day 1      |
| E4    | Day 6  | Credit   | ACC-001 | AED 5.00                              | Day 6      |
| Closing ledger balance  | 285.76                                             | 10.008        |
| Errors                  | E4 refused: ID already used with different content | none          |
```

The event ID is the ledger's idempotency key (AMB-034). E1 again, with the same content, is a retry: it is logged as a
duplicate, moves nothing, and is not an error. The second E4 has different content, so it is a clash, refused and
printed as Day 6's error. The closing is still 285.76. Both rows are in the log, because nothing the ledger receives is
dropped (AMB-014).

## 6. Reverse a Fee

A reversal may undo any accepted event, including one the ledger generated (AMB-035). Reverse the fee for Day 2,
value-dated Day 5 like the fee itself:

```bash
cp streams/challenge.csv ../../local-tmp/tutorial/reverse-fee.csv
echo 'E11,6,REVERSAL,ACC-001,,5,FEE-001-D2@D5,,' >> ../../local-tmp/tutorial/reverse-fee.csv
PYTHONPATH=src uv run --no-sync python -m account_ledger ../../local-tmp/tutorial/reverse-fee.csv | tail -n 11
```

```text
| Item                    | ACC-001 (AED)                                     | ACC-002 (BHD) |
+-------------------------+---------------------------------------------------+---------------+
| Day 2 closing, restated | 250.00                                            | -             |
| Day 3 closing, restated | 650.00                                            | -             |
| Day 4 closing, restated | 285.00                                            | -             |
| Day 5 closing, restated | 235.00                                            | 10.000        |
| Closing ledger balance  | 285.77                                            | 10.008        |
| Available balance       | 285.77                                            | 10.008        |
| Authorizations          | Auth-A settled for 185.00; Auth-B declined, 90.00 | none          |
| Errors                  | none                                              | none          |
+-------------------------+---------------------------------------------------+---------------+
```

The reversal gives the 25.00 back from Day 5, the fee's own value date, where a refund would give it back from Day 6. So
Day 5 closes at 235.00 instead of 210.00, earns 0.09 instead of 0.08, and the account capitalizes 0.77 and closes at
285.77. Run the command without `| tail -n 11` and Day 6's EOD applied shows refunds for Days 4 and 5 only: the Day 2
fee is no longer in force, and Day 2, at 250.00, is not charged again. Had Day 2 still been negative, the next close
would have charged it again (AMB-035).

## 7. Make the Ledger Refuse

Add seven rows to a copy, each one the ledger must refuse for a different reason:

```bash
cp streams/challenge.csv ../../local-tmp/tutorial/refusals.csv
cat >> ../../local-tmp/tutorial/refusals.csv <<'ROWS'
E11,6,REVERSAL,ACC-001,,1,E4,,
E12,6,REVERSAL,ACC-001,,2,E7,,
E13,6,REVERSAL,ACC-002,,6,E4,,
E14,6,AUTHORIZATION,ACC-002,1.000,6,Auth-A,,
E15,6,REVERSAL,ACC-001,,6,E8,,
E16,6,REVERSAL,ACC-001,,6,E99,,
E17,6,REVERSAL,ACC-001,,6,E9,,
ROWS
PYTHONPATH=src uv run --no-sync python -m account_ledger ../../local-tmp/tutorial/refusals.csv \
  | grep -o 'E1[1-7] refused: [^;|]*' | sed 's/ *$//'
```

The Errors row joins a day's refusals with `;`, so the `grep` prints each on its own line, ACC-001's first:

```text
E11 refused: E4 is value-dated later, Day 3
E12 refused: E7 is already reversed by E9
E15 refused: E8 moved no money
E16 refused: E99 is not in the log
E17 refused: E9 is a reversal
E13 refused: E4 is on ACC-001, not ACC-002
E14 refused: Auth-A is already used by E3
```

| Row | Refused because                                            | Entry   |
| --- | ---------------------------------------------------------- | ------- |
| E11 | it is value-dated Day 1, before its target E4, dated Day 3 | AMB-037 |
| E12 | E9 already reversed E7                                     | AMB-028 |
| E13 | its row names ACC-002, but E4 is on ACC-001                | AMB-036 |
| E14 | Auth-A already names the hold E3 opened                    | AMB-038 |
| E15 | E8 was declined, so it moved no money to undo              | AMB-035 |
| E16 | no event E99 exists                                        | AMB-035 |
| E17 | E9 is itself a reversal; a mistaken one is corrected anew  | AMB-028 |

Every refusal is a row the ledger could read, so the run still prints its report and exits 0. Each is recorded in the
log with its reason and moves no balance (AMB-014), so Day 6 still closes at 285.76. The
[code walkthrough](../explanation/code-walkthrough.md#a-reversal) shows the order a reversal's checks run in.

## 8. Break a Row

A row the ledger cannot read at all is not a refusal but a fault in the input. Give E4 a third decimal place, which AED
does not have:

```bash
sed 's/^E4,3,CREDIT,ACC-001,400.00,/E4,3,CREDIT,ACC-001,400.001,/' streams/challenge.csv \
  > ../../local-tmp/tutorial/bad.csv
PYTHONPATH=src uv run --no-sync python -m account_ledger ../../local-tmp/tutorial/bad.csv; echo "exit status $?"
```

```text
error: line 5: amount '400.001' has more than 2 places for AED
exit status 2
```

Nothing is printed on standard output: the first fault stops the run before any day is reported, and the message names
the file's line, the header being line 1. The ledger refuses to round the amount, because rounding would post money its
sender never sent (AMB-006, AMB-014). The [application README](../../apps/account-ledger-cli/README.md#exit-statuses)
lists every exit status.

## Clean Up

Remove your copies:

```bash
rm -r ../../local-tmp/tutorial
```

## What You Saw

- A closing is a sum over the log by value date, so a late event moves days already printed, and each day's report
  restates them (AMB-022).
- A generated fee or refund is dated the day it is generated, so undoing E7 on Day 6 cannot give Day 5 back its fees:
  285.76, not 285.79.
- A retry has no effect; a clash, a refusal, and a decline are all recorded, and only unreadable input stops a run.

The [code walkthrough](../explanation/code-walkthrough.md) follows each of these through the functions that decide it,
and [fees and interest](../explanation/fees-and-interest.md) works through every figure of the close.
