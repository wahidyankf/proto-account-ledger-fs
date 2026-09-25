"""The configuration the challenge brief sets: ACC-001 in AED and ACC-002 in BHD, both opening at zero, Days 1 to 6,
and interest capitalized on Day 6. It is the shell's composition data: the CLI passes it to the stream reader and the
ledger, and the domain never imports it."""

from account_ledger.domain.model.config import AccountOpeningIn, LedgerConfig
from account_ledger.domain.model.ids import AccountId, Day
from account_ledger.domain.model.money import Aed, Bhd

CHALLENGE = LedgerConfig(
    accounts=(
        AccountOpeningIn(AccountId("ACC-001"), Aed.make_zero()),
        AccountOpeningIn(AccountId("ACC-002"), Bhd.make_zero()),
    ),
    first_day=Day(1),
    last_day=Day(6),
    capitalization_days=frozenset({Day(6)}),
)
