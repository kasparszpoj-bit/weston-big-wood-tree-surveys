# Figure list

Fifteen figures in the report. Eleven are maps, four are statistical charts.

Most maps exist in two versions: a matplotlib one built by
`scripts/02_make_figures.py`, and a QGIS one built by
`scripts/08_qgis_figures.py`. Figure 1 is QGIS only, because it needs a
basemap. Figures 12 to 15 are matplotlib only, because they have no geometry.

| Fig | Title | Python | QGIS |
|---|---|---|---|
| 1 | Survey coverage on an OS basemap | | `qgis/fig01_survey_coverage_basemap.png` |
| 2 | Survey coverage, 20 of 49 planned transects | `fig02_coverage.png` | `qgis/fig02_survey_coverage_plain.png` |
| 3 | Established trees per hectare | `fig03_density.png` | `qgis/fig03_established_per_ha.png` |
| 4 | Smoothed tree density surface | `fig04_density_surface.png` | `qgis/fig04_density_surface.png` |
| 5 | Species diversity, Shannon H' | `fig05_species_diversity.png` | `qgis/fig05_species_diversity.png` |
| 6 | Smoothed species diversity surface | `fig06_diversity_surface.png` | `qgis/fig06_diversity_surface.png` |
| 7 | Structural diversity, size classes present | `fig07_structural_diversity.png` | `qgis/fig07_structural_diversity.png` |
| 8 | Smoothed structural diversity surface | `fig08_structural_surface.png` | `qgis/fig08_structural_surface.png` |
| 9 | Deadwood distribution per transect | `fig09_deadwood.png` | `qgis/fig09_deadwood.png` |
| 10 | Small-leaved lime and wild service tree | `fig10_lime_wild_service.png` | `qgis/fig10_lime_wild_service.png` |
| 11 | Invasive and non-native trees | `fig11_non_natives.png` | `qgis/fig11_non_natives.png` |
| 12 | Age structure by species | `fig12_age_structure.png` | |
| 13 | Seedlings per sapling | `fig13_seedlings_per_sapling.png` | |
| 14 | Canopy and the layer replacing it | `fig14_canopy_successors.png` | |
| 15 | Deadwood by type and size | `fig15_deadwood_types.png` | |

All paths are relative to `outputs/figures/`.

## Where the numbers come from

Every figure is a `groupby` on the single tidy table produced by
`wbw.ingest.read_workbook()`. The layers they are drawn on come from four
GeoPackages in `data/external/`:

| Layer | Written by | Carries |
|---|---|---|
| `survey_results.gpkg → results` | script 05 | `est_per_ha`, `shannon`, `n_classes`, `dead_total`, `dead_standing`, `lime_est`, `lime_young`, `wild_service`, `non_native` per square |
| `survey_plan.gpkg → plan_cells` | script 04 | `surveyed`, `mean_slope_deg`, `max_slope_deg`, `contains_cliff` |
| `boundaries.gpkg` | script 01 | `sssi_boundary`, `sssi_units`, `ancient_woodland` |
| `non_natives.gpkg → non_natives` | script 07 | one point per transect per species, with `stems` |

## Conventions used on every map

- **Blank means not surveyed, never zero.** Unsurveyed squares are drawn as
  grey diagonal hatch, and the legend says so.
- Seedlings are excluded from every density figure, because field counts were
  capped at 100 per cell, so including them would give a floor rather than a
  number.
- Established trees means stems of 7 cm dbh or more: the small, medium, mature
  and overmature classes.
- Each 200 m² transect is scaled to a hectare by multiplying by 50.
- Figures carry a title and legend only. Captions live in the report document
  so they stay editable, which means the honesty caveats have to be stated
  there.
