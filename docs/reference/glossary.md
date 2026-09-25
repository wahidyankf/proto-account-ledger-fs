# Glossary

The terms this repository uses, each with a one-line meaning and the document that owns it. A meaning here is a pointer,
not a rule: the owning document states the rule, and where the two seem to differ, the owner is right.

## The Ledger's Terms

- **day, Day 0, window**: an integer with no calendar; Day 0 is the opening, and the window is Days 1 to 6.
  [AMB-001][amb-001].
- **booked day**: the day the bank recorded the event; every open day before it closes before the event is processed.
  [AMB-015][amb-015].
- **value date**: the day an event's money counts from; every balance is summed by value date. [AMB-002][amb-002].
- **backdated event**: an event whose value date is earlier than the day it is processed, such as E7, E9, and E10. [Fees
  and interest][fees-dates].
- **late event**: an event booked on a day that has already closed; processed on the open day, as E10 is.
  [AMB-015][amb-015].
- **listed order**: the order of rows in the stream, the order events are processed in. [AMB-015][amb-015].
- **closing balance**: the ledger balance at a day's end: the opening plus every effect value-dated that day or before.
  [AMB-024][amb-024].
- **available balance**: the closing less the holds; what an authorization is checked against. [AMB-008][amb-008].
- **hold**: the amount an approved authorization reserves, from its value date until released. [AMB-010][amb-010].
- **authorization state**: approved, declined, partially settled, or settled. [AMB-019][amb-019].
- **decline**: an authorization state, decided on arrival and final; not an error. [AMB-009][amb-009].
- **final flag**: a settlement's mark of whether more settlements follow; with none, the settlement is final.
  [AMB-013][amb-013].
- **force-post**: a settlement with no transition to apply: it debits its amount and releases no hold.
  [AMB-012][amb-012].
- **reversal**: an event that undoes what its target moved, from the reversal's own value date. [AMB-035][amb-035].
- **duplicate**: an event repeating an ID with the same content; recorded, with no effect. [AMB-034][amb-034].
- **refusal, rejection**: an event the ledger will not carry out; recorded with its reason and printed as an error.
  [AMB-014][amb-014].
- **overdraft fee**: AED 25.00, or BHD 2.560, for each day whose closing is below zero, at most one a day.
  [AMB-002][amb-002].
- **fee in force, refund**: a fee not yet refunded; a refund cancels it once its day closes at or above zero again.
  [AMB-004][amb-004].
- **interest accrual**: a day's interest, generated at that day's close on its closing as then known.
  [AMB-005][amb-005].
- **interest adjustment**: a correction of an earlier day's interest, generated when its closing changes.
  [AMB-005][amb-005].
- **capitalization**: the sum of the rounded interest events, credited to the balance at the end of Day 6.
  [AMB-007][amb-007].
- **instalment**: one of the parts a credit in instalments posts, all with the credit's value date. [AMB-017][amb-017].
- **generated event**: an event the ledger makes itself: a fee, a refund, interest, a capitalization, an instalment.
  [architecture][domain].
- **end of day, close**: fees, then interest, then capitalization on Day 6 only. [AMB-023][amb-023].
- **point-in-time report**: each day's report shows what was known at its close; a later day restates what changed.
  [AMB-022][amb-022].
- **restated**: a row in a day's report giving an earlier day's closing, changed by a backdated event.
  [AMB-022][amb-022].
- **append-only**: one log of immutable entries; nothing is changed or removed, and balances are worked out.
  [AMB-024][amb-024].
- **known weakness**: holds never expire; the deliberately failing test records it. [AMB-018][amb-018].

## The Code's Terms

- `Ledger`: every configured account and the one log they share; checks what spans accounts, and closes a day.
  [walkthrough][walk-event].
- **aggregate**, `AccountIn`: one account and its own entries, answering every rule about the account as a method.
  [architecture][domain].
- **log**, `LogEntry`: the append-only entries, one kind per fact recorded, such as `FeeCharged` or `EventRejected`.
  [architecture][domain].
- **event and entry**: an event is what happened, such as a `Debit` or a `Fee`, from the stream or generated; an entry
  is the log's record of it, such as `DebitPosted` or `FeeCharged`, holding the event with the day it was processed and,
  where it has them, a refusal's reason or a settlement's states. [Code walkthrough][walk-event].
- **D, R, and S numbers**: decision records of the two delivered plans: S and D in [the first build's][first-plan], R in
  [the restructure's][restructure-plan]. The code's docstrings cite them, such as `(D8)` or `(S3)`, and the first plan's
  design documents, such as "tech-docs 003", its `tech-docs/003-input-output-and-cli.md`.
- **port**: a `Protocol` at the application's edge: `EventSource` and `ReportSink`, which it drives, and `RunLedger`,
  which drives it. [architecture][l3].
- **adapter**: a port's implementation at the edge: the CSV reader and the text report. [architecture][l3].
- `Result`, `Ok`, `Err`: a return value that is a success or an expected failure, in place of an exception. [crash
  course][result].
- `Rejection`: the union of every refusal reason, one frozen dataclass each. [walkthrough][walk-event].
- `EventRejected`: the log entry of a refusal; returned as `Ok`, since a refusal is an outcome, not a failure.
  [walkthrough][rules].
- `SourceFault`: a stream that cannot be read or a row that cannot be an event; the run stops with status 2.
  [walkthrough][faults].
- `InternalFault`: a currency mismatch or an unknown account, which only a bug brings; status 2. [walkthrough][faults].
- `M: (Aed, Bhd)`: the type parameter that makes each account one currency, so pyright refuses mixing them. [crash
  course][generics].
- **strict xfail**: an expected failure whose unexpected pass fails the run; the known weakness's marker.
  [AMB-031][amb-031].
- **golden test**: `test_the_brief_stream_prints_output_target`: the CLI's output against OUTPUT_TARGET.
  [OUTPUT_TARGET][target].

[amb-001]: ../../AMBIGUITIES.md#amb-001--what-a-day-is
[amb-002]: ../../AMBIGUITIES.md#amb-002--which-days-a-backdated-event-makes-liable-for-an-overdraft-fee
[amb-004]: ../../AMBIGUITIES.md#amb-004--what-happens-to-fees-once-e9-reverses-e7
[amb-005]: ../../AMBIGUITIES.md#amb-005--which-balance-daily-interest-accrues-on
[amb-007]: ../../AMBIGUITIES.md#amb-007--whether-daily-interest-compounds-before-capitalization
[amb-008]: ../../AMBIGUITIES.md#amb-008--the-ledger-balance-an-authorization-is-checked-against
[amb-009]: ../../AMBIGUITIES.md#amb-009--when-an-authorization-is-decided
[amb-010]: ../../AMBIGUITIES.md#amb-010--what-a-value-date-means-on-an-authorization
[amb-012]: ../../AMBIGUITIES.md#amb-012--settlements-with-no-authorization-in-production
[amb-013]: ../../AMBIGUITIES.md#amb-013--a-settlement-smaller-than-its-hold
[amb-014]: ../../AMBIGUITIES.md#amb-014--whether-rejected-and-declined-events-are-recorded
[amb-015]: ../../AMBIGUITIES.md#amb-015--processing-order-when-booked-days-are-out-of-sequence
[amb-017]: ../../AMBIGUITIES.md#amb-017--whether-the-e10-instalments-are-spread-over-days
[amb-018]: ../../AMBIGUITIES.md#amb-018--how-long-a-hold-lives
[amb-019]: ../../AMBIGUITIES.md#amb-019--whether-a-declined-authorization-is-an-authorization-state-or-an-error
[amb-022]: ../../AMBIGUITIES.md#amb-022--what-a-days-report-shows-once-backdated-events-exist
[amb-023]: ../../AMBIGUITIES.md#amb-023--end-of-day-ordering-and-the-day-6-capitalization
[amb-024]: ../../AMBIGUITIES.md#amb-024--what-append-only-covers
[amb-031]: ../../AMBIGUITIES.md#amb-031--how-a-deliberately-failing-test-coexists-with-a-runnable-suite
[amb-034]: ../../AMBIGUITIES.md#amb-034--an-event-whose-id-arrives-twice
[amb-035]: ../../AMBIGUITIES.md#amb-035--what-a-reversal-may-target
[fees-dates]: ../explanation/fees-and-interest.md#booked-day-and-value-date
[domain]: ../../specs/apps/account-ledger/cli/architecture.md#domain-model
[l3]: ../../specs/apps/account-ledger/cli/architecture.md#l3--components
[walk-event]: ../explanation/code-walkthrough.md#one-incoming-event
[rules]: ../explanation/code-walkthrough.md#three-rules-that-explain-the-code
[faults]: ../explanation/code-walkthrough.md#faults-and-exit-statuses
[result]: ../explanation/python-crash-course.md#result-instead-of-exceptions
[generics]: ../explanation/python-crash-course.md#generics
[target]: ../../OUTPUT_TARGET.md
[first-plan]: ../../plans/done/2026-09-25__in-memory-account-ledger-init/tech-docs/005-decision-records.md
[restructure-plan]: ../../plans/done/2026-09-25__restructure-around-the-domain/tech-docs/007-decision-records.md
