# proto-account-ledger-fs

An in-memory account ledger core written in F#. There is no web layer, persistence, UI, or database: the ledger is
exercised by a runnable test suite that replays an event stream.

The repository is an Nx monorepo. Rhino and husky gate every commit and push, and governance is adopted from
`ose-rules`.

## Prerequisites

| Tool     | Version                     | Pinned by                   |
| -------- | --------------------------- | --------------------------- |
| Node.js  | 24.x                        | `.nvmrc`, `package.json`    |
| .NET     | SDK 10.0.300 (feature band) | `global.json`               |
| F# tools | Fantomas, FSharpLint        | `.config/dotnet-tools.json` |

## Getting Started

```bash
npm install            # installs Nx, Prettier, commitlint, and the git hooks
dotnet tool restore    # installs the pinned F# formatter and linter
```

## Common Commands

```bash
npx nx run account-ledger-cli:run               # run the CLI
npx nx run account-ledger-cli:test:quick        # typecheck, lint, unit tests (99% line coverage gate)
npx nx run account-ledger-cli:test:integration  # integration tests
npm run check:hygiene                           # every repository gate Rhino declares for main
```

## Repository Map

| Path                                          | Holds                                                               |
| --------------------------------------------- | ------------------------------------------------------------------- |
| [apps/](apps/)                                | runnable applications, starting with `account-ledger-cli`           |
| [libs/](libs/README.md)                       | reusable libraries (none yet)                                       |
| [specs/](specs/README.md)                     | Gherkin behaviours and architecture, shared by unit and integration |
| [docs/](docs/README.md)                       | documentation for people                                            |
| [plans/](plans/README.md)                     | delivery plans                                                      |
| [repo-governance/](repo-governance/README.md) | principles, conventions, standards, and workflows                   |
| [AGENTS.md](AGENTS.md)                        | instructions for coding agents                                      |

## Working Agreement

Work lands directly on `main` as thematic Conventional Commits; there are no pull requests. The pre-push hook runs
`test:quick` and `test:integration` for every affected project. See [AGENTS.md](AGENTS.md) for the full agreement.

## License

[MIT](LICENSE).
