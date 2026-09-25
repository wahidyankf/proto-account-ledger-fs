"""Events: each kind's guard refuses a value only a bug could build."""

import pytest

from account_ledger.domain.model.events import Instalments
from account_ledger.domain.model.ids import InstalmentCount
from account_ledger.domain.model.money import AmountIn
from support.values import make_aed


def test_instalments_refuse_parts_whose_number_is_not_the_count() -> None:
    """Instalments hold as many parts as their count; three parts under a count of two are refused."""
    part = AmountIn(make_aed("1.00"))
    with pytest.raises(ValueError, match="2 instalments hold 2 parts, not 3"):
        Instalments(InstalmentCount(2), (part, part, part))
