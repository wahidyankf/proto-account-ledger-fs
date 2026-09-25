# Specification, Rule, and Doc Changes

Every specification, rule, and document the restructure makes stale, file by file, as
[plan specification changes](../../../../repo-governance/conventions/structure/plan-specification-changes.md) requires.
Each is updated as built, in the phase whose code makes it stale, never in one sweep at the end; the phase that updates
each is named under it.

## What Becomes a Durable Contract

- **Durable.** The as-built architecture (`specs/apps/account-ledger/cli/architecture.md`), the application README's
  layout and exit statuses, the Python rules on operations and inheritance, and the five new tests, which specify the
  behaviour they prove as every test here does.
- **Plan-only.** The behaviour corpus, the test inventory, the mutation spot-checks, and the timings. Each proves the
  restructure and has no meaning once it is done; each is verified by a Phase 8 item in `delivery.md` and kept in
  `evidence/`.
- **No new scenario in any other form.** The repository writes no Gherkin, as its
  [BDD rule](../../../../repo-governance/development/quality/testing/behaviour-driven-development.md) holds, so the
  plain pytest tests are the executable specification, and each binds at the boundary its suite declares.

## Public Contracts

The exit statuses the application README publishes are a public contract. This plan proposes a release decision: it adds
one standard-error line to the internal row, `error: internal: ACC-NNN is not a configured account`, which no input can
reach, and changes no status, no other line, and no byte of standard output. Every other surface, the command, its one
argument, and the stream file's columns, stays as it is.

## Executable Specifications

The tests move as [the target layout](001-target-layout.md#where-every-current-file-goes) maps them. A moved test keeps
its name, cases, and expectations ([behaviour preservation](004-behaviour-preservation-and-tests.md)); only its calls
follow the new API. Each file below binds at the unit boundary unless its path says otherwise.

### [M] `tests/unit/test_money.py` → `tests/unit/domain/model/test_money.py`

```diff
- assert sum_money(make_aed("1.00"), [make_aed("2.00"), make_aed("0.50")]) == Ok(make_aed("3.50"))
+ assert make_aed("1.00").add_all([make_aed("2.00"), make_aed("0.50")]) == Ok(make_aed("3.50"))
- assert aed_amount.compute_rest(bhd_amount) == aed_to_bhd
+ assert aed_amount.take(bhd_amount) == aed_to_bhd
+ def test_taking_all_of_a_hold_or_more_leaves_nothing() -> None:
+ def test_a_zero_change_has_no_direction() -> None:
```

- = Preserve: every current test, by name, with its cases.
- → Bindings: the unit suite.
- ✓ Proof: `npx nx run account-ledger-cli:test:unit`.
- Phase 1.

### [N] `tests/unit/domain/model/test_events.py`

```diff
+ def test_instalments_refuse_parts_whose_number_is_not_the_count() -> None:
```

- = Preserve: nothing; the file is new. Actor: the code building a credit; precondition: three parts; action:
  `Instalments(InstalmentCount(2), parts)`; outcome: `ValueError`, as `InterestAccrual`'s guard raises today.
- → Bindings: the unit suite. ✓ Proof: `test:unit`. Phase 1.

### [M] `tests/unit/test_ids.py`, `test_config.py`, `test_result.py`

Each moves to its mirrored directory, `domain/model/` or `common/`; `test_config.py` builds `AccountOpeningIn` where it
builds `AccountIn`, and reads `CHALLENGE` from `account_ledger.challenge`. = Preserve: every test. ✓ Proof: `test:unit`.
Phase 1.

### [M] `tests/unit/domain/account/test_account.py`

From `tests/unit/test_fees.py`, `test_interest.py`, `test_reversals.py`, and `test_authorizations.py`, merged.

```diff
- history = find_history(log, ACC_001)
- assert sum_holds(history, Day(3)) == Ok(make_aed("185.00"))
+ account = Ledger(CHALLENGE, log).find_account(ACC_001_OPENING)
+ assert account.sum_holds(Day(3)) == Ok(make_aed("185.00"))
```

- = Preserve: every test, in the files' current order, grouped under a comment naming its topic.
- Moved elsewhere: the AMB-036 test to `test_ledger.py`; the two table tests to `test_authorizations.py`.
- ✓ Proof: `test:unit`. Phase 2.

### [N] `tests/unit/domain/account/test_authorizations.py`

```diff
+ def test_every_state_and_settlement_input_pair_follows_the_table(
+     state: AuthorizationState, kind: SettlementKind, amount: Amount, expected_state: ...
+ ) -> None:
+     assert apply_settlement(state, kind, amount) == expected_state
+ def test_an_unconfigured_transition_leaves_the_state_unchanged() -> None:
```

- = Preserve: both tests, by name, with their ten and two cases; the table's rows keep their states, amounts, and
  expected outcomes, and each `FinalSettlement(x)` becomes `(SettlementKind.FINAL, x)` (R17).
- ✓ Proof: `test:unit`. Phase 2.

### [M] `tests/unit/test_processing.py` → `tests/unit/domain/ledger/test_ledger.py`

```diff
- log = unwrap_ok(process_event(log, event, Day(1), CHALLENGE))
+ ledger = unwrap_ok(ledger.process_event(event, Day(1)))
+ def test_an_event_on_an_unconfigured_account_is_an_internal_fault() -> None:
```

- = Preserve: every test, and the AMB-036 test moved in from `test_reversals.py`.
- New: actor, the ledger; precondition, `Ledger.open(CHALLENGE)`; action, a credit on `ACC-003`; outcome,
  `Err(UnknownAccount(AccountId("ACC-003")))`.
- ✓ Proof: `test:unit`. Phase 3.

### [M] `tests/unit/application/test_stream.py`

From `tests/unit/test_stream_processing.py`, `test_criteria.py`, and `test_known_weakness.py`, merged.

```diff
- processed = unwrap_ok(process_stream(build_brief_stream(), CHALLENGE))
+ processed = unwrap_ok(IncomingStream(build_brief_stream()).process(CHALLENGE))
```

- = Preserve: every test; the known weakness keeps `xfail(strict=True)`, its reason, and its inline annotations.
- ✓ Proof: `test:unit`, which reports `1 xfailed`. Phase 4.

### [M] `tests/unit/test_report.py` → `tests/unit/application/test_report.py`

`build_report(log, day, CHALLENGE, {})` becomes
`DayReport.build(Ledger(CHALLENGE, log), day, ReportedClosings.make_empty())`. = Preserve: every test. ✓ Proof:
`test:unit`. Phase 4.

### [M] `tests/unit/test_stream_csv.py` → `tests/unit/adapters/test_csv_file.py`

`parse_stream(text, CHALLENGE)` becomes `CsvFileSource.parse(text, CHALLENGE)`. = Preserve: every test. ✓ Proof:
`test:unit`. Phase 4.

### [M] `tests/unit/test_render.py` → `tests/unit/adapters/test_text_report.py`

`render_reports(reports)` becomes `TextReportSink.render(reports)`. = Preserve: every test. ✓ Proof: `test:unit`.
Phase 4.

### [E] `tests/unit/test_cli.py`

```diff
- monkeypatch.setattr(cli, "process_stream", process_with_mismatch)
- exit_code = run_cli(["streams/challenge.csv"], read_brief, out, err)
+ exit_code = run_cli(["streams/challenge.csv"], read_brief, out, err, FailingRun(Err(CurrencyMismatch("AED", "BHD"))))
+ def test_an_unknown_account_exits_2_naming_it() -> None:
```

- = Preserve: every test, its standard output, standard error, and exit code; the brief's run passes
  `LedgerRun(CHALLENGE)`; `ClosedPipe` becomes a plain class with `write` and `flush`, a `TextOutput` without
  inheritance (R20).
- New: actor, the operator; precondition, a run that returns `UnknownAccount(AccountId("ACC-003"))`; action, `run_cli`;
  outcome, `("", "error: internal: ACC-003 is not a configured account\n", 2)`.
- ✓ Proof: `test:unit`. The new test lands in Phase 3, patching the processing as its neighbours do; Phase 4 gives every
  CLI test the fake port.

### [M] `tests/integration/test_stream_file.py` → `tests/integration/adapters/test_csv_file.py`

Its test keeps reading the shipped file from disk, through `CsvFileSource.parse`, at the integration boundary. ✓ Proof:
`npx nx run account-ledger-cli:test:integration`. Phase 4.

### [M] `tests/integration/test_main.py` → `tests/integration/test_cli.py`

Its two tests keep running `main` on the real descriptors, at the integration boundary. ✓ Proof: `test:integration`.
Phase 4.

### [E] `tests/e2e/test_program.py`, `tests/support/*.py`

`test_program.py` changes only the import of the render function it compares with; the support modules follow the new
API, and `streams.py`'s `ACC_001`, an opening, becomes `ACC_001_OPENING` beside `brief_stream.py`'s `ACC_001`, an ID
(polish, R19). ✓ Proof: `npx nx run account-ledger-cli:test:e2e`. Phases 1 to 6, as each API lands.

## Architecture

### [E] `specs/apps/account-ledger/cli/architecture.md`

```diff
- the shell is `cli.py` at its root, the adapters are `adapters/`, and the domain is `domain/`, with
- `stream_processing.py` and `report.py` at its root, the ledger service in `domain/ledger/` ...
+ the shell is `cli.py` and `challenge.py`; `application/` declares the ports and holds the use case, the stream
+ processing, and the report; `adapters/` implements the ports; `domain/` holds `ledger/`, `account/`, and `model/`
- | `account/aggregate`      | `AccountAggregateIn[M]`: the history, with each rule a caller outside uses as a method |
+ | `account/account`        | `AccountIn[M]`: the Account aggregate, one account's entries and every rule about them |
- Log = tuple[LogEntry, ...]     find_history(log, account) -> AccountAggregateIn[M]
+ EventLog = entries: LogEntry...   Ledger = config + log: EventLog   Ledger.find_account(opening) -> Account
```

- **L3 Components**: the prose, the diagram, and the table gain `application/` and its ports, lose `stream_processing`,
  `ledger/processing`, `ledger/end_of_day`, `ledger/event_log`, `account/aggregate`, `history`, `balances`, `decisions`,
  `fees`, `interest`, `reversals`, and `states`, and gain `ledger/ledger`, `account/account`, `account/event_log`,
  `account/rejections`, `application/*`, `adapters/csv_file`, `adapters/text_report`, and `challenge`. The paragraph
  under the table on why `states` sits apart goes, since the states join `authorizations`. Reason: the components move.
- **L4 Code**: every block names the new types; the `_…Base` lines go, replaced by one line on no inheritance; the
  state-machine paragraph and diagram name `SettlementKind.FINAL` and `.PARTIAL` and the rest `take` leaves (R17).
  Reason: the shapes change.
- **Dynamic View**: the calls become `IncomingStream.process`, `Ledger.process_event`, `Ledger.close_day`,
  `DayReport.build`, and `TextReportSink.publish`, in today's order. Reason: the names change; the sequence does not.
- **Domain Model**: the table's rows name `AccountIn[M]` as the aggregate and `AccountOpeningIn[M]` as the configured
  account, and `EventLog` as the ledger; the aggregate paragraph says every rule is one of its methods in one module;
  the service paragraph becomes the `Ledger` paragraph; the report paragraph moves it to `application/`. Reason: the
  model's types change; its invariants do not.
- **Reading the Code**: the order becomes `cli.py`, `application/run.py`, `application/stream.py`,
  `domain/ledger/ledger.py`, then `domain/account/account.py` topic by topic, `authorizations.py`, `domain_events.py`
  and `rejections.py`, `application/report.py`, and `adapters/text_report.py`. Reason: the files change.
- **Constraints**: one bullet added: no class derives from another, save `Protocol`, `Generic`, `Enum`, or an exception.
- = Preserve: the Scope, L1, and L2 sections, word for word; the state machine's transitions.
- ✓ Proof: `npm run check:hygiene`, the width check, and a reading against the tree at each phase gate.
- Phases 1 to 4 update the sections their code changes; Phase 7 reads the whole file against the tree.

## Rules

Each change goes through [rules-propagation](../../../../repo-governance/workflows/maintenance/rules-propagation.md),
with its placement record in `local-tmp/rules-propagation-no-inheritance.md`, in Phase 5, after the code already follows
it, so no rule describes code that does not exist yet.

### [E] `repo-governance/development/quality/stacks/python-standards/003-operations.md`

```diff
- 3. **No class to hold it:** its subject is a type alias such as a tuple or a mapping, it builds one of a union's kinds
+ 3. **No class to hold it:** it builds one of a union's kinds
- 4. **A service:** it runs across aggregates, such as processing an event or closing a day.
- 6. **Keeps a type variable:** it is a generic rule that must return `Result[M, …]` for the caller's currency. ...
- Inside an aggregate's package, a rule several of its modules share stays a public function, ...
+ An aggregate is one class in one module, and a rule about it is its method, private where only it calls the rule.
- ## Shared Bases
- Kinds of one concept must share a base class when they share behaviour, or share fields ...
+ ## No Inheritance
+ A class must derive from nothing but `Protocol`, `Generic`, `Enum`, or an exception class. Kinds of one concept each
+ declare their own fields; behaviour they share is one private function each kind's method calls; a contract a
+ signature consumes is a `Protocol` whose members are read-only properties. pylint's `too-many-ancestors` enforces it.
```

- = Preserve: the opening paragraph, the criterion, exceptions 1, 2, and 5, and the followed and violated sentences.
- Reason: the Ledger and the EventLog are classes now, a `Self` method keeps the currency, and the owner chose
  composition over inheritance (R3, R9). Principle trace: Simplicity Over Complexity prefers composing small parts to an
  inheritance hierarchy. The file stays under the 750-word budget.

### [E] `repo-governance/development/quality/stacks/python-standards.md`

```diff
- Each operation is a method of its subject type, save six named cases, and kinds of one concept share a base when the
- code reads their common fields through their union, as [Operations](python-standards/003-operations.md) holds.
+ Each operation is a method of its subject type, save four named cases, and no class derives from another but a
+ `Protocol`, `Generic`, `Enum`, or exception, as [Operations](python-standards/003-operations.md) holds.
- The `lint`, `typecheck`, and `test:*` Nx targets enforce the gates in hooks.
+ The `lint`, `typecheck`, and `test:*` Nx targets enforce the gates, inheritance included, in hooks.
```

- The file holds 749 of its 750 words today, so each replacement is no longer than the text it replaces, counted with
  `./rhino governance word-budget validate` before the commit.

### [E] `repo-governance/development/quality/stacks/python-standards/README.md`

```diff
- | [Operations](003-operations.md) | ... the cases left as functions, shared bases |
+ | [Operations](003-operations.md) | ... the cases left as functions, no inheritance |
```

### [E] `repo-governance/development/quality/stacks/python-standards/001-naming.md`

```diff
- `parse_stream`, `_format_amount`, or `compute_closing`, never a bare noun like `_amount` or a bare verb like
+ `parse_event_id`, `_format_amount`, or `compute_closing`, never a bare noun like `_amount` or a bare verb like
```

Reason: `parse_stream` becomes `CsvFileSource.parse`. `AccountIn[M]` and `Account`, its other examples, keep their
meaning, now the aggregate's.

### [E] `apps/account-ledger-cli/pyproject.toml`

```diff
- enable = ["missing-module-docstring", "missing-class-docstring", "missing-function-docstring", "invalid-name"]
+ enable = ["missing-module-docstring", "missing-class-docstring", "missing-function-docstring", "invalid-name",
+           "too-many-ancestors"]
+ [tool.pylint.design]
+ max-parents = 0
+ ignored-parents = ["typing.Protocol", "typing.Generic", "enum.Enum", "builtins.NoneType", "builtins.Exception",
+                    "builtins.BaseException"]
- function-rgx = "^_?(accrue|add|advance|...|derive|...|sign|...)(_[a-z0-9]+)+$"
+ function-rgx = "^_?(accrue|add|advance|...|open|...|publish|...)(_[a-z0-9]+)+$"
```

- The verbs `open` (`Ledger.open`) and `publish` (`ReportSink.publish`) join both lists; `derive` and `sign` leave them
  once nothing uses them, in the phase that removes their last user.
- ✓ Proof: the RED run in Phase 5 flags today's twenty-plus derived classes on the baseline copy and nothing on the
  working tree.

## Documents

### [E] `apps/account-ledger-cli/README.md`

```diff
- | `src/account_ledger/cli.py`    | imperative shell: `run_cli` injects every effect; `main` binds the real ones    |
- | `src/account_ledger/adapters/` | pure translators: `stream_csv` reads the stream, `render` writes the report     |
+ | `src/account_ledger/cli.py`    | the shell: `run_cli` takes every effect and the use case; `main` binds them     |
+ | `src/account_ledger/application/` | the use case, its ports, the stream processing, and the report             |
+ | `src/account_ledger/adapters/` | the ports' implementations: `csv_file` reads the stream, `text_report` prints   |
- | `2`    | a currency mismatch, which only a bug brings | nothing         | `error: internal: ...`                   |
+ | `2`    | an internal fault, which only a bug brings   | nothing         | `error: internal: ...`                   |
- `tests/unit/test_known_weakness.py` holds the brief's one failing test
+ `tests/unit/application/test_stream.py` holds the brief's one failing test
```

- The DDD paragraph under the layout names the new packages; the sentence after the exit table adds the unknown
  account's line. Phases 4 and 7.

### [E] `docs/explanation/architecture-trade-offs.md`

"Append-only at scale" keeps its argument; "the account's history" reads "the account's entries", and the timing table
and the 0.71 s figure take the re-measured values if any moves by more than a fifth
([behaviour preservation](004-behaviour-preservation-and-tests.md#every-other-proof)). Phase 7.

### [E] `WORKLOG.md`

One entry per session of work, with real times, newest first; no earlier entry is reworded. Every phase.

### [E] `plans/in-progress/README.md`

Its directory map lists this plan while it is in progress; the archival move takes it out and adds it to
`plans/done/README.md`. With the plan's first commit, and at archival.

### Unchanged, Checked

`README.md`, `AGENTS.md`, `docs/` other than the trade-offs doc, `AMBIGUITIES.md`, `NUMBERS.md`, `REJECTED.md`,
`MOVEMENT.md`, `OUTPUT_TARGET.md`, and `challenge-raw.md` name no module, function, or test file, and stay as they are;
the Phase 7 doc sweep reads every Markdown file for a name the restructure removed and proves none remains outside
`plans/done/` and this plan.
