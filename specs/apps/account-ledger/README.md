# Account Ledger

Specifications for the in-memory account ledger. The ledger ships one owner today, a command-line interface. Its domain
is one bounded context, the Ledger, built as an Account aggregate over one append-only log and the `Ledger` for what
spans accounts; see the CLI architecture's [domain model](cli/architecture.md#domain-model).

## Directory Map

- [CLI](cli/README.md) — the specification corpus for `account-ledger-cli`.
