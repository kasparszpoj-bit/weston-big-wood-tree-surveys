# What is in this data, and what to do about it

Written before any visualisation work, 5 August 2026. Everything here comes
from a full parse of all 20 transect sheets, cross checked against the
methodology, the blank form, the sample location map, the 1984 SSSI citation
and Natural England's 2023 condition assessment.

Read this before writing plotting code. Several things below change what the
plots should be.

---

## 1. The trap you must fix first

**Coppice and multistem records are measured by stool width. Single stems are
measured by diameter at breast height. They share the same size class columns
but they are not the same measurement.**

From the methodology:

> For coppice (including natural coppice) or multistem (including pollarded)
> trees, measure the width of stool at the narrowest point between the ground
> and first branch fork.

So a hazel stool 60 cm across sits in the "Mature, <=75" column next to an oak
with a 60 cm trunk. One is a big old coppice stool about two metres tall. The
other is a canopy tree.

This matters enormously:

| Measure | Pooled | Single stems only |
|---|---|---|
| Trees over 50 cm in the large classes | 69 | **21** |
| Implied canopy density | 172 /ha | **52 /ha** |

Pooling inflates the canopy count more than threefold, mostly by promoting 16
large hazel stools into the canopy. **Every structural analysis must split
single stem from coppice and multistem.** Jenny's line that "for most analyses
the numbers can just be summed" is true for abundance and for species
composition. It is false for anything about structure, age or canopy.

This is worth telling her, and it is exactly the kind of catch that shows you
read the methodology rather than just the spreadsheet.

### What the three categories actually are

**Single stem**, also called a maiden. Grown from seed, one trunk, never cut.
Measured at diameter at breast height, 1.3 m.

**Coppice.** Deliberately cut to ground level and regrown as multiple shoots
from the cut stump, which is called a stool. The stems are young but the stool
and its root system can be centuries older. Historically this was the economic
basis of English woodland: a renewable crop of poles on a rotation of roughly 7
to 20 years.

**Multistem.** Multiple stems from one base that did not come from deliberate
coppicing. Storm damage, browsing, natural layering, pollarding (cut at head
height rather than ground level), or a species that simply grows that way.

### Why the distinction changes the ecology, not just the arithmetic

- **Diameter stops meaning age.** A 60 cm stool may carry 15 year old stems on a
  300 year old root system. For maidens, size is a rough age proxy. For coppice
  it is not.
- **Canopy position differs.** A coppice stool is usually understorey, a
  multi-stemmed shrub. A maiden of the same recorded size can be a canopy tree.
- **Deadwood futures differ.** Canopy maidens eventually become large standing
  deadwood, the habitat this site is failing on. Coppice stools rarely do.
- **Regeneration route differs.** Coppice regrowth is vegetative, so it is the
  *same individual persisting*, not a new one recruiting. Only seedlings from
  maidens represent actual reproduction.

### When Jenny's "just sum them" is right, and when it is not

She is correct, and not being careless. Summing is fine whenever the unit of
interest is a **stem**:

- Density, trees per hectare
- Species composition and relative abundance
- Species diversity indices
- Distribution maps: where lime is, where deadwood is

It breaks the moment size is used as a proxy for age or canopy position. Note
that the columns wear age names (Seedlings, Saplings, Mature, Overmature,
Ancient/veteran) but are **defined by size thresholds**. They are size classes
with age labels, which is normal survey practice but only reads as age for
maidens.

**And the catch bites on her own request.** She asked for age classes split by
species. That is precisely the analysis where pooling misleads.

**Tone note for the write up.** Do not present this as a correction. Present
it as a choice with a reason, and show both versions: "I have split single stem
from coppice for the age class figures, because stool width and dbh are not
comparable and pooling roughly triples the apparent canopy. Summed totals are
used everywhere else as you suggested." The brief was written from memory,
four years after the fieldwork.

---

## 2. The headline: this wood has no next generation of canopy trees

This is the most important thing in the dataset, and it is not what the site is
currently failing on.

### Oak is not regenerating at all

The 1984 citation says the wood is "dominated by Pedunculate Oak, which occurs
as open-canopy mature standards".

| Native oak | Count across 0.40 ha |
|---|---|
| Seedlings | 5 |
| **Saplings (3 to 7 cm)** | **0** |
| Small (<25 cm) | 2 |
| Established total | 34 |
| In the large classes (>50 cm) | 20 |

Oak is present on 16 of 20 transects, so the standards are still there. **There
is not a single oak sapling in the entire survey.** Sessile Oak has zero
seedlings, zero saplings and zero small trees: seven established stems and
nothing behind them.

Oak regenerating poorly under its own shade is normal woodland ecology. Oak
regenerating at literally zero across a whole site, in a wood notified for its
oak, is a finding. When the current standards go, on present evidence nothing
replaces them with oak.

### Ash has a bottleneck of a different kind

| Species | Seedlings | Saplings | Ratio |
|---|---|---|---|
| **Ash** | **1,824** | **2** | **912 : 1** |
| Holly | 433 | 15 | 29 : 1 |
| Field Maple | 55 | 7 | 8 : 1 |
| Hawthorn | 123 | 17 | 7 : 1 |
| Small-leaved Lime | 13 | 3 | 4 : 1 |
| Hazel | 29 | 10 | 3 : 1 |
| Wych Elm | 29 | 12 | 2 : 1 |

Ash is a masting species and huge seedling banks that mostly die are normal, so
some of this gap is natural. But every other species on the site converts
seedlings to saplings at between 2:1 and 29:1. Ash is at 912:1. That is two
orders of magnitude out of line with its neighbours in the same wood.

**The obvious hypothesis is ash dieback killing young ash before they reach
7 cm.** *Hymenoscyphus fraxineus* kills saplings faster than mature trees. If
that is what this pattern is, the dataset contains a quantified signature of
the exact process Natural England fails the site on, and nobody has noticed
because the data was never analysed.

Worth being honest about the limits: this is one snapshot, there is no control
site, and shade suppression could produce a similar pattern. It is a strong
hypothesis, not a demonstrated cause. Frame it that way.

### So who is actually in the pipeline?

Successors in the 7 to 50 cm range, single stems only, that could plausibly
reach the canopy:

Ash 27, Field Maple 17, Wych Elm 15, Pedunculate Oak 9, Sessile Oak 3, Wild
Cherry 3, English Elm 3, Small-leaved Lime 2.

The largest cohort of future canopy trees is **ash**, the species being killed.
Wych elm is second, and elm has its own well known ceiling from Dutch elm
disease, which tends to kill stems once they reach roughly 10 to 20 cm. Field
maple is the one genuinely healthy successor, and it is a smaller tree that
will not produce an oak-lime canopy.

**That is the story: the two species best represented in the replacement layer
are the two with active disease pressure.**

---

## 3. Holly is taking over the understorey

| Holly | Count |
|---|---|
| Seedlings | 433 |
| Saplings | 15 |
| Small (<25 cm) | 55 |
| Medium (<50 cm) | 5 |
| Mature or larger | 0 |

Holly is the second most abundant established plant on the site, 15.2% of
established stems, and unlike ash it **is** getting through: 55 stems already in
the small class. Zero in the mature classes means this is a young, expanding
population, not a stable one.

Why this matters for the SSSI specifically: the citation notifies the ground
flora, including "2 colonies of the Red Data book species, Purple Gromwell
*Buglossoides purpurocaerulea*". Holly casts dense evergreen shade year round.
An expanding holly understorey is one of the standard mechanisms by which
ancient woodland ground flora is lost.

**Nobody has flagged this. It is not in Natural England's list of pressures for
the site.** If the pattern holds up, it is a genuinely new contribution from
this survey, and it is actionable: holly is easy to control if you know where
it is. That makes it a strong candidate for a map.

---

## 4. The notified features are in worse shape than the citation implies

The citation is the legal basis for the designation. These are the species it
names.

### Small-leaved Lime, named as "locally abundant"

Present on 8 of 20 transects, 17 established stems. But the age structure is
badly skewed:

Overmature (>75 cm) 11, mature 2, medium 2, small 2, saplings 3, seedlings 13.

**Eleven of seventeen established limes are in the largest size class.** This is
an ageing remnant population with thin recruitment, not an abundant one. 45% of
lime records are coppice or multistem, consistent with old coppice stools.

#### Why Jenny keeps coming back to lime

She talked about small-leaved lime repeatedly on the phone call of 3 August, and
the ecology explains why. It is probably the most irreplaceable thing in the
wood.

*Tilia cordata* was one of the dominant trees of lowland Britain in the warmer
mid-Holocene. The climate has since cooled enough that it **rarely sets viable
seed here**, because fertilisation needs summer warmth most British summers do
not deliver. So populations persist not by reproducing but by **vegetative
means**: coppice regrowth and layering where a low branch roots.

The consequence is that a lime stool is effectively one genetic individual that
can persist for many centuries, possibly over a thousand years. It is a living
relic of the original forest, which is why lime is such a strong ancient
woodland indicator, and why you cannot plant a replacement that means the same
thing.

The limestone woods of North Somerset and the Avon Gorge are a regional
stronghold for lime and for the rare *Sorbus*, so AWT carries a real regional
responsibility here. Lime also **coppices well and responds positively to it**,
which links this species directly to any decision about restoring coppice
management.

#### The recording form cannot answer the lime question

The smallest size class is labelled **"Seedlings or suckers"**. For most species
that collapse does not matter. For lime it is the entire question, because a
seedling means sexual reproduction and a sucker means the same old individual
spreading sideways.

So the 13 lime records in that class show the population doing *something*, but
the form cannot say which. **Worth raising with Jenny**, and worth a targeted
field check, because "the lime is recruiting" and "the lime is clonally
persisting" are very different conservation positions.

### Wild Service Tree, also named as "locally abundant"

Fifteen records in total. Fourteen of them are seedlings on a **single**
transect, plus one medium tree on another. Present on 2 of 20 transects.

**One established Wild Service Tree in the whole survey.** Against a citation
that calls it locally abundant, that is a striking discrepancy and probably the
single most quotable number in the dataset.

Caveat that must go in the write up: wild service spreads by suckers and can be
patchy, and a 1% sample can easily miss clumps. This is evidence of scarcity in
the sampled area, not proof of decline site wide. But it justifies a targeted
search, which is a concrete recommendation Jenny can act on.

### Whitebeam, and a real gap

The citation names two rare whitebeams, *Sorbus rupicola* and *S. eminens*, plus
a hybrid with wild service. The survey has a generic "Whitebeam" row and an "a
whitebeam (unidentified)" row. Two records, not identified to species.

**The rare Sorbus that form part of the notification cannot be assessed from
this data at all.** That is worth saying plainly to Jenny, because it is a
monitoring gap rather than a data problem, and identifying it is useful to her.

---

## 5. Deadwood: the picture is more interesting than "insufficient"

Natural England fails all four units partly on insufficient standing deadwood.
Here is what the survey actually found across 0.40 ha.

| Type | <25 cm | <50 cm | <75 cm | >75 cm | Total |
|---|---|---|---|---|---|
| Dead standing | 15 | 5 | **0** | **0** | 20 |
| Dead fallen | 95 | 18 | 4 | 2 | 119 |
| Stump | 2 | 9 | 0 | 1 | 12 |

Two distinct findings, and they point in opposite directions.

**Large standing deadwood is completely absent.** Not scarce, absent. Zero
standing dead stems above 50 cm anywhere in the survey. Large standing dead
trees are the highest value deadwood habitat, supporting cavity nesting birds,
bats and the specialist saproxylic invertebrates that need big diameter, sun
exposed, standing wood. This is direct quantitative support for Natural
England's judgement, in the specific size class that matters most.

**But total deadwood is not obviously scarce.** 119 fallen pieces and 20
standing pieces across 0.40 ha is a lot of wood. Before drawing any conclusion
from that, two things need checking with Jenny:

- Does a "Dead fallen" record mean a whole fallen tree or a piece of fallen
  wood? The methodology says to measure the midpoint of the section inside the
  quadrat, which reads like pieces. It changes the number by a large factor.
- Natural England's condition targets for woodland deadwood are usually
  expressed as volume per hectare, or as counts of large pieces above a
  diameter threshold, not as raw piece counts. The survey records counts by
  size class, so it can answer a "large pieces per hectare" style target but
  cannot produce a volume.

If the counts do stand up, then this survey may **refine** rather than simply
confirm the Natural England assessment: the problem is not deadwood quantity,
it is deadwood **size and position**. Plenty on the ground, none standing large.
That is a much more useful message for management, because it points at a
specific intervention, which is retaining standing dead stems rather than
felling them.

Deadwood per transect ranges from 0 to 12. **Q1 is the only transect with none
at all**, and is worth a look on the map for why.

---

## 6. Invasives are minimal, which is good news worth stating

Jenny asked about invasive trees. The answer is that there is very little.

| Species | Records | Transects | Note |
|---|---|---|---|
| Sycamore | 8 | Q17, Q19, Q20 | all on the eastern edge |
| Buddleia | 4 | Q3 | |
| Holm Oak | 3 | Q2, Q12, Q15 | evergreen, spreads on limestone |
| Laurel, *Prunus* sp, unidentified | 1 | Q12 | **needs identifying** |

Sixteen records out of 3,218, so about 0.5%. Natural England's woodland
condition tables typically want non-natives held below a threshold in the order
of 5 to 10%, so on this evidence the site passes comfortably. Being able to say
that with a number is valuable.

Two things still worth flagging. The sycamore records cluster entirely on the
eastern edge near the village and road, which is a classic seed source pattern
and means it is worth watching rather than ignoring. And the unidentified
laurel matters: if it is Cherry Laurel, that is a serious invasive that forms
dense shade and is far harder to remove once established. One record now is
worth a field check.

---

## 7. The coppice legacy is clearly visible

| Species | Single | Coppice | Multi | % coppice or multi |
|---|---|---|---|---|
| Hazel | 34 | 122 | 4 | **79%** |
| Common Lime | 1 | 2 | 2 | 80% |
| Small-leaved Lime | 18 | 8 | 7 | 45% |
| Pedunculate Oak | 19 | 6 | 5 | 37% |
| Hawthorn | 154 | 31 | 4 | 19% |
| All live records | 2,921 | 187 | 110 | 9.2% |

The citation describes oak standards "together with coppice and maiden Ash".
The data confirms an abandoned coppice-with-standards system: hazel is
overwhelmingly coppiced, 16 hazel stools have grown past 50 cm across, and lime
shows the same signature.

Large stool diameter is a rough proxy for time since last cutting, so the stool
size distribution is a way of estimating **how long ago coppicing stopped**.
That is a genuinely interesting secondary analysis and nobody has asked for it.

---

## 8. Spatial patterns worth testing

These are patterns visible in the per transect summaries. They need proper
mapping before anyone should believe them.

**Established ash concentrates in the north east.** Q17 (8 stems), Q20 (7),
Q19 (5) against 0 to 3 everywhere else. Those same transects have the *lowest*
ash seedling counts (57, 40, uncapped). Everywhere else, established ash is
near zero and seedlings hit the 100 cap. That inverse relationship is worth
testing properly. It could mean the north east retains a surviving ash cohort
while the rest of the wood has already lost its ash and is carpeted in
seedlings that will not survive. If that holds up it is a dieback progression
map, which is exactly the kind of output that gets used.

**Diversity varies more than threefold.** Shannon index runs from 0.66 (Q13) to
1.90 (Q12); species richness from 3 (Q4) to 9 (Q12).

- Q4 is the poorest: 9 established stems, 3 species, hazel dominated.
- Q13 has 17 stems but 14 of them are hazel, hence the very low diversity.
- Q3 has the most stems (35) but low diversity, because 21 are hawthorn.
  Hawthorn dominance usually indicates former open ground or an edge, so Q3 may
  not be interior ancient woodland at all. Check it against the Ancient
  Woodland Inventory.

**The sample bias is subtler than it looks.** SUPERSEDED by the LIDAR result
of 2026-08-11, see section 13. The unsurveyed squares visually cluster on the
flanks, but slope analysis shows they are no steeper on average than the
surveyed ones (12.7 vs 12.2 degrees mean). What does differ is cliff presence:
8 of 29 unsurveyed squares contain a slope above 60 degrees against 1 of 20
surveyed. So the sample avoids rock faces, not steep ground in general, and at
least 21 skipped squares were walkable. Why they were skipped is a question
for Jenny, and the case for finishing the survey stands either way.

---

## 9. Mapping Jenny's requests onto why the SSSI is failing

Jenny listed her wants "off the top of my head". Every one of them happens to
map onto a stated reason the site is in Unfavourable and Declining condition.
Making that link explicit is what turns a mapping exercise into evidence.

| Jenny's request | What it actually tests |
|---|---|
| Density maps, trees per hectare | Baseline stocking. Must be split into established and seedlings, they behave completely differently |
| Diversity of species | Composition, a notified feature |
| Diversity of age classes | Structural diversity, a condition attribute, and the oak and ash regeneration failure |
| Distribution of dead wood | A named failure reason. Split standing from fallen, and by size |
| Lime and wild service | The two ancient woodland indicators named in the citation |
| Invasive trees | A standard condition attribute, and the site passes |
| Age classes split by species | The single most informative graph in the whole set |
| Heat maps | Presentation, with the caveats in data_audit.md |

Things she did **not** ask for that the data supports and that she would
probably want:

- **The regeneration bottleneck plot**, seedling to sapling ratio by species.
  This is where the ash story lives and it is one chart.
- **Holly expansion**, because nobody is tracking it and it threatens a
  notified feature.
- **Canopy versus successor composition**, which answers "what will this wood
  look like in fifty years".
- **Coppice stool size distribution**, as a proxy for time since abandonment.
- **A survey coverage map**, showing the 20 done and the 29 not done, with the
  reason. This is genuinely useful to her for planning the next field season,
  and it is the easiest map to produce.

---

## 10. What to investigate before writing plotting code

In priority order.

1. **Download the Natural England SSSI boundary and the four management unit
   boundaries.** Join each transect to its unit. Natural England assesses and
   reports by unit, so results in that form are directly usable by AWT. All
   four units are Unfavourable and Declining, but the reasons may differ by
   unit, and with 20 transects across 4 units you get roughly 5 per unit, which
   is thin but reportable.

2. **Get the Ancient Woodland Inventory layer.** Check whether all 20 transects
   fall inside ancient woodland. Q3, with its hawthorn dominance, is the one to
   look at.

3. **Read the actual favourable condition table for this site**, not a generic
   one. It is on the Natural England designated sites page under "Views about
   Management" or in the unit assessment. It gives the specific thresholds the
   site is judged against, and it tells you exactly which numbers to compute.
   This is the highest value hour you can spend, because it converts the whole
   analysis from "interesting" to "directly answers the regulator's question".
   Do this before deciding the final figure list.

4. **Establish what a "Dead fallen" record counts.** Piece or tree. It changes
   the deadwood conclusion.

5. **Decide how to handle the seven "unidentified" categories** (an oak, a lime,
   a whitebeam and so on). For a species diversity index they must not be
   silently dropped, and they must not be silently merged into the named
   species either, since that would inflate lime and oak counts. State the rule.

6. **Decide the seedling policy and stick to it.** 17 cells are censored at
   `>100`. Recommendation: report seedlings separately from established trees
   everywhere, treat `>100` as exactly 100, and label every affected figure as
   a minimum.

7. **Test the parser against all 90 distinct notation values** before trusting
   any number. It currently reproduces Jenny's two worked examples exactly and
   fails on only one cell, the Ribes comment.

---

## 11. Questions only Jenny or fieldwork can answer

Already covered in data_audit.md, plus these, which came out of the analysis:

- Are the "Whitebeam" records the rare *Sorbus rupicola* or *S. eminens* named
  in the citation, or common whitebeam? The notification depends on the
  difference and the survey cannot distinguish them.
- What is the *Prunus* laurel on Q12? Cherry Laurel would matter.
- Is there any earlier tree survey of the site to compare against? Without one,
  everything here is a single time point and no trend can be claimed.
- Does AWT hold the 2023 Natural England unit assessment narrative, not just the
  condition grade? It would say what the assessor actually saw.

---

## 12. Suggested order of work

1. Parser and tidy table, one row per transect per species per size class per
   stem type. Everything else is a groupby on that table.
2. Coverage map, 49 planned versus 20 surveyed. Easiest map, immediately useful.
3. The graphs, because they carry the findings: age class by species, the
   regeneration bottleneck, canopy versus successors, deadwood by type and size.
4. The maps Jenny asked for, on the gridded 100 m choropleth pattern.
5. Heat maps last, as presentation on top of results that already stand up.

One framing note for the write up. The 1984 citation describes a wood as it was
over forty years ago. The 2023 assessment gives a grade but little detail. **This
survey is the first quantitative test of whether the citation's description is
still true**, and on this evidence the answer for at least two named features,
Wild Service Tree and Small-leaved Lime, is that it is not. That is the sentence
this project is worth writing.

---

# 13. Survey coverage and terrain constraint analysis

**Added 2026-08-06. Confirmed as a wanted deliverable, not a maybe.**

This was listed in section 9 as a nice to have. It is now a definite output, and
it has grown a second half.

## Part one: the coverage map

Plot all **49 planned sample points** and symbolise them by whether they were
surveyed. 20 were, 29 were not.

The data is already in hand. The text layer of `tree_sample_locs.pdf` holds all
49 points as easting, northing and bearing, extracted with pypdf. No new data is
needed for this figure, which makes it the cheapest map in the project and the
one most immediately useful to Jenny for planning the next field season.

Draw the transects as 50 m lines on their recorded bearings rather than as dots.
The bearing is the only place that information exists, and a line shows what was
actually walked.

## Part two: test the terrain explanation

Jenny said some grid references could not be surveyed because of cliffs. The
unsurveyed points are not scattered randomly: they cluster on the **western,
south western and eastern edges**, which is where the steep limestone flanks
are. So the working assumption is terrain.

That assumption is testable, and testing it converts a caveat into a finding.

**Method sketch.** Get a bare earth terrain model for the site, compute slope,
then compare the slope distribution of surveyed against unsurveyed transects.

Two methodological points that matter:

- **Sample along the whole 50 m transect line, not just the start point.** A
  transect can begin on level ground and run straight off a cliff. Using only
  the start coordinate would miss exactly the cases the analysis is about.
- **Use the DTM (bare earth), not the DSM (surface).** The DSM includes the tree
  canopy, so slope computed from it would be measuring the treetops.

**Data source, verified 2026-08-06.** Environment Agency LIDAR Composite
Digital Terrain Model, 1 m resolution, free and open:

```
https://environment.data.gov.uk/spatialdata/
  lidar-composite-digital-terrain-model-dtm-1m/
```

- `.../wms` serves pictures. Layers include `Lidar_Composite_DTM_1m`,
  `Lidar_Composite_Elevation_DTM_1m` and `Lidar_Composite_Hillshade_DTM_1m`.
  The hillshade is good for a map background.
- `.../wcs` serves the **actual elevation values**, which is what slope needs.
  WMS alone is not enough.
- 1 m resolution is ample for a site of 915 m by 854 m.
- Confirm the CRS on download rather than assuming EPSG:27700.

## Why this is worth doing properly

**It quantifies the bias in every other output.** 20 of 49 points is not a
random 41% sample of the wood. It under represents steep ground, and steep
ground is typically where the least disturbed vegetation sits, and where the
rare *Sorbus* named in the citation are most likely to be. Every density,
diversity and deadwood figure in this project inherits that bias, and a
defensible report has to state it with evidence rather than as a hunch.

**It makes the case for finishing the survey.** If the unsurveyed points are
demonstrably steeper, that is a concrete argument for a targeted follow up
season on the flanks, which is a recommendation Jenny can act on and cost.

**It sharpens the legend.** A blank cell on a map must never read as zero trees.
Better still, it can distinguish *inaccessible* from *not yet reached*, which
are different things for planning.

## The limit of what this can show

Slope will explain some of the 29, not necessarily all. A point could have been
skipped for dense scrub, an ownership or boundary issue, or simply because the
season ran out. So the honest claim is "unsurveyed transects are systematically
steeper than surveyed ones", not "each unsurveyed transect was inaccessible".

**Jenny's answer is still needed**, and it is already on the questions list: of
the 29 not done, how many were genuinely impossible and how many were just not
reached? The terrain analysis supports her answer, it does not replace it.

## Suggested outputs

- Coverage map: 49 transect lines over the SSSI boundary on a hillshade
  background, surveyed and unsurveyed clearly distinguished.
- Slope comparison: surveyed versus unsurveyed, as a distribution rather than
  two means, since the spread is the interesting part.
- One quotable number for the report, of the form "unsurveyed transects average
  X degrees against Y degrees for surveyed".
- A standing caveat sentence, reused verbatim under every other map.

## RESULT (2026-08-11): the analysis ran, and it corrected the hypothesis

EA 1 m DTM downloaded via WCS (scripts/04_terrain_and_qgis_layers.py), slope
computed per 100 m square, all 49 squares.

| Measure | Surveyed (20) | Unsurveyed (29) |
|---|---|---|
| Mean slope | 12.2 deg | 12.7 deg |
| Mean-slope range | 2.3 to 21.5 | 2.4 to 24.9 |
| Contains slope >60 deg (a rock face) | **1** | **8** |

**Mean slope does not separate the groups at all.** The visual clustering on
the flanks misled; the surveyed sample covered ordinary steep ground at the
same rate it was skipped.

**Cliff presence does separate them.** 8 of 29 unsurveyed squares contain a
genuine rock face (max slopes up to 82 degrees, concentrated along the
southern edge, northings 174750 to 174950) against 1 of 20 surveyed. The
correct claim is now: "the sample avoids rock faces, not steep ground; terrain
explains at most 8 of the 29 gaps, and the other 21 were walkable."

This strengthens the question to Jenny rather than weakening it: were the 21
attempted and abandoned, or never reached before the season ended?

The old "biased toward the plateau" wording has been corrected in the figure
caption, the report, and the README. Do not reintroduce it.
