# GIS data sources and reference tools

Everything worked out on 2026-08-06 about where the external spatial data comes
from, how to get it, and the traps. All endpoints below were tested live on that
date.

Jenny recommended getting familiar with the first two tools. The third is the
one she did not mention, and it is the one that matters most for doing the work.

---

## The three tools do three different jobs

| Tool | Question it answers | What you get |
|---|---|---|
| **Designated Sites View** | "Why is this place protected, and how is it doing?" | The legal record for one site |
| **Magic Map** | "What is here?" | An interactive map browser |
| **Open Data Geoportal / API** | "Give me the actual data" | Files and features you can compute with |

The first two are things you *look at*. The third is where you *download*. That
distinction is the difference between reading a map and doing spatial analysis.
Magic can tell you Weston Big Wood is ancient woodland. Only the data can tell
you that a given transect sits 40 m outside it.

---

## 1. Natural England Designated Sites View

The official register, and the legal case file for a site.

- Site page: `https://designatedsites.naturalengland.org.uk/SiteDetail.aspx?SiteCode=S1003590`
- **Weston Big Wood site code: 1003590.** This code keys the whole Natural
  England ecosystem: the website, the Magic deep link, and the `HYPERLINK`
  field in the SSSI data layer are all the same number.

Holds the citation, the per unit condition assessments, Views About Management,
and Operations Requiring Consent.

**This is the only one of the three that can be searched by site name.** Always
start here, then follow its link out to Magic.

Natural England's own Magic link for this site, taken from that page:

```
https://magic.defra.gov.uk/MagicMap.html?startTopic=Designations
  &chosenLayers=sssiIndex&activelayer=sssiIndex&query=HYPERLINK%3D%271003590%27
```

**Still to do:** read the **favourable condition table** for this site, under
Views About Management or in the unit assessments. It gives the specific
thresholds the site is judged against, which tells you which numbers to compute.
Do this before fixing the final figure list.

---

## 2. Magic Map

Defra's viewer at `magic.defra.gov.uk`, combining layers from Natural England,
the Environment Agency, the Forestry Commission and Historic England.

### The search box does not search the map

This wasted a lot of time, so it is worth being blunt about it. **The search box
is an address and place name gazetteer.** It does not search the layers on the
map.

- `Weston Big Wood` returns nothing. A wood is not an address.
- `ST456750` returns nothing. A grid reference is not an address either.
- **`BS20 8PL` works.** Postcodes are addresses. That postcode is real and the
  wood is **396 m to the northwest** of it.

Site names live in Designated Sites View, not here.

### The eight themes

`Access`, `Administrative Geographies`, `Countryside Stewardship Targeting`,
`Designations`, `Habitats and Species`, `Land Based Schemes`, `Landscape`,
`Marine`.

Layer paths worth knowing:

```
Designations > Land-Based Designations > Statutory
    > Sites of Special Scientific Interest (England)
    > Sites of Special Scientific Interest Units (England)

Habitats and Species > Woodland
    > Ancient Woodland (England)
```

### Scale dependency, the reason layers look broken

Verified thresholds:

| Layer | Draws when |
|---|---|
| SSSI (England) **points** | zoomed out, to 1:505,001 |
| SSSI (England) **polygons** | zoomed in, from 1:505,000 |
| SSSI **Units** (England) | zoomed in from 1:505,000, **no point version at all** |

So the units layer draws absolutely nothing at national scale, with no error and
no explanation. Whenever a ticked layer shows nothing, check zoom first.

Group layers, for example `Sites of Special Scientific Interest (England)`, are
folders with no geometry. Ticking one switches on its children.

### What Magic does not have

**No public rights of way layer.** Footpaths are held by the local highway
authority, which here is **North Somerset Council**, not Defra. AWT will very
likely hold their own path network, which is worth asking Jenny for. This
matters because recreational pressure is one of the listed reasons the site is
failing, and because of the ash safety idea in brief.md.

---

## 3. Natural England open data, the ArcGIS REST API

This is where the boundaries actually came from. Same data as the website, but
as data.

Portal: `https://naturalengland-defra.opendata.arcgis.com`

Service root:

```
https://services.arcgis.com/JJzESW51TqeY9uat/arcgis/rest/services
```

Layers used, all published natively in **EPSG:27700**, so they align with the
survey coordinates with no reprojection:

| Layer | Used for |
|---|---|
| `SSSI_England` | The site boundary |
| `SSSI_Units_England` | The four management units, with `CONDITION` and `COND_DATE` |
| `Ancient_Woodland_England` | The Ancient Woodland Inventory |

Related layers that exist if ever needed: `SSSI_Impact_Risk_Zones_England`,
`Ancient_Woodland_Revised_England`.

Query pattern: filter server side with a `where` clause and an optional geometry
envelope so only the wanted features cross the network, request `outSR=27700`
and `f=geojson`, then set the CRS explicitly on the GeoDataFrame rather than
trusting the file. Implemented in `src/wbw/naturalengland.py`.

### Trap: the two layers spell the site differently

```
SSSI_England        NAME      = 'Weston Big Wood SSSI'
SSSI_Units_England  SSSI_NAME = 'Weston Big Wood'
```

One word, and the first query returned nothing. These layers are maintained by
different teams on different schedules and do not have to agree. **Search
loosely first, confirm what came back, then filter exactly.**

Also note `REF_CODE` is an internal identifier (1001368 here) and is **not** the
Designated Sites View code. That lives in `HYPERLINK`.

---

## 4. Environment Agency LIDAR, for the terrain analysis

Needed for the survey coverage work in section 13 of pre_analysis_findings.md.

```
https://environment.data.gov.uk/spatialdata/
  lidar-composite-digital-terrain-model-dtm-1m/
```

- `/wms` serves images. Layers include `Lidar_Composite_DTM_1m`,
  `Lidar_Composite_Elevation_DTM_1m`, `Lidar_Composite_Hillshade_DTM_1m`. The
  hillshade makes a good map background.
- `/wcs` serves the **actual elevation values**, which is what slope needs.
- 1 m resolution, ample for a site of 915 m by 854 m.
- Use the DTM (bare earth), not a DSM, or you measure the canopy.

---

## 5. Postcode lookups

`api.postcodes.io` is free, needs no key, and converts between postcodes,
latitude and longitude, and OS eastings and northings. Used to find `BS20 8PL`
by reverse geocoding the site centroid. Useful for navigation anchors and for
sanity checking coordinates.

---

## Coordinate reference systems, in one place

Everything in this project is **EPSG:27700, OSGB36 British National Grid**:
the survey coordinates, the Natural England layers, and the LIDAR.

- Coordinates are in **metres**, so distances and areas compute directly.
- Nothing needs reprojecting, which removes a whole category of error.
- **Trap:** converting to WGS84 for a web basemap (EPSG:3857 / 4326) is not a
  simple shift. It needs the OSTN15 grid shift, which pyproj applies correctly
  only if the CRS is declared as EPSG:27700 rather than hand rolled. Never
  reproject by arithmetic.

Magic shows live British National Grid coordinates in its status bar, which is
directly comparable to values like `345250 175050` on the survey sheets. Handy
for checking a transect location without writing code.
