"""The configuration refuses a window, account list, or capitalization day no ledger can run."""

from dataclasses import replace

import pytest

from account_ledger.challenge import CHALLENGE
from account_ledger.common.result import Err, Ok
from account_ledger.domain.model.config import AccountOpeningIn, ConfigFault, LedgerConfig
from account_ledger.domain.model.ids import AccountId, Day
from support.values import make_aed, make_bhd

ACC_001 = AccountOpeningIn(AccountId("ACC-001"), make_aed("0.00"))


def test_ledger_config_refuses_an_inverted_window() -> None:
    """An inverted window, a repeated account, or a capitalization day outside the window is refused."""
    assert LedgerConfig.make((ACC_001,), Day(6), Day(1), frozenset()) == Err(
        ConfigFault("the first day 6 is after the last 1")
    )
    assert LedgerConfig.make((ACC_001, ACC_001), Day(1), Day(6), frozenset()) == Err(
        ConfigFault("ACC-001 is configured twice")
    )
    assert LedgerConfig.make((ACC_001,), Day(1), Day(6), frozenset({Day(7)})) == Err(
        ConfigFault("capitalization day 7 is outside the window 1 to 6")
    )
    assert LedgerConfig.make((ACC_001,), Day(1), Day(6), frozenset()) == Ok(
        LedgerConfig((ACC_001,), Day(1), Day(6), frozenset())
    )
    with pytest.raises(ValueError, match="the first day 1 is after the last 0"):
        replace(CHALLENGE, last_day=Day(0))
    assert CHALLENGE.accounts == (ACC_001, AccountOpeningIn(AccountId("ACC-002"), make_bhd("0.000")))
    assert (CHALLENGE.first_day, CHALLENGE.last_day, CHALLENGE.capitalization_days) == (Day(1), Day(6), {Day(6)})
