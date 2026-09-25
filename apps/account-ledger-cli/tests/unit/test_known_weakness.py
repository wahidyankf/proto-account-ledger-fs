"""The brief's one failing test against this design, inline-annotated with what it reveals (AMB-018, AMB-031, D6)."""

from dataclasses import replace

import pytest

from account_ledger.domain.model.config import CHALLENGE
from account_ledger.domain.model.ids import Day
from account_ledger.domain.stream_processing import process_stream
from support.results import unwrap_ok
from support.streams import ACC_001, build_unsettled_auth_a


# KNOWN WEAKNESS (AMB-018): a hold never expires.
# What it reveals: an approved authorization that is never settled keeps its hold, and so keeps reducing the
# available balance, for as long as the ledger runs. Visa's longest authorization-to-clearing time frame is 30
# calendar days (Visa Business News AI13522, effective 13 April 2024), so by Day 32 no network would still honour
# Auth-A, yet this ledger still reserves its AED 200.00.
# The fix: a hold lifetime after which the end of day fires a hold-expiry event that releases the hold.
@pytest.mark.xfail(strict=True, reason="AMB-018: holds never expire, so an unsettled hold is never released")
def test_known_weakness_an_unsettled_hold_never_lapses() -> None:
    """AMB-018: Auth-A, never settled, should lapse by Day 32, but its hold still reduces the available balance."""
    processed = unwrap_ok(process_stream(build_unsettled_auth_a(), replace(CHALLENGE, last_day=Day(32))))
    day_32 = processed.find_report(Day(32))

    assert day_32.available_balances[ACC_001.id] == day_32.closing_balances[ACC_001.id]
