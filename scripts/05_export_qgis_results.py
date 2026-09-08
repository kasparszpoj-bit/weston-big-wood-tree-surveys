"""Export per-transect results as a QGIS-ready layer.

Run:  python scripts/05_export_qgis_results.py

Writes data/external/survey_results.gpkg with one layer, `results`, holding
all 49 planned 100 m squares. The 20 surveyed squares carry every metric
needed for the maps in the brief; the 29 unsurveyed squares carry NULL, so
QGIS draws nothing for them and the hatched `plan_cells` layer underneath
shows through as "not surveyed".

One layer, many fields, so each map in the report is the same layer styled on
a different field rather than a new export each time.
"""

import geopandas as gpd
import numpy as np

from wbw.config import DATA_EXTERNAL, SURVEY_WORKBOOK
from wbw.ingest import ESTABLISHED, read_workbook
from wbw.locations import grid_cell, planned_points, surveyed_points

SEEDLING_CLASSES = ["seedling_le100", "seedling_gt100"]

table, _, _ = read_workbook(SURVEY_WORKBOOK)
live = table[~table["dead"]]
dead = table[table["dead"]]
est = live[live["size_class"].isin(ESTABLISHED)]

# Each transect samples 200 m2, so stems per hectare is count x 50.
PER_HA = 50


def shannon(group):
    """Shannon diversity H' of established stems, by species."""
    p = group.groupby("species")["stems"].sum()
    p = p[p > 0] / p.sum()
    return float(-(p * np.log(p)).sum())


def by_transect(frame, column="stems"):
    return frame.groupby("transect")[column].sum()


metrics = {
    # Density
    "est_stems": by_transect(est),
    "est_per_ha": by_transect(est) * PER_HA,
    "seedlings": by_transect(live[live.size_class.isin(SEEDLING_CLASSES)]),
    # Diversity
    "richness": est.groupby("transect")["species"].nunique(),
    "shannon": est.groupby("transect").apply(shannon, include_groups=False),
    "n_classes": live.groupby("transect")["size_class"].nunique(),
    # Deadwood
    "dead_total": by_transect(dead),
    "dead_standing": by_transect(dead[dead.species == "Dead standing"]),
    "dead_fallen": by_transect(dead[dead.species == "Dead fallen"]),
    # Notified indicator species
    "lime_est": by_transect(est[est.species == "Small-leaved Lime"]),
    "lime_young": by_transect(
        live[(live.species == "Small-leaved Lime")
             & live.size_class.isin(SEEDLING_CLASSES + ["sapling"])]),
    "wild_service": by_transect(live[live.species == "Wild Service Tree"]),
    # Non-natives. Substring match: the workbook says "Sycamore (tree)".
    "non_native": by_transect(
        live[live.species.str.contains("sycamore|holm oak|buddleia|laurel",
                                       case=False, regex=True)]),
}

plan = planned_points()
pts = surveyed_points(SURVEY_WORKBOOK)
plan = plan.merge(pts[["easting", "northing", "transect"]],
                  on=["easting", "northing"], how="left")
plan["surveyed"] = plan["transect"].notna()

for name, series in metrics.items():
    # Surveyed squares with no records of that type get 0, not NULL.
    values = plan["transect"].map(series)
    plan[name] = np.where(plan.surveyed, values.fillna(0), np.nan)

plan["label"] = plan["transect"].fillna("")

results = gpd.GeoDataFrame(
    plan.drop(columns=["transect"]),
    geometry=[grid_cell(e, n) for e, n in zip(plan.easting, plan.northing)],
    crs="EPSG:27700")

out = DATA_EXTERNAL / "survey_results.gpkg"
out.unlink(missing_ok=True)
results.to_file(out, layer="results", driver="GPKG")

print(f"wrote {out}")
print(f"{len(results)} squares, {int(results.surveyed.sum())} with data\n")
print("field            surveyed range")
for name in metrics:
    col = results.loc[results.surveyed, name]
    print(f"  {name:14} {col.min():7.2f} to {col.max():8.2f}")
