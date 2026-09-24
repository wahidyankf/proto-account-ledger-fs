# Account Ledger CLI — Architecture

The current, as-built system. A change that alters an actor, a container, a component responsibility, a relationship, or
a boundary updates this document in the same commit.

## Scope

`account-ledger-cli` is a hello-world scaffold today: it proves the build, lint, and both test levels end to end before
the ledger itself is designed. It runs locally, reads nothing from disk, and never reaches the network.

## System Context

```text
+-------------+   argv    +--------------------+   text + exit code   +-----------------+
|  Developer  | --------> | account-ledger-cli | -------------------> | terminal stdout |
+-------------+           +--------------------+                      +-----------------+
```

One actor runs one executable, which writes one line to standard output and exits.

## Containers

| Container            | What it is             | How it is reached                   |
| -------------------- | ---------------------- | ----------------------------------- |
| `account-ledger-cli` | one .NET 10 executable | `npx nx run account-ledger-cli:run` |

## Components

```text
+--------------------------------+        +-----------------------------+
| Program (imperative shell)     | -----> | Greeting (functional core)  |
| entry point, writes to a       |  calls | pure: returns the greeting  |
| TextWriter, returns exit code  |        | text, performs no I/O       |
+--------------------------------+        +-----------------------------+
```

The shell owns every effect: it receives the output writer and returns the exit code. The core is pure, so unit tests
call it in-process with an injected writer while integration tests run the entry point against the real console.

| Component  | Responsibility                                                     |
| ---------- | ------------------------------------------------------------------ |
| `Greeting` | the greeting text; the future home of pure ledger logic            |
| `Program`  | the entry point: writes the greeting to its writer and returns `0` |

## Constraints

- No web layer, persistence, UI, or database.
- Every effect sits in the shell; the core stays pure and deterministic.
