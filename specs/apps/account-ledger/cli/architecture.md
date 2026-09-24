# Account Ledger CLI — Architecture

The current, as-built system. A change that alters an actor, a container, a component responsibility, a relationship, or
a boundary updates this document in the same commit.

## Scope

`account-ledger-cli` is a hello-world scaffold today: it proves lint, type checking, and every test level end to end
before the ledger itself is designed. It runs locally, reads nothing from disk, and never reaches the network.

## System Context

```text
+-------------+   argv    +--------------------+   text + exit code   +-----------------+
|  Developer  | --------> | account-ledger-cli | -------------------> | terminal stdout |
+-------------+           +--------------------+                      +-----------------+
```

One actor runs one executable, which writes one line to standard output and exits.

## Containers

| Container            | What it is              | How it is reached                   |
| -------------------- | ----------------------- | ----------------------------------- |
| `account-ledger-cli` | one Python 3.14 package | `npx nx run account-ledger-cli:run` |

## Components

```text
+--------------------------------+        +-----------------------------+
| cli (imperative shell)         | -----> | greeting (functional core)  |
| entry point, writes to a       |  calls | pure: returns the greeting  |
| TextIO, returns exit code      |        | text, performs no I/O       |
+--------------------------------+        +-----------------------------+
```

The shell owns every effect: it receives the output stream and returns the exit code. The core is pure, so unit tests
call the shell in-process with an injected stream, integration tests run the entry point against the real standard
output, and end-to-end tests run `python -m account_ledger` as a separate process.

| Component  | Responsibility                                                                 |
| ---------- | ------------------------------------------------------------------------------ |
| `greeting` | the greeting text; the future home of pure ledger logic                        |
| `cli`      | `run` writes the greeting to its stream and returns `0`; `main` binds `stdout` |

## Constraints

- No web layer, persistence, UI, or database.
- Every effect sits in the shell; the core stays pure and deterministic.
