# Account Ledger CLI Behaviours

Gherkin feature files for `account-ledger-cli`. Both test projects embed every `.feature` file here: the unit project
binds steps to the functional core with injected I/O, and the integration project binds the same steps to the entry
point against the real console.

## Directory Map

- [greeting.feature](greeting.feature) — the CLI greets the world and exits cleanly.
