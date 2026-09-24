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

                  +----------------------------------------+
                  | stream_csv (shell edge)                |
                  | text in; events or the first fault out |
                  +----------------------------------------+
                          | builds                | reads
                          v                       v
                  +----------------+      +----------------+
                  | events         |      | config         |
                  | incoming kinds |      | accounts,      |
                  | and posting    |      | window, days   |
                  +----------------+      +----------------+
                          |                       |
                          +-----------+-----------+
                                      | both use money and ids
                                      v
                  +----------------+      +----------------+
                  | money          | ---> | ids            |
                  | Aed, Bhd,      |      | days, IDs,     |
                  | Amount, split  |      | markers, count |
                  +----------------+      +----------------+
```

The shell owns every effect: it receives the output stream and returns the exit code. The core is pure, so unit tests
call the shell in-process with an injected stream, integration tests run the entry point against the real standard
output, and end-to-end tests run `python -m account_ledger` as a separate process. The stream reader is the one place
text becomes domain values: each value is built through its type's `parse`, which returns a typed fault instead of an
illegal value, so the core never checks a value again. `events` and `config` both use `money` and `ids`, and `money`
uses `ids` for the instalment count.

| Component    | Responsibility                                                                                      |
| ------------ | --------------------------------------------------------------------------------------------------- |
| `greeting`   | the greeting text; replaced by the ledger when the shell reads a stream                             |
| `cli`        | `run` writes the greeting to its stream and returns `0`; `main` binds `stdout`                      |
| `money`      | `Aed` and `Bhd`, one type per currency; `Amount` above zero; the split, the fee, the daily interest |
| `ids`        | days, account and hold IDs, incoming IDs, fired-event markers, and instalment counts                |
| `config`     | the configured accounts, each typed by its currency, the window of days, and capitalization days    |
| `events`     | the incoming event kinds, joined in `IncomingEvent`                                                 |
| `stream_csv` | parsing the stream file into incoming events, or the first fault with its line                      |

## Constraints

- No web layer, persistence, UI, or database.
- Every effect sits in the shell; the core stays pure and deterministic.
