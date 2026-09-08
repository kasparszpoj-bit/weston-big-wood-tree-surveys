"""Export non-native tree records as a species-level point layer.

Run:  python scripts/07_export_non_natives.py

The `results` layer carries `non_native` only as a total count per square, so
QGIS cannot colour sycamore differently from holm oak. This writes
data/external/non_natives.gpkg with one layer, `non_natives`, holding one point
per transect per species group, with a `species` field and a `stems` count.

Points are placed at the grid-square centre with a small fixed offset per
species so that two species in the same square (Q12 has both holm oak and the
unidentified laurel) do not draw on top of each other. The offset is cosmetic
and stays well inside the 100 m square.
"""

import geopandas as gpd
from shapely.geometry import Point

from wbw.config import DATA_EXTERNAL, SURVEY_WORKBOOK
from wbw.ingest import read_workbook
from wbw.locations import planned_points, surveyed_points

# Substring -> canonical group. Matches 05_export_qgis_results.py, which uses
# the same four terms, so the per-species counts here sum to `non_native` there.
GROUPS = {
    "sycamore": "Sycamore",
    "holm oak": "Holm Oak",
    "buddleia": "Buddleia",
    "laurel": "Laurel",
}

# Metres from the square centre, so co-located species stay legible.
OFFSETS = {
    "Sycamore": (-22, 22),
    "Holm Oak": (22, 22),
    "Buddleia": (-22, -22),
    "Laurel": (22, -22),
}

table, _, _ = read_workbook(SURVEY_WORKBOOK)
live = table[~table["dead"]].copy()


def group_of(species: str) -> str | None:
    key = species.lower()
    for needle, label in GROUPS.items():
        if needle in key:
            return label
    return None


live["group"] = live["species"].map(group_of)
non_native = live[live["group"].notna()]

counts = (
    non_native.groupby(["transect", "group"])["stems"].sum().reset_index(name="stems")
)

# Square centres, via the same plan/surveyed join the results export uses.
plan = planned_points()
pts = surveyed_points(SURVEY_WORKBOOK)
plan = plan.merge(
    pts[["easting", "northing", "transect"]], on=["easting", "northing"], how="left"
)
centres = plan.dropna(subset=["transect"]).set_index("transect")[["easting", "northing"]]

rows, geoms = [], []
for record in counts.itertuples(index=False):
    if record.transect not in centres.index:
        raise ValueError(f"transect {record.transect} has no planned location")
    east, north = centres.loc[record.transect]
    dx, dy = OFFSETS[record.group]
    rows.append(
        {"transect": record.transect, "species": record.group, "stems": int(record.stems)}
    )
    geoms.append(Point(east + dx, north + dy))

layer = gpd.GeoDataFrame(rows, geometry=geoms, crs="EPSG:27700")

out = DATA_EXTERNAL / "non_natives.gpkg"
out.unlink(missing_ok=True)
layer.to_file(out, layer="non_natives", driver="GPKG")

print(f"wrote {out}")
print(f"{len(layer)} records, {layer.stems.sum()} stems\n")
print("species       stems  transects")
for name, part in layer.groupby("species"):
    where = ", ".join(sorted(part.transect, key=lambda q: int(q.lstrip("Q"))))
    print(f"  {name:12} {part.stems.sum():4}  {where}")
