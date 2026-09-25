# Technical Design

How the application is restructured around its domain without changing what it does. Today the rules about one account
are spread over nine modules and reached through forwarding methods, seven base classes share fields, the stream
processing and the report sit inside the domain, and five `assert`s carry proofs the types do not. After the plan, the
Account aggregate is one class whose methods are every rule about one account, the `Ledger` and its `EventLog` are
classes, no class inherits from another, the application declares ports that two adapters implement, and every proof is
a type. The program's output, every test, and every assessment doc's figure stay exactly as they are.

## Shape at a Glance

```text
Today                                          After
-----                                          -----
cli.py        parse, process, render by hand   cli.py         run_cli(..., run_ledger) maps faults to exits
adapters/     stream_csv, render               challenge.py   CHALLENGE, the composition data
domain/       stream_processing, report        application/   ports, LedgerRun, IncomingStream, DayReport
domain/ledger processing, end_of_day,          adapters/      CsvFileSource, TextReportSink
              event_log (Log alias)            domain/ledger  Ledger: process_event, close_day
domain/account aggregate + 8 rule modules      domain/account AccountIn: every rule a method; EventLog;
              (functions over a history)                      authorizations; domain_events; rejections
domain/model  money, ids, events on bases      domain/model   money, ids, events, config, no bases
```

## Where the Final Layout Is

[001 Target Layout](001-target-layout.md) holds the layer diagram, the import bans, the complete source and test trees,
and where every current file goes. [008 File Impact](008-file-impact.md) holds every path the plan touches, labelled.

## Directory Map

The companions, read in the order listed; each builds on the ones before it.

- [001 Target Layout](001-target-layout.md) — the layers, what each may import, the final trees, and the old-to-new map.
- [002 Domain Model](002-domain-model.md) — every value, the Account aggregate, and the Ledger, method by method, and
  where each `assert` goes.
- [003 Application, Ports, and Adapters](003-application-ports-and-adapters.md) — one run end to end, the ports, the use
  case, the read model, the adapters, and the shell.
- [004 Behaviour Preservation and Tests](004-behaviour-preservation-and-tests.md) — what must not change, the behaviour
  corpus, the test inventory, and the new tests.
- [005 Specification, Rule, and Doc Changes](005-specification-rule-and-doc-changes.md) — every specification, rule, and
  document the restructure makes stale, file by file.
- [006 Migration Inventory](006-migration-inventory.md) — every moving source, its readers, its destination, the
  transition, deletion with proof, and recovery.
- [007 Decision Records](007-decision-records.md) — R1 to R21, each with its alternatives and its revisit trigger.
- [008 File Impact](008-file-impact.md) — every path the plan touches, as annotated trees.

## File Impact

The plan's File Impact section is [008 File Impact](008-file-impact.md).
