"""One stream for each reason an event is refused, a reversal or a reused event or authorization ID, with the reason
and the error text it prints."""

from account_ledger.domain.account.rejections import (
    AlreadyReversed,
    AlreadyUndone,
    AuthorizationIdReused,
    DatedBeforeTarget,
    IdReused,
    MovedNoMoney,
    Rejection,
    ReversesAReversal,
    TargetOnAnotherAccount,
    UnknownTarget,
)
from account_ledger.domain.model.events import IncomingEvent
from account_ledger.domain.model.ids import AccountId, AuthorizationId, Day, IncomingId, InstalmentId
from support.streams import ACC_001_OPENING, ACC_002_OPENING, make_authorization, make_credit, make_debit, make_reversal

type Refusal = tuple[tuple[IncomingEvent, ...], AccountId, Rejection, str]

REFUSALS: dict[str, Refusal] = {
    "IdReused": (
        (make_credit("E1", 1, "100.00"), make_credit("E1", 1, "90.00")),
        ACC_001_OPENING.id,
        IdReused(),
        "E1 refused: ID already used with different content",
    ),
    "AuthorizationIdReused": (
        (
            make_credit("E1", 1, "500.00"),
            make_authorization("E2", 1, "Auth-A", "100.00"),
            make_authorization("E3", 1, "Auth-A", "50.00"),
        ),
        ACC_001_OPENING.id,
        AuthorizationIdReused(AuthorizationId("Auth-A"), IncomingId("E2")),
        "E3 refused: Auth-A is already used by E2",
    ),
    "AlreadyReversed": (
        (
            make_credit("E1", 1, "1000.00"),
            make_debit("E7", 1, "620.00"),
            make_reversal("E9", 1, "E7"),
            make_reversal("E12", 1, "E7"),
        ),
        ACC_001_OPENING.id,
        AlreadyReversed(IncomingId("E7"), IncomingId("E9")),
        "E12 refused: E7 is already reversed by E9",
    ),
    "ReversesAReversal": (
        (
            make_credit("E1", 1, "1000.00"),
            make_debit("E7", 1, "620.00"),
            make_reversal("E9", 1, "E7"),
            make_reversal("E12", 1, "E9"),
        ),
        ACC_001_OPENING.id,
        ReversesAReversal(IncomingId("E9")),
        "E12 refused: E9 is a reversal",
    ),
    "UnknownTarget": (
        (make_credit("E1", 1, "100.00"), make_reversal("E12", 1, "E99")),
        ACC_001_OPENING.id,
        UnknownTarget(IncomingId("E99")),
        "E12 refused: E99 is not in the log",
    ),
    "TargetOnAnotherAccount": (
        (
            make_credit("E1", 1, "100.00"),
            make_credit("E2", 1, "100.000", account="ACC-002"),
            make_reversal("E12", 1, "E1", account="ACC-002"),
        ),
        ACC_002_OPENING.id,
        TargetOnAnotherAccount(IncomingId("E1"), ACC_001_OPENING.id),
        "E12 refused: E1 is on ACC-001, not ACC-002",
    ),
    "MovedNoMoney": (
        (
            make_credit("E1", 1, "100.00"),
            make_authorization("E8", 1, "Auth-B", "900.00"),
            make_reversal("E12", 1, "E8"),
        ),
        ACC_001_OPENING.id,
        MovedNoMoney(IncomingId("E8")),
        "E12 refused: E8 moved no money",
    ),
    "DatedBeforeTarget": (
        (
            make_credit("E1", 1, "1000.00"),
            make_debit("E7", 1, "620.00", value=3),
            make_reversal("E12", 1, "E7", value=2),
        ),
        ACC_001_OPENING.id,
        DatedBeforeTarget(IncomingId("E7"), Day(3)),
        "E12 refused: E7 is value-dated later, Day 3",
    ),
    "AlreadyUndone": (
        (
            make_credit("E10", 1, "10.000", account="ACC-002", instalments=3),
            make_reversal("E11", 1, "E10", account="ACC-002"),
            make_reversal("E12", 1, "E10-1", account="ACC-002"),
        ),
        ACC_002_OPENING.id,
        AlreadyUndone(InstalmentId(IncomingId("E10"), 1), IncomingId("E11")),
        "E12 refused: E10-1 is already undone by E11",
    ),
}
