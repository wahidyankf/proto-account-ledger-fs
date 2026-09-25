"""The brief's stream, E1 to E10, built in code, so a unit test never reads the stream file."""

from account_ledger.domain.model.events import (
    Authorization,
    Credit,
    Debit,
    IncomingEvent,
    Instalments,
    Reversal,
    Settlement,
    SettlementKind,
    Whole,
)
from account_ledger.domain.model.ids import AccountId, AuthorizationId, Day, IncomingId, InstalmentCount
from account_ledger.domain.model.money import Amount
from support.values import make_aed, make_bhd

ACC_001, ACC_002 = AccountId("ACC-001"), AccountId("ACC-002")


def build_brief_stream() -> tuple[IncomingEvent, ...]:
    """E1 to E10 in the order the brief lists them."""
    return (
        Credit(IncomingId("E1"), Day(1), ACC_001, Day(1), Amount(make_aed("1200.00")), Whole()),
        Debit(IncomingId("E2"), Day(1), ACC_001, Day(1), Amount(make_aed("950.00"))),
        Authorization(IncomingId("E3"), Day(2), ACC_001, Day(2), AuthorizationId("Auth-A"), Amount(make_aed("200.00"))),
        Credit(IncomingId("E4"), Day(3), ACC_001, Day(3), Amount(make_aed("400.00")), Whole()),
        Settlement(
            IncomingId("E5"),
            Day(4),
            ACC_001,
            Day(4),
            AuthorizationId("Auth-A"),
            Amount(make_aed("185.00")),
            SettlementKind.FINAL,
        ),
        Settlement(
            IncomingId("E6"),
            Day(4),
            ACC_001,
            Day(4),
            AuthorizationId("Auth-Z"),
            Amount(make_aed("180.00")),
            SettlementKind.FINAL,
        ),
        Debit(IncomingId("E7"), Day(5), ACC_001, Day(2), Amount(make_aed("620.00"))),
        Authorization(IncomingId("E8"), Day(5), ACC_001, Day(5), AuthorizationId("Auth-B"), Amount(make_aed("90.00"))),
        Reversal(IncomingId("E9"), Day(6), ACC_001, Day(2), IncomingId("E7")),
        Credit(IncomingId("E10"), Day(5), ACC_002, Day(5), Amount(make_bhd("10.000")), Instalments(InstalmentCount(3))),
    )


BRIEF_CSV = """\
event,booked,type,account,amount,value_date,reference,instalments,final
E1,1,CREDIT,ACC-001,1200.00,1,,,
E2,1,DEBIT,ACC-001,950.00,1,,,
E3,2,AUTHORIZATION,ACC-001,200.00,2,Auth-A,,
E4,3,CREDIT,ACC-001,400.00,3,,,
E5,4,SETTLEMENT,ACC-001,185.00,4,Auth-A,,
E6,4,SETTLEMENT,ACC-001,180.00,4,Auth-Z,,
E7,5,DEBIT,ACC-001,620.00,2,,,
E8,5,AUTHORIZATION,ACC-001,90.00,5,Auth-B,,
E9,6,REVERSAL,ACC-001,,2,E7,,
E10,5,CREDIT,ACC-002,10.000,5,,3,
"""
"""The brief's stream as the stream file holds it, for a unit test that reads no file."""
