"""Build every figure for the Weston Big Wood report.

Run:  python scripts/02_make_figures.py
Writes PNGs to outputs/figures/ and summary tables to outputs/tables/.

Figures carry a title and legend only. Captions are written in the report
document rather than burned into the image, so they stay editable. The
honesty rules each figure depends on (seedling counts are censored minima,
blank map cells mean NOT SURVEYED rather than zero, and the smoothed surface
is indicative) therefore have to be stated in those captions.
"""

import json

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle

from wbw.config import (
    DATA_EXTERNAL,
    FIGURES,
    SURVEY_WORKBOOK,
    TABLES,
    ensure_output_dirs,
)
from wbw.ingest import CLASS_ORDER, ESTABLISHED, read_workbook
from wbw.locations import grid_cell, planned_points, surveyed_points, transect_line

# ---------------------------------------------------------------- style ----
INK = "#0b0b0b"; INK2 = "#52514e"; MUTED = "#898781"
GRID = "#e1e0d9"; SURFACE = "#fcfcfb"; NEUTRAL = "#f0efec"
BLUE = "#2a78d6"; ORANGE = "#eb6834"; AQUA = "#1baf7a"
VIOLET = "#4a3aa7"; CRITICAL = "#d03b3b"
SEQ = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7",
       "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281"]

plt.rcParams.update({
    "font.family": "Segoe UI", "font.size": 9,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK2,
    "axes.titlecolor": INK, "axes.titlesize": 10, "axes.titleweight": "bold",
    "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.axisbelow": True, "figure.dpi": 150, "savefig.dpi": 150,
    "savefig.facecolor": SURFACE, "savefig.bbox": "tight",
})

CLASS_TICKS = ["Seedling\n≤100 cm", "Seedling\n>1 m", "Sapling\n3–7 cm",
               "Small\n≤25 cm", "Medium\n≤50 cm", "Mature\n≤75 cm",
               "Over-\nmature"]


def seq_color(value, vmax):
    """Sequential blue for a magnitude in [0, vmax]."""
    if vmax <= 0 or value <= 0:
        return SEQ[0]
    i = round((len(SEQ) - 1) * min(value, vmax) / vmax)
    return SEQ[i]


def save(fig, name):
    fig.savefig(FIGURES / name)
    plt.close(fig)
    print(f"  wrote {name}")


def despine(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


# ---------------------------------------------------------------- data ----
ensure_output_dirs()
print("Reading workbook ...")
table, problems, notes = read_workbook(SURVEY_WORKBOOK)
live = table[~table["dead"]].copy()
dead = table[table["dead"]].copy()
est = live[live["size_class"].isin(ESTABLISHED)].copy()

pts = surveyed_points(SURVEY_WORKBOOK)
plan = planned_points()
plan = plan.merge(pts[["easting", "northing", "transect"]],
                  on=["easting", "northing"], how="left")
plan["surveyed"] = plan["transect"].notna()

sssi = gpd.read_file(DATA_EXTERNAL / "boundaries.gpkg", layer="sssi_boundary")
units = gpd.read_file(DATA_EXTERNAL / "boundaries.gpkg", layer="sssi_units")
awi = gpd.read_file(DATA_EXTERNAL / "boundaries.gpkg", layer="ancient_woodland")

pts_gdf = gpd.GeoDataFrame(
    pts, geometry=[grid_cell(e, n) for e, n in zip(pts.easting, pts.northing)],
    crs="EPSG:27700")
starts = gpd.GeoDataFrame(
    pts, geometry=gpd.points_from_xy(pts.easting, pts.northing), crs="EPSG:27700")
unit_join = gpd.sjoin(starts, units[["NUMBER", "geometry"]],
                      how="left", predicate="within")
pts_gdf["unit"] = unit_join["NUMBER"].values

per_tr = {
    "est": est.groupby("transect")["stems"].sum(),
    "richness": est.groupby("transect")["species"].nunique(),
    "classes": live.groupby("transect")["size_class"].nunique(),
    "standing": dead[dead.species == "Dead standing"].groupby("transect")["stems"].sum(),
    "fallen": dead[dead.species.isin(["Dead fallen", "Stump"])].groupby("transect")["stems"].sum(),
    "lime": est[est.species == "Small-leaved Lime"].groupby("transect")["stems"].sum(),
}


def shannon(group):
    p = group.groupby("species")["stems"].sum()
    p = p[p > 0] / p.sum()
    return float(-(p * np.log(p)).sum())


per_tr["shannon"] = est.groupby("transect").apply(shannon, include_groups=False)
for key, series in per_tr.items():
    pts_gdf[key] = pts_gdf["transect"].map(series).fillna(0)


def draw_base(ax, boundary=True, boundary_awi=False):
    if boundary_awi:
        awi.plot(ax=ax, facecolor="#e9efe4", edgecolor="none")
    if boundary:
        sssi.plot(ax=ax, facecolor=NEUTRAL if not boundary_awi else "none",
                  edgecolor=INK2, linewidth=1.2)
        units.plot(ax=ax, facecolor="none", edgecolor=MUTED,
                   linewidth=0.6, linestyle="--")
    ax.set_aspect("equal")
    ax.grid(False)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


def scale_bar(ax, x, y):
    ax.plot([x, x + 100], [y, y], color=INK, lw=2, solid_capstyle="butt")
    ax.text(x + 50, y - 28, "100 m", ha="center", fontsize=7, color=INK2)


def cell_map(ax, value_col, vmax=None, fmt="{:.0f}", label_color=None):
    """Gridded 100 m choropleth: every coloured cell is a real measurement."""
    vmax = vmax or pts_gdf[value_col].max()
    unsurveyed = plan[~plan.surveyed]
    for _, r in unsurveyed.iterrows():
        cell = grid_cell(r.easting, r.northing)
        xs, ys = cell.exterior.xy
        ax.fill(xs, ys, facecolor="none", edgecolor=MUTED,
                linewidth=0.5, hatch="///", alpha=0.45)
    for _, r in pts_gdf.iterrows():
        xs, ys = r.geometry.exterior.xy
        ax.fill(xs, ys, facecolor=seq_color(r[value_col], vmax),
                edgecolor=SURFACE, linewidth=1.4)
        v = r[value_col]
        step = round((len(SEQ) - 1) * min(v, vmax) / vmax) if vmax else 0
        ink = SURFACE if step >= 7 else INK
        ax.text(r.easting, r.northing, fmt.format(v), ha="center",
                va="center", fontsize=6.5, color=label_color or ink)


def map_legend(ax, title, low="low", high="high"):
    for i, c in enumerate(SEQ[::3]):
        ax.add_patch(Rectangle((0.02 + i * 0.025, 0.035), 0.025, 0.03,
                     transform=ax.transAxes, facecolor=c, edgecolor="none"))
    ax.text(0.02, 0.075, title, transform=ax.transAxes, fontsize=7.5,
            color=INK2, weight="bold")
    ax.text(0.02, 0.012, low, transform=ax.transAxes, fontsize=6.5, color=MUTED)
    ax.text(0.125, 0.012, high, transform=ax.transAxes, fontsize=6.5,
            color=MUTED, ha="right")
    ax.add_patch(Rectangle((0.155, 0.035), 0.025, 0.03, transform=ax.transAxes,
                 facecolor="none", edgecolor=MUTED, hatch="///", lw=0.5))
    ax.text(0.185, 0.042, "not surveyed ≠ zero", transform=ax.transAxes,
            fontsize=6.5, color=INK2)


# ------------------------------------------------ fig 1: coverage map ----
print("Figures ...")
fig, ax = plt.subplots(figsize=(7.5, 7))
draw_base(ax)
for _, r in plan.iterrows():
    cell = grid_cell(r.easting, r.northing)
    xs, ys = cell.exterior.xy
    if r.surveyed:
        ax.fill(xs, ys, facecolor="#b7d3f6", edgecolor=BLUE, linewidth=0.8)
    else:
        ax.fill(xs, ys, facecolor="none", edgecolor=MUTED, linewidth=0.6,
                hatch="///", alpha=0.5)
for _, r in plan.iterrows():
    line = transect_line(r.easting, r.northing, r.bearing)
    xs, ys = line.xy
    color = "#184f95" if r.surveyed else MUTED
    ax.plot(xs, ys, color=color, lw=1.6 if r.surveyed else 1.0,
            solid_capstyle="round", alpha=1 if r.surveyed else 0.7)
    ax.plot(xs[0], ys[0], "o", color=color, ms=3)
for _, r in plan[plan.surveyed].iterrows():
    ax.annotate(r.transect, (r.easting, r.northing),
                textcoords="offset points", xytext=(0, -20),
                ha="center", fontsize=6, color="#184f95", weight="bold")
ax.set_title("Survey coverage")
handles = [
    Patch(facecolor="#b7d3f6", edgecolor=BLUE, label="Surveyed (20)"),
    Patch(facecolor="none", edgecolor=MUTED, hatch="///", label="Not surveyed (29)"),
    Line2D([0], [0], color="#184f95", lw=1.6, label="50 m transect, on its bearing"),
    Line2D([0], [0], color=INK2, lw=1.2, label="SSSI boundary"),
    Line2D([0], [0], color=MUTED, lw=0.6, ls="--", label="Management units"),
]
ax.legend(handles=handles, loc="upper left", fontsize=7.5, frameon=False)
save(fig, "fig02_coverage.png")

# --------------------------------- fig 2: age structure by species ----
# Narrative order, not abundance order: the two dieback and oak stories
# first, then the possible successors, the understorey, and finally the two
# species the SSSI is notified for.
species_panels = ["Ash", "Pedunculate Oak",
                  "Sessile Oak", "Wych Elm",
                  "Field Maple", "Hazel",
                  "Holly", "Hawthorn",
                  "Small-leaved Lime", "Wild Service Tree"]

# Portrait 5x2 so the figure fills an A4 page instead of being shrunk to a
# strip. Each panel keeps its own y scale: the point is the SHAPE of each
# species' distribution, and a shared scale would flatten everything except
# Ash, whose seedling bank is two orders of magnitude above the rest.
fig, axes = plt.subplots(5, 2, figsize=(7.2, 9.2), sharex=True)
x = np.arange(len(CLASS_ORDER))
ABBREV = ["S", "S+", "Sap", "Sm", "Med", "Mat", "OM"]

for ax, sp in zip(axes.flat, species_panels):
    sub = live[live.species == sp]
    singles = [int(sub[sub.size_class == c]["single"].sum()) for c in CLASS_ORDER]
    stools = [int(sub[sub.size_class == c][["coppice", "multi"]].sum().sum())
              for c in CLASS_ORDER]
    censored = {c: bool(sub[sub.size_class == c]["censored"].any())
                for c in CLASS_ORDER}
    totals = [s + m for s, m in zip(singles, stools)]
    top = max(totals) if max(totals) else 1

    ax.bar(x, singles, 0.7, color=BLUE, label="Single stem", zorder=3)
    ax.bar(x, stools, 0.7, bottom=singles, color=ORANGE,
           label="Coppice / multistem", zorder=3)

    # Mark absent classes that sit between occupied ones. An interior gap is
    # a break in the pipeline; an empty tail is just a species that has not
    # reached that size, which is a different thing.
    occupied = [i for i, t in enumerate(totals) if t]
    if occupied:
        for i in range(min(occupied), max(occupied) + 1):
            if not totals[i]:
                ax.plot(i, top * 0.045, marker="x", color=CRITICAL, ms=5,
                        mew=1.4, zorder=4)

    despine(ax)
    ax.set_title(sp, fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(ABBREV, fontsize=7)
    ax.set_ylim(0, top * 1.32)
    ax.tick_params(labelsize=7)
    for xi, (t, c) in enumerate(zip(totals, CLASS_ORDER)):
        if t:
            mark = "≥" if censored[c] else ""
            ax.text(xi, t + top * 0.05, f"{mark}{t}", ha="center",
                    fontsize=6.5, color=INK2)

handles = [
    Patch(facecolor=BLUE, label="Single stem (dbh)"),
    Patch(facecolor=ORANGE, label="Coppice / multistem (stool width)"),
    Line2D([0], [0], marker="x", color=CRITICAL, lw=0, mew=1.4, ms=6,
           label="Size class absent, with larger stems present"),
]
fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.962),
           ncol=1, fontsize=7.5, frameon=False)
fig.suptitle("Age structure by species",
             fontsize=12, weight="bold", color=INK, y=0.995)
# top leaves room for the suptitle plus the three-row legend above the first
# row of panel titles; without it the legend text runs into them.
fig.subplots_adjust(top=0.855, bottom=0.04, hspace=0.45, wspace=0.22)
save(fig, "fig12_age_structure.png")

# --------------------------------- fig 3: regeneration bottleneck ----
# Shown as the conversion RATE, not as two absolute counts. The finding is a
# ratio, so plotting the ratio directly means the reader sees it rather than
# inferring it from the slope of a line. A linear axis is deliberate: Ash's
# bar running thirty times past the next species IS the finding, and a log
# axis would flatten exactly the outlier the figure exists to show.
SEED_CLASSES = ["seedling_le100", "seedling_gt100"]

conv = []
for sp in live.species.unique():
    s = live[live.species == sp]
    seed = int(s[s.size_class.isin(SEED_CLASSES)]["stems"].sum())
    sap = int(s[s.size_class == "sapling"]["stems"].sum())
    if seed >= 10:
        conv.append({"species": sp, "seedlings": seed, "saplings": sap,
                     "ratio": seed / sap if sap else np.inf})
conv = pd.DataFrame(conv).sort_values("ratio")

fig, ax = plt.subplots(figsize=(7.2, 4.8))
y = np.arange(len(conv))

# Species with no saplings have no finite ratio, so there is no bar length to
# draw. Rather than exiling them to a footnote, where they get missed, they
# are drawn as open bars running just past the worst measurable species and
# labelled for what they are. The hatching signals "off the scale" rather
# than a value.
NO_SAPLING_BAR = 950
COUNT_COL_X = 1440

for i, r in enumerate(conv.itertuples()):
    if np.isfinite(r.ratio):
        bold = r.species == "Ash"
        ax.barh(i, r.ratio, 0.62, color=ORANGE if bold else "#c3c2b7",
                zorder=3)
        ax.text(r.ratio + 15, i, f"{r.ratio:,.0f} : 1", va="center",
                fontsize=8.5, color=ORANGE if bold else INK2,
                weight="bold" if bold else "normal")
    else:
        ax.barh(i, NO_SAPLING_BAR, 0.62, facecolor="none", edgecolor=MUTED,
                hatch="////", linewidth=0.8, zorder=3)
        ax.text(NO_SAPLING_BAR + 15, i, "no saplings", va="center",
                fontsize=8.5, color=INK2, style="italic")
    ax.text(COUNT_COL_X, i, f"{r.seedlings:,} → {r.saplings}", ha="right",
            va="center", fontsize=7.5, color=MUTED)

ax.text(COUNT_COL_X, len(conv) - 0.35, "seedlings → saplings",
        ha="right", va="bottom", fontsize=7, color=MUTED, style="italic")

ax.set_yticks(y)
ax.set_yticklabels(conv.species, fontsize=9)
for tick, sp in zip(ax.get_yticklabels(), conv.species):
    if sp == "Ash":
        tick.set_color(ORANGE)
        tick.set_fontweight("bold")
ax.set_xlim(0, 1500)
ax.set_xticks([0, 200, 400, 600, 800, 1000])
ax.set_xlabel("seedlings recorded per sapling reaching 3–7 cm")
ax.grid(axis="y", visible=False)
despine(ax)
ax.spines["left"].set_visible(False)
ax.tick_params(axis="y", length=0)

ax.set_title("Seedlings per sapling")
fig.subplots_adjust(left=0.30, right=0.97, top=0.9, bottom=0.2)
save(fig, "fig13_seedlings_per_sapling.png")


# ------------------------------------------- fig 4: deadwood chart ----
fig, ax = plt.subplots(figsize=(7.2, 4.6))
dw_classes = ["small", "medium", "mature", "overmature"]
dw_types = [("Dead standing", BLUE), ("Dead fallen", ORANGE), ("Stump", AQUA)]
w = 0.26
for i, (kind, color) in enumerate(dw_types):
    vals = [int(dead[(dead.species == kind) & (dead.size_class == c)]["stems"].sum())
            for c in dw_classes]
    bars = ax.bar(np.arange(4) + (i - 1) * w, vals, w * 0.92, color=color,
                  label=kind, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.6, str(v), ha="center",
                fontsize=7.5, color=INK2)
ax.set_xticks(np.arange(4))
ax.set_xticklabels(["Small ≤25 cm", "Medium ≤50 cm", "Mature ≤75 cm",
                    "Overmature >75 cm"], fontsize=8.5)
ax.set_ylabel("pieces in 0.40 ha")
despine(ax)
ax.legend(fontsize=8, frameon=False)
ax.set_title("Deadwood by type and size")
ax.annotate("0 standing pieces\nabove 50 cm",
            xy=(2.74, 1), xytext=(1.9, 42), fontsize=8, color=CRITICAL,
            weight="bold",
            arrowprops={"arrowstyle": "-", "color": CRITICAL, "lw": 1})
save(fig, "fig15_deadwood_types.png")

# ------------------------------------------- fig 5: density map ----
pts_gdf["est_ha"] = pts_gdf["est"] * 50
fig, ax = plt.subplots(figsize=(7.5, 7))
draw_base(ax)
cell_map(ax, "est_ha", fmt="{:.0f}")
ax.set_title("Established trees per hectare (≥7 cm dbh, live stems)")
map_legend(ax, "stems / ha", "450", f"{int(pts_gdf.est_ha.max()):,}")
save(fig, "fig03_density.png")

# ------------------------------------- fig 6: species diversity map ----
fig, ax = plt.subplots(figsize=(7.5, 7))
draw_base(ax)
cell_map(ax, "shannon", fmt="{:.2f}")
ax.set_title("Species diversity of established trees (Shannon H′)")
map_legend(ax, "Shannon H′", "0.66", "1.90")
save(fig, "fig05_species_diversity.png")

# ----------------------------------- fig 7: age-class diversity map ----
fig, ax = plt.subplots(figsize=(7.5, 7))
draw_base(ax)
cell_map(ax, "classes", vmax=7, fmt="{:.0f}")
ax.set_title("Structural diversity: size classes present (of 7)")
map_legend(ax, "classes present", "3", "7")
save(fig, "fig07_structural_diversity.png")

# ------------------------------------------- fig 8: deadwood map ----
pts_gdf["deadwood"] = pts_gdf["standing"] + pts_gdf["fallen"]
fig, ax = plt.subplots(figsize=(7.5, 7))
draw_base(ax)
cell_map(ax, "deadwood", fmt="{:.0f}")
for _, r in pts_gdf.iterrows():
    if r.standing:
        ax.text(r.easting + 32, r.northing + 30, f"▲{int(r.standing)}",
                ha="center", fontsize=6, color=CRITICAL, weight="bold")
q1 = pts_gdf[pts_gdf.transect == "Q1"].iloc[0]
ax.add_patch(Rectangle((q1.easting - 50, q1.northing - 50), 100, 100,
             facecolor="none", edgecolor=CRITICAL, lw=1.4))
ax.annotate("Q1: zero deadwood", (q1.easting, q1.northing - 50),
            textcoords="offset points", xytext=(0, -14), ha="center",
            fontsize=7, color=CRITICAL, weight="bold")
ax.set_title("Deadwood distribution (pieces per transect)")
map_legend(ax, "total pieces", "0", "12")
ax.text(0.63, 0.042, "▲n  standing pieces", transform=ax.transAxes,
        fontsize=6.5, color=CRITICAL)
save(fig, "fig09_deadwood.png")

# ---------------------------------- fig 9: lime and wild service ----
lime_seed = live[(live.species == "Small-leaved Lime")
                 & live.size_class.isin(["seedling_le100", "seedling_gt100", "sapling"])]
lime_seed_tr = lime_seed.groupby("transect")["stems"].sum()
pts_gdf["lime_young"] = pts_gdf["transect"].map(lime_seed_tr).fillna(0)
wst = live[live.species == "Wild Service Tree"].groupby(
    ["transect", "size_class"])["stems"].sum().reset_index()

fig, ax = plt.subplots(figsize=(7.5, 7))
draw_base(ax)
cell_map(ax, "lime", vmax=int(pts_gdf["lime"].max()), fmt="{:.0f}")
for _, r in pts_gdf[pts_gdf.lime_young > 0].iterrows():
    ax.plot(r.easting - 32, r.northing + 30, "o", color=AQUA, ms=5, zorder=5)
    ax.text(r.easting - 32, r.northing + 30, int(r.lime_young), fontsize=5,
            ha="center", va="center", color=SURFACE, zorder=6, weight="bold")
for _, r in wst.iterrows():
    p = pts_gdf[pts_gdf.transect == r.transect].iloc[0]
    ax.plot(p.easting + 32, p.northing - 30, "*", color=VIOLET, ms=13, zorder=5)
    what = "1 medium tree" if r.size_class == "medium" else f"{int(r.stems)} seedlings"
    ax.annotate(f"Wild service: {what}", (p.easting + 32, p.northing - 30),
                textcoords="offset points", xytext=(8, -10), fontsize=7,
                color=VIOLET, weight="bold")
ax.set_title("Small-leaved Lime and Wild Service Tree")
map_legend(ax, "established lime", "0", str(int(pts_gdf.lime.max())))
ax.text(0.63, 0.042, "green dot: young lime   purple star: wild service",
        transform=ax.transAxes, fontsize=6.5, color=INK2)
save(fig, "fig10_lime_wild_service.png")

# ------------------------------------------- fig 10: invasives map ----
# Match on substring, not exact name: the workbook records sycamore as
# "Sycamore (tree)", and an exact-match filter silently dropped all 8 records.
INVASIVE_PATTERNS = {"Sycamore": "sycamore", "Holm Oak": "holm oak",
                     "Buddleia": "buddleia", "Laurel": "laurel"}
inv = live[live.species.str.contains("|".join(INVASIVE_PATTERNS.values()),
                                     case=False, regex=True)].copy()
inv["species"] = inv["species"].str.replace(r"\s*\(tree\)", "", regex=True)
assert int(inv.stems.sum()) == 16, f"expected 16 non-native stems, got {inv.stems.sum()}"
inv_tr = inv.groupby(["transect", "species"])["stems"].sum().reset_index()
fig, ax = plt.subplots(figsize=(7.5, 7))
draw_base(ax)
for _, r in plan[plan.surveyed].iterrows():
    cell = grid_cell(r.easting, r.northing)
    xs, ys = cell.exterior.xy
    ax.fill(xs, ys, facecolor="#eef1ee", edgecolor=SURFACE, linewidth=1.2)
for _, r in plan[~plan.surveyed].iterrows():
    cell = grid_cell(r.easting, r.northing)
    xs, ys = cell.exterior.xy
    ax.fill(xs, ys, facecolor="none", edgecolor=MUTED, linewidth=0.5,
            hatch="///", alpha=0.4)
markers = {"Sycamore": ("o", BLUE), "Holm Oak": ("s", ORANGE),
           "Buddleia": ("D", AQUA)}
offsets = {"Sycamore": (-25, 22), "Holm Oak": (25, 22), "Buddleia": (-25, -25)}
for _, r in inv_tr.iterrows():
    p = pts_gdf[pts_gdf.transect == r.transect].iloc[0]
    sp = r.species if r.species in markers else "Laurel"
    if sp == "Laurel":
        ax.plot(p.easting + 25, p.northing - 25, "X", color=CRITICAL, ms=9, zorder=6)
        ax.annotate("unidentified laurel",
                    (p.easting + 25, p.northing - 25), textcoords="offset points",
                    xytext=(10, -16), fontsize=7, color=CRITICAL, weight="bold")
        continue
    mk, color = markers[sp]
    dx, dy = offsets[sp]
    ax.plot(p.easting + dx, p.northing + dy, mk, color=color, ms=7, zorder=6)
    ax.text(p.easting + dx, p.northing + dy - 22, int(r.stems), fontsize=6.5,
            ha="center", color=INK2)
handles = [Line2D([0], [0], marker=m, color="none", markerfacecolor=c, ms=7,
                  label=s) for s, (m, c) in markers.items()]
handles.append(Line2D([0], [0], marker="X", color="none",
                      markerfacecolor=CRITICAL, ms=8, label="Laurel (unidentified)"))
ax.legend(handles=handles, loc="upper left", fontsize=7.5, frameon=False)
ax.set_title("Invasive and non-native trees")
save(fig, "fig11_non_natives.png")

# ------------------------------------------ figs 11-13: heat maps --------
# Gaussian kernel smoothing, not inverse-distance weighting. IDW puts a
# spike on every sample point, producing bullseye rings that look like real
# structure and are purely an artefact of the method. A Gaussian kernel with
# a bandwidth comparable to the sample spacing (100 m) blends smoothly and
# is honest about how coarse the underlying information is.
KERNEL_SIGMA_M = 90.0

from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MplPath


def smoothed_surface(value_col, title, cbar_label, name,
                     sigma=KERNEL_SIGMA_M, fmt=None):
    """Smoothed 'heat map' of a per-transect metric, clipped to the site."""
    xs = np.arange(sssi.total_bounds[0], sssi.total_bounds[2], 5.0)
    ys = np.arange(sssi.total_bounds[1], sssi.total_bounds[3], 5.0)
    gx, gy = np.meshgrid(xs, ys)
    px = pts.easting.to_numpy(float)
    py = pts.northing.to_numpy(float)
    pv = pts_gdf[value_col].to_numpy(float)

    d2 = (gx[..., None] - px) ** 2 + (gy[..., None] - py) ** 2
    w = np.exp(-d2 / (2 * sigma ** 2))
    z = (w * pv).sum(-1) / w.sum(-1)

    fig, ax = plt.subplots(figsize=(7.5, 7))
    cmap = LinearSegmentedColormap.from_list("seq", SEQ)
    im = ax.pcolormesh(gx, gy, z, cmap=cmap, shading="auto", zorder=1,
                       rasterized=True)

    # Clip with the polygon itself rather than a pixel mask, so the edge is
    # smooth instead of stepped.
    poly = sssi.geometry.iloc[0]
    verts, codes = [], []
    for ring in [poly.exterior, *poly.interiors]:
        coords = np.asarray(ring.coords)
        verts.extend(coords)
        codes.extend([MplPath.MOVETO] + [MplPath.LINETO] * (len(coords) - 2)
                     + [MplPath.CLOSEPOLY])
    im.set_clip_path(PathPatch(MplPath(verts, codes), transform=ax.transData))

    sssi.plot(ax=ax, facecolor="none", edgecolor=INK2, linewidth=1.2, zorder=3)
    ax.scatter(px, py, s=22, color=SURFACE, zorder=4)
    ax.scatter(px, py, s=8, color=INK, zorder=5)
    ax.set_aspect("equal"); ax.grid(False)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    cb = fig.colorbar(im, ax=ax, shrink=0.55, pad=0.01)
    cb.set_label(cbar_label, fontsize=8, color=INK2)
    cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=7.5)
    if fmt:
        cb.ax.yaxis.set_major_formatter(fmt)
    ax.set_title(title)
    save(fig, name)


smoothed_surface(
    "est_ha", "Smoothed tree density surface",
    "established stems / ha (interpolated)", "fig04_density_surface.png")

smoothed_surface(
    "shannon", "Smoothed species diversity surface",
    "Shannon H′ (interpolated)", "fig06_diversity_surface.png")

smoothed_surface(
    "classes", "Smoothed structural diversity surface",
    "size classes present (interpolated)", "fig08_structural_surface.png")

# ------------------------------------------------ unit summary table ----
unit_rows = []
for u in sorted(pts_gdf["unit"].dropna().unique()):
    sub = pts_gdf[pts_gdf.unit == u]
    trs = sub.transect.tolist()
    est_u = est[est.transect.isin(trs)]
    unit_rows.append({
        "unit": int(u),
        "area_ha": float(units[units.NUMBER == u].geometry.area.sum() / 1e4),
        "transects": len(trs),
        "est_stems_ha": round(est_u.stems.sum() * 50 / len(trs)) if trs else 0,
        "species_richness": est_u.species.nunique(),
        "standing_dead": int(sub.standing.sum()),
        "fallen_dead": int(sub.fallen.sum()),
        "established_lime": int(sub.lime.sum()),
        "condition": "Unfavourable – Declining (Apr 2023)",
    })
unit_df = pd.DataFrame(unit_rows)
unit_df.to_csv(TABLES / "unit_summary.csv", index=False)
print(unit_df.to_string(index=False))

stats = {
    "live_stems": int(live.stems.sum()),
    "established": int(est.stems.sum()),
    "est_per_ha": round(est.stems.sum() * 2.5),
    "species_established": int(est.species.nunique()),
    "ash_seedlings_min": int(live[(live.species == "Ash") & live.size_class.isin(
        ["seedling_le100", "seedling_gt100"])].stems.sum()),
    "ash_saplings": 2, "oak_saplings": 0,
    "standing_dead": 20, "fallen_dead": 119, "stumps": 12,
    "wild_service_established": 1, "lime_established": 17,
    "invasive_share_pct": 0.5,
    "transects_per_unit": {int(k): int(v) for k, v in
                           pts_gdf.groupby("unit")["transect"].count().items()},
}
(TABLES / "headline_stats.json").write_text(json.dumps(stats, indent=2))


# --------------------- fig 14: canopy now vs the layer replacing it ------
# SINGLE STEMS ONLY. Coppice and multistem are measured as stool width, so
# counting them here would promote large hazel stools into the canopy and
# make the comparison meaningless.
CANOPY_CLASSES = ["mature", "overmature"]   # >50 cm dbh
SUCCESSOR_CLASSES = ["small", "medium"]     # 7 to 50 cm dbh

canopy_n = live[live.size_class.isin(CANOPY_CLASSES)].groupby("species")["single"].sum()
succ_n = live[live.size_class.isin(SUCCESSOR_CLASSES)].groupby("species")["single"].sum()
comp = pd.DataFrame({"canopy": canopy_n, "succ": succ_n}).fillna(0)
comp["canopy_pct"] = comp.canopy / comp.canopy.sum() * 100
comp["succ_pct"] = comp.succ / comp.succ.sum() * 100

# Only 21 stems make up the canopy layer, so a single stem is nearly 5%.
# Drop the species resting on one or two stems, which would otherwise show
# large percentages that are really sampling noise.
shown = comp[(comp.canopy >= 2) | (comp.succ >= 5)].sort_values("canopy_pct")

fig, ax = plt.subplots(figsize=(7.4, 5.2))
y = np.arange(len(shown))

for i, r in enumerate(shown.itertuples()):
    falling = r.succ_pct < r.canopy_pct
    ax.plot([r.canopy_pct, r.succ_pct], [i, i],
            color=CRITICAL if falling else "#c3c2b7",
            lw=2.2 if falling else 1.6, zorder=2, solid_capstyle="round")

ax.scatter(shown.canopy_pct, y, s=70, color=INK, zorder=3,
           label=f"Canopy, >50 cm (n={int(comp.canopy.sum())})")
ax.scatter(shown.succ_pct, y, s=70, color=BLUE, zorder=3,
           label=f"Replacing it, 7–50 cm (n={int(comp.succ.sum())})")

for i, r in enumerate(shown.itertuples()):
    lo, hi = sorted((r.canopy_pct, r.succ_pct))
    ax.text(hi + 1.6, i, f"{r.canopy_pct:.0f}% → {r.succ_pct:.0f}%",
            va="center", fontsize=7.5, color=INK2)

ax.set_yticks(y)
ax.set_yticklabels(shown.index, fontsize=9)
ax.set_xlim(-1.5, 48)
ax.set_xlabel("share of that layer, single stems")
ax.grid(axis="y", visible=False)
despine(ax)
ax.spines["left"].set_visible(False)
ax.tick_params(axis="y", length=0)
ax.legend(loc="lower right", fontsize=8, frameon=False)
ax.set_title("Canopy and the layer replacing it")
fig.subplots_adjust(left=0.26, right=0.97, top=0.9, bottom=0.13)
save(fig, "fig14_canopy_successors.png")

print("\nAll figures written to outputs/figures/")
