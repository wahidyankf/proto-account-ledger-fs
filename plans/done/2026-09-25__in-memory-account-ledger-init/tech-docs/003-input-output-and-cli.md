# Input, Output, and the Command Line

The shell around the core: the stream file it reads (D1, D2), the text it prints, and the command-line contract (D13).
Parsing and rendering are pure functions over text, so the unit layer tests them without touching a file; only `main`
touches the operating system. They are also the only two places raw values exist (D15): the parser turns text into the
domain types of [the domain model](001-domain-model.md), and the renderer turns them back into text.

## The Stream File

CSV, UTF-8, with a header row and one event per row. Every cell is read as text; an amount goes from text to `Aed` or
`Bhd` through its `parse`, in the account's currency, and never passes through a float.

| Column        | Holds                                                                 | Required for         |
| ------------- | --------------------------------------------------------------------- | -------------------- |
| `event`       | the event ID, such as `E1`                                            | every row            |
| `booked`      | the booked day, a whole number                                        | every row            |
| `type`        | `CREDIT`, `DEBIT`, `AUTHORIZATION`, `SETTLEMENT`, or `REVERSAL`       | every row            |
| `account`     | an account ID the configuration holds                                 | every row            |
| `amount`      | above zero, with no more places than the account's currency           | all but `REVERSAL`   |
| `value_date`  | the value day, a whole number                                         | every row            |
| `reference`   | the hold ID for an authorization or settlement; the reversed event ID | the last three types |
| `instalments` | a whole number of at least 2, or blank for one posting                | `CREDIT` only        |
| `final`       | `yes`, `no`, or blank for `yes`                                       | `SETTLEMENT` only    |

The `final` column arrives with partial capture, built last (Phase 8, AMB-013); until then the header is the first eight
columns, and if partial capture falls back (recovery item RC2), it stays eight. The parser checks the header and the
cell count against the columns of the version it is.

`apps/account-ledger-cli/streams/challenge.csv` holds the brief's stream. With all nine columns it reads as below;
before Phase 8 each row lacks the last cell and the header its last column.

```text
event,booked,type,account,amount,value_date,reference,instalments,final
E1,1,CREDIT,ACC-001,1200.00,1,,,
E2,1,DEBIT,ACC-001,950.00,1,,,
E3,2,AUTHORIZATION,ACC-001,200.00,2,Auth-A,,
E4,3,CREDIT,ACC-001,400.00,3,,,
E5,4,SETTLEMENT,ACC-001,185.00,4,Auth-A,,
E6,4,SETTLEMENT,ACC-001,180.00,4,Auth-Z,,
E7,5,DEBIT,ACC-001,620.00,2,,,
E8,5,AUTHORIZATION,ACC-001,90.00,5,Auth-B,,
E9,6,REVERSAL,ACC-001,,2,E7,,
E10,5,CREDIT,ACC-002,10.000,5,,3,
```

## Parsing

```text
stream_csv.py
  parse_stream(text, config) -> tuple[IncomingEvent, ...] | StreamError
  StreamError     line, message
```

A malformed stream is an expected failure, so it is a returned value, not an exception (S3 in the
[decision records](005-decision-records.md)). So is a well-formed row the ledger cannot represent, such as one naming an
account it does not hold: that is a fault in the input, never a logged refusal (AMB-014, D21). The first fault found is
reported, with the physical line number, the header being line 1. `H` is the header of this version and `K` its column
count:

| Fault                                                 | Message                                                     |
| ----------------------------------------------------- | ----------------------------------------------------------- |
| the header is not exactly the version's columns       | `line 1: expected the header H`                             |
| a row has another number of cells                     | `line N: expected K cells, found M`                         |
| an event ID, account ID, or hold ID of the wrong form | `line N: event ID 'X' is not valid`, and so on per column   |
| an unknown type                                       | `line N: type 'X' is not one of CREDIT, DEBIT, …, REVERSAL` |
| an account the configuration does not hold            | `line N: account 'X' is not held by this ledger`            |
| an amount that is not a decimal                       | `line N: amount 'X' is not a decimal number`                |
| an amount with more places than its currency          | `line N: amount 'X' has more than P places for AED`         |
| an amount that is zero or negative                    | `line N: amount 'X' must be above zero`                     |
| a missing required cell                               | `line N: column 'C' is required for TYPE`                   |
| a cell given for a type that takes none               | `line N: column 'C' does not apply to TYPE`                 |
| a day that is not a whole number inside the window    | `line N: day 'X' is outside the window 1 to 6`              |
| a reversal whose target is not an event ID or marker  | `line N: reference 'X' is not an event ID`                  |
| an instalment count below 2                           | `line N: instalments must be at least 2`                    |
| more instalments than the amount has minor units      | `line N: 0.002 cannot be split into 3 instalments`          |
| a `final` cell other than yes, no, or blank           | `line N: final must be yes or no`                           |

The currency, its places, and the window in these messages are the configuration's. Each fault is refused by the
constructor of the type it would have built, so the parser adds only the line number and the column name.

## Rendering

```text
render.py
  render(reports) -> str       every day's report, in order, ending with a newline
```

The exact text is [OUTPUT_TARGET](../../../../OUTPUT_TARGET.md)'s fenced block followed by one newline, and the
end-to-end test compares them byte for byte (AC-01). OUTPUT_TARGET is the source for every text the brief's stream
prints: each Type string, Detail pattern, Item label, column header, and state text is copied from it, never reinvented.
The rules that produce it:

- **Layout.** A day opens with a line of 120 `=`, the line `Day N`, and another line of 120 `=`. The banner and the
  three titled blocks, `Events processed`, `EOD applied`, and `Closing summary`, are separated by one blank line, as is
  each day from the next. The output ends with the last table's closing border and a newline. A block with no rows
  prints two spaces and `none` instead of a table (AMB-033).
- **Tables.** Borders of `+`, `-`, and `|`; one space either side of each cell; every cell left-aligned; every column as
  wide as its widest cell, header included, counted in characters, so `−` is one.
- **Columns.** Events processed: `Event`, `Booked`, `Type`, `Account`, `Detail`, `Value date`. EOD applied: `Step`,
  `Event`, `Type`, `Account`, `Detail`, `Value date`. Closing summary: `Item`, then `ACC-001 (AED)` and `ACC-002 (BHD)`
  in configuration order. Day cells read `Day N`.
- **Types.** `Credit`, `Debit`, `Authorization`, `Settlement`, and `Reversal` for incoming events, an instalment
  printing as `Credit`; `Fee re-evaluation`, `Overdraft fee`, `Fee refund`, `Interest accrual`, `Interest adjustment`,
  and `Interest capitalization` for end-of-day rows. The fee re-evaluation row's Account cell lists every account,
  joined by `, `.
- **Amounts.** Their currency's places, a comma every three digits, and `−` (U+2212) for a negative. In a Detail cell an
  amount carries its currency code, `AED 25.00`, except an interest accrual's or adjustment's, which prints as
  `0.10, for Day 2` or `−0.10, for Day 2`, a `DOWN` adjustment taking the minus. The closing summary and the state texts
  print no code.
- **Missing values.** `-` for a cell with no value, such as an unchanged restated closing or a row with no marker.
- **Items.** `Day N closing, restated` rows first, oldest day first, then `Closing ledger balance`, `Available balance`,
  `Authorizations`, and `Errors`; `none` in the last two for an account with nothing.
- **Instalment wording.** `in three equal instalments` spells the count as an English word from two to ten, and as
  digits above; each part prints as `BHD 3.333, instalment 1 of 3`.
- **Capitalization days.** `accrued Days 1 to 6` for three or more consecutive days, `Days 5 and 6` for two, `Day 5` for
  one, and `Days 1, 2, and 4` otherwise, counting the days whose interest events do not net to zero.

The brief's stream never prints the texts below, so they are chosen here (D22), each in the pattern of the nearest text
OUTPUT_TARGET does print:

| Case                                 | Where               | Text                                               |
| ------------------------------------ | ------------------- | -------------------------------------------------- |
| a partial settlement                 | Detail              | `Auth-A settles for AED 120.00, hold kept`         |
| a force-post against a known hold ID | Detail              | `Auth-A force-posts AED 40.00`, as E6 prints       |
| a partially settled authorization    | Authorizations      | `Auth-A partially settled for 120.00, hold 80.00`  |
| a settled one after several captures | Authorizations      | `Auth-A settled for 200.00`, the captures' sum     |
| a duplicate                          | Detail              | `duplicate of E4, no effect`                       |
| a rejected event                     | Detail              | its usual detail; the reason prints under Errors   |
| a reversal of a fired event          | Detail              | `reverses FEE-001-D2@D5`                           |
| nothing capitalized on its day       | EOD applied, step 3 | `no interest capitalized`, with `-` Event and date |
| several errors for one account       | Errors              | joined by `; `, as authorizations are              |

## The Command-Line Contract

The floor tier of the
[command-line interface convention](../../../../repo-governance/conventions/structure/command-line-interface.md) (D13):

```text
cli.py
  run(argv, read_text, out, err) -> int     every effect injected; catches every failure below
  main() -> int                             binds sys.argv[1:], a UTF-8 file reader, sys.stdout, sys.stderr
```

| Situation                               | Standard output | Standard error                           | Exit |
| --------------------------------------- | --------------- | ---------------------------------------- | ---- |
| the replay completes, refusals included | the report      | nothing                                  | 0    |
| no argument, or more than one           | nothing         | `usage: account-ledger-cli <stream.csv>` | 2    |
| the file cannot be read                 | nothing         | `error: cannot read PATH: REASON`        | 2    |
| the stream is malformed                 | nothing         | `error: ` and the `StreamError` message  | 2    |
| any other exception                     | nothing         | `error: internal failure: ` and its type | 2    |
| standard output is closed early         | what was taken  | nothing                                  | 141  |
| interrupted                             | what was taken  | nothing                                  | 130  |

- A rejected event is a result the ledger reports, not a failure of the program, so it prints on the Errors row and the
  exit is 0.
- `run` catches every case in the table, so the unit tests reach each status through it; `main` only binds the real
  effects and, for a closed pipe, points standard output at the null device so the exit-time flush cannot raise again.
- `REASON` is `no such file` for a missing file, and the operating system's message otherwise.
- The report is rendered in full before it is written, since the stream is finite.
- Standard output and error are written as UTF-8 whatever the locale, because the report prints `−`.
- The floor tier has no `--help`, so the statuses are published in the application README instead, recorded there as the
  adaptation.

`nx run account-ledger-cli:run` passes `streams/challenge.csv`.
