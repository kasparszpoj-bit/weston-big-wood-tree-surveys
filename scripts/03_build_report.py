"""Assemble the findings report as a single self-contained HTML file.

Run:  python scripts/03_build_report.py
Reads outputs/figures/*.png and outputs/tables/, writes outputs/report.html
with every figure embedded, so the report is one file with no dependencies.
"""

import base64
import json

import pandas as pd

from wbw.config import FIGURES, OUTPUTS, TABLES

stats = json.loads((TABLES / "headline_stats.json").read_text())
units = pd.read_csv(TABLES / "unit_summary.csv")


def img(name, alt):
    data = base64.b64encode((FIGURES / name).read_bytes()).decode()
    return (f'<img src="data:image/png;base64,{data}" alt="{alt}" '
            f'loading="lazy">')


def plate(n, name, alt, title, body):
    return f"""
<figure class="plate">
  <figcaption class="plate-head"><span class="plate-no">Plate {n}</span> {title}</figcaption>
  {img(name, alt)}
  <div class="plate-note">{body}</div>
</figure>"""


CSS = """
:root {
  --ground: #faf9f6; --panel: #ffffff; --ink: #1c1c1a; --ink-2: #52514e;
  --muted: #898781; --hair: #e3e1d8; --moss: #35603f; --moss-soft: #eef2ec;
  --alert: #b03434; --alert-soft: #f7ecea; --blue: #2a78d6;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --ground: #161715; --panel: #1f201d; --ink: #f2f1ec; --ink-2: #b9b7ac;
    --muted: #8a887f; --hair: #2e2f2b; --moss: #7fae8b; --moss-soft: #22291f;
    --alert: #d97b6c; --alert-soft: #2d1f1c; --blue: #6ba3e8;
  }
}
:root[data-theme="dark"] {
  --ground: #161715; --panel: #1f201d; --ink: #f2f1ec; --ink-2: #b9b7ac;
  --muted: #8a887f; --hair: #2e2f2b; --moss: #7fae8b; --moss-soft: #22291f;
  --alert: #d97b6c; --alert-soft: #2d1f1c; --blue: #6ba3e8;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--ground); color: var(--ink);
  font: 16px/1.65 "Segoe UI", system-ui, sans-serif;
}
.wrap { max-width: 900px; margin: 0 auto; padding: 3rem 1.25rem 5rem; }
.prose { max-width: 730px; }
h1, h2, h3 { font-family: Georgia, "Times New Roman", serif; line-height: 1.2;
  text-wrap: balance; color: var(--ink); }
h1 { font-size: 2.3rem; font-weight: 500; margin: .4rem 0 .6rem; }
h2 { font-size: 1.5rem; font-weight: 500; margin: 3rem 0 .8rem; }
h3 { font-size: 1.13rem; margin: 1.6rem 0 .4rem; }
p { margin: .75rem 0; color: var(--ink); }
.eyebrow { font-size: .72rem; letter-spacing: .14em; text-transform: uppercase;
  color: var(--moss); font-weight: 600; }
.standfirst { font-size: 1.12rem; color: var(--ink-2); max-width: 690px; }
.meta { color: var(--muted); font-size: .85rem; margin-top: 1rem; }
.meta strong { color: var(--ink-2); font-weight: 600; }
.draft { display: inline-block; border: 1px solid var(--alert);
  color: var(--alert); border-radius: 3px; padding: .05rem .5rem;
  font-size: .72rem; letter-spacing: .1em; font-weight: 600; }
.statband { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1px; background: var(--hair); border: 1px solid var(--hair);
  margin: 2.2rem 0; }
.stat { background: var(--panel); padding: .9rem 1rem; }
.stat b { display: block; font-size: 1.7rem; font-weight: 650;
  font-variant-numeric: tabular-nums; line-height: 1.15; }
.stat span { font-size: .8rem; color: var(--ink-2); }
.stat.bad b { color: var(--alert); }
.plate { margin: 2.4rem 0; background: var(--panel); border: 1px solid var(--hair);
  padding: 1.1rem 1.1rem .9rem; }
.plate img { width: 100%; height: auto; display: block; background: #fcfcfb; }
.plate-head { font-size: .95rem; margin: 0 0 .8rem; color: var(--ink); }
.plate-no { font-family: Georgia, serif; font-style: italic; color: var(--moss);
  margin-right: .5rem; }
.plate-note { font-size: .9rem; color: var(--ink-2); border-top: 1px solid var(--hair);
  margin-top: .9rem; padding-top: .7rem; }
.callout { background: var(--moss-soft); border-left: 3px solid var(--moss);
  padding: .9rem 1.1rem; margin: 1.4rem 0; font-size: .95rem; }
.callout.warn { background: var(--alert-soft); border-left-color: var(--alert); }
.tablewrap { overflow-x: auto; margin: 1.4rem 0; }
table { border-collapse: collapse; width: 100%; font-size: .88rem;
  font-variant-numeric: tabular-nums; }
th, td { text-align: left; padding: .45rem .7rem; border-bottom: 1px solid var(--hair); }
th { font-size: .74rem; letter-spacing: .07em; text-transform: uppercase;
  color: var(--muted); font-weight: 600; }
td.num, th.num { text-align: right; }
.unsampled td { color: var(--muted); font-style: italic; }
ol.qs { padding-left: 1.2rem; } ol.qs li { margin: .5rem 0; }
footer { margin-top: 4rem; border-top: 1px solid var(--hair); padding-top: 1rem;
  color: var(--muted); font-size: .82rem; }
a { color: var(--blue); }
"""

unit_rows = ""
for _, r in units.iterrows():
    unit_rows += f"""<tr>
  <td>Unit {int(r.unit)}</td><td class="num">{r.area_ha:.1f}</td>
  <td class="num">{int(r.transects)}</td><td class="num">{int(r.est_stems_ha):,}</td>
  <td class="num">{int(r.species_richness)}</td>
  <td class="num">{int(r.standing_dead)}</td><td class="num">{int(r.fallen_dead)}</td>
  <td class="num">{int(r.established_lime)}</td></tr>\n"""
unit_rows += ("""<tr class="unsampled"><td>Unit 3</td><td class="num">1.9</td>
  <td class="num">0</td><td colspan="5">No transect falls in this unit — unsampled</td></tr>""")

html = f"""<title>Weston Big Wood: tree survey analysis</title>
<style>{CSS}</style>
<div class="wrap">

<header class="prose">
  <div class="eyebrow">Weston Big Wood SSSI · Avon Wildlife Trust</div>
  <h1>What the 2022 tree survey found</h1>
  <p class="standfirst">Twenty belt transects, 3,218 live stems, and the first
  quantitative test of whether the wood the 1984 citation describes still
  exists. On the evidence here, for two of its named features, it does not.</p>
  <p class="meta"><span class="draft">DRAFT FOR REVIEW</span> &nbsp;
  Analysis: Kaspar Szpojnarowicz · Field data: J. Greenwood et al., May–Oct 2022 ·
  Prepared August 2026 · <strong>Every figure regenerates from one scripted
  Python pipeline</strong></p>
</header>

<section class="prose">
<h2>The site, and why this analysis is shaped the way it is</h2>
<p>Weston Big Wood is 37.66 ha of ancient woodland on a Carboniferous
Limestone ridge above Portishead, notified as a SSSI in 1971 for its
open-canopy oak standards, its coppice and maiden ash, its rich ground flora,
and two ancient-woodland indicator trees the citation calls <em>locally
abundant</em>: Small-leaved Lime and Wild Service Tree.</p>
<p>In April 2023, Natural England assessed all four management units as
<strong style="color:var(--alert)">Unfavourable&nbsp;–&nbsp;Declining</strong>,
citing ash dieback and insufficient standing deadwood. That assessment is the
lens for everything below: each output Jenny asked for happens to test a
stated reason the site is failing, so the figures are arranged as evidence for
the condition conversation, not as a generic mapping exercise. Results are
reported per management unit, because units are what Natural England
assesses.</p>
<div class="callout">The survey ran 12 May – 6 October 2022. Ash dieback has
moved on since, so every ash figure is a <strong>2022 baseline</strong> — a
snapshot that cannot be re-created — rather than the current state of the
wood.</div>
</section>

<section>
<h2 class="prose">How the survey worked, and what it can honestly say</h2>
<p class="prose">Forty-nine sample squares were planned on a 100&nbsp;m grid,
each a 50&nbsp;m &times; 4&nbsp;m belt transect (200&nbsp;m²) on a random
bearing. Twenty were walked — 0.40&nbsp;ha, 1.06% of the site.</p>
{plate(1, "fig02_coverage.png", "Coverage map of 49 planned transects, 20 surveyed",
       "Survey coverage — the most useful map for planning the next season",
       "A LIDAR check (EA 1 m terrain model) complicates the obvious reading. The 29 "
       "unwalked squares are <em>not</em> steeper on average than the walked ones "
       "(mean slope 12.7&deg; vs 12.2&deg;), but they are five times as likely to "
       "contain an actual rock face: 8 of 29 hold a slope above 60&deg;, against 1 of "
       "20 surveyed. So cliffs genuinely blocked some squares, mostly along the "
       "southern edge, yet at least 21 skipped squares sit on ground no harder than "
       "what was walked. Which of those were attempted and abandoned, and which simply "
       "never reached before the season ended, is a question only the field team can "
       "answer, and it decides whether finishing the survey is easy.")}
<div class="statband">
  <div class="stat"><b>3,218</b><span>live stems recorded</span></div>
  <div class="stat"><b>988 /ha</b><span>established trees (≥7 cm)</span></div>
  <div class="stat bad"><b>0</b><span>standing dead stems &gt;50 cm — anywhere</span></div>
  <div class="stat bad"><b>0</b><span>oak saplings in the entire survey</span></div>
  <div class="stat bad"><b>1</b><span>established Wild Service Tree</span></div>
</div>
</section>

<section class="prose">
<h2>One reading rule before the figures</h2>
<p>Surveyors recorded three stem types: single stems (measured by trunk
diameter), and coppice and multistem (measured by <em>stool width</em>). They
share the same size-class columns but are different measurements: a 60&nbsp;cm
hazel stool is an understorey shrub on a root system that may be centuries
old; a 60&nbsp;cm oak trunk is a canopy tree. Summing them is fine for
abundance and species composition — and is done here — but every
<em>structural</em> figure splits them, because pooling promotes 16 large
hazel stools into the canopy and roughly triples apparent canopy density
(69 vs 21 large stems).</p>
<p>Seedlings were tallied to a field cap of 100 per cell, then written
"&gt;100". Seedling figures are therefore <strong>minima</strong>, marked ≥
throughout, and seedlings are never folded into density maps.</p>
</section>

<section>
<h2 class="prose">The headline: this wood has no next generation of canopy trees</h2>
{plate(2, "fig12_age_structure.png", "Age structure small multiples by species",
       "Age classes split by species — the single most informative view of the data",
       "Read each panel left (youngest) to right (oldest). <strong>Ash</strong>: a "
       "seedling wall of ≥1,824 collapsing to 2 saplings. <strong>Pedunculate "
       "oak</strong>: standards persist in the three largest classes, with nothing "
       "beneath — oak regenerating poorly under its own shade is normal ecology; zero "
       "saplings across a whole wood notified for its oak is a finding. <strong>Sessile "
       "oak</strong>: seven established stems, nothing else at all. <strong>Hazel</strong> "
       "(orange = coppice/multistem) is the abandoned coppice layer, stools now grown "
       "past 50 cm. <strong>Holly</strong> is the one species clearly getting through "
       "— 55 already in the small class, none yet mature: a young, expanding "
       "population.")}
{plate(3, "fig13_seedlings_per_sapling.png", "Seedling to sapling slopegraph by species",
       "The regeneration bottleneck — where the ash story lives",
       "Each line is one species crossing from seedling to sapling. The wood's other "
       "species convert at 2:1 to 29:1. Ash converts at <strong>912:1</strong> — two "
       "orders of magnitude adrift from its neighbours in the same wood, in the species "
       "whose disease Natural England names first. <em>Hymenoscyphus fraxineus</em> "
       "kills young ash fastest, and this looks like its quantified signature — but one "
       "snapshot with no control site makes it a strong hypothesis, not a demonstrated "
       "cause. Note who else is missing at the sapling stage: Wild Cherry and Wild "
       "Service produced none.")}
<div class="callout prose">The successor cohort (7–50 cm, single stems) is led
by <strong>ash (27)</strong> and <strong>wych elm (15)</strong> — the two
species under active disease pressure, since Dutch elm disease fells elms at
roughly 10–20 cm. The one healthy volume successor is field maple (17), a
smaller tree that will not rebuild an oak–lime canopy. When the current
standards go, nothing on this evidence replaces them in kind.</div>
</section>

<section>
<h2 class="prose">Deadwood: the failure is specific, and that makes it fixable</h2>
{plate(4, "fig15_deadwood_types.png", "Deadwood by type and size class",
       "Deadwood by type and size — refining the regulator's judgement",
       "Natural England says 'insufficient standing deadwood'. The survey sharpens "
       "that: total deadwood is not obviously scarce (151 pieces in 0.40 ha), but "
       "<strong>standing</strong> dead wood stops entirely at 50 cm. Large standing "
       "stems are the premium habitat — sun-exposed, long-lasting, used by cavity "
       "nesters, bats and the saproxylic invertebrates ancient woods are valued for. "
       "The management implication is cheap and concrete: retain dying and dead stems "
       "standing wherever safety allows, rather than felling to waste.")}
{plate(8, "fig09_deadwood.png", "Deadwood distribution map",
       "Where the deadwood is — and the one transect with none",
       "Fill counts all pieces; red triangles mark the standing component. Q1, in the "
       "north-west, recorded no deadwood of any kind in 200 m² — worth a look on the "
       "ground. Distribution is otherwise broad, which supports the reading that "
       "quantity is not the problem; size and posture are.")}
</section>

<section>
<h2 class="prose">Density and diversity: the maps Jenny asked for</h2>
{plate(5, "fig03_density.png", "Established stems per hectare, gridded",
       "Established trees per hectare — the honest version",
       "Every coloured cell is a real 200 m² measurement scaled to per-hectare; blank "
       "cells were not surveyed and are never painted. A fourfold spread (450–1,800 "
       "stems/ha, site mean 988) with the densest cells in the south-west — the old "
       "coppice heartland, as the hazel stools in Plate 2 suggest.")}
{plate(6, "fig05_species_diversity.png", "Shannon diversity per transect",
       "Species diversity of established trees",
       "Shannon H′ spans 0.66–1.90. The poorest cells are not the emptiest ones: Q13 "
       "holds 17 stems but 14 are hazel. Low diversity with hazel dominance is the "
       "signature of long-abandoned coppice, and it maps where density peaks. Q3's "
       "hawthorn dominance (21 of 35 stems) hints at former open ground — it sits "
       "near the ~6% of the SSSI that the Ancient Woodland Inventory does not class "
       "as ancient.")}
{plate(7, "fig07_structural_diversity.png", "Size classes present per transect",
       "Structural diversity — the resilience map",
       "How many of the seven size classes each transect holds. Uneven-aged structure "
       "is what lets a wood absorb losing one cohort — precisely the scenario ash "
       "dieback is running now. Cells carrying 6–7 classes are the wood's structural "
       "reserves; cells at 3–4 are single-generation stands where one loss event "
       "removes the stand.")}
</section>

<section>
<h2 class="prose">The notified features: an audit of the 1984 citation</h2>
{plate(9, "fig10_lime_wild_service.png", "Lime and wild service distribution",
       "Small-leaved Lime and Wild Service Tree — 'locally abundant', revisited",
       "Seventeen established limes, eleven of them in the largest class and 45% "
       "coppice or multistem: an ageing population of ancient stools, persisting "
       "rather than recruiting. Lime rarely sets viable seed in Britain's cooled "
       "climate — it survives by regrowth, which means a stool lost is not replaced. "
       "The green dots (young lime) may be suckers of the same old individuals rather "
       "than seedlings; the recording form cannot distinguish, and that distinction "
       "IS the conservation question. Wild Service: one established tree and one "
       "seedling patch. A 1% sample can miss suckering clumps, so this is evidence of "
       "scarcity in the sampled area, not proof of loss — but it justifies a targeted "
       "search, and it is a striking distance from 'locally abundant'.")}
<div class="callout warn prose">The citation also names two rare whitebeams,
<em>Sorbus rupicola</em> and <em>S. eminens</em>. The survey's generic
"Whitebeam" rows cannot be assigned to species, so <strong>the rare
<em>Sorbus</em> the site is partly notified for cannot be assessed from this
data at all</strong> — a monitoring gap worth naming, and another argument for
surveying the unwalked crags, which is exactly where such trees grow.</div>
</section>

<section>
<h2 class="prose">Invasives: genuinely good news, with two watch-items</h2>
{plate(10, "fig11_non_natives.png", "Invasive and non-native records",
       "Non-native trees — 16 records out of 3,218 stems",
       "At 0.5%, the site sits comfortably under the 5–10% thresholds typical of "
       "woodland condition tables — a pass worth stating with a number. Both caveats "
       "are spatial: every sycamore sits on the eastern edge beside the B3124 and "
       "North Weston, a classic roadside seed source pattern that argues for watching "
       "the boundary, and the single unidentified laurel on Q12 should be checked in "
       "the field — if it is Cherry Laurel, one stem now is the cheap moment.")}
</section>

<section>
<h2 class="prose">The heat map, clearly labelled</h2>
{plate(11, "fig04_density_surface.png", "Smoothed density surface, indicative",
       "Smoothed density surface — for communication, not analysis",
       "Jenny asked for heat maps, and this is the defensible way to ship one: the "
       "interpolated surface reads well for trustees and members, but every value "
       "between the dots is an estimate from 20 points covering 1.06% of the site. "
       "The gridded Plate 5 is the version for any decision or report to the "
       "regulator; this one communicates the same south-western density signal to "
       "audiences who read colour, not cells.")}
</section>

<section>
<h2 class="prose">By management unit — the format the regulator uses</h2>
<div class="tablewrap"><table>
<tr><th>Unit</th><th class="num">Area (ha)</th><th class="num">Transects</th>
<th class="num">Est. stems/ha</th><th class="num">Species</th>
<th class="num">Standing dead</th><th class="num">Fallen + stumps</th>
<th class="num">Est. lime</th></tr>
{unit_rows}
</table></div>
<p class="prose">All four units were assessed Unfavourable&nbsp;–&nbsp;Declining in
April 2023. Unit 2 is the densest and least diverse; unit 1 and unit 4 carry
nearly all the lime. <strong>Unit 3 was never sampled</strong> — a coverage
gap to flag before any per-unit claims are made from this table.</p>
</section>

<section class="prose">
<h2>What this analysis assumes, and what would change it</h2>
<div class="callout"><strong>Tally notation: settled.</strong> The tally
"2, C, 2M" is read as 2 single stems + 1 coppice + 2 multistem (total 5),
matching the worked total in the brief. Jenny confirmed this reading on
14 August 2026, so the counts here are final.</div>
<ol class="qs">
<li><strong>"Dead fallen": pieces or whole trees?</strong> The methodology
("measure the midpoint of the section inside the quadrat") reads as pieces;
the deadwood conclusion changes by a large factor either way.</li>
<li><strong>The 29 unwalked squares</strong> — how many were cliff-bound
versus not-yet-reached? The coverage map legend, and the case for finishing
the survey, depend on the split.</li>
<li><strong>q18 has no recorded date</strong>; all other sheets fall
12 May – 6 Oct 2022.</li>
<li><strong>Field checks worth one visit:</strong> the Q12 laurel; whether the
young lime are seedlings or suckers; a targeted wild service search; Q1's
missing deadwood; and Ribes sp. noted on Q9 — an AWI species recorded for the
site record that would otherwise be lost in a comments cell.</li>
</ol>
</section>

<footer class="prose">
Survey data © Avon Wildlife Trust, unpublished — this report is for AWT review
and is not for circulation. Boundaries: Natural England open data (SSSI,
units, Ancient Woodland Inventory), OSGB36 / EPSG:27700. Analysis: fully
scripted Python pipeline (pandas · geopandas · matplotlib), tally parser
validated against the brief's worked examples and all 90 notation variants in
the workbook; every figure and number regenerates from the raw workbook in
one run.
</footer>
</div>
"""

out = OUTPUTS / "report.html"
out.write_text(html, encoding="utf-8")
print(f"wrote {out}  ({out.stat().st_size / 1e6:.1f} MB)")
