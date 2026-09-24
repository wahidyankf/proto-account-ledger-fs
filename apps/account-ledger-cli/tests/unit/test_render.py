"""The report as text: layout, tables, amounts, and every Type and Detail text (tech-docs 003)."""

from account_ledger.config import CHALLENGE
from account_ledger.events import Capture
from account_ledger.ids import Day
from account_ledger.render import render
from account_ledger.replay import replay
from support.brief_stream import brief_stream
from support.output_target import expected_output
from support.streams import authorization, credit, debit, reversal, settlement

RULE = "=" * 120
TITLES = ("Events processed", "EOD applied", "Closing summary")


def test_a_day_opens_with_its_banner_and_its_blocks() -> None:
    """tech-docs 003: a day opens with a banner between two lines of 120 `=`, then the three titled blocks, each after
    one blank line, as is each day from the next; the output ends with a newline."""
    result = replay((), CHALLENGE)

    text = render((result.report(Day(0)), result.report(Day(1))))

    lines = text.split("\n")
    assert lines[:5] == [RULE, "Day 0", RULE, "", "Events processed"]
    titled = [n for n, line in enumerate(lines) if line in TITLES]
    assert [lines[n] for n in titled] == [*TITLES, *TITLES]
    assert all(lines[n - 1] == "" for n in titled)
    day_1 = lines.index("Day 1")
    assert lines[day_1 - 2 : day_1 + 2] == ["", RULE, "Day 1", RULE]
    assert text.endswith("\n")


def test_an_empty_block_prints_none() -> None:
    """AMB-033: a block with nothing in it prints two spaces and `none` instead of a table; Day 0 is such a day."""
    lines = render((replay((), CHALLENGE).report(Day(0)),)).split("\n")

    assert lines[4:10] == ["Events processed", "  none", "", "EOD applied", "  none", ""]


def test_a_table_is_a_box_as_wide_as_its_cells() -> None:
    """tech-docs 003: borders of `+`, `-`, and `|`, one space either side of each cell, every cell left-aligned, and
    every column as wide as its widest cell, header included; Day 0 prints exactly as OUTPUT_TARGET's Day 0."""
    day_0 = render((replay((), CHALLENGE).report(Day(0)),))

    assert day_0 == expected_output().split(f"\n\n{RULE}\nDay 1\n")[0] + "\n"


def test_amounts_print_in_their_currencys_format() -> None:
    """tech-docs 003: an amount prints its currency's places, a comma every three digits, and `−` (U+2212) for a
    negative, counted as one character when a column is sized."""
    opening = (credit("E1", 1, "1200.00"), credit("E2", 1, "1000.000", account="ACC-002"))
    day_1 = render((replay(opening, CHALLENGE).report(Day(1)),)).split("\n")
    day_5 = render((replay(brief_stream(), CHALLENGE).report(Day(5)),)).split("\n")

    assert "| Closing ledger balance | 1,200.00      | 1,000.000     |" in day_1
    assert any(line.startswith("| Day 2 closing, restated | \u2212370.00 ") for line in day_5)
    summary = day_5[day_5.index("Closing summary") + 1 :]
    assert len({len(line) for line in summary if line}) == 1


def _rows(output: str, day: int) -> str:
    """A day's Events processed and EOD applied blocks, as one text."""
    start = output.index(f"{RULE}\nDay {day}\n")
    return output[output.index("Events processed", start) : output.index("Closing summary", start)]


def test_each_row_prints_its_type_and_detail() -> None:
    """tech-docs 003: every Events processed and EOD applied row prints OUTPUT_TARGET's Type and Detail texts; Days 1 to
    5 of the brief print those blocks exactly as OUTPUT_TARGET does."""
    printed = render(replay(brief_stream(), CHALLENGE).reports)

    for day in range(1, 6):
        assert _rows(printed, day) == _rows(expected_output(), day)


def test_instalment_counts_print_as_words() -> None:
    """tech-docs 003: `in three equal instalments` spells the count as an English word from two to ten, and as digits
    above; E10 and its parts print as OUTPUT_TARGET's Day 6 shows them."""
    brief = render(replay(brief_stream(), CHALLENGE).reports).split("\n")
    target = expected_output().split("\n")
    e10 = [line for line in target if line.startswith("| E10")]

    assert [line for line in brief if line.startswith("| E10")] == e10

    def detail(count: int) -> str:
        stream = (credit("E1", 1, "12.000", account="ACC-002", instalments=count),)
        lines = render((replay(stream, CHALLENGE).report(Day(1)),)).split("\n")
        return next(line for line in lines if line.startswith("| E1 ")).split(" | ")[4].strip()

    assert [detail(2), detail(10), detail(11)] == [
        "BHD 12.000 in two equal instalments",
        "BHD 12.000 in ten equal instalments",
        "BHD 12.000 in 11 equal instalments",
    ]


def test_authorization_states_print_as_output_target_shows() -> None:
    """AMB-019, tech-docs 003: each authorization prints its state as OUTPUT_TARGET does, with no currency code, and an
    account's several authorizations are joined by `; `."""
    brief = render(replay(brief_stream(), CHALLENGE).reports).split("\n")

    def rows(lines: list[str]) -> list[str]:
        return [line for line in lines if line.startswith("| Authorizations")]

    assert rows(brief) == rows(expected_output().split("\n"))


def test_capitalization_names_the_days_it_accrued() -> None:
    """tech-docs 003: a capitalization names the days whose interest events do not net to zero: `Days 1 to 6` for three
    or more in a row, `Days 5 and 6` for two, `Day 6` for one, and `Days 1, 2, and 4` otherwise."""
    brief = render(replay(brief_stream(), CHALLENGE).reports).split("\n")
    gaps = (
        credit("E1", 1, "1000.00"),
        debit("E2", 3, "1000.00"),
        credit("E3", 4, "1000.00"),
        debit("E4", 5, "1000.00"),
        credit("E5", 6, "10.000", account="ACC-002"),
    )
    gapped = render((replay(gaps, CHALLENGE).report(Day(6)),)).split("\n")

    def details(lines: list[str]) -> list[str]:
        return [line.split(" | ")[4].strip() for line in lines if line.startswith("| 3    | CAP-")]

    assert details(brief) == ["AED 0.76, accrued Days 1 to 6", "BHD 0.008, accrued Days 5 and 6"]
    assert details(gapped) == ["AED 1.20, accrued Days 1, 2, and 4", "BHD 0.004, accrued Day 6"]


def test_the_texts_beyond_output_target_follow_its_patterns() -> None:
    """D22, tech-docs 003: a duplicate prints `duplicate of E1, no effect`; a force-post against a known hold prints as
    E6 does; a rejected event prints its usual detail, with its reason under Errors, several joined by `; `; and a
    reversal of a fired event names its marker."""
    stream = (
        credit("E1", 1, "400.00"),
        credit("E1", 1, "400.00"),
        authorization("E2", 1, "Auth-A", "100.00"),
        settlement("E3", 1, "Auth-A", "100.00"),
        settlement("E4", 1, "Auth-A", "40.00"),
        reversal("E5", 2, "E98"),
        reversal("E6", 2, "E99"),
        reversal("E7", 2, "INT-001-D1@D1"),
    )
    lines = render(replay(stream, CHALLENGE).reports[1:3]).split("\n")

    def details(block: list[str]) -> list[str]:
        return [line.split(" | ")[4].strip() for line in block if line[:3] == "| E" and line[3].isdigit()]

    day_2 = lines.index("Day 2")
    assert details(lines[:day_2]) == [
        "AED 400.00",
        "duplicate of E1, no effect",
        "Auth-A, hold AED 100.00",
        "Auth-A settles for AED 100.00",
        "Auth-A force-posts AED 40.00",
    ]
    assert details(lines[day_2:]) == ["reverses E98", "reverses E99", "reverses INT-001-D1@D1"]
    errors = next(line for line in lines[day_2:] if line.startswith("| Errors"))
    assert errors.split(" | ")[1].strip() == "E5 refused: E98 is not in the log; E6 refused: E99 is not in the log"


def test_a_partially_settled_authorization_prints_its_remaining_hold() -> None:
    """D22, tech-docs 003: a partial settlement prints `settles for ..., hold kept`, and its authorization `partially
    settled for C, hold H`; once a final capture follows, it prints `settled for` the captures' sum."""
    stream = (
        credit("E1", 1, "500.00"),
        authorization("E2", 1, "Auth-A", "200.00"),
        settlement("E3", 2, "Auth-A", "120.00", capture=Capture.PARTIAL),
        settlement("E4", 3, "Auth-A", "40.00"),
    )
    lines = render(replay(stream, CHALLENGE).reports[2:4]).split("\n")
    day_3 = lines.index("Day 3")

    def cell(block: list[str], start: str, column: int) -> str:
        return next(line for line in block if line.startswith(start)).split(" | ")[column].strip()

    assert cell(lines[:day_3], "| E3 ", 4) == "Auth-A settles for AED 120.00, hold kept"
    assert cell(lines[:day_3], "| Authorizations", 1) == "Auth-A partially settled for 120.00, hold 80.00"
    assert cell(lines[day_3:], "| E4 ", 4) == "Auth-A settles for AED 40.00"
    assert cell(lines[day_3:], "| Authorizations", 1) == "Auth-A settled for 160.00"
