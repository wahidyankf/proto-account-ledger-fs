# Migration Inventory

The restructure relocates, merges, and retires modules that other code, tests, configuration, and documents read, so
[plan migrations](../../../../repo-governance/conventions/structure/plan-migrations.md) and
[deletion with proof](../../../../repo-governance/development/quality/deletion-with-proof.md) apply. No persistent data
exists: the ledger is in-memory and keeps nothing after it exits, so no schema, data model, or field guide is involved.

## What Every Source Shares

- **Accepted shape.** A Python 3.14 module under `apps/account-ledger-cli/src/account_ledger/` or `tests/`, imported by
  its dotted path, or a Markdown or TOML file read by people and tools. No version marker; the commit is the version.
- **Owner.** The application, under the
  [Python standards](../../../../repo-governance/development/quality/stacks/python-standards.md).
- **Consumers.** Every reader is inside this repository. `pyproject.toml` sets `package = false`, so nothing is
  published and no outside code imports a module. The Nx targets read the trees by glob (`src/**/*.py`,
  `tests/unit/**/*.py`, `src/**/ruff.toml`), and every glob still matches after the move; coverage omits
  `*/account_ledger/__main__.py`, which stays.
- **Compatibility.** None, and none is needed: a module's readers move in the same commit as the module, and deletion
  with proof forbids a forwarding stub. That adapts the migration rule's contract step, which keeps the old path for a
  stated period, to a period of zero; the reason is that no consumer outside the commit exists to need it.

## Sources

Readers are the modules that import the source today, found by reading every `import` under `src/` and `tests/`; the
phase named is the one whose items move the source and its readers and prove the disposition.

- **`cli.py`.** Read by `__main__`, `test_cli`, `test_main`. Destination: stays for the shell; `CHALLENGE` to
  `challenge.py`, the reader to `adapters/csv_file.py`. Phase 4.
- **`__main__.py` and the `__init__.py` files.** Read by the interpreter. Destination: they stay; `application/` and
  `adapters/` already have or gain an `__init__.py`. Phase 4.
- **`adapters/stream_csv.py`.** Read by `cli`, `test_stream_csv`, `test_stream_file`. Destination:
  `adapters/csv_file.py`. Phase 4.
- **`adapters/render.py`.** Read by `cli`, `test_render`, `test_cli`, `test_main`. Destination:
  `adapters/text_report.py`. Phase 4.
- **`domain/stream_processing.py`.** Read by `cli`, eleven unit test modules, `test_main`. Goes to
  `application/stream.py`. Phase 4.
- **`domain/report.py`.** Read by `render`, `stream_processing`, `test_report`, `test_interest`. Goes to
  `application/report.py`. Phase 4.
- **`domain/ledger/processing.py`.** Read by `stream_processing`. Destination: `domain/ledger/ledger.py`. Phase 3.
- **`domain/ledger/end_of_day.py`.** Read by `stream_processing`. Destination: `domain/ledger/ledger.py`. Phase 3.
- **`domain/ledger/event_log.py`.** Read by the ledger modules, `report`, `stream_processing`, two support modules, five
  tests. Destination: `EventLog` to `domain/account/event_log.py` in Phase 2; `find_history_of` to
  `Ledger.find_account`. Phase 3.
- **`domain/account/aggregate.py`.** Read by `end_of_day`, `event_log`, `report`. Destination:
  `domain/account/account.py`. Phase 2.
- **`domain/account/history.py`.** Read by every account module, `processing`. Destination: `account.py`;
  `find_first_entry` to `EventLog`. Phase 2.
- **`domain/account/balances.py`.** Read by `aggregate`, `decisions`, `fees`, `interest`. Goes to
  `domain/account/account.py`. Phase 2.
- **`domain/account/decisions.py`.** Read by `aggregate`. Destination: `domain/account/account.py`. Phase 2.
- **`domain/account/fees.py`.** Read by `aggregate`. Destination: `domain/account/account.py`. Phase 2.
- **`domain/account/interest.py`.** Read by `aggregate`. Destination: `domain/account/account.py`. Phase 2.
- **`domain/account/reversals.py`.** Read by `decisions`, `interest`. Destination: `domain/account/account.py`. Phase 2.
- **`domain/account/authorizations.py`.** Read by `render`, four account modules, `report`, `test_authorizations`. Goes
  to stays for the table, the states, and the record; its history rules to `account.py`. Phase 2.
- **`domain/account/states.py`.** Read by `render`, three account modules, `support/states`, four tests. Goes to
  `domain/account/authorizations.py`. Phase 2.
- **`domain/account/domain_events.py`.** Read by `render`, every account and ledger module, `report`, three support
  modules, seven tests. Destination: stays; the rejection reasons to `rejections.py`. Phase 2.
- **`domain/model/config.py`.** Read by twenty-five modules across every layer and suite. Destination: stays, reshaped;
  `CHALLENGE` to `challenge.py`. Phase 1.
- **`domain/model/events.py`.** Read by twenty-three modules across every layer and suite. Destination: stays, reshaped.
  Phase 1.
- **`domain/model/ids.py`.** Read by thirty-six modules across every layer and suite. Destination: stays, reshaped.
  Phase 1.
- **`domain/model/money.py`.** Read by twenty-nine modules across every layer and suite. Destination: stays, reshaped.
  Phase 1.
- **`common/result.py`.** Read by twenty-five modules across every layer and suite. Destination: stays unchanged. no
  phase.
- **The five `ruff.toml` files.** Read by ruff, through the `lint` target. Destination: stay, their bans rewritten;
  `application/` and `adapters/` gain one each. Phase 4.

The test modules move as [the target layout](001-target-layout.md#where-every-current-file-goes) maps them, each with
the source it tests. The documents that name a moving source are listed, file by file, in
[the specification, rule, and doc changes](005-specification-rule-and-doc-changes.md).

## Transition

Each move follows the migration rule's order inside one commit, so the main line never holds a half-moved tree:

1. **Expand.** The new module is written beside the old, holding the moved code under its new shape.
2. **Migrate.** Each reader in the inventory row switches its import to the new module; `grep` for the old dotted path
   under `src/` and `tests/` returns nothing.
3. **Verify.** The real consumers run: the three suites, pyright, ruff, pylint, vulture, and the behaviour corpus, which
   runs the program as a process, never through the moved code's own tests alone.
4. **Contract.** The old module is deleted in the same commit, under the deletion-with-proof steps below.

## Deletion With Proof

For each module a phase deletes:

1. **Inventory.** Its row above, and every definition in it, listed by `grep -nE '^(def|class|type) '` in the phase's
   first item.
2. **Successor.** Each definition's new home, by path and name, from [the domain model](002-domain-model.md) and
   [the application, ports, and adapters](003-application-ports-and-adapters.md).
3. **Prove it is missed.** Before the delete, the phase breaks one rule the module holds in its new home, on a scratch
   edit, and a named test fails; the edit is reverted. A module whose code no test can make fail has an untested rule,
   and the phase stops and adds the test first.
4. **Prove the successor provides it.** The same test passes against the successor.
5. **Compare on recorded inputs.** The behaviour corpus equals the Phase 0 record.
6. **Full gate.** `npx nx run account-ledger-cli:test:quick`, `test:integration`, `test:e2e`, and
   `npm run check:hygiene`.

Then delete, and update every reference in the same commit. No alias, re-export, or forwarding function stays. The
destination of every removed responsibility is recorded in the phase's items and in the architecture's L3 table.

## Recovery

- **Recovery source.** Git history: commit `83dfd58`, the last before the plan, and the baseline copy Phase 0 extracts
  into `local-tmp/restructure/baseline/` with its manifest, the commit and the `git archive` command, in
  `evidence/phase-0-baseline.txt`.
- **Rollback.** A commit that proves wrong after it is pushed is undone by `git revert`, a new commit, never by a reset
  or a force-push, per
  [no destructive git operations](../../../../repo-governance/development/workflow/no-destructive-git-operations.md).
  Because every commit is build-valid and each phase ends at a passing gate, reverting a phase's commits in reverse
  order returns the tree to the previous phase's coherent state.
- **Mixed-version boundary.** Between phases, the tree is coherent: every gate green, every import resolved, the old and
  new names never both present. Inside a phase, before its commit, the working tree is the only place a half-moved state
  exists, and a pause records which items are done.
- **Retry.** Every item is repeatable: a move re-run over a moved file finds nothing to move, and the corpus and the
  inventory compare, never append.
- **Manual check.** At Phase 8, a person-readable diff of the program's output on the brief against `OUTPUT_TARGET.md`,
  and a reading of the architecture document against the tree.
