# Decision Records

Every material decision this plan rests on, in the shape
[Decision Records](../../../../repo-governance/conventions/structure/plans/012-decision-records.md) fixes. `S` records
were settled before this plan and are restated so the plan reads without its history; `D` records were resolved one by
one on 2026-09-24, D1 to D13 in the pre-write gate and the rest in the review after it, and are logged in
[WORKLOG](../../../../WORKLOG.md). A record the owner later changed says so in its own text. The ledger's rules
themselves are not repeated here: each is an entry in [AMBIGUITIES](../../../../AMBIGUITIES.md).

## S1 — Scope: Part 1 and the Trade-Offs Document

- **Evidence.** The brief has two parts: the repository, and a 2–4 page PDF "arising directly from your ledger
  implementation".
- **Selected.** All of Part 1, plus `docs/explanation/architecture-trade-offs.md`, the Markdown the PDF is made from.
- **Alternatives.** Part 1 only, leaving the trade-offs to a later plan; or Part 1 and the PDF itself.
- **Prior art.** The plan README recorded this scope before this plan was written.
- **Trade-offs.** Part 1 alone leaves the document to be written after the code is forgotten; the PDF adds layout and
  upload work no test can check.
- **Consequences.** The last phase writes the document from the built code; converting it is left to the owner.
- **Revisit when.** The brief's submission form changes what it accepts.

## S3 — Expected Failures Are Typed Result Values

- **Evidence.** The [Python standards](../../../../repo-governance/development/quality/stacks/python-standards.md) leave
  exceptions against result values open, "recorded here when the ledger is planned".
- **Selected.** Result values: a parse returns `tuple[IncomingEvent, ...] | StreamError`, a refusal is a `Rejected` log
  entry carrying its `Rejection`, a smart constructor returns its fault, and only the shell catches exceptions.
- **Alternatives.** Domain exceptions caught at the shell; or a generic `Result[T, E]` wrapper type.
- **Prior art.** The plan README chose result values; pyright's strict mode checks a union exhaustively with
  `assert_never`.
- **Trade-offs.** Exceptions hide a failure from the signature; a generic wrapper adds a type the stdlib lacks.
- **Consequences.** The Python standards record the choice (AC-29).
- **Revisit when.** A caller needs to compose many fallible steps and the unions grow unwieldy.

## D1 — The Program Reads the Stream From a File Path

- **Evidence.** The program has no input today. D3 needs streams other than the brief's.
- **Selected.** `account-ledger-cli <stream.csv>`; the brief's stream ships as `streams/challenge.csv`.
- **Alternatives.** Standard input; or the brief's stream written into the code.
- **Prior art.** Most replay tools take a file argument; the brief asks for a "runnable test suite or script that
  replays the event stream".
- **Trade-offs.** Standard input needs a redirect for the default run and gives integration no real file; a stream in
  code needs no parser but cannot replay anything else.
- **Consequences.** A parser, its faults, and exit status 2 for a bad file (D13).
- **Revisit when.** The stream has to arrive from another process as it happens.

## D2 — The Stream Is CSV

- **Evidence.** Amounts must never pass through a float; each event kind has different fields.
- **Selected.** CSV with fixed columns, blank where a kind takes none: eight, and nine once partial capture adds `final`
  (tech-docs 003).
- **Alternatives.** JSON, one object per event; or TOML, one table per event.
- **Prior art.** The events table in OUTPUT_TARGET already has this shape; the stdlib `csv` module reads it.
- **Trade-offs.** JSON and TOML name each field and can read numbers as `Decimal` (`parse_float=Decimal` in both stdlib
  readers), but are longer to write by hand and to diff; CSV shares one `reference` column across kinds and so validates
  per kind.
- **Consequences.** Per-kind validation in `parse_stream`, one message per fault.
- **Revisit when.** An event kind needs a nested or repeated field.

## D3 — Every Resolved Rule Is Built and Tested

- **Evidence.** AMB-013, 027, 028, 029, 030, 034, and 035 state what the ledger does, yet the brief's stream triggers
  none of what they add; it triggers only AMB-013's final settlement, through E5.
- **Selected.** Build and test all of them; AMB-013 last, with a fallback the owner approved (delivery Phase 8).
- **Alternatives.** Build only those that come nearly free (AMB-027, 029, 030) and reword the rest as not built; or
  build only what the stream triggers.
- **Prior art.** REJECTED already promises a test for every refused criterion.
- **Trade-offs.** Each skipped rule becomes a claim without proof in a defense that asks for proof; building all costs
  about seven more tests and the partial-capture state.
- **Consequences.** AC-14 to AC-22 and AC-31 to AC-33.
- **Revisit when.** The fallback's trigger fires (delivery Phase 8).

## D6 — The Failing Test Is One Plain Unit Test

- **Evidence.** The brief asks for "One failing test against your own design, inline-annotated with what it reveals";
  AMB-031 makes it a strict expected failure.
- **Selected.** `tests/unit/test_known_weakness.py`, one function, annotated inline (tech-docs 004).
- **Alternatives.** A scenario bound at every layer, three expected failures; or one bound at the unit layer only.
- **Prior art.** The strict-xfail rule in
  [Test Design](../../../../repo-governance/development/quality/testing/test-driven-development/002-test-design.md).
- **Trade-offs.** A scenario states behaviour the as-built system lacks; three failures are not "one".
- **Consequences.** The window is configuration, so the test replays through Day 32.
- **Revisit when.** Holds gain a lifetime, which turns the test green and removes the marker.

## D7 — Balances Are Recomputed From the Log

- **Evidence.** Each close re-reads every day of the window for fees and interest (AMB-002, AMB-005); the log holds
  fewer than fifty entries.
- **Selected.** Pure functions that scan the whole log on every query.
- **Alternatives.** A running projection of totals by account and value day, updated on each append; or a cache per
  account and day, dropped when a backdated event arrives.
- **Prior art.** Event sourcing treats projections as an optimisation over the log (Martin Fowler, "Event Sourcing",
  2005).
- **Trade-offs.** A projection must stay in step with the log and hides its bugs at this size; a cache adds
  invalidation, the classic source of defects, for no gain here. Scanning costs O(days × entries) per close.
- **Consequences.** The trade-offs document names this scan as what breaks first at 100×, and the projection as the
  cheapest structural change that defers it.
- **Revisit when.** A replay takes long enough to notice.

## D8 — The Authorization Lifecycle Is a Hand-Written State Machine

- **Evidence.** Four states and business transitions, which the finite-state machine standard makes a declared machine,
  leaving library against hand-written to the adopter.
- **Selected.** Hand-written transitions over an explicit closed type, with pure guards (tech-docs 001). D17 later made
  the closed type a union of one dataclass per state, and the table a `match`.
- **Alternatives.** A library such as `python-statemachine` or `transitions`; or state derived from flags.
- **Prior art.** None in the repository; the standard lists both options.
- **Trade-offs.** The libraries hold state in mutable objects, against the functional core, and add a dependency and an
  idiom to defend; flags are what the standard forbids.
- **Consequences.** The Python standards record the choice for the stack (AC-29).
- **Revisit when.** A lifecycle grows past what a readable table holds.

## D9a — A Test-First Item Is Three Items

- **Evidence.** Test-driven development here requires a recorded red; module 011 leaves the checklist form open.
- **Selected.** Split: RED, GREEN, and REFACTOR are separate items, each with its evidence.
- **Alternatives.** One item whose proof records the red and the green; or one item proved by the passing test.
- **Prior art.** [Task tracking](../../../../repo-governance/development/agents/task-tracking/001-list-lifecycle.md)
  already splits each step in the task list.
- **Trade-offs.** One item can be ticked with both records at once; a passing test alone shows nothing failed first. The
  split makes the checklist long.
- **Consequences.** Recorded as the repository's choice under module 011 (AC-29).
- **Revisit when.** A plan's checklist becomes too long to resume from cold.

## D9b — A Baseline Phase Comes First

- **Evidence.** A failure that predates a plan must still be fixed, and without a baseline it looks like the plan's.
- **Selected.** Phase 0 runs and records every gate before any change.
- **Alternatives.** No baseline. Module 011 offers only these two, and no third was found in the repository.
- **Prior art.** Module 011 lists both.
- **Trade-offs.** One more phase against an unattributable failure.
- **Consequences.** Recorded under module 011 (AC-29).
- **Revisit when.** Never for this plan; the choice binds later plans too.

## D9c — Every Phase Ends at a Gate

- **Evidence.** Module 011 leaves phase boundaries open: a gate per phase, or plan-level pause safety only.
- **Selected.** A `### Phase N Gate` of exact commands and observable criteria, then a pause-safety note, per phase.
- **Alternatives.** Plan-level pause safety only. Module 011 offers only these two, and no third was found.
- **Prior art.** None; this is the first plan.
- **Trade-offs.** A longer checklist against a resumed executor re-deriving whether the last phase left things coherent,
  which D10's push per phase would make worse.
- **Consequences.** Recorded under module 011 (AC-29); each gate commits and pushes (D10).
- **Revisit when.** A plan has a single phase.

## D9d — A Defective Archived Plan Is Reopened

- **Evidence.** Module 011 offers a follow-up plan or reopening; `plans/done/README.md` already says "reopen it".
- **Selected.** Reopen: move the folder back to `in-progress/`, strip the date prefix, and add a dated note.
- **Alternatives.** A follow-up plan linking the archived one. Module 011 offers only these two.
- **Prior art.** `plans/done/README.md`, written with the scaffold.
- **Trade-offs.** A second reverse edge in the lifecycle, recorded as adapted, against a repair living apart from the
  claim it corrects.
- **Consequences.** Recorded under module 011 (AC-29), matching what `plans/done/README.md` states.
- **Revisit when.** Archived plans accumulate and a reopened one would disturb others.

## D10 — Each Phase Gate Commits and Pushes

- **Evidence.** [Commit Authorization](../../../../repo-governance/development/workflow/commit-authorization.md) lets an
  approved plan's step name the action; the pre-push hook runs every test layer.
- **Selected.** Every phase ends by committing its theme and pushing to `origin/main`.
- **Alternatives.** Commit each phase and wait for the owner to push; or wait for the owner for both.
- **Prior art.** Every commit so far was made on an explicit request.
- **Trade-offs.** Waiting keeps the owner's review before publication but stalls execution at every phase.
- **Consequences.** Approving the plan and ordering execution authorizes these commits and pushes, and nothing else;
  every commit must be build-valid, so no commit holds a failing test, and red evidence lives in delivery.
- **Revisit when.** The owner asks to see a phase before it is pushed.

## D11 — Archival Needs the Execution Check Only

- **Evidence.** [Execution](../../../../repo-governance/workflows/plan/plan-execution.md) leaves the completion gate to
  the adopter.
- **Selected.** The execution check alone: its permitting verdict, on a check that every delivered item was executed as
  written, closes the plan. The owner first chose a fresh quality gate on the end as well, then changed it on
  2026-09-24, before execution, to the execution check alone.
- **Alternatives.** The execution check and a fresh, explicitly directed quality-gate `PASS` on the finished plan. The
  workflow offers only these two, and no third was found.
- **Prior art.** None; this is the first plan.
- **Trade-offs.** One review closes the plan, against judging the delivered plan's documents once more; the quality gate
  that runs once before execution already judged them.
- **Consequences.** Recorded under the Execution workflow (AC-29); resuming interrupted work needs no fresh gate.
- **Revisit when.** An archived plan is found to have claimed work its execution check passed.

## D12 — Plain Pytest, Not Gherkin

- **Evidence.** The repository binds every Gherkin scenario at three layers. At the integration and end-to-end layers
  the only observable is the printed report, so each step there would parse ASCII tables, and the unit layer would need
  the whole report copied into a docstring.
- **Selected.** Plain pytest: rule and criterion tests on the model at the unit layer, the real file and streams at the
  integration layer, and one golden run against OUTPUT_TARGET end to end.
- **Alternatives.** Gherkin at three layers, keeping the rules; or Gherkin for the criteria only.
- **Prior art.** The scaffold binds `greeting.feature` at three layers through pytest-bdd.
- **Trade-offs.** Gherkin reads well to an assessor but adds two machines, the bindings and a report parser, that prove
  nothing about the ledger and must be defended without AI; the hybrid keeps both costs and two styles.
- **Consequences.** Supersedes the gate's D4 (features by domain) and D5 (the report as a docstring). pytest-bdd and the
  behaviour-driven rules are retired through Rules Propagation (tech-docs 006).
- **Revisit when.** Behaviour must be agreed with someone who reads Gherkin but not Python.

## D12b — ACCEPTANCE_CRITERIA.feature Is Deleted

- **Evidence.** It holds the brief's wording, which `challenge-raw.md` owns, and verdict tags, which REJECTED and
  MOVEMENT own.
- **Selected.** Delete it; MOVEMENT and REJECTED name each criterion's test.
- **Alternatives.** Keep it as an unexecuted draft; or replace it with a Markdown index.
- **Prior art.** It was drafted to move under `specs/`, a plan D12 cancels.
- **Trade-offs.** Keeping it leaves a `.feature` file in a repository without Gherkin and a second copy of each verdict.
- **Consequences.** The assessment-docs convention drops its row.
- **Revisit when.** D12 is revisited.

## D12c and D12d — The Specification Corpus Is Architecture Only, as Full C4

- **Evidence.** The specification-tree convention requires a non-empty `behaviours/`; with D12 behaviour is stated by
  AMBIGUITIES and proven by tests.
- **Selected.** Delete `behaviours/`; `architecture.md` becomes a full C4 model: system context, containers, components,
  code, and a dynamic view of one day (AC-26).
- **Alternatives.** A Markdown catalogue of rules under `behaviours/`; or no `specs/` at all.
- **Prior art.** `architecture.md` holds a context, containers, and two components today.
- **Trade-offs.** A catalogue repeats AMBIGUITIES; removing `specs/` moves the as-built model among documents written
  for people.
- **Consequences.** The specification-tree convention records the adaptation.
- **Revisit when.** A second owner joins the product.

## D13 — The Program Sits at the Floor Tier

- **Evidence.** The command-line convention binds a tool at the floor tier or the full bar, and says the adopter records
  which.
- **Selected.** The floor: the closed exit vocabulary, stream discipline, and the closed-pipe and signal statuses.
- **Alternatives.** The full bar, adding `--help`, a machine-readable mode, and structured diagnostics. The convention
  names only these two tiers, and no third was found; a tier between them would be an adaptation of its own.
- **Prior art.** The scaffold returns 0 and writes one line.
- **Trade-offs.** The full bar adds an output schema and its tests for callers that do not exist.
- **Consequences.** The application README records the tier and publishes the statuses; no governance file changes.
- **Revisit when.** Another program consumes the report.

## D14 — Money Is a Sum Type, One Class per Currency

- **Evidence.** The ledger holds AED and BHD accounts, and nothing in `Decimal` stops
  `Decimal("1.00") + Decimal("1.000")` from adding dirhams to dinars.
- **Selected.** `Aed` and `Bhd` frozen dataclasses joined in `Money`, with operators only between the same type, generic
  code over `M: (Aed, Bhd)`, and a typed `CurrencyMismatch` where a union must be narrowed; no `Decimal` leaves
  `money.py` (tech-docs 001).
- **Alternatives.** One `Money(amount, currency)` class checked at runtime; or `Decimal` with the currency beside it, as
  the Python standards state today.
- **Prior art.** The sum types of the functional languages, `type currency = AED of decimal | BHD of decimal`, which the
  owner named as the model; `NewType` gives a name but no operators.
- **Trade-offs.** Two small classes and a generic signature per money function, against a mismatch found only when a
  test happens to hit it.
- **Consequences.** The Python standards' money row changes (R2); pyright strict proves no cross-currency sum exists.
- **Revisit when.** A third currency arrives, which adds a class and a case to each narrowing `match`.

## D14b — Each Money Type Wraps a Quantized Decimal

- **Evidence.** AMB-006 rounds half-even to each currency's places; the brief says "Amounts stored and rounded to their
  own precision".
- **Selected.** The wrapped value is a `Decimal` with exactly its currency's places, checked on construction; parsing
  refuses more places, and only computed values are rounded, inside `money.py`.
- **Alternatives.** An integer count of minor units (fils); or an unquantized `Decimal` rounded on output.
- **Prior art.** The Python standards already require a quantized `Decimal`.
- **Trade-offs.** Minor units make rounding explicit everywhere but make every figure in MOVEMENT a conversion to
  explain; rounding on output lets an unrounded sum reach a balance, as C8's remainder would.
- **Consequences.** A stream amount with too many places is a parse fault (tech-docs 003).
- **Revisit when.** Performance at scale makes `Decimal` too slow.

## D15 — Days and Every ID Are Value Objects

- **Evidence.** A day, an account ID, a hold ID, and an event ID are all plain `int` or `str` today, so any two can be
  swapped without an error.
- **Selected.** `Day`, `AccountId`, `AuthorizationId`, the six event ID types, and `InstalmentCount` as frozen value
  objects with smart constructors; raw values exist only in the parser and the renderer.
- **Alternatives.** `NewType` aliases, which the type checker separates but which validate nothing; or plain values
  validated in the parser only.
- **Prior art.** The value-object row of the finite-state machine standard, "validating the shape or range of a value".
- **Trade-offs.** More types to construct in tests, which `tests/support/streams.py` hides, against a marker or a day
  built from a wrong string.
- **Consequences.** The Python standards gain a value-object row (R2); markers are built from their parts.
- **Revisit when.** Never for this plan.

## D16 — No Illegal State Is Representable

- **Evidence.** The owner's direction on 2026-09-24: the application is type-safe, and its domain model correct.
- **Selected.** Every type is built so no value of it can be illegal, and each constructor refuses what would be; D17
  and D18 apply it where the first design still allowed an illegal value, as did the outcome, capture, and posting types
  of tech-docs 001.
- **Alternatives.** Validate at the edges and trust the core; or check invariants in `__post_init__` without changing
  the shapes.
- **Prior art.** "Make illegal states unrepresentable", from typed functional programming.
- **Trade-offs.** More types, against every function re-checking its inputs or trusting that someone did.
- **Consequences.** The Python standards record the principle beside the domain shapes (R2).
- **Revisit when.** A type's constructor would need data it cannot see, which is where a runtime check stays.

## D17 — Each Authorization State Is Its Own Type

- **Evidence.** An `Enum` state with a separate `remaining` field can say "declined with a hold of 200.00".
- **Selected.** `Approved(hold)`, `PartiallySettled(captured, hold)`, `Settled(captured)`, and `Declined(requested)`,
  joined in a union; `transition` is one `match` ending in `assert_never`, and a test walks every pair of state and
  trigger against the table. Revises D8's form, not its choice of hand-written transitions.
- **Alternatives.** Keep the `Enum` and a frozen table, checking data in `__post_init__`; or both, a union with an
  `Enum` tag for the table.
- **Prior art.** The finite-state machine standard asks for a closed set of states with an explicit type.
- **Trade-offs.** The table is code rather than data, so it cannot be looped over; the test of every pair takes the
  loop's place. The tagged hybrid keeps two representations that must agree.
- **Consequences.** A partial settlement reaching the hold settles, since a `PartiallySettled` hold is above zero.
- **Revisit when.** The lifecycle gains states whose table no longer reads as one `match`.

## D18 — An Event Amount Is Positive; a Balance Is Signed

- **Evidence.** A credit of −400.00 means nothing, while a closing of −370.00 is routine.
- **Selected.** `Amount[M]`, above zero by construction, on every event; balances as plain `M`; a `Direction` on the
  interest adjustment, the one event that moves either way.
- **Alternatives.** One signed money type, with each event's constructor checking the sign; or a signed amount on every
  event, its sign giving the direction, as a single-column ledger stores it.
- **Prior art.** Double-entry ledgers record a positive amount and a side.
- **Trade-offs.** One more generic type, against a sign rule each event must remember.
- **Consequences.** The renderer prints a `DOWN` adjustment with `−`, as OUTPUT_TARGET's `−0.10, for Day 2` shows.
- **Revisit when.** An event kind needs a signed amount of its own.

## D19 — A Duplicate Is Logged With No Effect

- **Evidence.** AMB-014 appends every incoming event with its outcome; AMB-034 says a repeated event with the same
  content "has no effect and is not an error".
- **Selected.** Append it as `Duplicate`, moving nothing and printing no error; AMB-014 and AMB-034 say so.
- **Alternatives.** Append nothing, since the event is already in the log, the recommendation the owner did not take; or
  refuse every repeated ID as an error, AMB-034's second option.
- **Prior art.** Payment systems keep idempotency keys and return the first result; the delivery itself is usually kept
  in an inbox or access log.
- **Trade-offs.** The log records deliveries as well as events, and aggregations must skip duplicates, against losing
  the trace that a retry arrived.
- **Consequences.** AC-14 asserts the duplicate is in the log and the balance moved once.
- **Revisit when.** Deliveries are kept elsewhere, in an inbox in front of the ledger.

## D20 — Any Accepted Event May Be Reversed

- **Evidence.** The brief reverses one debit and says nothing of other targets; the plan accepted any.
- **Selected.** Any accepted event, incoming or fired, as AMB-035 resolves; after a fired end-of-day event is reversed,
  the next close fires again whatever the rules still require (D20b, the second question).
- **Alternatives.** Only accepted incoming postings, the recommendation; those plus a void of an approved authorization;
  or any accepted event with a reversed fired event waived for good, the recommendation for the second question.
- **Prior art.** Operations teams correct bank-generated fees and interest through the same reversal path as a
  customer's postings.
- **Trade-offs.** A reversed fee on a day still negative is charged again at the next close, so a fee cannot be waived;
  the trade-offs document records the waiver as cut.
- **Consequences.** AC-31 to AC-33; a reversal's reference accepts a marker (tech-docs 003).
- **Revisit when.** Fees must be waived, which needs a waiver event the fee rule reads.

## D21 — A Row the Ledger Cannot Represent Is an Input Fault

- **Evidence.** AMB-014 logs refused events; the parser also meets rows naming an unknown account, a non-positive
  amount, or a day outside the window.
- **Selected.** They stop the replay with exit 2 and a line-numbered message, as AMB-014 now says; only refusals that
  depend on what the ledger holds are logged.
- **Alternatives.** Log them as rejected and continue, which needs an entry holding raw, unvalidated values; or skip the
  row with a warning on standard error and replay the rest.
- **Prior art.** Batch file ingestion rejects a file whose records break its schema.
- **Trade-offs.** One bad row stops the whole file, against a log entry D16 forbids or a report that silently omits an
  event its sender sent.
- **Consequences.** The parse faults of tech-docs 003; AC-03's second scenario.
- **Revisit when.** The stream arrives live, where stopping is not an option and a quarantine is.

## D22 — The Texts the Brief Never Prints Are Chosen Here

- **Evidence.** AC-02 to AC-04, AC-15 to AC-17, the parse faults, and the rows no stream in the brief prints need
  wording, and the brief and OUTPUT_TARGET give none.
- **Selected.** The texts in tech-docs 001 and 003, each in the pattern of the nearest text OUTPUT_TARGET prints, and
  the diagnostics in the `error: ` form the command-line convention's floor tier uses.
- **Alternatives.** Leave each to the executor; or copy another tool's messages.
- **Prior art.** OUTPUT_TARGET's own patterns, such as `Auth-A settled for 185.00`.
- **Trade-offs.** Wording fixed before the code exists may read oddly once seen, against an executor inventing it
  mid-cycle and a test pinning whatever came out.
- **Consequences.** Each text is pinned by the test that names it; changing one is a plan change.
- **Revisit when.** A reader of the report finds one unclear.

## D23 — Money Is Undone at Most Once

- **Evidence.** Under AMB-035 as first written, reversing an instalment and then its credit undid the instalment twice,
  and reversing a refunded fee paid back 25.00 never charged; AMB-028 says each event is undone at most once.
- **Selected.** Refuse a reversal whose target's money is already undone another way, as `AlreadyUndone`, naming the
  part and what undid it; a refund may be reversed, putting its fee back in force (AMB-035).
- **Alternatives.** Accept it and undo only what is left, possibly nothing; or let each reversal undo its whole target
  regardless, as the first wording did.
- **Prior art.** AMB-028's rule for a second reversal of the same event.
- **Trade-offs.** One more rejection to test and explain, against a reversal that moves no money or moves money twice.
- **Consequences.** AC-35; `AlreadyUndone` in tech-docs 001.
- **Revisit when.** Partial reversals, of part of an amount, are needed.
