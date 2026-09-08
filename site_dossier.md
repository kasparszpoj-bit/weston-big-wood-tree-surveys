# Weston Big Wood SSSI: site dossier

Compiled 5 August 2026 from the Natural England Designated Sites View, the
official SSSI citation, and the unit condition report.

Source page:
https://designatedsites.naturalengland.org.uk/SiteDetail.aspx?SiteCode=S1003590

The citation PDF is saved in this folder as
`weston_big_wood_sssi_citation_1984.pdf`.

## Site facts

| Field | Value |
|---|---|
| Site name | Weston Big Wood SSSI |
| Site code | S1003590 |
| Designation | Site of Special Scientific Interest |
| Area | 37.66 ha (citation states 37.48 ha, 92.61 acres) |
| County | Avon |
| Local authority | North Somerset (citation: Woodspring District) |
| Central grid reference | ST 456 750 (citation: ST 455750) |
| National Character Area | Bristol, Avon Valleys and Ridges |
| OS sheets | 1:50,000 sheet 155. 1:10,000 ST 47 NE and ST 47 SE |
| First notified | 1971 under the 1949 Act, revised 1974 |
| Renotified | 3 January 1984 under the Wildlife and Countryside Act 1981 |
| Status | Live, biological interest |
| Monitored features | 2 |
| Management units | 4 |
| Identified pressures | 2 |
| Responsible team | Natural England Wessex |
| Contact | ProtectedSites@naturalengland.org.uk |

The small area discrepancy between the 1984 citation and the current portal
figure is normal, and reflects boundary redigitising rather than a change to
the site.

## Why it is designated: the 1984 citation

Quoted and summarised from the official citation document.

**Overall.** A fine example of mixed deciduous woodland with a rich variety of
plant species. It occupies largely uncultivatable land across two parishes. Its
shape, its name, the heterogeneous structure of the oaks, the presence of
ancient woodland indicator species and the historical record all point to it
being the remnant of an ancient forest.

**Geology and soils.** The plateau and steeply sloping flanks of a narrow ridge
of Carboniferous Limestone. Well drained calcareous to mildly acidic clay loams
over a layer of limestone fragments.

**Tree layer.**

- Dominated by **pedunculate oak**, occurring as open canopy mature standards.
- Together with **coppice and maiden ash**.
- Discrete blocks containing abundant **wild cherry**, **wych elm** and **lime**.

**Trees of particular interest.**

- **Small-leaved lime**, *Tilia cordata*: ancient woodland indicator, locally
  abundant.
- **Wild service tree**, *Sorbus torminalis*: ancient woodland indicator,
  locally abundant.
- Rare whitebeams *Sorbus rupicola* and *Sorbus eminens*.
- The hybrid between common whitebeam and wild service, *Sorbus aria* x
  *torminalis*.

**Ground flora.** Includes two colonies of **purple gromwell**, *Buglossoides
purpurocaerulea*, a Red Data Book species.

## Current condition: all four units failing

Assessed April 2023. Every unit is classed **Unfavourable and Declining**.

| Unit | Area (ha) | Habitat | Condition | Assessed |
|---|---|---|---|---|
| 001 | 15.6865 | Broadleaved, mixed and yew woodland, lowland | Unfavourable, declining | 05/04/2023 |
| 002 | 7.9716 | Broadleaved, mixed and yew woodland, lowland | Unfavourable, declining | 05/04/2023 |
| 003 | 1.9044 | Broadleaved, mixed and yew woodland, lowland | Unfavourable, declining | 12/04/2023 |
| 004 | 12.0953 | Broadleaved, mixed and yew woodland, lowland | Unfavourable, declining | 12/04/2023 |

Unit areas sum to 37.6578 ha, matching the portal total.

**Stated reasons for the downgrade:**

- **Ash dieback**, affecting woodland composition.
- **Insufficient standing deadwood**, affecting woodland structure.
- **Recreational and visitor pressure**, with compaction from pedestrians and
  dogs negatively affecting tree health.
- **Honey fungus** infection.

Natural England's condition categories, for reference: Favourable,
Unfavourable Recovering, Unfavourable No Change, Unfavourable Declining,
Part Destroyed, Destroyed. Unfavourable Declining is the worst of the
non destroyed grades.

## What this means for the analysis

The overlap between Jenny's requested outputs and the official reasons for
failure is close to exact:

| Jenny's request | Corresponding designated feature or failure reason |
|---|---|
| Distribution of dead wood | "Insufficient standing deadwood" damaging structure |
| Age classes split by species | Ash dieback damaging composition, and what regenerates under it |
| Lime and wild service distribution | The two named ancient woodland indicators in the citation |
| Species diversity mapped | The "rich variety of plant species" the site was notified for |
| Coppice and multistem categories | The citation's "coppice and maiden ash" and heterogeneous oaks |
| Tree density per hectare | Baseline structure measure across the four units |

Two consequences worth acting on:

1. **Report per management unit.** Natural England assesses per unit and all
   four are failing. Outputs broken down by unit are directly usable by AWT in
   condition reporting. Whole site averages are not.

2. **Ash is the story.** If the survey captured ash before or during the worst
   of the dieback, the dataset is a baseline that cannot be recreated. That is
   worth far more than a generic density map, and it is worth saying so to
   Jenny.

## Site geometry, from the downloaded boundary

Measured from the Natural England SSSI polygon on 2026-08-06, now in
`data/external/boundaries.gpkg`. All values EPSG:27700.

| Property | Value |
|---|---|
| Area | 37.66 ha (geometry agrees with the published `MEASURE` field) |
| Perimeter | 3.75 km |
| Centroid | 345618, 175047 |
| Bounds | 345121, 174626 to 346035, 175480 |
| Extent | 915 m east to west by 854 m north to south |

For comparison, the survey transects span 345250 to 345950 east and 174750 to
175350 north, so the surveyed area sits well inside the boundary.

Unit areas from the units layer match this dossier's table to four decimal
places, and all four carry `CONDITION = UNFAVOURABLE DECLINING`.

## Ancient woodland: the site is not entirely ancient

Computed 2026-08-06 by intersecting the SSSI polygon with the Ancient Woodland
Inventory.

| | Area | Share |
|---|---|---|
| SSSI total | 37.66 ha | |
| **On the Ancient Woodland Inventory** | **35.37 ha** | **93.9%** |
| **Not on the inventory** | **2.29 ha** | **6.1%** |

The inventory's own `WESTON BIG WOOD` polygon is 36.35 ha and is classed
**Ancient and Semi-Natural Woodland**, so roughly 1 ha of it lies outside the
SSSI boundary as well.

**Why this mattered, and the answer.** Q3 was flagged in
pre_analysis_findings.md as suspicious: 35 stems but low diversity, 21 of them
hawthorn. Hawthorn dominance usually indicates former open ground or an edge
rather than woodland interior, so the hypothesis was that Q3 might fall in the
2.29 ha of the SSSI that is not on the inventory.

**TESTED 2026-08-12: the hypothesis is wrong.** A spatial join of all 20
transect start points against the Ancient Woodland Inventory puts **all 20
inside ancient woodland**, Q3 included. So Q3's hawthorn dominance is not
explained by its being outside the inventory, and some other reason (an
internal glade, a former ride, past felling) would have to account for it.

Do not repeat the "Q3 sits beside the non-ancient part" line: it was a
plausible hunch that the data does not support.

## Neighbouring designated sites

Weston Big Wood is not an isolated fragment. It sits in a cluster of designated
sites along the same limestone ridge:

- **Nightingale Valley SSSI**, immediately west
- **Weston-in-Gordano SSSI**, to the southwest
- **Seven Acre Wood**, 5.87 ha, also classed Ancient and Semi-Natural Woodland
  on the inventory

Relevant to any discussion of seed sources, connectivity and landscape context.

The **B3124** runs along the eastern edge of the wood. All eight sycamore
records in the survey came from Q17, Q19 and Q20 on that eastern edge, which is
consistent with a roadside and settlement seed source.

## One caution on the Priority Habitat Inventory

Magic shows this wood as Priority Habitat Inventory deciduous woodland, but the
`PRIMSOURCE` field reads **National Forest Inventory 2020**, which is derived
from remote sensing rather than ground survey.

So for this site, **the AWT transect data is better evidence than the national
layer**. Worth saying so in the write up, politely and with the reason, because
it makes the case for why this survey was worth doing.

## Open data to download

All free, all British National Grid (EPSG:27700), so they align with the survey
grid references.

- **SSSI boundaries** and **SSSI units**: Natural England Open Data Geoportal.
- **Ancient Woodland Inventory**: Natural England.
- **Priority Habitat Inventory**: Natural England.
- Everything is also viewable, though not always downloadable, through
  **Magic Map** at magic.defra.gov.uk.
