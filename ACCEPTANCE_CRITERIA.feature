Feature: Acceptance criteria from the challenge brief
  The eight acceptance criteria the brief lists, restated as Gherkin in the brief's order and wording. The brief says
  some of them are wrong. A refused criterion is recorded in REJECTED.md; a scenario carries the verdict-rejected tag
  once its criterion is refused there, the verdict-accepted tag once it is accepted, and the verdict-open tag until
  either, and asserts only what the brief asserts. The ambiguities each scenario depends on are named above it.

  This file is a draft and is not executed. It moves under specs/ once every verdict is decided, and each scenario is
  then rewritten to state the behaviour the ledger actually adopts.

  Background:
    Given account "ACC-001" in AED with an opening balance of 0.00
    And account "ACC-002" in BHD with an opening balance of 0.000
    And the event stream E1 to E10 from the brief

  # Ambiguities: AMB-016, AMB-022
  @C1 @verdict-accepted
  Scenario: C1 - Day 2 closing ledger balance, evaluated at end of Day 5 before any fee
    When the stream is replayed through the end of Day 5
    Then the Day 2 closing ledger balance of "ACC-001", before any fee is assessed, is AED -370.00

  # Ambiguities: AMB-002, AMB-003, AMB-016
  @C2 @verdict-rejected
  Scenario: C2 - E7 causes exactly one overdraft fee, on Day 2
    When the stream is replayed through the end of Day 5
    Then exactly one overdraft fee caused by E7 is assessed on "ACC-001"
    And that fee is assessed on Day 2

  # Ambiguities: AMB-013
  @C3 @verdict-accepted
  Scenario: C3 - the Day 4 settlement of Auth-A is accepted
    When the stream is replayed through E5
    Then the settlement of "Auth-A" for AED 185.00 is accepted

  # Ambiguities: AMB-012, AMB-029
  @C4 @verdict-rejected
  Scenario: C4 - a settlement with an authorization ID not in the ledger is rejected
    When the stream is replayed through E6
    Then the settlement referencing "Auth-Z" is rejected
    And no funds leave "ACC-001" because of it

  # Ambiguities: AMB-021
  @C5 @verdict-rejected
  Scenario: C5 - an approved Auth-B hold reduces available balance but not ledger balance
    Given the authorization "Auth-B" for AED 90.00 is approved
    Then the available balance of "ACC-001" falls by AED 90.00
    And the ledger balance of "ACC-001" does not change

  # Ambiguities: AMB-004, AMB-005
  @C6 @verdict-rejected
  Scenario: C6 - after E9, balances and fees return to their pre-E7 values
    When the stream is replayed through E9
    Then every balance returns to its value before E7
    And every fee returns to its value before E7

  # Ambiguities: AMB-020
  @C7 @verdict-rejected
  Scenario: C7 - each of the three BHD instalments in E10 is BHD 3.334
    When the stream is replayed through E10
    Then "ACC-002" is credited in three instalments
    And each instalment is BHD 3.334

  # Ambiguities: AMB-006, AMB-023
  @C8 @verdict-rejected
  Scenario: C8 - a remainder between rounded accruals and the capitalized total is discarded
    Given the rounded daily interest accruals do not sum to the capitalized total
    When interest capitalizes at the end of Day 6
    Then the remainder is discarded
