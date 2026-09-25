"""The ledger's configuration: its accounts, its window of days, and its capitalization days."""

from dataclasses import dataclass
from typing import TypeIs

from account_ledger.common.result import Err, Ok, Result
from account_ledger.domain.model.ids import AccountId, Day
from account_ledger.domain.model.money import Aed, Bhd


@dataclass(frozen=True, slots=True)
class Account[M: (Aed, Bhd)]:
    """An account; its currency is the type of its opening balance."""

    id: AccountId
    opening: M


type AnyAccount = Account[Aed] | Account[Bhd]


def is_aed(account: AnyAccount) -> TypeIs[Account[Aed]]:
    """Narrow an account to its currency; the other branch is ``Account[Bhd]``."""
    return isinstance(account.opening, Aed)


@dataclass(frozen=True, slots=True)
class ConfigFault:
    """A configuration no ledger can run."""

    reason: str


def _check_config(
    accounts: tuple[AnyAccount, ...], first_day: Day, last_day: Day, capitalization_days: frozenset[Day]
) -> Result[None, ConfigFault]:
    """Nothing when the configuration is valid, or the first reason it is not."""
    if first_day > last_day:
        return Err(ConfigFault(f"the first day {first_day.number} is after the last {last_day.number}"))
    ids = [account.id for account in accounts]
    for account_id in ids:
        if ids.count(account_id) > 1:
            return Err(ConfigFault(f"{account_id.value} is configured twice"))
    for day in sorted(capitalization_days):
        if not first_day <= day <= last_day:
            window = f"{first_day.number} to {last_day.number}"
            return Err(ConfigFault(f"capitalization day {day.number} is outside the window {window}"))
    return Ok(None)


@dataclass(frozen=True, slots=True)
class LedgerConfig:
    """The accounts in order, the window of days replayed, and the days interest is capitalized."""

    accounts: tuple[AnyAccount, ...]
    first_day: Day
    last_day: Day
    capitalization_days: frozenset[Day]

    def __post_init__(self) -> None:
        checked = _check_config(self.accounts, self.first_day, self.last_day, self.capitalization_days)
        if isinstance(checked, Err):
            raise ValueError(checked.error.reason)

    @staticmethod
    def make(
        accounts: tuple[AnyAccount, ...], first_day: Day, last_day: Day, capitalization_days: frozenset[Day]
    ) -> Result[LedgerConfig, ConfigFault]:
        """The configuration, or the fault that makes it invalid."""
        return _check_config(accounts, first_day, last_day, capitalization_days).map(
            lambda _: LedgerConfig(accounts, first_day, last_day, capitalization_days)
        )

    def find_account(self, account_id: AccountId) -> AnyAccount | None:
        """The configured account with this ID, if the ledger holds it."""
        return next((account for account in self.accounts if account.id == account_id), None)


CHALLENGE = LedgerConfig(
    accounts=(Account(AccountId("ACC-001"), Aed.make_zero()), Account(AccountId("ACC-002"), Bhd.make_zero())),
    first_day=Day(1),
    last_day=Day(6),
    capitalization_days=frozenset({Day(6)}),
)
