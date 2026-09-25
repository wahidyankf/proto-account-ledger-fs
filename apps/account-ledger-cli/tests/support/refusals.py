"""One stream for each reason a reversal or a reused ID is refused, with the reason and the error text it prints."""

from account_ledger.domain.model.event_log import (
    AlreadyReversed,
    AlreadyUndone,
    IdReused,
    MovedNoMoney,
    Rejection,
    ReversesAReversal,
    UnknownTarget,
)
from account_ledger.domain.model.events import IncomingEvent
from account_ledger.domain.model.ids import AccountId, IncomingId, InstalmentId
from support.streams import ACC_001, ACC_002, authorization, credit, debit, reversal

type Refusal = tuple[tuple[IncomingEvent, ...], AccountId, Rejection, str]

REFUSALS: dict[str, Refusal] = {
    "IdReused": (
        (credit("E1", 1, "100.00"), credit("E1", 1, "90.00")),
        ACC_001.id,
        IdReused(),
        "E1 refused: ID already used with different content",
    ),
    "AlreadyReversed": (
        (credit("E1", 1, "1000.00"), debit("E7", 1, "620.00"), reversal("E9", 1, "E7"), reversal("E12", 1, "E7")),
        ACC_001.id,
        AlreadyReversed(IncomingId("E7"), IncomingId("E9")),
        "E12 refused: E7 is already reversed by E9",
    ),
    "ReversesAReversal": (
        (credit("E1", 1, "1000.00"), debit("E7", 1, "620.00"), reversal("E9", 1, "E7"), reversal("E12", 1, "E9")),
        ACC_001.id,
        ReversesAReversal(IncomingId("E9")),
        "E12 refused: E9 is a reversal",
    ),
    "UnknownTarget": (
        (credit("E1", 1, "100.00"), reversal("E12", 1, "E99")),
        ACC_001.id,
        UnknownTarget(IncomingId("E99")),
        "E12 refused: E99 is not in the log",
    ),
    "MovedNoMoney": (
        (credit("E1", 1, "100.00"), authorization("E8", 1, "Auth-B", "900.00"), reversal("E12", 1, "E8")),
        ACC_001.id,
        MovedNoMoney(IncomingId("E8")),
        "E12 refused: E8 moved no money",
    ),
    "AlreadyUndone": (
        (
            credit("E10", 1, "10.000", account="ACC-002", instalments=3),
            reversal("E11", 1, "E10", account="ACC-002"),
            reversal("E12", 1, "E10-1", account="ACC-002"),
        ),
        ACC_002.id,
        AlreadyUndone(InstalmentId(IncomingId("E10"), 1), IncomingId("E11")),
        "E12 refused: E10-1 is already undone by E11",
    ),
}
