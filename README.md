# proto-account-ledger-py

An in-memory account ledger core written in Python. There is no web layer, persistence, UI, or database: a command-line
program replays an event stream and prints one report a day, and a test suite at three levels proves every figure.

The repository is an Nx monorepo. Rhino and husky gate every commit and push, and governance is adopted from
`ose-rules`.

## Prerequisites

| Tool         | Version                    | Pinned by                                 |
| ------------ | -------------------------- | ----------------------------------------- |
| Node.js      | 24.x                       | `.nvmrc`, `package.json`                  |
| uv           | 0.12 or later              | installed separately                      |
| Python       | 3.14.x                     | `apps/account-ledger-cli/.python-version` |
| Python tools | ruff, pyright, pytest, cov | `apps/account-ledger-cli/uv.lock`         |

## Getting Started

```bash
npm install    # installs Nx, Prettier, commitlint, and the git hooks
# every Nx target first runs `uv sync --locked`, which installs Python 3.14 and the locked tools if missing
```

## Run and Read the Report

### Run It

```bash
npx nx run account-ledger-cli:run               # replay streams/challenge.csv and print the report
```

The program prints the fenced text in [OUTPUT_TARGET.md](OUTPUT_TARGET.md), byte for byte. How to replay another stream
file, its columns, the exit statuses, and the ledger's known weakness are in the
[application README](apps/account-ledger-cli/README.md).

### Test It

```bash
npx nx run account-ledger-cli:test:quick        # typecheck, lint, unit tests (80% line coverage gate)
npx nx run account-ledger-cli:test:integration  # the real entry point against real files
npx nx run account-ledger-cli:test:e2e          # the program as a process, compared with OUTPUT_TARGET
npm run check:hygiene                           # every repository gate Rhino declares for main
```

Each criterion in [MOVEMENT.md](MOVEMENT.md) and each resolution in [AMBIGUITIES.md](AMBIGUITIES.md) names the tests
that prove it.

### Read a Day

The report opens with Day 0, the opening balances, and then prints each day of the window between rules of `=`, as three
tables:

- **Events processed** lists every incoming event the day processed, in the order processed, with its booked day, its
  kind, its account, what it moved, and its value date. A credit in instalments is followed by one row per instalment; a
  late event carries a value date before the day it is printed under.
- **EOD applied** lists what the day's close fired, by step: 1 fee re-evaluation (fees and refunds), 2 interest
  (accruals for the day and adjustments for earlier days), and 3 capitalization, on a capitalization day only. Each
  fired event shows its marker; a step that fired nothing shows a row with `-` in place of a marker.
- **Closing summary** gives one column per account in its own currency. A `restated` row appears for each earlier day
  whose closing changed since it was last printed, the new figure in place of the old; then come the day's closing
  ledger balance, its available balance after holds, every authorization with its state, and the errors, which are the
  events refused that day. A `-` means that account's figure did not change; `−` is a negative amount.

## Repository Map

| Path                                          | Holds                                                  |
| --------------------------------------------- | ------------------------------------------------------ |
| [apps/](apps/)                                | runnable applications, such as `account-ledger-cli`    |
| [libs/](libs/README.md)                       | reusable libraries (none yet)                          |
| [specs/](specs/README.md)                     | behaviours and architecture shared by every test level |
| [docs/](docs/README.md)                       | documentation for people                               |
| [plans/](plans/README.md)                     | delivery plans                                         |
| [repo-governance/](repo-governance/README.md) | principles, conventions, standards, and workflows      |
| [AGENTS.md](AGENTS.md)                        | instructions for coding agents                         |
| [challenge-raw.md](challenge-raw.md)          | the assessment brief, verbatim                         |
| [AMBIGUITIES.md](AMBIGUITIES.md)              | every ambiguity in the brief and how it is resolved    |
| [NUMBERS.md](NUMBERS.md)                      | every constant and why it has that value               |
| [REJECTED.md](REJECTED.md)                    | refused acceptance criteria and abandoned approaches   |
| [WORKLOG.md](WORKLOG.md)                      | timestamped record of the work                         |
| [MOVEMENT.md](MOVEMENT.md)                    | each day's movement per account, fully analysed        |
| [OUTPUT_TARGET.md](OUTPUT_TARGET.md)          | the exact text the CLI must print                      |

## Working Agreement

Work lands directly on `main` as thematic Conventional Commits; there are no pull requests. The pre-push hook runs
`test:quick`, `test:integration`, and `test:e2e` for every affected project. See [AGENTS.md](AGENTS.md) for the full
agreement.

## License

[MIT](LICENSE).
