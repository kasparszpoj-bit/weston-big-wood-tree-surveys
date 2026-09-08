"""Terrain analysis of the survey plan, and QGIS-ready layers.

Run:  python scripts/04_terrain_and_qgis_layers.py

Reads the EA 1 m LIDAR DTM tile (data/external/dtm_1m.tif, downloaded via
WCS; bounding box 345000-346150 E, 174500-175600 N), computes slope, and
answers the question behind the coverage map: are the 29 unsurveyed squares
actually the steep ones?

Writes data/external/survey_plan.gpkg with three layers for QGIS styling:
    plan_cells      the 49 100 m squares: surveyed, mean/max slope, steep flag
    transect_lines  the 49 planned 50 m transects on their bearings
    start_points    the 49 start coordinates

Also prints the surveyed-vs-unsurveyed slope comparison for the report.
"""

import geopandas as gpd
import numpy as np
import tifffile

from wbw.config import DATA_EXTERNAL, SURVEY_WORKBOOK
from wbw.locations import grid_cell, planned_points, surveyed_points, transect_line

# The WCS request that produced the tile fixes its georeferencing.
WEST, EAST = 345_000, 346_150
SOUTH, NORTH = 174_500, 175_600

# The discriminator that works is cliff PRESENCE, not average steepness:
# mean slope barely differs between surveyed and unsurveyed squares (12.2 vs
# 12.7 deg), but a maximum slope above 60 deg means the square contains a
# rock face, and those are five times as frequent in the unsurveyed set
# (8 of 29 vs 1 of 20). Threshold stated on the figure so it can be argued with.
CLIFF_MAX_DEG = 60


def load_slope():
    z = tifffile.imread(DATA_EXTERNAL / "dtm_1m.tif").astype(float)
    # GeoServer nodata arrives as large negative values.
    z[z < -1000] = np.nan
    # Row 0 is the northern edge, so northing decreases with row index.
    dz_north, dz_east = np.gradient(z, -1.0, 1.0)
    return np.degrees(np.arctan(np.hypot(dz_east, dz_north)))


def cell_stats(slope, easting, northing):
    """Mean and max slope inside the 100 m square centred on a point."""
    col0, col1 = int(easting - 50 - WEST), int(easting + 50 - WEST)
    row0 = int(NORTH - (northing + 50))
    row1 = int(NORTH - (northing - 50))
    window = slope[row0:row1, col0:col1]
    return float(np.nanmean(window)), float(np.nanmax(window))


slope = load_slope()
plan = planned_points()
pts = surveyed_points(SURVEY_WORKBOOK)
plan = plan.merge(pts[["easting", "northing", "transect"]],
                  on=["easting", "northing"], how="left")
plan["surveyed"] = plan["transect"].notna()

stats = [cell_stats(slope, e, n) for e, n in zip(plan.easting, plan.northing)]
plan["mean_slope_deg"] = [round(m, 1) for m, _ in stats]
plan["max_slope_deg"] = [round(x, 1) for _, x in stats]
plan["contains_cliff"] = plan["max_slope_deg"] > CLIFF_MAX_DEG

# Three-way category for the map legend.
plan["status"] = np.where(
    plan.surveyed, "surveyed",
    np.where(plan.contains_cliff,
             "not surveyed - contains cliff",
             "not surveyed - no clear obstacle"),
)

cells = gpd.GeoDataFrame(
    plan.drop(columns="transect").assign(label=plan.transect.fillna("")),
    geometry=[grid_cell(e, n) for e, n in zip(plan.easting, plan.northing)],
    crs="EPSG:27700")
lines = gpd.GeoDataFrame(
    plan[["easting", "northing", "bearing", "surveyed", "status"]],
    geometry=[transect_line(e, n, b)
              for e, n, b in zip(plan.easting, plan.northing, plan.bearing)],
    crs="EPSG:27700")
points = gpd.GeoDataFrame(
    plan[["easting", "northing", "surveyed", "status"]],
    geometry=gpd.points_from_xy(plan.easting, plan.northing), crs="EPSG:27700")

out = DATA_EXTERNAL / "survey_plan.gpkg"
# Remove the file first: mode="w" replaces one layer, not the whole package,
# so a rerun would otherwise append duplicate rows to the other layers.
out.unlink(missing_ok=True)
cells.to_file(out, layer="plan_cells", driver="GPKG", mode="w")
lines.to_file(out, layer="transect_lines", driver="GPKG", mode="a")
points.to_file(out, layer="start_points", driver="GPKG", mode="a")
print(f"wrote {out}\n")

# ------------------------------------------------ the comparison ----------
surveyed = plan[plan.surveyed]
unsurveyed = plan[~plan.surveyed]
print("Slope of 100 m squares (EA LIDAR 1 m DTM):")
print(f"  surveyed   (n={len(surveyed)}):  "
      f"mean {surveyed.mean_slope_deg.mean():.1f} deg,  "
      f"range {surveyed.mean_slope_deg.min():.1f}-{surveyed.mean_slope_deg.max():.1f}")
print(f"  unsurveyed (n={len(unsurveyed)}):  "
      f"mean {unsurveyed.mean_slope_deg.mean():.1f} deg,  "
      f"range {unsurveyed.mean_slope_deg.min():.1f}-{unsurveyed.mean_slope_deg.max():.1f}")
print(f"\n  squares containing a cliff face (max slope > {CLIFF_MAX_DEG} deg):")
print(f"    unsurveyed: {int(unsurveyed.contains_cliff.sum())} of {len(unsurveyed)}")
print(f"    surveyed:   {int(surveyed.contains_cliff.sum())} of {len(surveyed)}")
print("\nSteepest five unsurveyed squares:")
top = unsurveyed.nlargest(5, "mean_slope_deg")
for _, r in top.iterrows():
    print(f"  {int(r.easting)} {int(r.northing)}  "
          f"mean {r.mean_slope_deg} deg, max {r.max_slope_deg} deg")
