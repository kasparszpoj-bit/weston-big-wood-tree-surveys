"""Project paths and survey constants.

Every magic number in the analysis lives here, with its source, so that a
reader can check any figure against the methodology document.
"""

from pathlib import Path

# Paths are derived from this file's location, so the pipeline runs the same
# way regardless of the working directory it is called from.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_EXTERNAL = PROJECT_ROOT / "data" / "external"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
OUTPUTS = PROJECT_ROOT / "outputs"
FIGURES = OUTPUTS / "figures"
TABLES = OUTPUTS / "tables"

SURVEY_WORKBOOK = DATA_RAW / "WBW_tree_age_distributions_tallied.xlsx"
SAMPLE_LOCATIONS_PDF = DATA_RAW / "tree_sample_locs.pdf"

# Coordinate reference system.
# Confirmed by Jenny: grid references are OSGB36, so British National Grid.
# Natural England publish their layers in the same CRS, so no transformation
# is needed. Never reproject by arithmetic: pyproj applies the OSTN15 grid
# shift correctly only when the CRS is declared like this.
CRS_BNG = "EPSG:27700"

# Transect geometry, from the Methodology sheet of the survey workbook:
# "Run a 50m long tape from the starting point along the angle specified by
# the map. Walking along the transect, record each tree, or sapling within 2m
# of the line on either side, which will give a 200m2 area."
TRANSECT_LENGTH_M = 50
TRANSECT_HALF_WIDTH_M = 2
TRANSECT_AREA_M2 = TRANSECT_LENGTH_M * TRANSECT_HALF_WIDTH_M * 2  # 200

# Multiply a per transect count by this to get stems per hectare.
PER_TRANSECT_TO_HA = 10_000 / TRANSECT_AREA_M2  # 50.0

# Site area from Natural England Designated Sites View, site code S1003590.
# The 1984 citation states 37.48 ha; the difference is boundary redigitising.
SSSI_AREA_HA = 37.66

# Seedling counts were capped in the field: "Seedlings counted up to 100, then
# recorded as >100." Any figure including seedlings is therefore a minimum.
SEEDLING_CENSOR_LIMIT = 100

# Two sheets recorded their coordinates without the leading digit. Every other
# transect is 345xxx / 17xxxx, both repaired values land on the same 100 m
# lattice, both fall inside the site, and both appear in the sample plan PDF
# with a bearing. Left uncorrected they plot about 300 km southwest, at sea.
# The repair is applied in code and reported, never done silently in the data.
COORDINATE_REPAIRS = {
    "Q5": {"recorded": (45650, 75150), "repaired": (345650, 175150)},
    "Q11": {"recorded": (45550, 75050), "repaired": (345550, 175050)},
}

# Column headers are reprinted partway down 12 of the sheets, because the
# species list continues below. A naive read would ingest "Small trees" and
# "Overmature" as species names, so the ingest skips any row whose first cell
# repeats a header label.
REPEATED_HEADER_LABELS = frozenset(
    {
        "common name",
        "seedlings or suckers",
        "saplings or suckers",
        "saplings",
        "small trees",
        "medium trees",
        "mature trees",
        "overmature",
        "ancient/ veteran",
    }
)


def ensure_output_dirs() -> None:
    """Create the generated directories if they are missing.

    These are not tracked by git, since everything in them is rebuilt by the
    pipeline, so a fresh clone will not have them.
    """
    for path in (DATA_EXTERNAL, DATA_PROCESSED, FIGURES, TABLES):
        path.mkdir(parents=True, exist_ok=True)
