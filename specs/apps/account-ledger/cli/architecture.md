# Account Ledger CLI — Architecture

The current, as-built system. A change that alters an actor, a container, a component responsibility, a relationship, or
a boundary updates this document in the same commit.

## Scope

`account-ledger-cli` is being built toward the ledger: its core reads a stream and replays it into an append-only log
and a report per day, while the program still prints the greeting until the shell reads a stream. It runs locally, reads
nothing from disk yet, and never reaches the network.

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

The ledger core sits above those types. `replay` feeds each event to `processing` on the day it arrives and asks
`report` for each day's figures; every other component reads the log, and only `processing` appends to it.

```text
                  +----------------------------------------+
                  | replay (functional core)               |
                  | the stream in listed order, day by day |
                  +----------------------------------------+
                        | each event            | each day
                        v                       v
                  +----------------+      +----------------+
                  | processing     |      | report         |
                  | one entry per  |      | closing and    |
                  | event, plus    |      | available per  |
                  | instalments    |      | account        |
                  +----------------+      +----------------+
                     |          |                 |
       decides and   |          | available       | closing and available
       settles       v          v                 v
     +----------------+  reads  +------------------+
     | authorizations | <------ | balances         |
     | the state      | states  | closing, holds,  |
     | machine        |         | available        |
     +----------------+         +------------------+
               |                   |
               +---------+---------+
                         | reads; processing also appends
                         v
                  +----------------+
                  | log            |
                  | entries and    |
                  | rejections     |
                  +----------------+
```

`authorizations` is a hand-written state machine: one frozen dataclass per state, and `transition` as one `match` over
the state and its trigger, ending in `assert_never`. As built:

```text
             available >= 0 after the hold            SettleFinal
  (arrives) ------------------------------> Approved --------------> Settled
      |
      | available < 0 after the hold
      v
   Declined
```

`Settled` and `Declined` have no transition for any trigger, so a settlement against either, or against an authorization
the log does not know, is accepted as a force-post: it debits its amount and releases no hold.

The shell owns every effect: it receives the output stream and returns the exit code. The core is pure, so unit tests
call the shell in-process with an injected stream, integration tests run the entry point against the real standard
output, and end-to-end tests run `python -m account_ledger` as a separate process. The stream reader is the one place
text becomes domain values: each value is built through its type's `parse`, which returns a typed fault instead of an
illegal value, so the core never checks a value again. `events` and `config` both use `money` and `ids`, and `money`
uses `ids` for the instalment count.

| Component        | Responsibility                                                                                  |
| ---------------- | ----------------------------------------------------------------------------------------------- |
| `greeting`       | the greeting text; replaced by the ledger when the shell reads a stream                         |
| `cli`            | `run` writes the greeting to its stream and returns `0`; `main` binds `stdout`                  |
| `money`          | `Aed` and `Bhd`, one type per currency; `Amount` above zero; the split, fee, and daily interest |
| `ids`            | days, account and hold IDs, incoming IDs, fired-event markers, and instalment counts            |
| `config`         | the accounts, each typed by its currency, the window of days, and the capitalization days       |
| `events`         | the incoming event kinds, joined in `IncomingEvent`, and the fired `Instalment`                 |
| `stream_csv`     | parsing the stream file into incoming events, or the first fault with its line                  |
| `log`            | the append-only tuple of entries, each kind holding only its outcome, and every `Rejection`     |
| `balances`       | closing, holds, and available per account and day, each scanning the log whole                  |
| `authorizations` | the authorization states, `decide`, `transition`, and the records replayed from the log         |
| `processing`     | one entry per incoming event: idempotency first, then by kind, with reversal checks in order    |
| `replay`         | the stream in listed order, closing each day on time, with the log and report of every day      |
| `report`         | a day's closing and available balance per account                                               |

## Constraints

- No web layer, persistence, UI, or database.
- Every effect sits in the shell; the core stays pure and deterministic.
