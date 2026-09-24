# Rejected

The acceptance criteria this ledger refuses, with the reasoning, followed by approaches abandoned along the way. Each
refusal cites the entry in [AMBIGUITIES](AMBIGUITIES.md) that decided it; a criterion not listed here is still under
review.

## Refused Criteria

### C5 — An approved Auth-B hold

> If Auth-B is approved, its hold reduces available balance but not ledger balance.

Refused as a claim about this stream (AMB-021). Auth-B is never approved: E7, booked on Day 5 and value-dated Day 2,
lands before E8, so Auth-B would leave an available balance of 285.00 − 620.00 − 90.00 = −425.00 and is declined. The
criterion describes an event that does not happen, so it cannot be checked, and accepting it as vacuously true would
pass over that. The hold rule it states is the ledger's rule all the same, and it is tested with Auth-A: on Day 2 its
hold of 200.00 leaves the ledger balance at 250.00 and the available balance at 50.00.

## Abandoned Approaches

None yet.
