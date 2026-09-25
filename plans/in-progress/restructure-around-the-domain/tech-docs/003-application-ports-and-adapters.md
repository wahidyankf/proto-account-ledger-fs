# Application, Ports, and Adapters

The layers around the domain after the plan (R2, R5): the use case and the read model in `application/`, the ports it
declares, the two adapters that implement them, and the shell that composes them. Every message, exit code, and byte of
standard output stays as it is ([behaviour preservation](004-behaviour-preservation-and-tests.md)).

## One Run, End to End

```text
main()                                   cli.py: binds sys.argv, the UTF-8 file reader, stdout, stderr
  |
  v
run_cli(argv, read_text, out, err, run_ledger)
  |  wrong argument count -> "usage: account-ledger-cli <stream.csv>", exit 2
  |  builds CsvFileSource(path, read_text) and TextReportSink(out)
  v
run_ledger.run(source, sink)             application/run.py: LedgerRun(CHALLENGE)
  |  source.read_events(config)  ------> adapters/csv_file.py: read the file, parse the CSV
  |       Err(SourceFault) ------------> "error: {message}", exit 2
  |  IncomingStream(events).process(config)
  |       Err(InternalFault) ----------> "error: internal: ...", exit 2
  |  sink.publish(reports)  -----------> adapters/text_report.py: render, write, flush
  v
Ok(None) -> exit 0
  BrokenPipeError -> 141; KeyboardInterrupt -> 130; any other exception -> "error: internal failure: NAME", exit 2
```

The order of effects is today's: the file is read, then parsed, then processed, and standard output is written only once
every day is reported, so a fault leaves standard output empty, as it does today.

## `application/ports.py`

| Name          | Shape                                                                    | Implemented by      |
| ------------- | ------------------------------------------------------------------------ | ------------------- |
| `SourceFault` | frozen dataclass: `message: str`                                         | the source          |
| `EventSource` | `Protocol`: `read_events(config) -> Result[IncomingStream, SourceFault]` | `CsvFileSource`     |
| `ReportSink`  | `Protocol`: `publish(reports: tuple[DayReport, ...]) -> None`            | `TextReportSink`    |
| `RunFault`    | `type RunFault = SourceFault \| InternalFault`                           |                     |
| `RunLedger`   | `Protocol`: `run(source, sink) -> Result[None, RunFault]`                | `LedgerRun`, a fake |

- These three and `TextOutput` are the only `Protocol`s the plan adds, each consumed by a signature (R18). `RunLedger`
  is the driving port: `run_cli` takes one, so a CLI test passes a fake instead of patching a module attribute.
- `SourceFault.message` is the text after `error: `, so the CLI prints every source fault the same way:
  `cannot read PATH: no such file`, `cannot read PATH: not UTF-8 text`, `cannot read PATH: <the OS message>`, or
  `line N: …`, each exactly as today.
- `publish` returns nothing: a write that fails raises, as `out.write` does today, and `run_cli` catches it where it
  does today.

## `application/run.py`

`LedgerRun(config: LedgerConfig)` with `run(source, sink) -> Result[None, RunFault]`: read the events, process them,
publish the reports; the first `Err` ends it. It replaces `cli._process_file` after the argument check, with the config
the shell passes in instead of the imported `CHALLENGE`.

## `application/stream.py`

- `IncomingStream(events: tuple[IncomingEvent, ...])` with `process(config) -> Result[ProcessedStream, InternalFault]`,
  today's `process_stream` and its docstring, unchanged in order and in every rule.
- `ProcessedStream(reports: tuple[DayReport, ...], logs: tuple[EventLog, ...])` keeps `find_report(day)`,
  `find_log(day)`, and `_find_index(day)`.
- `_ProcessingState(ledger: Ledger, reports, logs, reported: ReportedClosings, day: Day)` keeps `process_event`,
  `close_days_before`, and `close_current_day`, now calling `self.ledger.process_event(event, self.day)` and
  `self.ledger.close_day(self.day)`; the config lives in the ledger, so the methods lose their `config` argument.

## `application/report.py`

The read model, moved out of `domain/` because it serves the report, not a rule (R2):

| Type or method                           | Replaces                                                |
| ---------------------------------------- | ------------------------------------------------------- |
| `DayReport.build(ledger, day, reported)` | `build_report(log, day, config, reported_closings)`     |
| `ReportedClosings(closings)`             | the alias `ReportedClosings`, a `Mapping` of `Mapping`s |
| `ReportedClosings.make_empty()`          | each `{}` passed as the closings reported so far        |
| `ReportedClosings.update(report)`        | `update_reported(reported_closings, day_report)`        |
| `ReportedClosings.list_days_before(day)` | the sorted filter inside `_list_restatements`           |
| `ReportedClosings.find_closings(day)`    | `reported_closings[earlier_day]`                        |

- `Restatement`, `Step`, `Note`, `EndOfDayEvent`, `Generated`, `Capitalized`, `NothingGenerated`, `Processed`, and
  `DayReport`'s fields stay as they are, so the renderer reads the same values.
- The private builders stay private functions of the module, taking the `Ledger` where they took the log and config.
  `_compute_closing` and `_compute_available`, which only forward to a method, go: `_map_balances` takes the lambdas
  `lambda account, day: account.compute_closing(day)` and its twin (polish, R19).
- `_map_histories` becomes `ledger.list_accounts()`, keyed by `account.id`, in the configured order as today.

## `adapters/csv_file.py`

- `type Reader = Callable[[str], Result[str, OSError | UnicodeDecodeError]]` and `read_file(path) -> Result[str, …]`,
  both moved from `cli.py`; `read_file` is today's `_read_file`, public because the shell binds it.
- `StreamError(line, message)`, `RowFault`, the column tables, and every private `_parse_…` function stay, and
  `parse_stream` becomes the static method `CsvFileSource.parse(text, config) -> Result[IncomingStream, StreamError]`.
- `CsvFileSource(path: str, read_text: Reader)` with `read_events(config) -> Result[IncomingStream, SourceFault]`:
  `cannot read {path}: {reason}` from `_describe_fault`, moved from `cli.py`, or the `StreamError`'s message.
- `REQUIRED` and `OPTIONAL` become `MappingProxyType`s, and a `type RowKind = Literal["CREDIT", …]` names their keys
  (R12); `KINDS` and `COLUMNS` stay tuples.
- The credit parser calls `Instalments.make(amount, count)` where it calls `amount.split(count)` today, so the
  `TooManyInstalments` refusal and its message stay.

## `adapters/text_report.py`

- `TextOutput`, a `Protocol` with `write(text: str, /) -> int` and `flush() -> None`, the two calls the sink and the CLI
  make on a stream (R20). `sys.stdout`, `sys.stderr`, and `io.StringIO` satisfy it as they are, and a test's closed pipe
  is a plain class with the two methods, so no class in the tests derives from `io.StringIO`.
- `TextReportSink(out: TextOutput)` with `publish(reports)`: `out.write(TextReportSink.render(reports))`, then
  `out.flush()`, the flush that surfaces a closed pipe inside `run_cli`'s handlers, as today.
- `render(reports) -> str` is today's `render_reports`, a static method so the render tests and the golden test call it
  without a stream. Every private `_format_…` and `_build_…` function stays.
- `NUMBER_WORDS` becomes a `MappingProxyType` (R12); `_build_applied_row`'s repeated tuples fold into one (polish, R19).

## The Shell: `cli.py` and `challenge.py`

- `challenge.py` holds `CHALLENGE`, moved from `domain/model/config.py` unchanged (R14).
- `run_cli(argv, read_text, out: TextOutput, err: TextOutput, run_ledger: RunLedger) -> int` keeps its three handlers
  and its argument check. It maps each fault to its line:

| Fault              | Standard error                                                              | Exit |
| ------------------ | --------------------------------------------------------------------------- | ---- |
| `SourceFault`      | `error: {message}`                                                          | 2    |
| `CurrencyMismatch` | `error: internal: {found} met where {expected} was required`                | 2    |
| `UnknownAccount`   | `error: internal: {account} is not a configured account` (new, unreachable) | 2    |

- `main()` binds `sys.argv[1:]`, `read_file`, the reconfigured standard streams, and `LedgerRun(CHALLENGE)`, and keeps
  its closed-pipe `dup2`.
- `USAGE`, `CLOSED_PIPE`, and `INTERRUPTED` stay in `cli.py`.

## The Import Bans

Each package's `ruff.toml` refuses what [the target layout](001-target-layout.md#layers) says, through `TID251`, as the
five it has today do. A nested `ruff.toml` extends `pyproject.toml`, not its parent's file, so each lists every ban of
its own:

- `application/ruff.toml` and `adapters/ruff.toml` are new, the sixth and seventh.
- The four domain files refuse `account_ledger.application`, `account_ledger.adapters`, `account_ledger.cli`, and
  `account_ledger.challenge`, in place of today's `domain.report` and `domain.stream_processing`, which leave the
  domain; `domain/model/` still refuses `domain.account` and `domain.ledger`, and `domain/account/` `domain.ledger`.
- `common/ruff.toml` adds `account_ledger.application` and `account_ledger.challenge`.
