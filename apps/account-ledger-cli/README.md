# account-ledger-cli

The command-line entry point for the in-memory account ledger. Today it is a hello-world scaffold that proves the F#
build, lint, and both test levels end to end; the ledger logic comes next.

Specification: [specs/apps/account-ledger/cli/](../../specs/apps/account-ledger/cli/README.md).

## Layout

| Path                 | Holds                                                                      |
| -------------------- | -------------------------------------------------------------------------- |
| `src/Greeting.fs`    | functional core: pure values and functions, no I/O                         |
| `src/Program.fs`     | imperative shell: `run` writes to an injected writer; `main` is the entry  |
| `tests/unit/`        | xUnit v3 + TickSpec; steps call the shell with an injected `StringWriter`  |
| `tests/integration/` | xUnit v3 + TickSpec; steps run `main` against the real, redirected console |
| `fsharplint.json`    | FSharpLint configuration                                                   |
| `project.json`       | Nx targets                                                                 |

Both test projects embed every `.feature` file under `specs/apps/account-ledger/cli/behaviours/`, so one scenario drives
both levels. `Suite.fs` turns each embedded scenario into one xUnit theory row.

## Commands

```bash
npx nx run account-ledger-cli:run               # prints "Hello, world!"
npx nx run account-ledger-cli:typecheck         # dotnet build, warnings as errors
npx nx run account-ledger-cli:lint              # Fantomas check + FSharpLint
npx nx run account-ledger-cli:test:unit         # unit suite, 80% line coverage gate (Program.fs excluded)
npx nx run account-ledger-cli:test:integration  # integration suite
npx nx run account-ledger-cli:test:quick        # typecheck, lint, test:unit in order
npx nx run account-ledger-cli:build             # dotnet publish to dist/
```

A test is never skipped: `test:unit` and `test:integration` fail if an xUnit `Skip=` attribute appears.
