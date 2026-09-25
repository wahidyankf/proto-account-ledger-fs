# Decision Records

Every material decision behind the restructure, as
[decision records](../../../../repo-governance/conventions/structure/plans/012-decision-records.md) require. R1 to R14
were settled with the owner at the pre-write gate, one question each, on 2026-09-25. R15, R16, R19, and R21 follow from
a rule or a probe and needed no question. R17, R18, and R20 came out of drafting and were settled on the recommendation,
because the owner's goal for this plan said not to stop before every phase is done; the final report names them for the
owner to reopen. Prior art cites this repository first: its rules, its archived plan
`plans/done/2026-09-25__in-memory-account-ledger-init/`, and the commits before `83dfd58`.

## R1 — The Account Aggregate Is One Class in One Module

- **Evidence.** The rules about one account are spread over nine modules (`history`, `aggregate`, `balances`,
  `decisions`, `fees`, `interest`, `reversals`, `authorizations`, part of `event_log`), with `AccountAggregateIn`
  forwarding to generic functions. The owner's example: `list_records` takes only a history yet lives in
  `authorizations.py`.
- **Selected.** One class, `AccountIn[M]`, in `domain/account/account.py`, every rule a method, private where only the
  class calls it (owner's pick).
- **Alternatives.** Topic mixins composed into one class (recommended at the gate: keeps topic files, adds an MRO);
  topic objects the aggregate holds (`account.fees.assess(...)`: more classes, each needing the history); the status quo
  (functions per topic, forwarding methods).
- **Prior art.** The archived plan's tech-docs put every rule on a history; `003-operations.md` already asks for
  methods. Evans' aggregate is one root through which every invariant of the cluster is reached.
- **Trade-offs.** One file of about 650 lines against one place to look; mixins lost to the owner's composition
  preference, topic objects to their added indirection, the status quo to the scatter the owner named.
- **Consequences.** A reader finds every rule about an account in one class; the file is long and ordered by topic.
- **Revisit.** The file passes 1,000 lines, or two people edit it at once often enough to conflict.

## R2 — Three Layers, Hexagonal

- **Evidence.** The domain today holds the stream processing and the report beside the rules; the shell wires parse,
  process, and render by hand.
- **Selected.** `domain/`, `application/`, `adapters/`, and the shell; the application declares ports and the adapters
  implement them (owner: "DDD + hexagonal aja sekalian").
- **Alternatives.** Keep two layers, the domain and the adapters; a layer per bounded context, which the one-context
  domain does not need.
- **Prior art.** `functional-core-imperative-shell.md`; the `ruff.toml` bans per package already enforce a direction.
  Cockburn's ports and adapters.
- **Trade-offs.** Two more packages and two more ban files against a use case that knows no text, file, or CSV.
- **Consequences.** A new input or output format is one adapter; the domain and the use case do not change.
- **Revisit.** A second use case appears that the one `LedgerRun` cannot serve.

## R3 — Composition and Protocols, No Inheritance

- **Evidence.** Seven shared bases were committed in `7106c88` to `b9979da`; the owner then said they prefer composition
  over inheritance and asked whether mixins are unsafe.
- **Selected.** No class derives from another save `Protocol`, `Generic`, `Enum`, or an exception class; the seven bases
  go (owner's pick).
- **Alternatives.** Keep one-level data-only bases; plain duplication with no contract at all.
- **Prior art.** `simplicity-over-complexity.md` prefers composing small parts to an inheritance hierarchy; pyright
  checks a `Protocol` structurally (probe `local-tmp/restructure/probe_proto.py`, 0 errors).
- **Trade-offs.** Each kind repeats its field list, against no hidden coupling through a base.
- **Consequences.** The rule's "Shared Bases" section is replaced (R9 enforces it).
- **Revisit.** A family grows past about ten kinds sharing the same fields and behaviour.

## R4 — Flat Fields

- **Evidence.** Code reads `event.account`, builds events positionally, and matches `Credit(posting=…)` everywhere.
- **Selected.** Each kind declares its own fields in today's order (owner's pick).
- **Alternatives.** A composed header value object (`event.header.account`); a header plus forwarding properties.
- **Prior art.** Every value in `domain/model/` before `7106c88` declared its own fields.
- **Trade-offs.** Repeated field lines against unchanged call sites, patterns, and constructors.
- **Consequences.** No call site changes for R3.
- **Revisit.** A field is added to every kind of a family more than once.

## R5 — The Ports: EventSource, ReportSink, RunLedger

- **Evidence.** `cli._process_file` reads, parses, processes, and renders; its tests patch `cli.process_stream`.
- **Selected.** `EventSource.read_events`, `ReportSink.publish`, and the driving port `RunLedger.run`; `run_cli` takes a
  `RunLedger`, so its tests pass a fake (owner picked the first two; the driving port and the injection shape follow).
- **Alternatives.** A port per format, a parser and a renderer; ports down to the operating system (a file reader, a
  clock).
- **Prior art.** `run_cli` already takes its reader and streams as arguments; the archived plan's D13 fixed the exit
  statuses.
- **Trade-offs.** Three `Protocol`s against a CLI test that no longer patches a module attribute.
- **Consequences.** File reading moves into the source adapter; every message and exit code stays.
- **Revisit.** A second driving adapter, such as a service, needs a different port.

## R6 — Ledger and EventLog Classes

- **Evidence.** `Log` is a tuple alias, and `process_event` and `close_day` are functions over it and the config.
- **Selected.** `Ledger(config, log)` and `EventLog(entries)`, each frozen, each method returning a new value (owner's
  pick).
- **Alternatives.** A `Ledger` holding a raw tuple; the domain-service functions as they are.
- **Prior art.** `003-operations.md` exceptions 3 and 4 existed only for the alias and the service; Evans' domain
  service is stateless, which a frozen `Ledger` is too.
- **Trade-offs.** Two classes against two rule exceptions gone.
- **Consequences.** The `Log` alias goes; `ProcessedStream.logs` holds `EventLog`s.
- **Revisit.** The log needs an index for speed, which would live in `EventLog`.

## R7 — Account and AccountOpening

- **Evidence.** `AccountIn` names the configured account today, and `AccountHistoryIn` and `AccountAggregateIn` the
  aggregate.
- **Selected.** The aggregate is `AccountIn[M]` and `Account`; the configured account is `AccountOpeningIn[M]` and
  `AccountOpening` (owner's pick).
- **Alternatives.** Keep `AccountHistoryIn`; keep `AccountAggregateIn`.
- **Prior art.** `001-naming.md`: a type generic over the currency is its noun and `In`.
- **Trade-offs.** A rename of the configured account against the aggregate taking the domain's own noun.
- **Consequences.** `001-naming.md`'s `AccountIn` example keeps its words and gains the aggregate's meaning.
- **Revisit.** A second kind of account, such as a card account, needs the noun.

## R8 — Every `assert` Replaced by a Type

- **Evidence.** Five `assert`s in `src/` prove what the types do not carry.
- **Selected.** Each replaced as [the domain model](002-domain-model.md#where-each-assert-goes-r8) lists, with a
  bug-only `UnknownAccount` fault; the owner added that no assessment-doc result and no user-visible behaviour change.
- **Alternatives.** Keep the `assert`s; replace them with raised exceptions.
- **Prior art.** `002-failures.md`: an expected failure is a returned value, an exception is for bugs.
- **Trade-offs.** One new internal fault and one CLI line against no escape from the type checker.
- **Consequences.** The exit table gains an unreachable internal line (a release decision, 005).
- **Revisit.** Python gains refinement types that carry these proofs directly.

## R9 — No Inheritance, Gated by pylint

- **Evidence.** No review catches a new base reliably; pylint's `too-many-ancestors` counts ancestors.
- **Selected.** `too-many-ancestors` with `max-parents = 0` and six ignored parents; a probe flags only a dataclass
  subclass (owner's pick).
- **Alternatives.** Review only; a custom ruff rule, which ruff does not support.
- **Prior art.** The naming rule is already a pylint `invalid-name` gate.
- **Trade-offs.** One more message enabled against a rule no one has to remember.
- **Consequences.** A test double that subclasses a library class fails lint, hence R20.
- **Revisit.** pylint changes how astroid reports `Enum` or `Protocol` ancestors.

## R10 — Tests Mirror the Source Tree

- **Evidence.** All unit tests sit flat in `tests/unit/`, named by topic.
- **Selected.** `tests/unit/` mirrors `src/account_ledger/`; every test and every case stays (owner's pick, adding that
  no behaviour may change).
- **Alternatives.** Keep the flat layout; mirrored directories with topic files.
- **Prior art.** The source tree already mirrors the layers; pytest's importlib mode allows equal basenames (probe).
- **Trade-offs.** Every test file moves against a test found where its code is.
- **Consequences.** R13 fixes the grain.
- **Revisit.** A test file passes 1,500 lines.

## R11 — The Behaviour Corpus and the Test Inventory Prove Preservation

- **Evidence.** The owner's hard constraint: nothing observable changes. The golden test covers only the brief.
- **Selected.** A recorded corpus of program runs, compared at every phase gate, plus a test inventory by name and case
  count ([behaviour preservation](004-behaviour-preservation-and-tests.md)).
- **Alternatives.** The three suites alone; a snapshot of the whole log for each input.
- **Prior art.** `deletion-with-proof.md` step 5: compare on recorded inputs.
- **Trade-offs.** A scratch script and two evidence files against a proof that reaches every error path.
- **Consequences.** Any difference fails a gate inside its phase.
- **Revisit.** None; the corpus ends with the plan.

## R12 — Module-Level Containers Frozen

- **Evidence.** `stream_csv.REQUIRED`, `OPTIONAL`, and `render.NUMBER_WORDS` are module-level `dict`s.
- **Selected.** `MappingProxyType`s; local accumulators stay.
- **Alternatives.** Leave them; turn them into functions.
- **Prior art.** `immutability.md` confines mutation to one scope; `DayReport` already holds `MappingProxyType`s.
- **Trade-offs.** None worth weighing; no reader writes them.
- **Consequences.** No shared mutable state remains.
- **Revisit.** None.

## R13 — One Test File per Source Module

- **Evidence.** R10 leaves the grain open.
- **Selected.** One test file per source module that has tests; the aggregate's in one `test_account.py`; whole-stream
  tests with `application/stream.py` (owner's pick).
- **Alternatives.** Topic files inside mirrored directories; one directory per module.
- **Prior art.** None in the repository; common pytest practice.
- **Trade-offs.** A long `test_account.py` against one file per module to find.
- **Consequences.** The known weakness lives in `test_stream.py`; the README names its path and test.
- **Revisit.** The same trigger as R10.

## R14 — CHALLENGE at the Composition Root

- **Evidence.** The brief's configuration lives in the domain's `config.py`, beside the type it instantiates.
- **Selected.** `account_ledger/challenge.py`, beside `cli.py` (owner's pick).
- **Alternatives.** Keep it in `config.py`; a data file the CLI reads.
- **Prior art.** The shell binds every effect in `main`.
- **Trade-offs.** One more module against a domain that holds no instance.
- **Consequences.** Tests import `CHALLENGE` from `account_ledger.challenge`.
- **Revisit.** The program takes its accounts from input.

## R15 — Money's Generic Rules Become Methods Returning `Self`

- **Evidence.** Exception 6 kept `sum_money` a function because a method lost the currency. Probes `probe_self.py` and
  `probe_proto.py` show a method returning `Result[Self, …]`, called on `M: (Aed, Bhd)`, gives `Result[M, …]` with 0
  pyright errors.
- **Selected.** `add_all`, `require_same`, and `compute_daily_interest` become methods of `Aed` and `Bhd`.
- **Alternatives.** Keep the generic functions; a generic helper class.
- **Prior art.** `Aed.make` and `parse` already return `Self`.
- **Trade-offs.** Two short methods per currency against one rule exception gone.
- **Consequences.** `003-operations.md` loses exception 6.
- **Revisit.** A pyright release changes how it binds `Self` on a constrained variable.

## R16 — CurrencyMismatch Stays a Returned Value

- **Evidence.** The archived plan's tech-docs 005 decided it, and the README publishes its message.
- **Selected.** Keep it, and add `UnknownAccount` beside it (R8).
- **Alternatives.** Raise on a mismatch; make it impossible by a single currency per ledger, which the brief refutes.
- **Prior art.** `002-failures.md`.
- **Trade-offs.** `Result`s through every sum against a published, tested behaviour kept.
- **Consequences.** None new.
- **Revisit.** The type system can prove the currency of every effect.

## R17 — The D8 Table Matches Kind and Rest

- **Evidence.** `FinalSettlement` and `PartialSettlement` only relabel `SettlementKind`, and `_compute_rest` needs an
  `assert`.
- **Selected.** `apply_settlement(state, kind, amount)` matches the state, the kind, and what `take` leaves of the hold;
  the settlement inputs go.
- **Alternatives.** Keep the inputs and add `take` beside them; a guard boolean, as today.
- **Prior art.** `python-standards.md`: one `match` over the state and trigger unions is the table.
- **Trade-offs.** The table test's cases are rebuilt from kinds, against five definitions and one `assert` gone.
- **Consequences.** The architecture's state diagram names kinds, not input classes.
- **Revisit.** A third settlement kind appears.

## R18 — A Protocol Only Where a Signature Consumes It

- **Evidence.** A closed union already states what its members share, and pyright checks every member has a field read
  through it; vulture reports a Protocol nothing uses.
- **Selected.** Four Protocols: the three ports and `TextOutput`.
- **Alternatives.** A Protocol per family (money, IDs, events); none at all, which the ports need.
- **Prior art.** The code has no Protocol today and reads shared fields through unions.
- **Trade-offs.** Families without a named contract against no unused declarations.
- **Consequences.** R3's contracts are the unions and these four.
- **Revisit.** A function takes "any event" beyond a closed union.

## R19 — Polish, Line by Line

- **Evidence.** Reading every module found parenthesized single imports, a wrapped `if (day == today):`, forwarding
  wrappers in the report, repeated tuples in the renderer, faults defined after their users, and two meanings of
  `ACC_001` in the test support.
- **Selected.** Each fixed in Phase 6, with no behaviour change.
- **Alternatives.** Leave them; fix them in each phase as met.
- **Prior art.** The earlier readability commits in the log.
- **Trade-offs.** A phase against a mixed diff in every other.
- **Consequences.** Phase 6 holds only polish.
- **Revisit.** None.

## R20 — TextOutput for the Streams

- **Evidence.** The closed-pipe test's double subclasses `io.StringIO`, which R9's gate flags.
- **Selected.** A `TextOutput` Protocol of `write` and `flush`, taken by `run_cli` and `TextReportSink`; the double is a
  plain class.
- **Alternatives.** Run the gate on `src` only; keep `TextIO` and a separate lint command for the tests.
- **Prior art.** `run_cli` uses only `write` and `flush` on its streams.
- **Trade-offs.** One Protocol against a gate with no exemption.
- **Consequences.** The rule binds the tests too.
- **Revisit.** The program needs another stream method, such as `fileno`.

## R21 — Plan, Quality Gate, Then Execution; the Rule Lands With Its Code

- **Evidence.** The owner asked for the plan, then its quality gate, then execution phase by phase, each committed and
  pushed.
- **Selected.** That order; the operations and inheritance rule changes land in Phase 5, after the code follows them.
- **Alternatives.** Change the rule first; change it at the end with the docs.
- **Prior art.** `rules-propagation.md` carries a rule change into what it makes stale; the archived plan landed its
  rules with their code.
- **Trade-offs.** Phases 1 to 4 run against a rule that still describes bases, against no rule describing code that does
  not exist.
- **Consequences.** Between Phase 1 and Phase 5, review reads the plan's rule, not the file's.
- **Revisit.** None.
