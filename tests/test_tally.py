"""Tests for the field tally notation parser.

The first test is the one that matters to the client: it checks the parser
reproduces the totals Jenny Greenwood stated in her own worked examples. Every
count in the analysis depends on this parser being right, so it is tested
against the client's arithmetic rather than against our own assumptions.
"""

import math

import pytest

from wbw.tally import Tally, TallyParseError, parse_tally


def test_matches_jennys_worked_examples():
    """Both examples from the brief of 5 August 2026, with her stated totals.

    The first example described "3 single stem trees" but gave a total of 5,
    which only holds at 2. Jenny confirmed 2 on 14 August 2026, so this test
    now encodes a settled rule rather than a working assumption.
    """
    first = parse_tally("2, C, 2M")
    assert (first.single, first.coppice, first.multi) == (2, 1, 2)
    assert first.total == 5, "Jenny states this example totals 5"

    second = parse_tally("2C, 2M")
    assert (second.single, second.coppice, second.multi) == (0, 2, 2)
    assert second.total == 4, "Jenny states this example totals 4"


@pytest.mark.parametrize(
    ("cell", "expected"),
    [
        # Notation variants observed in the workbook. Order, spacing and
        # whether the number precedes or follows the letter all vary.
        ("2C", Tally(coppice=2)),
        ("C", Tally(coppice=1)),
        ("1,C", Tally(single=1, coppice=1)),
        ("1, C", Tally(single=1, coppice=1)),
        ("4M, C", Tally(coppice=1, multi=4)),
        ("4M,C", Tally(coppice=1, multi=4)),
        ("C,M", Tally(coppice=1, multi=1)),
        ("C, M", Tally(coppice=1, multi=1)),
        ("M,C", Tally(coppice=1, multi=1)),
        ("M, 1", Tally(single=1, multi=1)),
        ("5C,M", Tally(coppice=5, multi=1)),
        ("70,4M", Tally(single=70, multi=4)),
    ],
)
def test_notation_variants(cell, expected):
    assert parse_tally(cell) == expected


def test_case_and_whitespace_are_tolerated():
    assert parse_tally("  2c ,  3m  ") == Tally(coppice=2, multi=3)


@pytest.mark.parametrize("blank", [None, "", "   ", math.nan])
def test_blank_cells_are_empty_not_errors(blank):
    assert parse_tally(blank) == Tally()
    assert parse_tally(blank).total == 0


def test_numeric_cells_are_single_stems():
    """openpyxl returns bare numbers as int or float, not text."""
    assert parse_tally(12) == Tally(single=12)
    assert parse_tally(12.0) == Tally(single=12)


def test_censored_seedling_counts_are_flagged():
    """Seedlings were counted to 100 then recorded as >100, so 100 is a floor."""
    censored = parse_tally(">100")
    assert censored.single == 100
    assert censored.censored is True

    # A plain 100 is a real count, not a censored one.
    exact = parse_tally("100")
    assert exact.single == 100
    assert exact.censored is False


def test_dead_standing_coppice_stool_parses():
    """Q19 records Dead standing as C, most likely a dead coppice stool.

    Flagged in the data audit as an oddity. It must parse rather than be
    dropped, so the record survives to be reported.
    """
    assert parse_tally("C") == Tally(coppice=1)


@pytest.mark.parametrize(
    "junk",
    [
        "Ribes sp (currant) noted on transect - AWI for site record.",
        "Laurel (Prunus sp) Cherry or Portuguese?",
        "?",
        "83 ash in 2m2",
    ],
)
def test_free_text_raises_so_it_can_be_logged(junk):
    """Free text sits in some data cells and must not be silently counted."""
    with pytest.raises(TallyParseError):
        parse_tally(junk)


def test_total_sums_all_three_stem_types():
    assert parse_tally("3, 2C, 4M").total == 9
