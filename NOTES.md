# Weston Big Wood tree surveys (Avon Wildlife Trust)

A real GIS and data analysis job for a named client: turning Avon Wildlife
Trust's paper tree survey sheets for Weston Big Wood SSSI into density maps,
diversity maps and age class analysis.

Folder location: 02_skills_and_portfolio/projects/weston_big_wood_tree_surveys

This is the first portfolio project with an actual organisation, an actual
brief, and a named contact who can act as a non academic reference. That makes
it more valuable than any self directed practice project.

## What is in this folder

- **brief.md**: what Jenny asked for, the data structure, the tally notation,
  the deliverables list, and the open questions that need answering.
- **data_audit.md**: first full read of the raw files. What is in them, what is
  broken, and the first numbers.
- **pre_analysis_findings.md**: what the data actually shows, what is worth
  investigating, and what to do before writing any plotting code. **Read this
  one first.**
- **site_dossier.md**: everything about Weston Big Wood SSSI. Citation text,
  designated features, the four management units and their condition, and why
  the condition data shapes the analysis.
- **gis_data_sources.md**: where all the external spatial data comes from.
  Designated Sites View, Magic Map, the Natural England API, Environment Agency
  LIDAR, the endpoints, and the traps. Read this before hunting for a layer.

## The code

```
pyproject.toml        dependencies and package metadata
src/wbw/              the analysis package, installed into the venv
  config.py           paths, CRS, transect geometry, documented data repairs
  tally.py            parser for the field tally notation
scripts/              numbered entry points, run in order
tests/                pytest suite
data/raw/             the survey files as received. Never written to
data/external/        downloaded Natural England layers
data/processed/       tidy tables built by the pipeline
outputs/              figures and tables, all regenerable
notebooks/            exploration only, never a deliverable
```

Everything under `data/processed`, `data/external` and `outputs` is rebuilt by
the pipeline, so all three are untracked. Delete them and rerun and you get the
same results.

### Setup

```bash
python -m venv .venv
.venv/Scripts/activate          # Windows. On macOS or Linux: source .venv/bin/activate
python -m pip install -e ".[dev]"
```

### Running

```bash
python -m pytest                # run the tests
python -m ruff check .          # lint
```

Python 3.14 is confirmed working: every dependency including shapely and pyproj
has a `cp314` wheel, so no conda and no compiler are needed.

One Windows gotcha: the size class headers contain the `≤` character, which the
default cp1252 console cannot print. Set `PYTHONUTF8=1` if a script fails with
`UnicodeEncodeError`.

### A note on the data

`data/raw/` is deliberately untracked, permanently. The survey data belongs to
Avon Wildlife Trust and has not been published, so it is not ours to put in a
public repository, and it has never been committed at any point in this
repository's history. The code, the method and the written findings are ours;
the raw data is not. This repository is public with Jenny's agreement.

## Why this work exists

The 2022 survey is a whole-wood structural baseline: 49 planned transects
recording every stem by species and size class, plus three deadwood
categories. It was run deep into the ash dieback outbreak in southwest
England, when a manager of an ash-rich wood with public access needs to know
how much ash there is, how big it is, and what might replace it. It also
feeds reserve management plan renewal, and gives AWT its own evidence base
for the Natural England condition assessment, which was made in April 2023.

## The idea in three lines

Avon Wildlife Trust surveyed trees across roughly 20 grid squares in Weston Big
Wood, on paper, and the data has never been analysed. All four management units
of the SSSI are currently classed Unfavourable and Declining, on ash dieback and
insufficient standing deadwood. The analysis produces the spatial evidence base
for exactly those failing features.

## Status (2026-08-06)

- Brief received in full from Jenny Greenwood, GIS and Monitoring Manager.
- **Data IS in hand**, in `data/raw/`. Jenny gave up on the SharePoint share and
  sent the files directly. The Conditional Access block was bypassed, not fixed.
- Site background research complete: SSSI citation and unit condition data
  pulled from Natural England and captured in site_dossier.md.
- **Python project scaffolded and working.** Virtual environment, package,
  linting and tests all running.
- **Tally parser written and tested.** 26 tests pass, including both of Jenny's
  worked examples. Verified against the workbook: 437 cells across 79 distinct
  notation values parse, and the only cells that do not are the repeated header
  blocks and the three known free text entries.
- Ingest, spatial join and plotting are not written yet.
- **Jenny has specified the analysis must be done in Python.**
- Grid references confirmed as OSGB36, so EPSG:27700.
- No AWT site boundary supplied. Jenny said to use the Natural England SSSI
  polygon as a stand-in.

## Next steps

Immediate, before Friday 7 August:

- Send Jenny the open questions in brief.md. She is in the field Thursday and
  Friday and away all the following week.
- Complete the AWT volunteer registration form.

The analysis, now unblocked:

- ~~Read the methodology PDF and the blank input form, and reconcile them
  against the workbook columns.~~ Done, see data_audit.md.
- ~~Write the tally notation parser.~~ Done, `src/wbw/tally.py`.
- ~~Write the OS grid reference converter.~~ Not needed: the coordinates are
  already numeric eastings and northings.
- ~~Download the SSSI boundary, the four unit boundaries and the Ancient
  Woodland Inventory from Natural England open data.~~ Done, in
  `data/external/boundaries.gpkg`.
- Parse the 20 Q sheets into one tidy table, one row per tree record.
- **Survey coverage map, plus the terrain constraint analysis.** Confirmed as a
  wanted output. 49 planned transects against 20 surveyed, with LIDAR slope used
  to test whether the 29 skipped points really were the steep ones. Full spec
  and the verified data source are in section 13 of pre_analysis_findings.md.
- Build the density, diversity and deadwood maps.
- Build the age class graphs split by species.
- Report per management unit as well as whole site.

## Related

- The warm intro chain and reference value: see [[project-portfolio-sequence]]
  in the memory notes.
- The Iceland placement project that follows this one:
  02_skills_and_portfolio/projects/thorsmork_trail_effectiveness
