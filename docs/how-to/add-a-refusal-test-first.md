# Add a Refusal, Test First

Use this when the ledger must refuse a new kind of event, with its own reason on the Errors row. The steps are the ones
AMB-038, an authorization ID used twice, took in commit `c7aa953`; that commit is a complete example to read beside
them. Every behaviour here is written test-first, as the
[test-driven development](../../repo-governance/development/quality/testing/test-driven-development.md) rule requires:
the test fails before the code exists.

Run the `uv` and `pytest` commands from `apps/account-ledger-cli`, and the Nx commands from the repository root. On a
fresh clone, run `npm install` and then `npx nx run account-ledger-cli:install` once first: `uv run --no-sync` uses the
environment that target creates and never creates it.

## Steps

1. **Record the decision.** A new refusal is a reading of the brief, so it starts as an entry in
   [AMBIGUITIES](../../AMBIGUITIES.md), numbered after the last, with the six parts every entry has: where, why it is
   problematic, the options with one recommended, then the status, resolution, and rationale once the decision is made.
   The decision is the owner's, asked as one question with a recommendation.

2. **Write the failing test.** Put it beside the rule it tests: [`test_ledger.py`][test-ledger] for a check that spans
   accounts, [`test_account.py`][test-account] for one about one account. Name it for the entry and the behaviour, and
   build its stream from the builders in [`tests/support/streams.py`][streams]. AMB-038's first test:

   ```python
   def test_amb_038_an_authorization_id_already_used_is_refused() -> None:
       """AMB-038: an authorization ID names one hold, so a second Auth-A is refused and holds nothing, and the
       settlement for Auth-A settles the first alone."""

       second_authorization = make_authorization("E3", 1, "Auth-A", "50.00")

       stream = (
           make_credit("E1", 1, "500.00"),
           make_authorization("E2", 1, "Auth-A", "100.00"),
           second_authorization,
           make_settlement("E4", 2, "Auth-A", "100.00"),
       )

       result = unwrap_ok(IncomingStream(stream).process(CHALLENGE))

       assert list_entries(result.find_log(Day(1)), "E3") == [
           EventRejected(
               second_authorization, Day(1), AuthorizationIdReused(AuthorizationId("Auth-A"), IncomingId("E2"))
           )
       ]
       ...  # the test goes on to check Auth-A's state and its settlement
   ```

3. **Watch it fail.** Run the test alone:

   ```bash
   uv run --no-sync pytest tests/unit/domain/ledger/test_ledger.py -k amb_038 -q
   ```

   It must fail for the reason you expect: here, the name `AuthorizationIdReused` does not exist yet, so pytest reports
   `ERROR collecting tests/unit/domain/ledger/test_ledger.py` with an `ImportError`, not a `FAILED` test; once the class
   exists and the check does not, it fails as `FAILED` on the assertion. A test that passes before the code is written
   proves nothing.

4. **Add the reason.** In [`rejections.py`][rejections], add a frozen dataclass holding what the error text needs, and
   add it to the `Rejection` union:

   ```python
   @dataclass(frozen=True, slots=True)
   class AuthorizationIdReused:
       """The authorization's ID already names the hold of the authorization event given, on any account (AMB-038)."""

       authorization: AuthorizationId
       first_id: IncomingId
   ```

5. **Add the check.** A check across accounts goes in `Ledger.process_event` in [`ledger.py`][ledger], after the
   duplicate check and before the account decides; a check on one account goes in the account's decision, as a
   reversal's checks do in `AccountIn._check_reversal`. The check returns `Err(reason)`, and the caller records
   `EventRejected(event, today, reason)`, a success: the refusal is an entry in the log, not a failed run.

6. **Give it its sentence.** Run pyright; it now fails on `_format_reason` in [`text_report.py`][text-report], because
   its `match` has no case for the new reason and `assert_never` no longer type-checks. Add the case:

   ```python
   case AuthorizationIdReused(authorization=authorization, first_id=first_id):
       return f"{authorization.value} is already used by {first_id.format()}"
   ```

7. **Add it to the refusal table.** In [`tests/support/refusals.py`][refusals], add an entry to `REFUSALS`: a stream
   that meets the refusal, the account, the reason, and the text the Errors row prints. Two parametrized tests read the
   table, `test_amb_014_a_rejected_event_is_that_days_error` for the report and
   `test_amb_014_a_rejected_event_prints_its_refusal` for the text, so the new reason is covered in both without a new
   test.

8. **Run the gates.** The quick gate runs pyright, the linters, and the unit tests with their coverage floor; the other
   two run the real program:

   ```bash
   npx nx run account-ledger-cli:test:quick
   npx nx run account-ledger-cli:test:integration
   npx nx run account-ledger-cli:test:e2e
   ```

   The end-to-end golden test must still pass: a new refusal the brief's stream never meets changes nothing it prints.

9. **Update what names the refusals.** Finish the entry's resolution with the tests' names. Add the reason to the
   architecture's copy of the `Rejection` union and to the Ledger or aggregate paragraph in the
   [architecture](../../specs/apps/account-ledger/cli/architecture.md), and to [MOVEMENT](../../MOVEMENT.md) where a
   day's readings or a constraint names the entries that bear on it. Add a [WORKLOG](../../WORKLOG.md) row with the real
   times.

## Check Your Work

- The new test failed before step 4 and passes now.
- `grep -rn "AuthorizationIdReused" apps/account-ledger-cli/src` finds the class, the check, and the text.
- The AMB entry's tests, the architecture's union, and the code list the same reasons.

[test-ledger]: ../../apps/account-ledger-cli/tests/unit/domain/ledger/test_ledger.py
[test-account]: ../../apps/account-ledger-cli/tests/unit/domain/account/test_account.py
[streams]: ../../apps/account-ledger-cli/tests/support/streams.py
[rejections]: ../../apps/account-ledger-cli/src/account_ledger/domain/account/rejections.py
[ledger]: ../../apps/account-ledger-cli/src/account_ledger/domain/ledger/ledger.py
[text-report]: ../../apps/account-ledger-cli/src/account_ledger/adapters/text_report.py
[refusals]: ../../apps/account-ledger-cli/tests/support/refusals.py
