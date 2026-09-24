# Technical Design

How the ledger is built. The design is a functional core, an event-sourced log with pure aggregations over it, inside a
thin imperative shell that reads a CSV stream and prints the report. Each rule it implements is a resolved entry in
[AMBIGUITIES](../../../../AMBIGUITIES.md); each figure it must reproduce is fixed in [MOVEMENT](../../../../MOVEMENT.md)
and printed as [OUTPUT_TARGET](../../../../OUTPUT_TARGET.md) shows.

## Shape at a Glance

```text
               streams/challenge.csv
                        |
                        v
+---------------------- shell -----------------------+
| cli.run  --> read the file (the only I/O in)       |
|   |                                                |
|   +--> stream_csv.parse_stream  -> events | error  |
|   +--> replay.replay            -> day reports     |------> core, all pure
|   +--> render.render            -> text            |
|   +--> write stdout / stderr, return the exit      |
+----------------------------------------------------+

core:  money, ids --> config, events --> log --> balances, authorizations --> processing, end_of_day
       --> replay --> report
```

Dependencies point inward only: the shell imports the core, and the core imports nothing from the shell and performs no
I/O. Raw text and numbers live only in the parser and the renderer, and `Decimal` only inside `money.py`; everything
between them is a domain type that cannot hold an illegal value (D16).

## Companions

Read in order; each builds on the ones before it.

1. [Domain Model](001-domain-model.md) — money, identifiers, accounts, events, the log, balances, and the authorization
   machine.
2. [Replay and End of Day](002-replay-and-end-of-day.md) — the driver, processing, the three end-of-day steps, and the
   day report.
3. [Input, Output, and the Command Line](003-input-output-and-cli.md) — the CSV stream, parse faults, rendering rules,
   and the exit contract.
4. [Testing Strategy](004-testing-strategy.md) — the three layers, every test file, and the one strict expected failure.
5. [Decision Records](005-decision-records.md) — every material choice, its alternatives, and when to revisit it.
6. [Specification and Rule Changes](006-specification-and-rule-changes.md) — the architecture delta and the rule
   changes, file by file.
7. [File Impact](007-file-impact.md) — every path the plan touches.

## File Impact

The annotated tree is in [File Impact](007-file-impact.md).
