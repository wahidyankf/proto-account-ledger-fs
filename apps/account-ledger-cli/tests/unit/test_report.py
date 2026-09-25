"""The day report as data: restated closings (AMB-022), authorizations (AMB-019), errors (AMB-014), and rows."""

from typing import assert_never

import pytest

from account_ledger.domain.account.domain_events import (
    Rejection,
)
from account_ledger.domain.account.states import (
    Approved,
    AuthorizationState,
    Declined,
    Settled,
)
from account_ledger.domain.model.config import CHALLENGE
from account_ledger.domain.model.events import IncomingEvent
from account_ledger.domain.model.ids import AccountId, AuthorizationId, Day, format_id
from account_ledger.domain.model.money import AmountIn
from account_ledger.domain.report import Capitalized, DayReport, Generated, Note, NothingGenerated, Restatement, Step
from account_ledger.domain.stream_processing import (
    process_stream,
)
from support.brief_stream import build_brief_stream
from support.refusals import REFUSALS
from support.results import unwrap_ok
from support.streams import ACC_001, ACC_002, make_credit
from support.values import make_aed, make_bhd


def test_amb_022_a_day_restates_each_earlier_closing_it_changed() -> None:
    """AMB-022: when a backdated event changes an earlier closing, that day's report adds a restated closing for each
    earlier day it changed; an account whose closing for that day did not change shows none."""
    result = unwrap_ok(process_stream(build_brief_stream(), CHALLENGE))

    assert result.find_report(Day(5)).restatements == (
        Restatement(Day(2), {ACC_001.id: make_aed("-370.00"), ACC_002.id: None}),
        Restatement(Day(3), {ACC_001.id: make_aed("30.00"), ACC_002.id: None}),
        Restatement(Day(4), {ACC_001.id: make_aed("-335.00"), ACC_002.id: None}),
    )
    assert result.find_report(Day(6)).restatements == (
        Restatement(Day(2), {ACC_001.id: make_aed("250.00"), ACC_002.id: None}),
        Restatement(Day(3), {ACC_001.id: make_aed("650.00"), ACC_002.id: None}),
        Restatement(Day(4), {ACC_001.id: make_aed("285.00"), ACC_002.id: None}),
        Restatement(Day(5), {ACC_001.id: make_aed("210.00"), ACC_002.id: make_bhd("10.000")}),
    )


def test_amb_019_every_known_authorization_is_listed_with_its_state() -> None:
    """AMB-019, AMB-025: every authorization known by the end of the day is listed with its state then, in the order
    first seen; a declined authorization is a state, printed with the others."""
    result = unwrap_ok(process_stream(build_brief_stream(), CHALLENGE))

    def list_authorizations(day: int) -> list[tuple[AuthorizationId, AuthorizationState]]:
        """Each authorization the day's report lists, with its state then."""
        return [
            (record.authorization.authorization, record.state) for record in result.find_report(Day(day)).authorizations
        ]

    assert list_authorizations(1) == []
    assert list_authorizations(2) == [(AuthorizationId("Auth-A"), Approved(AmountIn(make_aed("200.00"))))]
    assert list_authorizations(5) == [
        (AuthorizationId("Auth-A"), Settled(AmountIn(make_aed("185.00")))),
        (AuthorizationId("Auth-B"), Declined(AmountIn(make_aed("90.00")))),
    ]


@pytest.mark.parametrize(("stream", "account", "reason", "_text"), REFUSALS.values(), ids=REFUSALS.keys())
def test_amb_014_a_rejected_event_is_that_days_error(
    stream: tuple[IncomingEvent, ...], account: AccountId, reason: Rejection, _text: str
) -> None:
    """AMB-014: every event is recorded with its outcome, and a refused one is that day's error, by account, with the
    reason it was refused; the renderer prints it in the text tech-docs 001 fixes (D22)."""
    errors = unwrap_ok(process_stream(stream, CHALLENGE)).find_report(Day(1)).errors

    assert {account_id: tuple(entry.reason for entry in entries) for account_id, entries in errors.items()} == {
        configured_account.id: (reason,) if configured_account.id == account else ()
        for configured_account in CHALLENGE.accounts
    }


def list_rows(day_report: DayReport) -> list[tuple[int, str | Note, tuple[str, ...]]]:
    """Each end-of-day row as its step, its generated ID or note, and its accounts."""
    found_rows: list[tuple[int, str | Note, tuple[str, ...]]] = []
    for row in day_report.end_of_day:
        match row:
            case Generated(step=step, event=event):
                found_rows.append((step.value, format_id(event.id), (event.account.value,)))
            case Capitalized(event=event):
                found_rows.append((Step.CAPITALIZATION.value, format_id(event.id), (event.account.value,)))
            case NothingGenerated(step=step, accounts=accounts, note=note):
                found_rows.append((step.value, note, tuple(account.value for account in accounts)))
            case _:
                assert_never(row)
    return found_rows


BOTH = ("ACC-001", "ACC-002")


def test_amb_033_a_step_that_generates_nothing_reports_its_row() -> None:
    """AMB-033: every end-of-day step is printed with the events it generates, and a step that generates nothing prints
    a row saying so (tech-docs 002)."""
    result = unwrap_ok(process_stream(build_brief_stream(), CHALLENGE))

    assert list_rows(result.find_report(Day(1))) == [
        (1, Note.NO_FEE, BOTH),
        (2, "INT-001-D1@D1", ("ACC-001",)),
        (2, Note.NO_INTEREST, ("ACC-002",)),
    ]
    assert list_rows(result.find_report(Day(5)))[3:] == [
        (2, "INT-001-D2@D5", ("ACC-001",)),
        (2, "INT-001-D3@D5", ("ACC-001",)),
        (2, "INT-001-D4@D5", ("ACC-001",)),
        (2, Note.NO_INTEREST, ("ACC-001",)),
        (2, Note.NO_INTEREST, ("ACC-002",)),
    ]
    assert list_rows(result.find_report(Day(6)))[:4] == [
        (1, "REFUND-001-D2@D6", ("ACC-001",)),
        (1, "REFUND-001-D4@D6", ("ACC-001",)),
        (1, "REFUND-001-D5@D6", ("ACC-001",)),
        (1, Note.NO_NEW_FEE, BOTH),
    ]
    assert list_rows(result.find_report(Day(6)))[-2:] == [
        (3, "CAP-001@D6", ("ACC-001",)),
        (3, "CAP-002@D6", ("ACC-002",)),
    ]
    aed_only_report = unwrap_ok(process_stream((make_credit("E1", 1, "100.00"),), CHALLENGE)).find_report(Day(6))
    assert list_rows(aed_only_report)[-2:] == [
        (3, "CAP-001@D6", ("ACC-001",)),
        (3, Note.NO_CAPITALIZATION, ("ACC-002",)),
    ]
