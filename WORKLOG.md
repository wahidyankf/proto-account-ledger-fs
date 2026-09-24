# Worklog

What was done, and when. Times are local (UTC+07:00). The newest entry comes first. Each entry is written when its work
happens, except the four oldest, at the bottom, which were reconstructed on 2026-09-24 at 14:48 from git commit times
and file creation times; no earlier work is claimed.

| When             | What                                                                                           |
| ---------------- | ---------------------------------------------------------------------------------------------- |
| 2026-09-24 21:59 | Refused C8: capitalization sums the rounded interest events, so no remainder exists            |
| 2026-09-24 21:58 | Refused C7: three instalments of 3.334 sum to 10.002; E10 posts 3.333, 3.333, 3.334            |
| 2026-09-24 21:57 | Refused C6: Day 5 stays 210.00 and interest 0.76, so Day 6 closes 285.76, not 285.79           |
| 2026-09-24 21:56 | Refused C4: E6 is honoured as a force-post; a bad settlement goes to chargeback                |
| 2026-09-24 21:55 | Accepted C3: Auth-A was approved on arrival, and E7 arriving later never reopens it            |
| 2026-09-24 21:54 | Refused C2: E7 causes three fees, for Days 2, 4, and 5, all value-dated Day 5                  |
| 2026-09-24 21:51 | Accepted C1: Day 2 closes at −370.00 at end of Day 5, before or after the fees                 |
| 2026-09-24 21:38 | Allowed strict xfail in every test target; TDD rule gains the design-weakness exception        |
| 2026-09-24 21:32 | Aligned the assessment docs with every resolution; no entry is worded as open any more         |
| 2026-09-24 21:27 | Listed WORKLOG newest first; new rows go on top, and no row is edited or removed               |
| 2026-09-24 21:25 | Opened each day in OUTPUT_TARGET with a banner between two full-width lines of =               |
| 2026-09-24 21:23 | Resolved AMB-033: three tables a day, drawn as plain-text boxes, beyond the four named items   |
| 2026-09-24 21:20 | Resolved AMB-032: NUMBERS lists given and chosen constants, each marked                        |
| 2026-09-24 21:18 | Resolved AMB-031: the failing test is a strict xfail in the regular suite; plan corrected      |
| 2026-09-24 21:13 | Resolved AMB-030: a settlement above its hold posts in full; excess goes to chargeback         |
| 2026-09-24 21:10 | Resolved AMB-029: a settlement with no active hold is a force-post, as E6 is                   |
| 2026-09-24 21:07 | Resolved AMB-034: the event ID is the idempotency key; same ID, different content, refused     |
| 2026-09-24 19:38 | Added AMB-034, open: an event whose ID arrives twice, for every kind of event                  |
| 2026-09-24 19:37 | Resolved AMB-028: a repeated reversal is idempotent; a conflicting one is refused              |
| 2026-09-24 19:33 | Resolved AMB-027: a BHD account pays BHD 2.560, AED 25.00 at 0.10238257, XE on 2026-09-24      |
| 2026-09-24 19:31 | Resolved AMB-026: the CLI prints the report; the test suite asserts every figure               |
| 2026-09-24 19:30 | Resolved AMB-025: every day lists both accounts and every known authorization                  |
| 2026-09-24 19:27 | Resolved AMB-023: fees, then interest, then capitalization; Day 6 closes 285.76 and 10.008     |
| 2026-09-24 19:20 | Resolved AMB-022: each day reports what it knew, plus earlier closings a late event restated   |
| 2026-09-24 19:17 | Resolved AMB-021: C5 refused as a claim about the stream; holds tested with Auth-A             |
| 2026-09-24 19:15 | Resolved AMB-019: a declined authorization is a state; errors read none every day              |
| 2026-09-24 19:10 | Resolved AMB-018: holds never expire, the weakness the failing test exposes                    |
| 2026-09-24 19:08 | Resolved AMB-017: all three E10 instalments value-dated Day 5; no schedule invented            |
| 2026-09-24 19:04 | Resolved AMB-015: listed order; E10 arrives late and is processed on Day 6                     |
| 2026-09-24 18:57 | Resolved AMB-014: refused events stay in the log with their outcome                            |
| 2026-09-24 18:54 | Resolved AMB-013: a final settlement releases the whole hold; unmarked means final             |
| 2026-09-24 18:50 | Recommended accepting AMB-029's settlements as force-posts, in line with AMB-012               |
| 2026-09-24 18:50 | Resolved AMB-012: E6 honoured as a force-post; Day 4 closes 285.00, interest 0.76              |
| 2026-09-24 18:38 | Resolved AMB-011: a fee counts toward later closings; one fee a day while negative             |
| 2026-09-24 18:34 | Resolved AMB-010: a hold reduces available balance from its value date                         |
| 2026-09-24 18:32 | Resolved AMB-009: an authorization is decided on arrival, against what preceded it             |
| 2026-09-24 17:39 | Resolved AMB-008: authorizations read the balance value-dated up to today                      |
| 2026-09-24 17:35 | Resolved AMB-007: no compounding; accruals join the balance only at capitalization             |
| 2026-09-24 17:34 | Resolved AMB-020: divide by N, round down, remainder on the last; E10 is 3.333/3.333/3.334     |
| 2026-09-24 17:34 | Resolved AMB-006: every amount rounds half-even; no figure in the stream moves                 |
| 2026-09-24 17:29 | Named fired events by kind, account, and days; realigned every doc to the event log            |
| 2026-09-24 17:29 | Resolved AMB-016 and AMB-024: fees fire at day close; the ledger is event-sourced              |
| 2026-09-24 17:29 | Resolved AMB-005: interest fired as known each day, corrected by adjusting events              |
| 2026-09-24 17:19 | Resolved AMB-004: event-sourced log; fees refunded by new events dated Day 6                   |
| 2026-09-24 17:06 | Resolved AMB-003: a retroactive fee is dated the day the check runs; Days 2 and 3 now fixed    |
| 2026-09-24 16:58 | Resolved AMB-002: every negative day since the value date is charged, each fee naming its day  |
| 2026-09-24 16:45 | Resolved AMB-001: integer days 1 to 6, each closing; Day 0 is the opening state                |
| 2026-09-24 16:15 | Gave every ambiguity where, why, options, status, and blank resolution and rationale           |
| 2026-09-24 16:09 | OUTPUT_TARGET prints the three MOVEMENT blocks per day; AMB-033 widened to match               |
| 2026-09-24 16:08 | MOVEMENT no longer states the open EOD order or accrual status as settled                      |
| 2026-09-24 16:05 | Moved fees, reversals, and capitalization out of the closing summary into EOD applied          |
| 2026-09-24 16:04 | Gave every MOVEMENT day three tables: events processed, EOD applied, and closing summary       |
| 2026-09-24 15:57 | Renumbered ambiguities by first appearance in MOVEMENT; earlier entries keep the old numbers   |
| 2026-09-24 15:53 | Listed the entries the ledger generates and each day's interest accrual in MOVEMENT            |
| 2026-09-24 15:49 | Day 0 now reports a closing ledger balance, in the same shape as every other day               |
| 2026-09-24 15:48 | Full rows for Day 0; restated closings on Days 5 and 6; AMB-011 and AMB-020 keyed on available |
| 2026-09-24 15:43 | Added Day 0, the opening state, to MOVEMENT and OUTPUT_TARGET; noted it under AMB-032          |
| 2026-09-24 15:37 | Added the assessment-docs convention; aligned NUMBERS, AMBIGUITIES, and the feature to it      |
| 2026-09-24 15:37 | Renamed OUTPUT-TARGET to MOVEMENT; added OUTPUT_TARGET, the exact printed text, and AMB-033    |
| 2026-09-24 15:27 | Drafted ACCEPTANCE_CRITERIA.feature (C1–C8, unexecuted) and linked it                          |
| 2026-09-24 15:23 | Renamed ambiguity IDs to AMB-001 to AMB-032; tagged constraints and criteria in OUTPUT-TARGET  |
| 2026-09-24 15:21 | Added the brief's constraints and acceptance criteria to OUTPUT-TARGET, quoted                 |
| 2026-09-24 15:18 | Gave each day in OUTPUT-TARGET an events table with booked and value dates                     |
| 2026-09-24 15:17 | Listed the events processed on each day in OUTPUT-TARGET                                       |
| 2026-09-24 15:15 | Added OUTPUT-TARGET: events and per-day target output, open figures marked pending             |
| 2026-09-24 15:12 | Limited Markdown outside rules and harness to 120 columns; fixed two wide tables               |
| 2026-09-24 14:59 | Re-read the brief line by line; added twelve missed ambiguities (A21–A32)                      |
| 2026-09-24 14:56 | Emptied REJECTED and reopened every ambiguity for a one-by-one review                          |
| 2026-09-24 14:48 | Moved the deliverables to the root; the plan keeps only a README                               |
| 2026-09-24 14:45 | Drafted AMBIGUITIES, NUMBERS, and REJECTED from a scratch replay                               |
| 2026-09-24 14:41 | Saved the challenge brief verbatim as `challenge-raw.md`                                       |
| 2026-09-24 14:15 | Started the ledger plan; read the planning, testing, and Python rules                          |
| 2026-09-24 13:56 | Capped pytest below 9.1 to silence pytest-bdd warnings (7228418)                               |
