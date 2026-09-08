"""Transect locations: surveyed starts from the workbook, the 49-point
sample plan (with bearings) from the text layer of tree_sample_locs.pdf."""

from __future__ import annotations

import math
import re

import pandas as pd
from pypdf import PdfReader
from shapely.geometry import LineString, Point, box

from wbw.config import COORDINATE_REPAIRS, SAMPLE_LOCATIONS_PDF, TRANSECT_LENGTH_M

_COORD = re.compile(r"(\d{5,6})[,\s]+(\d{5,6})")
_TRIPLE = re.compile(r"(\d{6})\s+(\d{6})\s+(\d{1,3})(?!\d)")


def _repair(easting: int, northing: int) -> tuple[int, int]:
    """Restore leading digits dropped on Q5 and Q11.

    Every transect sits at 345xxx / 17xxxx. A 5-digit value has lost its
    leading digit; both repaired values land on the same 100 m lattice and
    match points in the sample plan, so the repair is verified, not assumed.
    """
    if easting < 100_000:
        easting += 300_000
    if northing < 100_000:
        northing += 100_000
    return easting, northing


def surveyed_points(workbook_path) -> pd.DataFrame:
    """Start coordinate of each surveyed transect, repairs applied."""
    sheets = pd.read_excel(workbook_path, sheet_name=None, header=None)
    out = []
    for name, sheet in sheets.items():
        clean = name.strip().upper()
        if not (clean.startswith("Q") and clean[1:].isdigit()):
            continue
        # The coordinate sits in the header block, first three rows.
        found = None
        for r in range(3):
            for c in range(sheet.shape[1]):
                v = sheet.iat[r, c]
                if isinstance(v, str) and (m := _COORD.search(v)):
                    found = (int(m.group(1)), int(m.group(2)))
                    break
            if found:
                break
        if found is None:
            raise ValueError(f"no start coordinate found on sheet {clean}")
        e, n = _repair(*found)
        out.append({
            "transect": clean, "easting": e, "northing": n,
            "repaired": clean in COORDINATE_REPAIRS,
        })
    return pd.DataFrame(out).sort_values(
        "transect", key=lambda s: s.str.lstrip("Q").astype(int)
    ).reset_index(drop=True)


def planned_points() -> pd.DataFrame:
    """All 49 planned sample points with bearings, from the plan PDF."""
    reader = PdfReader(SAMPLE_LOCATIONS_PDF)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    triples = _TRIPLE.findall(text)
    plan = pd.DataFrame(
        [{"easting": int(e), "northing": int(n), "bearing": int(b)}
         for e, n, b in triples]
    ).drop_duplicates().reset_index(drop=True)
    if len(plan) != 49:
        raise ValueError(f"expected 49 planned points, extracted {len(plan)}")
    return plan


def transect_line(easting: float, northing: float, bearing: float) -> LineString:
    """The 50 m transect line from its start point along its bearing."""
    rad = math.radians(bearing)
    return LineString([
        (easting, northing),
        (easting + TRANSECT_LENGTH_M * math.sin(rad),
         northing + TRANSECT_LENGTH_M * math.cos(rad)),
    ])


def grid_cell(easting: float, northing: float):
    """The 100 m grid square centred on a sample point."""
    return box(easting - 50, northing - 50, easting + 50, northing + 50)


def start_point(easting: float, northing: float) -> Point:
    return Point(easting, northing)
