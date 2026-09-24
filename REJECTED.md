# Rejected

The acceptance criteria this ledger refuses, with the reasoning, followed by approaches abandoned along the way. Each
refusal cites the entry in [AMBIGUITIES](AMBIGUITIES.md) that decided it; the two criteria not listed here, C1 and C3,
are accepted, as [MOVEMENT](MOVEMENT.md) states beside each.

## Refused Criteria

### C2 — Exactly one fee from E7, on Day 2

> E7 causes exactly one overdraft fee to be assessed, on Day 2.

Refused on both counts (AMB-002, AMB-003). The fee is assessed "once per day per account when that day's closing ledger
balance … is negative", and a closing sums every event value-dated on or before its day, so E7's −620.00, value-dated
Day 2, reaches every later closing: Day 2 falls to −370.00, Day 3 recovers to +30.00 with E4, and Days 4 and 5 fall to
−335.00 once E5 and E6 settle. All three negative days are E7's doing, so E7 causes three fees, not one. Each is fired
at the close of Day 5, when E7 arrives, and value-dated Day 5, labelled for the day it is for (`FEE-001-D2@D5`,
`FEE-001-D4@D5`, `FEE-001-D5@D5`); none is dated Day 2, because a day already closed is never rewritten. Even with E6
rejected, Day 4 would close at −155.00, so no reading of the stream gives exactly one fee.
`test_c2_e7_causes_three_fees_all_value_dated_day_5` asserts the three.

### C4 — Rejecting a settlement with an unknown authorization

> Any settlement referencing an authorization ID not present in the ledger must be rejected and the funds must not leave
> the account.

Refused (AMB-012, AMB-029). E6 settles AED 180.00 against Auth-Z, which the ledger has never seen, and is honoured as a
force-post: it debits 180.00, releases no hold, and Day 4 closes at 285.00. A settlement without a prior authorization
is routine in production, as with a card taken offline on a flight and presented after landing, and by the time it
reaches the bank the card network has already paid the merchant, so refusing to post it keeps no funds in the account;
it only makes the ledger disagree with the money that moved. A settlement that should not have been paid is disputed
through a chargeback, outside the ledger core. "Any" also contradicts the ledger's other rules: a settlement against a
declined or already-settled authorization (AMB-029) and one above its hold (AMB-030) are posted too. The cost is
accepted: a customer can be debited for a payment the ledger never approved. `test_c4_e6_is_force_posted_for_180`
asserts that E6 debits 180.00.

### C5 — An approved Auth-B hold

> If Auth-B is approved, its hold reduces available balance but not ledger balance.

Refused as a claim about this stream (AMB-021). Auth-B is never approved: E7, booked on Day 5 and value-dated Day 2,
lands before E8, so Auth-B would leave an available balance of 285.00 − 620.00 − 90.00 = −425.00 and is declined. The
criterion describes an event that does not happen, so it cannot be checked, and accepting it as vacuously true would
pass over that. The hold rule it states is the ledger's rule all the same, and it is tested with Auth-A: on Day 2 its
hold of 200.00 leaves the ledger balance at 250.00 and the available balance at 50.00. `test_c5_auth_b_is_declined`
asserts the decline, and `test_c5_a_hold_reduces_available_balance_but_not_ledger_balance` the rule on Auth-A.

### C6 — Everything returning to its pre-E7 value after E9

> After E9, all balances and fees return to their pre-E7 values.

Refused (AMB-004, AMB-005, AMB-024). After E9, Days 2, 3, and 4 close at 250.00, 650.00, and 285.00 again, and the fees
net to zero, but not everything returns. The three fees stay in the log, each undone by a refund event
(`REFUND-001-D2@D6`, `REFUND-001-D4@D6`, `REFUND-001-D5@D6`), because "No event record is ever mutated or deleted". The
refunds are value-dated Day 6, the day E9 is known, so Day 5 still closes at 210.00, with its fees in, where it would
have closed at 285.00 without E7. Day 5 therefore earns 210.00 × 0.0004 = 0.084 → 0.08 in interest, not 0.11, so ACC-001
capitalizes 0.76, not 0.79, and closes Day 6 at 285.76, not 285.79. Returning everything would mean deleting the fees or
dating the refunds into days already closed, and the ledger does neither.
`test_c6_e9_restores_days_2_to_4_and_refunds_the_fees` asserts the restored days and the refunds, and
`test_c6_day_6_closes_at_285_76_not_285_79` the closings of Days 5 and 6.

### C7 — Three instalments of BHD 3.334

> The three BHD instalments in E10 must each be BHD 3.334.

Refused (AMB-020). E10 credits BHD 10.000 "posted as three equal instalments", and BHD has three decimal places, so the
instalments cannot all be equal: 10.000 ÷ 3 = 3.3333…. Three instalments of 3.334 sum to 10.002, crediting ACC-002 with
0.002 BHD that was never sent. The ledger divides by three, rounds down, and adds the remainder to the last instalment,
so E10 posts 3.333, 3.333, and 3.334, which sum to exactly 10.000. `test_c7_e10_posts_3_333_3_333_3_334` asserts the
three amounts and their sum.

### C8 — Discarding a rounding remainder

> If the rounded daily interest accruals do not sum to the capitalized total, the remainder is discarded.

Refused (AMB-006, AMB-023). The brief's own constraint is that "The rounded daily accruals must sum exactly to the
capitalized total", so the criterion's premise is one the ledger must never reach, and it never does: each
capitalization is the sum of the rounded interest events in the log, 0.76 for ACC-001 and 0.008 for ACC-002, so no
remainder can exist. A remainder appears only when the total is taken from unrounded interest, as 0.802 → 0.80 against
rounded accruals of 0.79 would be without E7; discarding it would move money with no event to show where it went, so it
is a defect to prevent, not a rule to follow. As with C5, a criterion about an event that never happens is refused
rather than accepted as vacuously true. `test_c8_capitalization_equals_the_sum_of_interest_events` asserts that each
capitalization equals the sum of its interest events.

## Abandoned Approaches

### Gherkin acceptance tests

The criteria were first drafted as Gherkin in `ACCEPTANCE_CRITERIA.feature`, and the repository's scaffold bound its one
scenario at three test levels with pytest-bdd. Both are abandoned for plain pytest (AMB-026): every criterion has at
least one named test whose docstring quotes the brief, so step bindings would add a second language and a mapping layer
without adding a reader. The feature file was deleted once each criterion named its test.
