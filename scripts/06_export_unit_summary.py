"""Export the four SSSI management units as a QGIS layer with results attached.

Run:  python scripts/06_export_unit_summary.py

Writes data/external/management_units.gpkg (layer `units`): the Natural
England unit polygons carrying their condition assessment plus the survey
results for each, so the analysis can be read in the format the regulator
assesses in.

Also records why unit 3 has no data. Five of the six planned squares
covering it contain rock faces, so it is unsampled because it is the quarry
and scarp, not because of a scheduling gap.
"""

import geopandas as gpd
import numpy as np
import pandas as pd

from wbw.config import DATA_EXTERNAL, SURVEY_WORKBOOK
from wbw.ingest import ESTABLISHED, read_workbook
from wbw.locations import surveyed_points

# A planned square counts as "covering" a unit if at least this share of it
# lies inside. Without a threshold, squares that merely clip a corner count.
COVERAGE_THRESHOLD = 0.10
PER_HA = 50

units = gpd.read_file(DATA_EXTERNAL / "boundaries.gpkg", layer="sssi_units")
cells = gpd.read_file(DATA_EXTERNAL / "survey_plan.gpkg", layer="plan_cells")

table, _, _ = read_workbook(SURVEY_WORKBOOK)
live = table[~table["dead"]]
dead = table[table["dead"]]
est = live[live["size_class"].isin(ESTABLISHED)]

pts = surveyed_points(SURVEY_WORKBOOK)
starts = gpd.GeoDataFrame(
    pts, geometry=gpd.points_from_xy(pts.easting, pts.northing),
    crs="EPSG:27700")


def shannon(group):
    p = group.groupby("species")["stems"].sum()
    p = p[p > 0] / p.sum()
    return float(-(p * np.log(p)).sum())


rows = []
for _, u in units.sort_values("NUMBER").iterrows():
    geom = u.geometry
    number = int(u["NUMBER"])

    inside = starts[starts.within(geom)]
    trs = inside["transect"].tolist()

    share = cells.geometry.intersection(geom).area / cells.geometry.area
    covering = cells[share >= COVERAGE_THRESHOLD]

    est_u = est[est.transect.isin(trs)]
    dead_u = dead[dead.transect.isin(trs)]
    n = len(trs)

    rows.append({
        "unit": number,
        "area_ha": round(geom.area / 1e4, 2),
        "condition": u["CONDITION"].title(),
        # Natural England serve the assessment date as epoch milliseconds.
        "assessed": pd.to_datetime(u["COND_DATE"], unit="ms").strftime("%d %b %Y"),
        "transects": n,
        "sampled": bool(n),
        "planned_squares": len(covering),
        "cliff_squares": int(covering["contains_cliff"].sum()),
        "est_stems_ha": round(est_u.stems.sum() * PER_HA / n) if n else None,
        "species_richness": int(est_u.species.nunique()) if n else None,
        "shannon_mean": round(est_u.groupby("transect")
                              .apply(shannon, include_groups=False).mean(), 2)
        if n else None,
        "dead_standing": int(dead_u[dead_u.species == "Dead standing"].stems.sum())
        if n else None,
        "dead_fallen": int(dead_u[dead_u.species == "Dead fallen"].stems.sum())
        if n else None,
        "lime_established": int(est_u[est_u.species == "Small-leaved Lime"].stems.sum())
        if n else None,
        "transect_list": ", ".join(sorted(trs, key=lambda t: int(t[1:]))),
    })

out_gdf = gpd.GeoDataFrame(
    pd.DataFrame(rows),
    geometry=units.sort_values("NUMBER").geometry.values,
    crs="EPSG:27700")

out = DATA_EXTERNAL / "management_units.gpkg"
out.unlink(missing_ok=True)
out_gdf.to_file(out, layer="units", driver="GPKG")

print(f"wrote {out}\n")
show = ["unit", "area_ha", "transects", "planned_squares", "cliff_squares",
        "est_stems_ha", "species_richness", "lime_established"]
print(out_gdf[show].to_string(index=False))
print()
for r in out_gdf.itertuples():
    if not r.sampled:
        print(f"unit {r.unit} is unsampled: {r.cliff_squares} of its "
              f"{r.planned_squares} covering squares contain a rock face")
