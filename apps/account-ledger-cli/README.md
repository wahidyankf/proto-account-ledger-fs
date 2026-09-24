# account-ledger-cli

The command-line entry point for the in-memory account ledger. Today it is a hello-world scaffold that proves lint, type
checking, and every test level end to end; the ledger logic comes next.

Specification: [specs/apps/account-ledger/cli/](../../specs/apps/account-ledger/cli/README.md).

## Layout

| Path                                 | Holds                                                                            |
| ------------------------------------ | -------------------------------------------------------------------------------- |
| `src/account_ledger/greeting.py`     | functional core: pure values and functions, no I/O                               |
| `src/account_ledger/cli.py`          | imperative shell: `run` writes to an injected stream; `main` binds `stdout`      |
| `src/account_ledger/__main__.py`     | `python -m account_ledger`; the only file outside the coverage denominator       |
| `tests/unit/`                        | steps call `run` with an injected `io.StringIO`                                  |
| `tests/integration/`                 | steps call `main` against the real standard output, captured with `capfd`        |
| `tests/e2e/`                         | steps run `python -m account_ledger` as a subprocess                             |
| `tests/conftest.py`, `tests/support` | the Then steps and the `CliRun` record every level shares                        |
| `pyproject.toml`, `uv.lock`          | uv project (`package = false`), pinned dev tools, and pytest/ruff/pyright config |
| `project.json`                       | Nx targets                                                                       |

Every level runs `scenarios("greeting.feature")` against `specs/apps/account-ledger/cli/behaviours/` (the
`bdd_features_base_dir`), so one scenario drives all three.

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
file or to a `.feature` file under `specs/`:

```bash
npx nx run account-ledger-cli:test:quick:watch        # nx watch: typecheck, lint, test:unit
npx nx run account-ledger-cli:test:integration:watch  # pytest-watcher on tests/integration
npx nx run account-ledger-cli:test:e2e:watch          # pytest-watcher on tests/e2e
```

Run only one copy of each watcher: Nx refuses to start a task that is already running in another process.

A test is never skipped: every test target fails if `pytest.skip`, `mark.skip`, `skipif`, or `mark.xfail` appears under
`tests/`.
