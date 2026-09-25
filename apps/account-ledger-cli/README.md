# account-ledger-cli

The in-memory account ledger as a command-line program. It reads a CSV stream of account events, processes it day by day
into an append-only log, and prints one report per day: the events processed, the end-of-day steps applied, and the
closing summary. For the brief's stream it prints [OUTPUT_TARGET](../../OUTPUT_TARGET.md) byte for byte.

Specification: [specs/apps/account-ledger/cli/](../../specs/apps/account-ledger/cli/README.md), with the as-built
[architecture](../../specs/apps/account-ledger/cli/architecture.md). Reading the code for the first time, start with its
[reading order](../../specs/apps/account-ledger/cli/architecture.md#reading-the-code).

## Layout

| Path                              | Holds                                                                           |
| --------------------------------- | ------------------------------------------------------------------------------- |
| `src/account_ledger/cli.py`       | the shell: `run_cli` takes every effect and the use case; `main` binds them     |
| `src/account_ledger/challenge.py` | `CHALLENGE`, the brief's configuration, which `main` passes to the use case     |
| `src/account_ledger/__main__.py`  | what `python -m account_ledger` runs: `main`, exiting with its status           |
| `src/account_ledger/adapters/`    | the adapters: `csv_file` reads the stream, `text_report` writes the report      |
| `src/account_ledger/application/` | the use case, `LedgerRun`, its ports, the stream processing, and the report     |
| `src/account_ledger/domain/`      | the domain, in DDD terms: `model/`, `account/`, and `ledger/`                   |
| `src/account_ledger/common/`      | tools with no ledger meaning, `Result` for now; imports nothing from the others |
| `streams/challenge.csv`           | the brief's stream, E1 to E10                                                   |
| `tests/unit/`                     | in-process tests, one directory per source package; `run_cli` gets every effect |
| `tests/integration/`              | the real stream file from disk, and `main` on the real descriptors with `capfd` |
| `tests/e2e/`                      | `python -m account_ledger` as a subprocess: the golden run and the error paths  |
| `tests/support/`                  | the brief's stream in code and CSV, builders, readers, refusals, OUTPUT_TARGET  |
| `pyproject.toml`, `uv.lock`       | uv project (`package = false`) pinning pytest, ruff, pylint, pyright, vulture   |
| `project.json`                    | Nx targets                                                                      |

The code is laid out in DDD and hexagonal terms. `domain/model/` holds the values: money, IDs, the brief's events, and
the accounts. `domain/account/` is the Account aggregate: one account's entries, the domain events it records, and every
rule about one account, each a method of `account.py`'s `AccountIn`. `domain/ledger/` is the `Ledger`: the configured
accounts and the one log of them all, idempotency, the cross-account check, and the day's close. Around the domain,
`application/` holds the one use case, `LedgerRun`, with the ports it declares, `EventSource`, `ReportSink`, and
`RunLedger`; the stream processing, `IncomingStream`; and the report read model, `DayReport`. `adapters/` implements the
two driven ports, and `cli.py` composes them. Each package's `ruff.toml` refuses an import from the layers around it
(TID251).

Every level is plain pytest, written test-first; there is no Gherkin corpus and no step binding.

## Commands

```bash
npx nx run account-ledger-cli:install           # uv sync --locked; every other target depends on it
npx nx run account-ledger-cli:run               # prints the daily report for streams/challenge.csv
npx nx run account-ledger-cli:typecheck         # pyright, strict
npx nx run account-ledger-cli:lint              # ruff check, format; pylint docstrings, names, bases; vulture dead code
npx nx run account-ledger-cli:test:unit         # unit suite, 80% line coverage gate
npx nx run account-ledger-cli:test:integration  # integration suite
npx nx run account-ledger-cli:test:e2e          # end-to-end suite
npx nx run account-ledger-cli:test:quick        # typecheck, lint, test:unit in order
```

To process another stream, run the module from this directory with the path as its one argument:

```bash
PYTHONPATH=src uv run --no-sync python -m account_ledger path/to/stream.csv
```

For a test-driven loop, run each watcher in its own terminal pane. Each runs once, then again on every change to a `.py`
file:

```bash
npx nx run account-ledger-cli:test:quick:watch        # nx watch: typecheck, lint, test:unit
npx nx run account-ledger-cli:test:integration:watch  # pytest-watcher on tests/integration
npx nx run account-ledger-cli:test:e2e:watch          # pytest-watcher on tests/e2e
```

Run only one copy of each watcher: Nx refuses to start a task that is already running in another process.

A test is never skipped: every test target fails if `pytest.skip`, `mark.skip`, or `skipif` appears under `tests/`. An
expected failure is allowed only as a strict one, which records a known weakness with its reason: `xfail_strict = true`
makes every `mark.xfail` strict, and every test target fails if `strict=False` appears under `tests/`.

## The Stream File

A UTF-8 CSV with the header `event,booked,type,account,amount,value_date,reference,instalments,final` and one event per
row; `final` is `yes`, `no`, or blank for `yes`, on a settlement only, and `instalments` is blank or 2 to 360. Amounts
are read as decimals in the account's currency and never pass through a float; one not below 10¹² in either direction is
refused, as [NUMBERS](../../NUMBERS.md) records. The first fault stops the run with its line number, the header being
line 1; a well-formed event the ledger refuses, such as a second reversal of the same event, is not a fault, and prints
on that day's Errors row instead.

## Exit Statuses

The program sits at the floor tier of the
[command-line interface convention](../../repo-governance/conventions/structure/command-line-interface.md) (D13): the
closed exit vocabulary, standard output for the report and standard error for everything else, and the closed-pipe and
signal statuses. The floor tier has no `--help`, so this table publishes the statuses instead; that is the adaptation
D13 records.

| Status | When                                        | Standard output | Standard error                           |
| ------ | ------------------------------------------- | --------------- | ---------------------------------------- |
| `0`    | the stream was processed, refusals included | the report      | nothing                                  |
| `2`    | no argument, or more than one               | nothing         | `usage: account-ledger-cli <stream.csv>` |
| `2`    | the file cannot be read                     | nothing         | `error: cannot read PATH: REASON`        |
| `2`    | the stream is malformed                     | nothing         | `error: line N: ...`                     |
| `2`    | an internal fault, which only a bug brings  | nothing         | `error: internal: ...`                   |
| `2`    | any other failure, never with a traceback   | nothing         | `error: internal failure: TYPE`          |
| `141`  | output closed early, as by `\| head`        | what was taken  | nothing                                  |
| `130`  | interrupted                                 | what was taken  | nothing                                  |

`REASON` is `no such file` for a missing file, `not UTF-8 text` for one that does not decode, and the operating system's
message otherwise. A currency mismatch prints `error: internal: FOUND met where EXPECTED was required`, and an event on
an account the ledger does not hold prints `error: internal: ACC-NNN is not a configured account`; no input reaches the
second, because the event source refuses an unconfigured account first. Both streams are written as UTF-8 whatever the
locale, because the report prints `−` (U+2212) for a negative amount.

## Known Weakness

A hold never expires (AMB-018): an approved authorization that is never settled keeps reducing the available balance for
as long as the ledger runs. `tests/unit/application/test_stream.py` holds the brief's one failing test against this
design, inline-annotated with what it reveals. It processes an authorization left unsettled through Day 32, past the 30
calendar days Visa allows at most, and asserts the hold has lapsed.

It is marked `xfail(strict=True)`, so the suite reports it as `1 xfailed` and passes. Once holds gain a lifetime, the
test passes, pytest reports `XPASS(strict)`, and the run fails until the marker is removed. The constants it uses are
defended in [NUMBERS](../../NUMBERS.md).
