# The brief

Source: email from Jenny Greenwood, 5 August 2026, 16:12. Reproduced and
structured here. Her words are paraphrased except where marked as quoted.

## The data

- Roughly **20 survey sheets** written up. Jenny thinks there should be **22**,
  with 2 not written up. She could not check before going away, so those two may
  turn up later and need incorporating.
- The survey is grid square based. The **central grid reference of each grid
  square is written on each survey sheet**.
- The **numbers on the maps correspond to the central grid reference and the
  bearing of each transect**.
- **Not all grid references were accessible.** Cliffs and similar terrain meant
  some squares could not be surveyed. So gaps in coverage are real, not data
  loss, and the maps should not imply zero trees where there was no access.
- Forms were **mostly completed on paper in the field**, then written up.
- A **methodology document** is included in the shared folder.

## The tally notation

Trees were recorded in three categories:

- **Single stemmed trees**: tallied as a plain number.
- **Coppice**: marked with a **C**.
- **Multistemmed**: marked with an **M**.

Values are comma separated in the written up version. Jenny's own examples,
quoted:

> 2, C, 2M is 3 single stem trees, 1 coppice, 2 multistem
>
> 2C, 2M is 2 coppice, 2 multistem, no single stem

> For most analyses, the numbers of trees of each type can just be summed (so 5
> in the first example, 4 in the second).

### Resolved: the first example did not add up

The second example is internally consistent: 2 coppice plus 2 multistem is 4,
which matches her stated total.

The first was not. If `2, C, 2M` means 2 single stem, 1 coppice and 2
multistem, the total is 5, which matches her stated total of 5. But she writes
"3 single stem trees", which would make the total 6.

**Jenny confirmed 2 single stems on 14 August 2026.** "3 single stem trees" was
a slip; her stated total of 5 is correct. The parser was already written that
way, so no counts changed. A bare number means exactly that many single stems.

## What Jenny wants to see

The requested outputs, given as an initial list with an explicit invitation to
go further: "Feel free to play around with the data as much as you like and with
the visualization too."

Maps:

- **Density maps of trees per hectare**
- **Diversity of species**, mapped
- **Diversity of age classes**, mapped
- **Distribution of dead wood**
- **Distribution of lime and wild service tree**
- **Any invasive trees** that may have been recorded

- **Heat maps** (added by Jenny after the original email)

Graphs:

- **Age classes split by species**

See data_audit.md for the heat map constraint. The survey is 20 points over
1.06% of the site, so a gridded 100 m choropleth is the defensible version and
any smoothed surface must be captioned as indicative.

## Why these specific outputs matter

This is the part Jenny did not spell out, but the Natural England data makes it
obvious. See site_dossier.md for the detail.

All four management units of the SSSI are currently **Unfavourable and
Declining**. The two stated reasons are **ash dieback** damaging composition and
**insufficient standing deadwood** damaging structure.

So:

- Deadwood distribution addresses a named, written reason the site is failing.
- Age classes split by species addresses the other one, since ash dieback raises
  the question of what is regenerating underneath the dying ash.
- Lime and wild service are the two ancient woodland indicator species the SSSI
  was notified for in the first place.
- The coppice and multistem categories map onto the citation's description of
  coppice and maiden ash, and the heterogeneous oak structure.

The analysis is therefore evidence for SSSI condition assessment, not a generic
mapping exercise. Frame it that way in the write up and in any CV bullet.

## What each figure is actually for

Worked out 2026-08-06. The useful reframe is that none of these are decoration.
Each one supports a decision AWT genuinely has to make about this wood.

| Figure | The decision it supports |
|---|---|
| Density, trees per hectare | Baseline stocking, and where the wood is thin. Thin patches may be where ash has already gone, so it points at where intervention is needed |
| Species diversity mapped | Composition is a notified feature. Operationally it finds species-poor compartments, and low diversity plus hazel dominance is the signature of neglected coppice |
| Age class diversity mapped | Structural diversity is a Natural England condition attribute, and fundamentally a **resilience** question. A single-aged wood loses its canopy to one disease event. This is the ash dieback resilience map |
| Deadwood distribution | A named failure reason, so regulatory. Also operational: shows **where the gaps are** so AWT knows where to retain or create standing deadwood |
| Lime and wild service | Legally notified features, but practically a **constraint map**. Before any felling, thinning or path work, somebody needs to know where the irreplaceable trees are. Probably the most useful output day to day |
| Invasive trees | Standard condition attribute, and early detection is when control is cheap. 16 records out of 3,218, about 0.5%, is good news worth stating with a number |
| Age classes split by species | The most informative graph in the set. Answers "what does this wood become in fifty years". On current numbers: no oak saplings at all, and the two best represented successors both under disease pressure |
| Heat maps | Added by Jenny afterwards, which is a **communication** signal. She is thinking about trustees, funders and members, not just ecologists |

The deadwood point is worth drawing out. The finding that standing dead exists
but **nothing above 50 cm** turns a vague regulatory failure into a specific,
cheap, actionable instruction: stop felling the big dead ones.

## What else she might want, that she did not ask for

In rough order of value.

**A survey coverage map.** Confirmed as wanted. See section 13 of
pre_analysis_findings.md. Cheapest map in the project and immediately useful for
planning the next field season.

**Large ash near paths and boundaries.** The one nobody has raised, and the only
output with a budget attached. Ash dieback makes ash brittle and prone to sudden
failure, and landowners have a duty of care where the public go. Recreational
pressure is already a listed reason the site is failing, so people clearly
visit. A map of large standing ash relative to the path network is a safety and
cost planning tool. **Needs AWT's path data**, since public rights of way are
not on Magic. Worth asking Jenny for.

**The regeneration bottleneck plot.** Seedling to sapling ratio by species. One
chart, and it is where the ash story lives: 912:1 against 2:1 to 29:1 for every
other species in the same wood.

**Coppice stool size distribution.** Large stool diameter is a rough proxy for
time since last cutting, so this estimates **when coppicing stopped**. Directly
informs whether to restore coppicing, which is a live question in a wood that is
79% coppiced hazel with lime stools that would respond well to it.

**Holly expansion.** 433 seedlings, 55 already in the small class, zero mature.
A young expanding population casting dense evergreen shade, in a wood notified
partly for ground flora including two colonies of a Red Data Book species.
Nobody is tracking this and it is not on Natural England's pressure list.

**A per unit summary table.** Not a figure, just the headline numbers broken
down by the four management units. This is what she can put straight into a
conversation with Natural England, because units are the currency of that
conversation.

**Say explicitly that the pipeline reruns.** When the two missing sheets turn
up, or the survey is finished, or it is repeated in five years, the numbers
regenerate. That converts a one off snapshot into the first point of a time
series, and no trend can be claimed from a single survey.

## Tooling constraint

**Jenny has asked that the analysis is done in Python.** Not R, not QGIS
point and click. This is a requirement, not a preference, so the whole pipeline
needs to be scripted.

Practical consequence: the stack is geopandas for the spatial work, pandas for
the tally parsing and tabulation, matplotlib for the graphs, and contextily or
plain geopandas plotting for the maps. QGIS is still useful for eyeballing the
data and checking alignment, but the deliverables must come out of code.

This is good news for the portfolio. A scripted, reproducible pipeline in a
public repository is far stronger evidence than a folder of exported PNGs, and
Python plus geopandas is what most UK geospatial job ads actually ask for. See
01_uk_data_science_goal/skills_gap.md.

## Scoping notes

**Report by management unit, not just whole site.** The SSSI has four units, and
Natural England assesses condition per unit. Joining the survey grid squares to
the unit boundaries, which are downloadable as open data, would let the outputs
be reported in the format AWT actually needs. Whole site averages are less
useful to them.

**Establish the survey date.** Jenny said "it's a while since I collected this
data". If the survey predates or straddles the worst of the ash dieback, the ash
figures are a historic baseline rather than current condition. That needs
stating explicitly in the outputs rather than being quietly presented as now.

**Coordinate system. Confirmed by Jenny: OSGB36.** So the grid references are OS
British National Grid, EPSG:27700. The Natural England layers are published in
the same CRS, so everything aligns with no transformation. The alphanumeric
refs, ST 456 750 style, still need converting to numeric eastings and northings
before anything can be plotted.

One trap. If any output is ever put on a web basemap, that is WGS84 web
mercator, EPSG:3857, and the OSGB36 to WGS84 conversion is not a simple shift.
Doing it properly needs the OSTN15 grid shift, which pyproj handles if the CRS
is declared as EPSG:27700 rather than hand rolled. Declare the CRS explicitly
and never reproject by arithmetic.

## Site boundary: none supplied, use a stand-in

Jenny could not put an AWT site boundary together before going away, and said
so. Her instruction, quoted:

> Natural England have a SSSI layer through their open data, and the Weston Big
> Wood polygon is very nearly our boundary, so will do for the time being!

So the SSSI polygon from Natural England open data is the working boundary. Two
consequences worth being deliberate about:

- "Very nearly" is not "exactly". The AWT reserve and the SSSI are different
  things with different edges. Any trees per hectare figure depends on the
  denominator, so the area used must be stated explicitly in the outputs, and
  labelled as the SSSI boundary rather than the reserve boundary.
- Ask for the real boundary later and rerun. If the pipeline is scripted the
  boundary is one input file, so swapping it should be a one line change. Build
  it that way from the start.

**Transect bearings.** The maps encode a bearing per transect. Worth clarifying
what the transects are: fixed length, variable, belt or line. That determines
whether density is per grid square or per unit area of transect, which changes
the trees per hectare calculation completely.

## Questions to send Jenny before Friday 7 August

**SUPERSEDED. The raw data answered several of these. See the revised list at
the end of data_audit.md. Original list kept below for the record.**

1. The `2, C, 2M` example: is it 2 single stem or 3? The stated total of 5
   suggests 2.
2. What are the transect dimensions? Length and width, or is it a point count?
   Needed to calculate trees per hectare correctly.
3. What year, or what range of years, was the survey carried out?
4. Was deadwood recorded as standing, fallen, or both, and how?
5. Are age classes recorded per tree or estimated per species per square?
6. For the inaccessible grid squares, are they marked as not surveyed anywhere,
   or simply absent from the sheets?
