"""Parser for the field tally notation used on the survey sheets.

Trees were recorded in three categories, comma separated within a single cell:

    plain number    single stemmed trees
    C               coppice
    M               multistemmed

A token may be a bare number, a bare letter, or a number followed by a letter.
Order and spacing vary between recorders, so the notation is tokenised rather
than split on a fixed pattern. All of these occur in the workbook:

    2C   C   1,C   1, C   4M, C   4M,C   C,M   C, M   M,C   M, 1   5C,M   70,4M

Jenny Greenwood's two worked examples, from her brief of 5 August 2026:

    "2, C, 2M is 3 single stem trees, 1 coppice, 2 multistem"   stated total 5
    "2C, 2M is 2 coppice, 2 multistem, no single stem"          stated total 4

The second example is internally consistent. The first was not: two single
stems plus one coppice plus two multistem is 5, which matches her stated total,
but she writes "3 single stem trees", which would total 6.

RESOLVED 14 August 2026. Jenny confirmed the bare number means 2 single stems,
so "3 single stem trees" in her brief was a slip and her stated total of 5 is
correct. The parser already read it that way, so no counts changed. The rule is
therefore settled: a bare number is exactly that number of single stems.

Seedlings were counted up to 100 and then recorded as ">100" (see the
Methodology sheet). Such a value is returned as 100 with censored=True, so
that any figure derived from it can be labelled a minimum rather than a count.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

__all__ = ["Tally", "TallyParseError", "parse_tally"]

# One token: an optional ">" censor marker, an optional count, an optional
# stem type letter. At least one of count or letter must be present.
_TOKEN = re.compile(
    r"^(?P<censor>>)?\s*(?P<count>\d+)?\s*(?P<letter>[CM])?$",
    re.IGNORECASE,
)


class TallyParseError(ValueError):
    """Raised when a cell cannot be read as tally notation.

    Some cells hold free text rather than a tally, for example the comment
    "Ribes sp (currant) noted on transect". Callers should catch this and log
    the offending cell rather than letting it fail the whole ingest.
    """


@dataclass(frozen=True)
class Tally:
    """Counts of stems in one cell, split by stem type.

    single, coppice and multi are kept apart deliberately. Coppice and
    multistem records are measured by stool width, single stems by diameter at
    breast height, so although they share the size class columns they are not
    the same measurement. Summing them is correct for abundance and species
    composition, and wrong for anything about structure, age or canopy.
    """

    single: int = 0
    coppice: int = 0
    multi: int = 0
    censored: bool = False

    @property
    def total(self) -> int:
        """Total stems, valid for abundance but not for structural analysis."""
        return self.single + self.coppice + self.multi


def parse_tally(value: object) -> Tally:
    """Read one spreadsheet cell as a Tally.

    Blank cells, None and NaN return an empty Tally. Raises TallyParseError on
    anything that is not tally notation.
    """
    if value is None:
        return Tally()

    # pandas represents an empty cell as NaN.
    if isinstance(value, float) and math.isnan(value):
        return Tally()

    # Whole numbers arrive from openpyxl as int or float, not text.
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        count = int(value)
        if count != value or count < 0:
            raise TallyParseError(f"not a whole positive count: {value!r}")
        return Tally(single=count)

    if not isinstance(value, str):
        raise TallyParseError(
            f"unsupported cell type {type(value).__name__}: {value!r}"
        )

    text = value.strip()
    if not text:
        return Tally()

    single = coppice = multi = 0
    censored = False

    for raw_token in text.split(","):
        token = raw_token.strip()
        if not token:
            continue

        match = _TOKEN.match(token)
        if match is None:
            raise TallyParseError(f"unreadable token {token!r} in cell {value!r}")

        count_text = match.group("count")
        letter = match.group("letter")
        if count_text is None and letter is None:
            raise TallyParseError(f"empty token {token!r} in cell {value!r}")

        if match.group("censor"):
            censored = True

        # A bare letter means one stem of that type.
        count = int(count_text) if count_text is not None else 1

        if letter is None:
            single += count
        elif letter.upper() == "C":
            coppice += count
        else:
            multi += count

    return Tally(single=single, coppice=coppice, multi=multi, censored=censored)
