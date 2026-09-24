# account-ledger-cli

The command-line entry point for the in-memory account ledger. Today it is a hello-world scaffold that proves lint, type
checking, and every test level end to end; the ledger logic comes next.

Specification: [specs/apps/account-ledger/cli/](../../specs/apps/account-ledger/cli/README.md).

## Layout

| Path                             | Holds                                                                          |
| -------------------------------- | ------------------------------------------------------------------------------ |
| `src/account_ledger/greeting.py` | functional core: pure values and functions, no I/O                             |
| `src/account_ledger/cli.py`      | imperative shell: `run` writes to an injected stream; `main` binds `stdout`    |
| `src/account_ledger/__main__.py` | `python -m account_ledger`; the only file outside the coverage denominator     |
| `tests/unit/`                    | plain pytest tests that call `run` with an injected `io.StringIO`              |
| `tests/integration/`             | tests that call `main` against the real standard output, captured with `capfd` |
| `tests/e2e/`                     | tests that run `python -m account_ledger` as a subprocess                      |
| `tests/support`                  | shared test support: the `CliRun` record of one run                            |
| `pyproject.toml`, `uv.lock`      | uv project (`package = false`), pinned dev tools, pytest/ruff/pyright config   |
| `project.json`                   | Nx targets                                                                     |

Every level is plain pytest, written test-first; there is no Gherkin corpus and no step binding.

## Commands

```bash
npx nx run account-ledger-cli:install           # uv sync --locked; every other target depends on it
npx nx run account-ledger-cli:run               # prints "Hello, world!"
npx nx run account-ledger-cli:typecheck         # pyright, strict
npx nx run account-ledger-cli:lint              # ruff check + ruff format --check
npx nx run account-ledger-cli:test:unit         # unit suite, 80% line coverage gate
npx nx run account-ledger-cli:test:integration  # integration suite
npx nx run account-ledger-cli:test:e2e          # end-to-end suite
npx nx run account-ledger-cli:test:quick        # typecheck, lint, test:unit in order
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
