# Data audit

First full read of the raw files, 5 August 2026. Everything below comes from
the data itself, not from Jenny's description of it.

## What we have

`data/raw/`

| File | Size | Content |
|---|---|---|
| WBW_tree_age_distributions_tallied.xlsx | 472 KB | The survey data. 22 sheets |
| Pdf methodology.pdf | 618 KB | Methodology document |
| tree_sample_locs.pdf | 1.75 MB | Sample location maps, transect numbers and bearings |
| PDF input form.pdf | 188 KB | Blank field recording form |

Workbook structure: `Methodology`, `Master form`, then `Q1` to `Q20`, one
sheet per transect. 20 transects, matching Jenny's count. The 2 she thinks are
missing are genuinely absent.

## The method, from the Methodology sheet

Quoted:

> Using the map, navigate to your GPS coordinate. Run a 50m long tape from the
> starting point along the angle specified by the map. Walking along the
> transect, record each tree, or sapling within 2m of the line on either side,
> which will give a 200m2 area.

**This answers the transect dimensions question. No need to ask Jenny.**

- 50 m long, 2 m either side, so a 4 m wide belt transect.
- 200 m2 per transect.
- Trees per hectare = count x 50.
- 20 transects x 200 m2 = 4,000 m2 = **0.40 ha**, against an SSSI area of 37.66
  ha. **The survey samples 1.06% of the site.**

Other method rules that affect parsing:

- Include a tree if any part of its base is within 2 m of the line.
- Single stem: measure dbh at 1.3 m, tally mark.
- Coppice or multistem: measure stool width at the narrowest point below the
  first fork, mark C or M by judgement.
- Stem clusters with no defined stool count as 1, marked M, in one of the two
  seedling classes.
- **Seedlings counted up to 100, then recorded as `>100`.** This is a censored
  count, see issues below.
- Dead trees: measure the midpoint of the section inside the quadrat, and
  **only count dead trees more than 10 cm wide**.

## Age and size classes

Eight columns, of which row 5 defines only seven:

| Class | Definition |
|---|---|
| Seedlings or suckers | <=100 cm tall |
| Seedlings or suckers | >100 cm, <=3 cm dbh |
| Saplings | >100 cm, 3 to 7 cm dbh |
| Small trees | <=25 cm dbh |
| Medium trees | <=50 cm dbh |
| Mature trees | <=75 cm dbh |
| Overmature | >75 cm dbh |
| Ancient / veteran | **no definition given** |

## Coordinates

All 20 are **already numeric OSGB36 eastings and northings**, not alphanumeric
grid references. No ST-style conversion is needed, which removes a task from
the plan.

They sit on a perfect 100 m lattice, all ending in 50, so each transect starts
at the centre of a 100 m grid square. Extent 345250 to 345950 east, 174750 to
175350 north, so 700 m by 600 m. No duplicates.

## The sample location PDF is a full survey plan, and it is machine readable

`tree_sample_locs.pdf` is not just a picture. Its text layer holds **49 planned
sample points**, each as easting, northing and bearing. Extracted with pypdf in
seconds.

This is the most useful single discovery in the audit. It gives:

- **The transect bearing for every point**, which the workbook does not
  contain. Without it the transects cannot be drawn as lines, only as points.
- **The denominator for coverage.** 49 planned, 20 surveyed, so **29 planned
  points were never surveyed, 59% of the intended sample.**
- **Independent confirmation of the Q5 and Q11 coordinate repairs.** Both
  repaired values, 345650 175150 and 345550 175050, appear in the plan, with
  bearings 30 and 7. All 20 surveyed points match a planned point exactly, and
  none is unaccounted for. The repair is now verified, not assumed.

Bearings of the surveyed transects range across the full compass, from 5 to
316 degrees, so they were randomised rather than fixed.

Planned coverage would have been 49 x 200 m2 = 0.98 ha, 2.6% of the site.
Actual is 0.40 ha, 1.06%.

**Caveat.** The plan does not say *why* each of the 29 was skipped. Jenny
mentioned cliffs, so some are inaccessible terrain, but some may simply be
unfinished. Those are different things for a map legend. This is now a question
worth asking her, and it replaces the vaguer original version.

## Recorded data

32 row labels carry data. Everything else on the form was left blank.

| Label | Sheets with data |
|---|---|
| Ash | 20 |
| Hazel | 20 |
| Field Maple, Hawthorn, Holly, Dead fallen | 19 |
| Pedunculate Oak | 15 |
| Dead standing | 14 |
| Wych Elm | 13 |
| Small-leaved Lime, Stump | 8 |
| Sessile Oak, Wild Cherry | 5 |
| Holm Oak, Sycamore | 3 |
| Spindle, Dogwood, Whitebeam, unidentified elm, Wild Service Tree, English Elm | 2 |
| Common Lime, Yew, Buddleia, Blackthorn, Crab Apple and others | 1 |

Deadwood is present and usable: fallen on 19 of 20 transects, standing on 14,
stumps on 8.

## The blank form PDF, and what it validates

Two pages. The printed form has **seven size classes and no Ancient / veteran
column**, so that column on Q1 to Q3 was added during write up, not in the
field.

The important detail: on the three deadwood rows, **the first three columns are
greyed out**. Deadwood is only recordable in the four established size classes,
which matches the methodology rule to count only dead trees over 10 cm wide.

Validation run against all 20 sheets:

- **Zero deadwood entries fall in a greyed out column.** The data obeys the
  form.
- **The Ancient / veteran column is never used for data on any sheet.** So it is
  cosmetic. This downgrades it from a blocking question to a curiosity.
- Only **one** cell in the whole workbook fails to parse, the Ribes comment.

The form also has four blank write in rows after Yew. That is where Dogwood,
Buddleia and the unidentified Laurel were added, which explains why those are
not on the master list.

## The map

`tree_sample_locs.pdf` is an aerial image (Maxar via Microsoft) with the 49
sample squares drawn in cyan and the site boundary in magenta. Each square is
labelled with easting, northing and bearing. Counting the squares on the image
gives exactly 49, matching the text extraction.

The unsurveyed squares are not randomly scattered. They cluster on the **western
and south western edge** and along the **eastern edge**, which is consistent
with Jenny's note about cliffs, since the wood sits on the steep flanks of a
limestone ridge. **This means the achieved sample is spatially biased toward the
plateau and away from the steep ground**, and that has to be stated. It is not a
random 41% of the wood.

## Parser check

A token based parser reproduces Jenny's own totals exactly:

| Input | single | coppice | multi | total | Jenny's stated total |
|---|---|---|---|---|---|
| `2, C, 2M` | 2 | 1 | 2 | **5** | 5 |
| `2C, 2M` | 0 | 2 | 2 | **4** | 4 |

This is consistent only with the "2 single stem" reading, confirming her "3
single stem trees" is a typo. Still worth a one line confirmation from her,
but the arithmetic is now on our side.

---

# First numbers

Provisional, pending Jenny's confirmation. Density conversion: each transect is
200 m2, so per hectare per transect is count x 50. For the site total across 20
transects the divisor is the full 0.40 ha, so count x 2.5.

## By size class, all 20 transects

| Class | Count | Site density |
|---|---|---|
| Seedling <=100 cm | 2,685 | 6,713 /ha |
| Seedling >100 cm, <=3 cm | 61 | 153 /ha |
| Sapling 3 to 7 cm | 77 | 193 /ha |
| Small <=25 cm dbh | 316 | 790 /ha |
| Medium <=50 cm dbh | 154 | 385 /ha |
| Mature <=75 cm dbh | 35 | 88 /ha |
| Overmature >75 cm dbh | 41 | 103 /ha |

**Live trees total 3,218. Of those, 2,823 are seedlings or saplings under 7 cm
dbh, and only 395 are established trees.** The seedling figure is censored and
is a minimum.

**Established trees: 395 over 0.40 ha, so about 988 stems per hectare.** That is
the defensible headline density. Per transect it ranges from 9 to 36, mean 19.8,
so a fourfold spread across the wood. There is real spatial signal here for the
maps.

## Established trees by species

| Species | Count | /ha | Share |
|---|---|---|---|
| Hazel | 121 | 303 | 30.6% |
| Holly | 60 | 150 | 15.2% |
| Hawthorn | 49 | 123 | 12.4% |
| Ash | 39 | 98 | 9.9% |
| Pedunculate Oak | 27 | 68 | 6.8% |
| Wych Elm | 24 | 60 | 6.1% |
| Field Maple | 21 | 53 | 5.3% |
| Small-leaved Lime | 17 | 43 | 4.3% |
| Dogwood | 8 | 20 | 2.0% |
| Sessile Oak | 7 | 18 | 1.8% |
| Wild Cherry, Common Lime | 4 each | 10 | 1.0% |
| Wild Service Tree | **1** | 2.5 | 0.3% |

## Three findings that matter for the SSSI

**1. No large standing deadwood exists in the sample.** Standing dead was
recorded on 14 of 20 transects, 20 pieces in total: 15 in the <=25 cm class and
5 in the <=50 cm class. **Zero in the mature or overmature classes.** Natural
England fails this site partly on insufficient standing deadwood, and this is
direct quantitative evidence of exactly that, in the size class that matters
most for saproxylic invertebrates. Fallen deadwood is more abundant, 119 pieces
including a handful of large ones.

**2. Ash dominates the regeneration and almost nothing else does.** Ash accounts
for 1,865 of 3,218 live records, nearly all seedlings, with 15 cells censored at
`>100`. Yet Ash is only 9.9% of established trees. A wood regenerating
overwhelmingly in the one species being killed by dieback is the central story
in this dataset.

**3. The citation's indicator species are barely present.** The 1984 citation
names Small-leaved Lime and Wild Service Tree as "locally abundant". The survey
found **17 established Small-leaved Lime and a single established Wild Service
Tree** in 0.40 ha. That is a headline finding, and also a caution: at n=1, the
Wild Service map is a presence dot, not a distribution.

These three are worth leading with when reporting to Jenny, because each one
speaks directly to a stated reason the SSSI is in Unfavourable and Declining
condition.

---

# Issues

Ordered by how much they can damage the result.

## 1. The worked tally example in the brief did not add up. RESOLVED 14 August 2026.

> 2, C, 2M is 3 single stem trees, 1 coppice, 2 multistem

Two single stem plus one coppice plus two multistem is 5, which matches the
total of 5 she states. But she writes "3 single stem".

I checked every sheet for a computed total column that would settle it
arithmetically. **There is none.** The only content outside the tally grid is a
single free text note, so the data could not settle it and Jenny had to.

**She confirmed 2 single stems.** "3 single stem trees" was a slip and her
stated total of 5 is correct. The parser already read it that way, so no counts
in this audit or the report changed.

## 2. Two coordinates have their leading digits missing

| Sheet | Recorded | Almost certainly means |
|---|---|---|
| Q5 | `45650 75150` | 345650 175150 |
| Q11 | `45550, 75050` | 345550 175050 |

Confident repair: every other transect is 345xxx and 17xxxx, both repaired
values land exactly on the same 100 m lattice, and both fall inside the site.
Left uncorrected they would plot roughly 300 km southwest, in the sea off
Cornwall. The repair must be done in code and documented, not silently.

## 3. Seedling counts are censored at 100

`>100` appears 17 times, and `100` twice. Per the methodology, counting stops
at 100. So seedling totals are a floor, not a count.

This matters most for Ash, which hits the cap repeatedly. Any trees per hectare
figure that includes seedlings is therefore an underestimate of unknown size.
Two defensible options: report seedlings separately from established trees, or
treat `>100` as exactly 100 and label every affected figure as a minimum. I
would do both, and never fold seedlings silently into a single density number.

## 4. The sample is 1.06% of the site, which constrains the heat maps

20 points, 200 m2 each, spread over 700 m by 600 m on a 100 m grid.

That is a real dataset and it supports per transect comparison and site level
totals. It does **not** support a smooth interpolated surface. Kriging or IDW
across 20 widely spaced points would produce a confident looking map whose
detail is invented.

See the heat map note below for what to do instead.

## 5. Header layouts differ between sheets

- 17 sheets have 7 size classes.
- **Q1, Q2 and Q3 have an 8th, `Ancient/ veteran`.**
- Q1 alone labels the second column `Saplings or suckers` where every other
  sheet says `Seedlings or suckers`.
- Row 5 gives only 7 size definitions on all 20 sheets, so `Ancient/ veteran`
  has no dbh threshold anywhere.

Parse by position with a per sheet header map. Do not assume a fixed column
count.

## 6. The header block repeats mid sheet

On 12 sheets (Q6, Q9, Q11 to Q20) the column headers are reprinted at **row
36**, because the species list continues below. A naive read would ingest
`Small trees` and `Overmature` as species. The parser must skip repeated header
rows.

## 7. Free text sitting in data cells

| Where | Content |
|---|---|
| Q2, cell J16 | `83 ash in 2m2` |
| One sheet, `Comments:` row | `Ribes sp (currant) noted on transect - AWI for site record.` |
| One sheet, species column | `Laurel (Prunus sp) Cherry or Portuguese?` |
| One sheet, species column | `?` |

The Ribes note is worth passing to Jenny separately, since it is an ancient
woodland indicator recorded for the site record and it will otherwise be lost.

## 8. Notation is inconsistent in ways the parser must absorb

All of these occur: `2C`, `C`, `1,C`, `1, C`, `4M, C`, `4M,C`, `C,M`, `C, M`,
`M,C`, `M, 1`, `5C,M`, `70,4M`.

So: order varies, spacing varies, and the number can come after the letter. The
parser needs a token regex, not string splitting on a fixed pattern. Test it
against all 90 distinct values found, which are listed in the audit script
output.

## 9. Species naming needs normalising

- `Dogwood` and `dogwood` are the same species recorded on different sheets.
- The master list contains both `Wild Service Tree` (*Sorbus torminalis*, the
  species named in the SSSI citation) and `Service-tree` (*Sorbus domestica*, a
  different and much rarer tree). Only Wild Service Tree carries data. Keep
  them apart and do not let a fuzzy match merge them.
- Seven `unidentified` categories exist, for example `a lime (unidentified)`.
  Decide explicitly whether these roll into the parent genus for diversity
  measures. They should not simply be dropped.

## 10. Dates and admin fields

- **q18 has no date.**
- Q15, Q16 and Q17 store the date as text (`15 Sept 2022` style) while the rest
  are real dates. Mixed types will break a naive read.
- Reserve name varies: `Weston Big Wood`, `WBW`, `weston big wood`. Cosmetic.
- Sheet `q18` is lowercase where all others are uppercase. Match case
  insensitively.

## 11. Survey dates: May to October 2022

The surveys ran 12 May to 6 October 2022. **The data is roughly four years
old.** Natural England's most recent condition assessments are April 2023.

Two consequences:

- The ash figures are a 2022 baseline, not current condition. Ash dieback has
  moved on since. This must be stated plainly in the outputs rather than
  presented as the present state of the wood.
- A season spanning May to October means detectability varies. Seedlings and
  ground vegetation differ a lot between May and October, so seedling counts
  are not strictly comparable between early and late transects. Worth a caveat,
  not worth trying to correct.

## 12. One odd value

`Dead standing` on Q19 is recorded as `C`, a coppice marker on a deadwood row.
Probably a dead coppice stool. Minor, but flag it rather than dropping it.

---

# Heat maps

**Jenny has asked for heat maps.** Added to the deliverables.

The honest constraint is issue 4 above: 20 sample points on a 100 m lattice.

Recommended approach, in order of defensibility:

1. **Gridded choropleth.** One 100 m cell per transect, coloured by the value.
   Every coloured cell is backed by a real measurement, and unsurveyed squares
   stay blank rather than being filled in. This is the honest version and it is
   what Natural England style reporting expects.
2. **A smoothed surface as a secondary figure**, if Jenny wants the classic
   heat map look. Clearly captioned as indicative only, with the sample points
   drawn on top so the viewer can see how thin the support is.

Do not produce only the smoothed version. A heat map over 20 points invites
readers to believe in detail that is not there, and being straight about that
is exactly the judgement an employer is looking for.

Blank cells matter too. Jenny said some grid references were inaccessible
because of cliffs. So a gap means not surveyed, never zero trees, and the
legend must say so.

---

# Questions for Jenny, revised

Two of the original six are now answered by the data.

**Answered by Jenny, 14 August 2026:**

- The `2, C, 2M` example is **2 single stems**, as her stated total of 5
  implied. This was the only open question that could change the numbers, and
  the parser had already taken that reading, so nothing shifted.

**Still needed:**

1. What is the `Ancient / veteran` class? It appears on Q1 to Q3 only, is not on
   the printed form, and has no dbh definition. **Low priority**: it is never
   used for data, so it does not affect any number.
2. Was q18 surveyed on a known date? It is the only sheet with none.
3. The sample plan has 49 points and 20 were surveyed. Of the 29 not done, how
   many were genuinely inaccessible (cliffs) and how many were simply not
   reached before the survey stopped? The map legend needs to distinguish
   inaccessible from not yet surveyed, and they mean different things for
   whether the sample is spatially biased.

**Answered by the data, no need to ask:**

- Transect dimensions: 50 m by 4 m, 200 m2. From the Methodology sheet.
- Survey dates: May to October 2022. From the sheet headers.
- Deadwood recording: standing, fallen and stump are separate rows, minimum
  10 cm wide. From the Methodology sheet and the form.
- Age classes: recorded per species per transect, as counts by size class, not
  per individual tree.

**Worth mentioning to her, not blocking:**

- The Ribes record in the comments, which belongs in the site record.
- Q5 and Q11 coordinates are missing their leading digits, and the assumed
  repair.
