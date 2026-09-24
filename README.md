# proto-account-ledger-py

An in-memory account ledger core written in Python. There is no web layer, persistence, UI, or database: the ledger is
exercised by a runnable test suite that replays an event stream.

The repository is an Nx monorepo. Rhino and husky gate every commit and push, and governance is adopted from
`ose-rules`.

## Prerequisites

| Tool         | Version                                | Pinned by                                 |
| ------------ | -------------------------------------- | ----------------------------------------- |
| Node.js      | 24.x                                   | `.nvmrc`, `package.json`                  |
| uv           | 0.12 or later                          | installed separately                      |
| Python       | 3.14.x                                 | `apps/account-ledger-cli/.python-version` |
| Python tools | ruff, pyright, pytest, pytest-bdd, cov | `apps/account-ledger-cli/uv.lock`         |

## Getting Started

```bash
npm install    # installs Nx, Prettier, commitlint, and the git hooks
# every Nx target first runs `uv sync --locked`, which installs Python 3.14 and the locked tools if missing
```

## Common Commands

```bash
npx nx run account-ledger-cli:run               # run the CLI
npx nx run account-ledger-cli:test:quick        # typecheck, lint, unit tests (80% line coverage gate)
npx nx run account-ledger-cli:test:integration  # integration tests
npx nx run account-ledger-cli:test:e2e          # end-to-end tests
npm run check:hygiene                           # every repository gate Rhino declares for main
```

## Repository Map

| Path                                          | Holds                                                           |
| --------------------------------------------- | --------------------------------------------------------------- |
| [apps/](apps/)                                | runnable applications, starting with `account-ledger-cli`       |
| [libs/](libs/README.md)                       | reusable libraries (none yet)                                   |
| [specs/](specs/README.md)                     | Gherkin behaviours and architecture, shared by every test level |
| [docs/](docs/README.md)                       | documentation for people                                        |
| [plans/](plans/README.md)                     | delivery plans                                                  |
| [repo-governance/](repo-governance/README.md) | principles, conventions, standards, and workflows               |
| [AGENTS.md](AGENTS.md)                        | instructions for coding agents                                  |

## Working Agreement

Work lands directly on `main` as thematic Conventional Commits; there are no pull requests. The pre-push hook runs
`test:quick`, `test:integration`, and `test:e2e` for every affected project. See [AGENTS.md](AGENTS.md) for the full
agreement.

## License

[MIT](LICENSE).
