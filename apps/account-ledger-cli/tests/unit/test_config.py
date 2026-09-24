"""The configuration refuses a window, account list, or capitalization day no ledger can run."""

from dataclasses import replace

import pytest

from account_ledger.config import CHALLENGE, Account, ConfigFault, LedgerConfig
from account_ledger.ids import AccountId, Day
from support.values import aed, bhd

ACC_001 = Account(AccountId("ACC-001"), aed("0.00"))


def test_ledger_config_refuses_an_inverted_window() -> None:
    assert LedgerConfig.of((ACC_001,), Day(6), Day(1), frozenset()) == ConfigFault(
        "the first day 6 is after the last 1"
    )
    assert LedgerConfig.of((ACC_001, ACC_001), Day(1), Day(6), frozenset()) == ConfigFault(
        "ACC-001 is configured twice"
    )
    assert LedgerConfig.of((ACC_001,), Day(1), Day(6), frozenset({Day(7)})) == ConfigFault(
        "capitalization day 7 is outside the window 1 to 6"
    )
    with pytest.raises(ValueError, match="the first day 1 is after the last 0"):
        replace(CHALLENGE, last_day=Day(0))
    assert CHALLENGE.accounts == (ACC_001, Account(AccountId("ACC-002"), bhd("0.000")))
    assert (CHALLENGE.first_day, CHALLENGE.last_day, CHALLENGE.capitalization_days) == (Day(1), Day(6), {Day(6)})
