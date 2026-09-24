# Account Ledger CLI Behaviours

Gherkin feature files for `account-ledger-cli`. Every test level binds the same `.feature` files here through
pytest-bdd: the unit level drives the shell with an injected output stream, the integration level runs the entry point
against the real standard output, and the end-to-end level runs the CLI as its own process.

## Directory Map

- [greeting.feature](greeting.feature) — the CLI greets the world and exits cleanly.
