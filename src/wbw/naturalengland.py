"""Download boundary layers from Natural England's open data services.

Natural England publish their spatial data through an ArcGIS REST API. The
same data sits behind the Designated Sites View website and behind Magic Map,
but querying the API directly means the boundaries arrive as data rather than
as a picture, and the download is repeatable rather than a manual click.

Every layer here is published in British National Grid (EPSG:27700), the same
grid the survey coordinates use, so nothing needs reprojecting.

Service root:
https://services.arcgis.com/JJzESW51TqeY9uat/arcgis/rest/services
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request

import geopandas as gpd

from wbw.config import CRS_BNG

SERVICE_ROOT = "https://services.arcgis.com/JJzESW51TqeY9uat/arcgis/rest/services"

# Layer names as published by Natural England.
SSSI_LAYER = "SSSI_England"
SSSI_UNITS_LAYER = "SSSI_Units_England"
ANCIENT_WOODLAND_LAYER = "Ancient_Woodland_England"

# Weston Big Wood, as it appears in the SSSI layer. The site code used by the
# Designated Sites View website (1003590) is stored in the HYPERLINK field,
# not in REF_CODE, which holds a different internal identifier.
SITE_NAME = "Weston Big Wood SSSI"
DESIGNATED_SITES_CODE = "1003590"

# The units layer names the same site without the "SSSI" suffix. The two
# layers are maintained separately, so their name fields do not have to agree.
SITE_NAME_IN_UNITS = "Weston Big Wood"

_TIMEOUT_SECONDS = 120


def query_layer(
    layer: str,
    where: str = "1=1",
    geometry_envelope: tuple[float, float, float, float] | None = None,
) -> gpd.GeoDataFrame:
    """Fetch features from a Natural England layer as a GeoDataFrame.

    `where` is a SQL style filter applied by the server, so only the wanted
    features cross the network. `geometry_envelope` is an optional
    (minx, miny, maxx, maxy) box in British National Grid, used to fetch only
    features near the site rather than all of England.

    The server is asked for outSR=27700 so the geometry arrives in British
    National Grid. GeoJSON nominally implies WGS84, so the CRS is set
    explicitly on the result rather than trusted from the file.
    """
    params = {
        "where": where,
        "outFields": "*",
        "returnGeometry": "true",
        "outSR": "27700",
        "f": "geojson",
    }

    if geometry_envelope is not None:
        minx, miny, maxx, maxy = geometry_envelope
        params["geometry"] = f"{minx},{miny},{maxx},{maxy}"
        params["geometryType"] = "esriGeometryEnvelope"
        params["inSR"] = "27700"
        params["spatialRel"] = "esriSpatialRelIntersects"

    url = f"{SERVICE_ROOT}/{layer}/FeatureServer/0/query?{urllib.parse.urlencode(params)}"

    with urllib.request.urlopen(url, timeout=_TIMEOUT_SECONDS) as response:
        payload = json.load(response)

    if "error" in payload:
        raise RuntimeError(f"Natural England API error for {layer}: {payload['error']}")

    features = payload.get("features", [])
    if not features:
        raise RuntimeError(f"No features returned from {layer} for where={where!r}")

    return gpd.GeoDataFrame.from_features(features, crs=CRS_BNG)


def fetch_sssi_boundary() -> gpd.GeoDataFrame:
    """The Weston Big Wood SSSI polygon.

    Jenny could not supply an AWT reserve boundary, and said the SSSI polygon
    "is very nearly our boundary, so will do for the time being". It is a
    stand-in, not the reserve, and every area figure derived from it must be
    labelled as the SSSI boundary.
    """
    return query_layer(SSSI_LAYER, where=f"NAME = '{SITE_NAME}'")


def fetch_sssi_units() -> gpd.GeoDataFrame:
    """The four management units, with their condition assessments.

    Natural England assess and report condition per unit, so results broken
    down this way are directly usable by AWT. The CONDITION and COND_DATE
    fields carry the assessment, so the grades do not have to be copied by
    hand from the website.
    """
    return query_layer(SSSI_UNITS_LAYER, where=f"SSSI_NAME = '{SITE_NAME_IN_UNITS}'")


def fetch_ancient_woodland(
    envelope: tuple[float, float, float, float],
) -> gpd.GeoDataFrame:
    """Ancient Woodland Inventory polygons intersecting the given box.

    Used to check whether all 20 transects fall within ancient woodland. Q3 is
    the one to look at, since its hawthorn dominance suggests former open
    ground rather than woodland interior.
    """
    return query_layer(ANCIENT_WOODLAND_LAYER, geometry_envelope=envelope)
