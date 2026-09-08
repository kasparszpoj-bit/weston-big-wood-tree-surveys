"""Read the survey workbook into one tidy table.

One row per transect, species, size class and the three stem-type counts.
Everything downstream, every map and graph Jenny asked for, is a groupby on
the table this module produces.

Size classes are mapped **by column position**, not by header label, because
the labels are unreliable: columns B and C both read "Seedlings or suckers"
on most sheets (Q1 alone says "Saplings or suckers" for column C), and only
row 5 distinguishes them by definition. Position is stable on every sheet.
"""

from __future__ import annotations

import pandas as pd

from wbw.tally import Tally, TallyParseError, parse_tally

# Zero-indexed grid positions, so row 3 here is row 4 in Excel.
SIZE_CLASS_HEADER_ROW = 3
FIRST_DATA_ROW = 5
SPECIES_COLUMN = 0

# Column position -> canonical size class, from the row-5 definitions.
# Column 8 (Ancient/veteran, sheets Q1-Q3 only) is validated as never used.
SIZE_CLASSES = {
    1: "seedling_le100",   # Seedlings or suckers, <=100 cm tall
    2: "seedling_gt100",   # Seedlings or suckers, >100 cm, <=3 cm dbh
    3: "sapling",          # Saplings, 3-7 cm dbh
    4: "small",            # Small trees, <=25 cm dbh
    5: "medium",           # Medium trees, <=50 cm dbh
    6: "mature",           # Mature trees, <=75 cm dbh
    7: "overmature",       # Overmature, >75 cm dbh
    8: "ancient_veteran",  # No definition given; never holds data
}

CLASS_ORDER = [
    "seedling_le100", "seedling_gt100", "sapling",
    "small", "medium", "mature", "overmature",
]

CLASS_LABELS = {
    "seedling_le100": "Seedling\n≤100 cm",
    "seedling_gt100": "Seedling\n>100 cm",
    "sapling": "Sapling\n3–7 cm",
    "small": "Small\n≤25 cm",
    "medium": "Medium\n≤50 cm",
    "mature": "Mature\n≤75 cm",
    "overmature": "Overmature\n>75 cm",
}

# Established trees: the four classes measured by dbh / stool width at or
# above 7 cm. Seedlings and saplings are reported separately throughout.
ESTABLISHED = ["small", "medium", "mature", "overmature"]

# Rows in the species column that are not living species.
DEADWOOD_LABELS = {"dead standing", "dead fallen", "stump"}

# The header block is reprinted mid-sheet on 12 sheets. Any species cell
# holding one of these is a repeated header, not a species.
HEADER_LABELS = {
    "common name", "seedlings or suckers", "saplings or suckers", "saplings",
    "small trees", "medium trees", "mature trees", "overmature",
    "ancient/ veteran", "ancient/veteran",
}

# Non-species rows worth keeping as notes rather than data.
NOTE_LABELS = {"comments:"}

# Observed spelling variants -> canonical name. Wild Service Tree
# (Sorbus torminalis) and Service-tree (S. domestica) are different species
# and are deliberately NOT merged.
SPECIES_FIXES = {
    "dogwood": "Dogwood",
}


def read_sheet(sheet: pd.DataFrame, name: str):
    """One transect sheet -> (tidy rows, problem cells, note cells)."""
    rows, problems, notes = [], [], []

    for row in range(FIRST_DATA_ROW, sheet.shape[0]):
        species = sheet.iat[row, SPECIES_COLUMN]
        if not isinstance(species, str) or not species.strip():
            continue
        species = species.strip()
        key = species.lower()

        if key in HEADER_LABELS:
            continue
        if key in NOTE_LABELS:
            # Free text lives in the row; collect it and move on.
            for col in range(1, sheet.shape[1]):
                v = sheet.iat[row, col]
                if isinstance(v, str) and v.strip():
                    notes.append({"transect": name, "note": v.strip()})
            continue

        species = SPECIES_FIXES.get(key, species)

        for col, size_class in SIZE_CLASSES.items():
            if col >= sheet.shape[1]:
                break
            value = sheet.iat[row, col]
            if pd.isna(value):
                continue

            try:
                tally: Tally = parse_tally(value)
            except TallyParseError:
                problems.append({
                    "transect": name, "species": species,
                    "size_class": size_class, "value": value,
                })
                continue

            if tally.total:
                rows.append({
                    "transect": name,
                    "species": species,
                    "size_class": size_class,
                    "single": tally.single,
                    "coppice": tally.coppice,
                    "multi": tally.multi,
                    "censored": tally.censored,
                    "dead": key in DEADWOOD_LABELS,
                })

    return rows, problems, notes


def read_workbook(path):
    """Every transect sheet -> one tidy DataFrame, plus problems and notes."""
    sheets = pd.read_excel(path, sheet_name=None, header=None)

    all_rows, all_problems, all_notes = [], [], []
    for name, sheet in sheets.items():
        # Sheet q18 is lowercase; match case-insensitively or lose a transect.
        clean = name.strip().upper()
        if not (clean.startswith("Q") and clean[1:].isdigit()):
            continue
        rows, problems, notes = read_sheet(sheet, clean)
        all_rows.extend(rows)
        all_problems.extend(problems)
        all_notes.extend(notes)

    table = pd.DataFrame(all_rows)
    table["stems"] = table["single"] + table["coppice"] + table["multi"]
    return table, pd.DataFrame(all_problems), pd.DataFrame(all_notes)
