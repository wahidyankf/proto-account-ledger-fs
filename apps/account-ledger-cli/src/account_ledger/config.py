"""The ledger's configuration: its accounts, its window of days, and its capitalization days."""

from dataclasses import dataclass

from account_ledger.ids import AccountId, Day
from account_ledger.money import Aed, Bhd


@dataclass(frozen=True, slots=True)
class Account[M: (Aed, Bhd)]:
    """An account; its currency is the type of its opening balance."""

    id: AccountId
    opening: M


type AnyAccount = Account[Aed] | Account[Bhd]


@dataclass(frozen=True, slots=True)
class ConfigFault:
    """A configuration no ledger can run."""

    reason: str


def _fault(
    accounts: tuple[AnyAccount, ...], first_day: Day, last_day: Day, capitalization_days: frozenset[Day]
) -> ConfigFault | None:
    if first_day > last_day:
        return ConfigFault(f"the first day {first_day.number} is after the last {last_day.number}")
    ids = [account.id for account in accounts]
    for account_id in ids:
        if ids.count(account_id) > 1:
            return ConfigFault(f"{account_id.value} is configured twice")
    for day in sorted(capitalization_days):
        if not first_day <= day <= last_day:
            window = f"{first_day.number} to {last_day.number}"
            return ConfigFault(f"capitalization day {day.number} is outside the window {window}")
    return None


@dataclass(frozen=True, slots=True)
class LedgerConfig:
    """The accounts in order, the window of days replayed, and the days interest is capitalized."""

    accounts: tuple[AnyAccount, ...]
    first_day: Day
    last_day: Day
    capitalization_days: frozenset[Day]

    def __post_init__(self) -> None:
        fault = _fault(self.accounts, self.first_day, self.last_day, self.capitalization_days)
        if fault is not None:
            raise ValueError(fault.reason)

    @staticmethod
    def of(
        accounts: tuple[AnyAccount, ...], first_day: Day, last_day: Day, capitalization_days: frozenset[Day]
    ) -> LedgerConfig | ConfigFault:
        fault = _fault(accounts, first_day, last_day, capitalization_days)
        return fault if fault is not None else LedgerConfig(accounts, first_day, last_day, capitalization_days)

    def account(self, account_id: AccountId) -> AnyAccount | None:
        """The configured account with this ID, if the ledger holds it."""
        return next((account for account in self.accounts if account.id == account_id), None)


CHALLENGE = LedgerConfig(
    accounts=(Account(AccountId("ACC-001"), Aed.zero()), Account(AccountId("ACC-002"), Bhd.zero())),
    first_day=Day(1),
    last_day=Day(6),
    capitalization_days=frozenset({Day(6)}),
)
