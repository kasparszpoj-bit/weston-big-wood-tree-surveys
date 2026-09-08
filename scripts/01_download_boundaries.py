"""Download the Natural England boundary layers for Weston Big Wood.

Run:
    python scripts/01_download_boundaries.py

Writes data/external/boundaries.gpkg with three layers: the SSSI boundary, the
four management units, and the Ancient Woodland Inventory around the site.

A GeoPackage is used rather than a shapefile. Shapefiles truncate field names
to 10 characters, cannot store a real date type, and are actually a scatter of
several files that get separated. A GeoPackage is one file that holds several
layers with their types and CRS intact.
"""

from wbw import naturalengland as ne
from wbw.config import DATA_EXTERNAL, SSSI_AREA_HA, ensure_output_dirs

# How far beyond the site to fetch neighbouring woodland, in metres.
SEARCH_BUFFER_M = 500

OUTPUT = DATA_EXTERNAL / "boundaries.gpkg"


def main() -> None:
    ensure_output_dirs()

    print("Fetching SSSI boundary ...")
    sssi = ne.fetch_sssi_boundary()
    area_ha = sssi.geometry.area.sum() / 10_000
    print(f"  {len(sssi)} polygon, {area_ha:.2f} ha")

    # The published MEASURE attribute is Natural England's own area figure.
    # Comparing it against the geometry is a cheap check that the download
    # arrived in the CRS we asked for. In degrees the area would be tiny.
    published = float(sssi["MEASURE"].iloc[0])
    if abs(area_ha - published) > 0.1:
        raise SystemExit(
            f"Geometry area {area_ha:.2f} ha disagrees with the published "
            f"MEASURE of {published:.2f} ha. Check the CRS of the download."
        )
    print(f"  matches the published area of {published:.2f} ha")

    print("Fetching SSSI management units ...")
    units = ne.fetch_sssi_units()
    units = units.sort_values("NUMBER")
    print(f"  {len(units)} units, {units.geometry.area.sum() / 10_000:.2f} ha total")
    for _, unit in units.iterrows():
        print(
            f"    unit {unit['NUMBER']}: {unit.geometry.area / 10_000:6.2f} ha"
            f"  {unit['CONDITION']}"
        )

    print("Fetching Ancient Woodland Inventory ...")
    minx, miny, maxx, maxy = sssi.total_bounds
    envelope = (
        minx - SEARCH_BUFFER_M,
        miny - SEARCH_BUFFER_M,
        maxx + SEARCH_BUFFER_M,
        maxy + SEARCH_BUFFER_M,
    )
    woodland = ne.fetch_ancient_woodland(envelope)
    print(f"  {len(woodland)} polygons within {SEARCH_BUFFER_M} m of the site")

    # mode="w" on the first write replaces the file, so rerunning is clean.
    sssi.to_file(OUTPUT, layer="sssi_boundary", driver="GPKG", mode="w")
    units.to_file(OUTPUT, layer="sssi_units", driver="GPKG", mode="a")
    woodland.to_file(OUTPUT, layer="ancient_woodland", driver="GPKG", mode="a")

    print(f"\nWritten to {OUTPUT.relative_to(OUTPUT.parents[2])}")
    print(f"Site area for density calculations: {area_ha:.2f} ha "
          f"(config records {SSSI_AREA_HA} ha)")


if __name__ == "__main__":
    main()
