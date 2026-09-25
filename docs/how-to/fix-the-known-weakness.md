# Fix the Known Weakness

Use this to see the deliberately failing test fail, and to walk through the fix a reviewer may ask for: holds that
expire. The brief asks for "One failing test against your own design, inline-annotated with what it reveals"; this
repository's is `test_known_weakness_an_unsettled_hold_never_expires`, and the weakness it reveals is
[AMB-018](../../AMBIGUITIES.md#amb-018--how-long-a-hold-lives): a hold never expires.

The fix below was built and run on a scratch copy of the application, and every gate passed on it. It is not in the
repository, and must not be: once the weakness is fixed, the brief's failing test is gone. Make the change on a copy, as
in step 2.

Run the `uv` and `pytest` commands from the folder named in each step.

## What the Test Shows

The test approves Auth-A for AED 200.00 on Day 1 against a credit of 1,000.00, never settles it, and runs the ledger
through Day 32. Visa's longest authorization-to-clearing time frame is 30 calendar days, so Day 31 is the thirtieth day
after Auth-A and Day 32 the first on which no network would still honour it
([hold time frame](../../NUMBERS.md#hold-time-frame), [known-weakness run](../../NUMBERS.md#known-weakness-run)). The
test asserts that on Day 32 the available balance equals the closing, which it would if the hold had lapsed:

```text
Day      1         6              31        32
         |---------|---------------|---------|
Auth-A   approved, hold 200.00 ------------------------------> still held, forever
closing  1,000.00  1,002.40 (interest capitalized on Day 6) --> 1,002.40
available  800.00    802.40 ---------------------------------->   802.40   the test expects 1,002.40
```

It is marked `@pytest.mark.xfail(strict=True, reason=…)`
([AMB-031](../../AMBIGUITIES.md#amb-031--how-a-deliberately-failing-test-coexists-with-a-runnable-suite)), so it runs on
every push and its failure is expected:

```text
            the test's assertion
            fails          passes
          +--------------+-------------------------------------------+
  marker  | XFAIL        | XPASS(strict): reported as FAILED,        |
  on      | run green    | run red until the marker is removed       |
          +--------------+-------------------------------------------+
  marker  | FAILED       | PASSED                                    |
  off     | run red      | run green                                 |
          +--------------+-------------------------------------------+
```

Strict is what keeps the marker honest: a fix cannot go unnoticed, and the guard in each test target refuses
`strict=False`.

## Steps

1. **See it fail.** From `apps/account-ledger-cli`:

   ```bash
   uv run --no-sync pytest tests/unit/application/test_stream.py -k known_weakness -q
   ```

   ```text
   XFAIL tests/unit/application/test_stream.py::test_known_weakness_an_unsettled_hold_never_expires - AMB-018: holds
   never expire, so an unsettled hold is never released
   14 deselected, 1 xfailed in 0.09s
   ```

   To see the assertion itself fail, add `--runxfail`, which runs the test as if it had no marker:

   ```bash
   uv run --no-sync pytest tests/unit/application/test_stream.py -k known_weakness -q --runxfail
   ```

   ```text
   E       AssertionError: assert Aed(value=Decimal('802.40')) == Aed(value=Decimal('1002.40'))
   ```

   802.40 is the available balance, 1,002.40 less Auth-A's 200.00; 1,002.40 is the closing, the credit plus six days of
   0.40 interest capitalized on Day 6. Interest after Day 6 still accrues, 0.40 a day, but the configuration capitalizes
   on Day 6 only, so it never reaches the balance.

2. **Work on a copy.** Go back to the repository root with `cd ../..`, then copy the application into the gitignored
   `local-tmp/` and give the copy its own environment:

   ```bash
   mkdir -p local-tmp/fix-proto
   rsync -a --exclude .venv --exclude .ruff_cache --exclude __pycache__ apps/account-ledger-cli/ local-tmp/fix-proto/
   cd local-tmp/fix-proto
   uv sync --locked
   ```

   The remaining steps run inside `local-tmp/fix-proto`.

3. **Add the state.** An authorization gains a fifth state. In `src/account_ledger/domain/account/authorizations.py`,
   add the lifetime, the state, and the state to the union:

   ```python
   HOLD_LIFETIME_DAYS = 30  # Visa's longest authorization-to-clearing time frame, in days (NUMBERS, AMB-018)


   @dataclass(frozen=True, slots=True)
   class Expired:
       """Left unsettled past the hold lifetime, so the close released its hold (AMB-018); it holds nothing more."""

       released: Amount


   type AuthorizationState = Approved | PartiallySettled | Declined | Settled | Expired
   ```

   The state machine becomes:

   ```text
                     +-- settlement, final or reaching the hold --> Settled
                     |
   Approved ---------+-- settlement, partial ----------------+
      |                                                      v
      |                                              PartiallySettled --+-- final or reaching --> Settled
      |                                                      |          |
      |                                                      |          +-- partial --> PartiallySettled
      |                                                      |
      +-- close, more than 30 days after its value date -----+--------> Expired
                                                                         |
   Declined, Settled, Expired -- any settlement: no transition, so the settlement is force-posted
   ```

4. **Let pyright list the matches.** Run it:

   ```bash
   uv run --no-sync pyright
   ```

   Every `match` on `AuthorizationState` that ends in `assert_never` now fails, which is the list of places the new
   state must reach: `apply_settlement` and `_take_from_hold` in `authorizations.py`, `AccountIn.sum_holds` in
   `account.py`, and `_format_state` in the text report. Give `Expired` the same answer as `Settled`: in
   `apply_settlement`, no transition, so a clearing after expiry is force-posted, as the
   [trade-offs](../explanation/architecture-trade-offs.md#authorization-lifecycle) mandate; in `_take_from_hold`,
   nothing is held; and in `AccountIn.sum_holds`, it adds no hold:

   ```python
   case Settled() | Declined() | Expired(), _, _:
       return Err(CannotSettle())
   ```

   The last is `_format_state` in `src/account_ledger/adapters/text_report.py`, which needs its sentence:

   ```python
   case Expired(released=amount):
       return f"{hold} expired, released {_format_amount(amount.money)}"
   ```

5. **Record the expiry as an entry.** The log is the only state, so an expiry is a new entry kind in `domain_events.py`,
   added to the `LogEntry` union:

   ```python
   @dataclass(frozen=True, slots=True)
   class HoldExpired:
       """An authorization's hold released at a close, once left unsettled past the hold lifetime (AMB-018)."""

       event: Authorization
       processed_day: Day
   ```

   `AccountIn.list_records` reads it into the record's state. Give `AuthorizationRecord` in `authorizations.py` a method
   that moves a kept hold to `Expired`, and call it from the new case:

   ```python
   def apply_expiry(self) -> AuthorizationRecord:
       """This record with its hold released, from a state that still keeps one (AMB-018)."""

       match self.state:
           case Approved(hold=hold) | PartiallySettled(hold=hold):
               return AuthorizationRecord(self.authorization, Expired(hold))
           case Settled() | Declined() | Expired():
               return self
           case _:
               assert_never(self.state)
   ```

   ```python
   case HoldExpired(event=event):
       records = [record.apply_expiry() if record.authorization == event else record for record in records]
   ```

   Add `HoldExpired()` to the entries `_list_counted_events` passes over, beside `AuthorizationApproved()`: an expiry
   moves no ledger balance.

6. **Generate it at the close.** In `account.py`, a method finds every hold still kept more than the lifetime after its
   value date:

   ```python
   def generate_hold_expiries(self, today: Day) -> Result[tuple[LogEntry, ...], CurrencyMismatch]:
       """An expiry for every hold still kept more than the hold lifetime after its value date (AMB-018)."""

       return Ok(
           tuple(
               HoldExpired(record.authorization, today)
               for record in self.list_records()
               if isinstance(record.state, Approved | PartiallySettled)
               and today.number - record.authorization.value_date.number > HOLD_LIFETIME_DAYS
           )
       )
   ```

   `Ledger.close_day` in `ledger.py` runs it as the first step, before fees. An expiry moves the available balance only,
   and a fee reads the closing, so the order changes no figure:

   ```python
   steps: list[_Step] = [
       lambda account: account.generate_hold_expiries(today),
       lambda account: account.assess_fees(today, self.config.first_day),
       lambda account: account.accrue_interest(today, self.config.first_day),
   ]
   ```

   With "more than 30", Auth-A approved on Day 1 expires at the close of Day 32 and is still held on Day 31, the
   thirtieth day after it.

7. **Watch the marker catch the fix.** Run the unit tests:

   ```bash
   uv run --no-sync pytest tests/unit -q
   ```

   ```text
   [XPASS(strict)] AMB-018: holds never expire, so an unsettled hold is never released
   FAILED tests/unit/application/test_stream.py::test_known_weakness_an_unsettled_hold_never_expires
   1 failed, 160 passed
   ```

   The test now passes, and strict mode turns that into a failure: this is the moment AMB-031 was designed for.

8. **Turn the test into a passing one, and pin the edges.** In `tests/unit/application/test_stream.py`, remove the
   `KNOWN WEAKNESS` comment and the marker, rename the test for what it now proves, and remove `import pytest` if
   nothing else uses it; pyright reports it unused. Add a test for each edge the fix introduced:

   ```python
   def test_amb_018_an_unsettled_hold_expires_after_its_lifetime() -> None:
       """AMB-018: Auth-A, never settled, lapses by Day 32, the first day after its thirty, so its hold no longer
       reduces the available balance."""

       processed = unwrap_ok(IncomingStream(build_unsettled_auth_a()).process(replace(CHALLENGE, last_day=Day(32))))
       day_32 = processed.find_report(Day(32))

       assert day_32.available_balances[ACC_001_OPENING.id] == day_32.closing_balances[ACC_001_OPENING.id]


   def test_amb_018_a_hold_is_kept_through_its_thirtieth_day() -> None:
       """AMB-018: on Day 31, the thirtieth day after Auth-A, a network may still clear it, so its hold is kept."""

       log = unwrap_ok(IncomingStream(build_unsettled_auth_a()).process(replace(CHALLENGE, last_day=Day(31)))).find_log(
           Day(31)
       )

       assert unwrap_ok(Ledger(CHALLENGE, log).find_account(ACC_001_OPENING).sum_holds(Day(31))) == make_aed("200.00")


   def test_amb_018_a_settlement_after_expiry_is_force_posted() -> None:
       """AMB-018: a clearing that arrives after its hold expired is force-posted: it debits its amount and releases
       nothing, since nothing is held."""

       settlement = make_settlement("E3", 33, "Auth-A", "200.00")
       stream = (*build_unsettled_auth_a(), settlement)
       log = unwrap_ok(IncomingStream(stream).process(replace(CHALLENGE, last_day=Day(33)))).find_log(Day(33))

       assert list_states(log, "Auth-A") == [Expired(AmountIn(make_aed("200.00")))]
       assert list_settlements(log, "E3") == [SettlementForcePosted(settlement, Day(33))]
   ```

   Import `Expired` beside `Approved` and `make_settlement` from `support.streams`.

9. **Read the report, not only the tests.** Every test passes at this point, yet the printed report has a fault: on Day
   32, E2 appears again under Events processed, because `HoldExpired` carries the authorization and the report takes any
   entry whose event is an incoming kind for an incoming event. Write the test first, in
   `tests/unit/application/test_report.py`:

   ```python
   def test_amb_018_an_expiry_is_not_listed_as_an_event_processed() -> None:
       """AMB-018: the ledger generates a hold's expiry at a close, so the day it expires lists no incoming event."""

       processed = unwrap_ok(IncomingStream(build_unsettled_auth_a()).process(replace(CHALLENGE, last_day=Day(32))))

       assert processed.find_report(Day(32)).processed_events == ()
   ```

   Import `replace` from `dataclasses` and `build_unsettled_auth_a` from `support.streams`. The test fails. Then, in
   `_select_incoming_event` in `src/account_ledger/application/report.py`:

   ```python
   if isinstance(entry, HoldExpired):
       return None  # an expiry names the authorization it releases, but the close generated it (AMB-018)
   ```

   Day 32's Closing summary then prints `Auth-A expired, released 200.00`, with the available balance equal to the
   closing, 1,002.40.

10. **Run every gate.** The names a method may start with are a fixed list of verbs, which pylint enforces: `expire`
    fails it, `apply_expiry` and `generate_hold_expiries` pass.

    ```bash
    uv run --no-sync ruff check .
    uv run --no-sync ruff format --check .
    uv run --no-sync pyright
    uv run --no-sync pylint src tests
    uv run --no-sync vulture
    uv run --no-sync pytest tests -q --cov=account_ledger --cov-fail-under=80
    ```

    On the scratch copy these passed with 173 tests and 95.32% coverage. The end-to-end golden test still passes: no
    hold in the brief's stream lives past Day 6, so no figure the brief fixes moves.

## What Else a Real Fix Would Change

Were the weakness fixed in the repository, every document that names it would change with it, and the brief would lose
its one failing test, so a new weakness would need its own test:

- [AMB-018](../../AMBIGUITIES.md#amb-018--how-long-a-hold-lives)'s resolution, from no expiry to a lifetime of 30 days,
  [AMB-031](../../AMBIGUITIES.md#amb-031--how-a-deliberately-failing-test-coexists-with-a-runnable-suite)'s, and
  [NUMBERS](../../NUMBERS.md#hold-time-frame)' hold time frame and known-weakness run, where the time frame would become
  the ledger's own constant.
- The application README's [known weakness](../../apps/account-ledger-cli/README.md#known-weakness), and the
  [architecture](../../specs/apps/account-ledger/cli/architecture.md)'s `AuthorizationState` union, its state diagram,
  and its "Holds never expire" line.
- The [trade-offs](../explanation/architecture-trade-offs.md#authorization-lifecycle): the lifecycle's "never settled"
  row and its mandate, which say the failing test records the gap, and the cut table's "a hold lifetime" row. The PDF
  printed from it would be rebuilt.
- In this folder, the [code walkthrough](../explanation/code-walkthrough.md#where-a-change-would-go), the
  [defense index](../reference/defense-index.md), the [glossary](../reference/glossary.md), and the
  [tutorial](../tutorials/change-the-stream-and-watch.md)'s partial-settlement step.
- The report's EOD applied table: this fix records the expiry in the Authorizations row only, and a fuller one would
  give it a step row of its own.
- One lifetime for every hold is the scratch fix's simplification: the
  [trade-offs](../explanation/architecture-trade-offs.md#authorization-lifecycle) mandate an expiry "after the network's
  time frame for the merchant category", with 30 calendar days as Visa's longest.

## Check Your Work

- In the repository, `test_known_weakness_an_unsettled_hold_never_expires` is still `1 xfailed`.
- On the copy, the old test's `XPASS(strict)` appeared before its marker was removed.
- On the copy, Day 31 still holds 200.00, Day 32 releases it, and a settlement on Day 33 is force-posted.
- Remove the copy when done: `rm -r local-tmp/fix-proto`.
