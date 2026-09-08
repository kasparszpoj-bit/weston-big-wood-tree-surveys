"""Build figures 1 to 11 as QGIS print layouts and export them as PNGs.

Run this INSIDE QGIS (Plugins > Python Console, or via the qgis MCP server).
It needs the QGIS Python environment for PyQGIS and Processing, so it will not
run under the project venv.

Idempotent: every layer it creates is named with a prefix and every layout with
"Fig ", and a previous run is torn down first, so it can be re-run after an
edit without duplicating anything.

Figures 12 to 15 are statistical charts with no geometry and stay in Python
(scripts/02_make_figures.py). Figures 4, 6 and 8 use IDW here, whereas the
Python versions use Gaussian kernel smoothing, so the two are related but not
identical surfaces and must not be presented as the same figure.
"""

import gc
import glob
import os

import processing
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsCategorizedSymbolRenderer,
    QgsClassificationJenks,
    QgsColorRampShader,
    QgsCoordinateReferenceSystem,
    QgsFillSymbol,
    QgsGeometryGeneratorSymbolLayer,
    QgsGradientColorRamp,
    QgsGraduatedSymbolRenderer,
    QgsLayerTree,
    QgsLayoutExporter,
    QgsLayoutItemLabel,
    QgsLayoutItemLegend,
    QgsLayoutItemMap,
    QgsLayoutItemPage,
    QgsLayoutMeasurement,
    QgsLinePatternFillSymbolLayer,
    QgsLineSymbol,
    QgsMapLayerLegendUtils,
    QgsMarkerSymbol,
    QgsPalLayerSettings,
    QgsPrintLayout,
    QgsProject,
    QgsProperty,
    QgsRasterLayer,
    QgsRasterShader,
    QgsRectangle,
    QgsRendererCategory,
    QgsRendererRange,
    QgsSimpleFillSymbolLayer,
    QgsSimpleLineSymbolLayer,
    QgsSingleBandPseudoColorRenderer,
    QgsSingleSymbolRenderer,
    QgsSymbol,
    QgsTextBufferSettings,
    QgsTextFormat,
    QgsUnitTypes,
    QgsVectorLayer,
    QgsVectorLayerSimpleLabeling,
)
from qgis.PyQt.QtCore import QRectF, Qt
from qgis.PyQt.QtGui import QColor, QFont

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------

# Resolved rather than hardcoded, so this runs on any machine. The QGIS Python
# console does not always define __file__, hence the fallbacks: set WBW_ROOT if
# neither the script location nor the working directory is the project root.
ROOT = os.environ.get("WBW_ROOT") or (
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if "__file__" in globals()
    else os.getcwd()
)
EXTERNAL = os.path.join(ROOT, "data", "external")
PROCESSED = os.path.join(ROOT, "data", "processed")
OUT_DIR = os.path.join(ROOT, "outputs", "figures", "qgis")

BOUNDARIES = os.path.join(EXTERNAL, "boundaries.gpkg")
SURVEY_PLAN = os.path.join(EXTERNAL, "survey_plan.gpkg")
RESULTS = os.path.join(EXTERNAL, "survey_results.gpkg")
NON_NATIVES = os.path.join(EXTERNAL, "non_natives.gpkg")

for folder in (PROCESSED, OUT_DIR):
    os.makedirs(folder, exist_ok=True)

PREFIX = "fig:"          # marks every layer this script owns, for teardown
GROUP = "Figure layers"  # tree group holding them all

# --------------------------------------------------------------------------
# Shared theme, in one place so all eleven figures match
# --------------------------------------------------------------------------

RAMP_LOW = "#cde2fb"
RAMP_HIGH = "#104281"

INK = "#1a1a1a"
GREY = "#9aa0a6"
NAVY = "#1f3864"
RED = "#c62828"
GREEN = "#2e7d32"
PURPLE = "#6a1b9a"
BLUE_FILL = "#b7d3f6"

FONT = "Arial"
DPI = 200

# The data extent is square (1140 x 1140 m), so a square frame wastes no page.
MAP_RECT = QRectF(8, 20, 182, 182)     # identical frame on every figure
LEGEND_RECT = QRectF(196, 20, 93, 160)
TITLE_RECT = QRectF(8, 5, 281, 12)


def _first(*candidates):
    """Return the first candidate that resolves, so one script spans QGIS 3/4."""
    for get in candidates:
        try:
            value = get()
        except (AttributeError, TypeError, NameError):
            # NameError matters: some fallbacks name classes that only exist on
            # the other major version and are therefore not imported here.
            continue
        if value is not None:
            return value
    raise AttributeError("no candidate resolved")


RENDER_MM = _first(lambda: Qgis.RenderUnit.Millimeters,
                   lambda: QgsUnitTypes.RenderMillimeters)
RENDER_PT = _first(lambda: Qgis.RenderUnit.Points,
                   lambda: QgsUnitTypes.RenderPoints)
LAYOUT_MM = _first(lambda: Qgis.LayoutUnit.Millimeters,
                   lambda: QgsUnitTypes.LayoutMillimeters)
LANDSCAPE = _first(lambda: QgsLayoutItemPage.Orientation.Landscape,
                   lambda: QgsLayoutItemPage.Landscape)
PLACEMENT_HORIZONTAL = _first(lambda: Qgis.LabelPlacement.Horizontal,
                              lambda: QgsPalLayerSettings.Horizontal)
PLACEMENT_OVER_POINT = _first(lambda: Qgis.LabelPlacement.OverPoint,
                              lambda: QgsPalLayerSettings.OverPoint)
LABEL_COLOR_PROP = _first(lambda: QgsPalLayerSettings.Property.Color,
                          lambda: QgsPalLayerSettings.Color)
SHADER_LINEAR = _first(lambda: Qgis.ShaderInterpolationMethod.Linear,
                       lambda: QgsColorRampShader.Interpolated)
SYMBOL_MARKER = _first(lambda: Qgis.SymbolType.Marker,
                       lambda: QgsSymbol.Marker)
EXPORT_OK = _first(lambda: QgsLayoutExporter.ExportResult.Success,
                   lambda: QgsLayoutExporter.Success)
# PyQt6 (QGIS 4) scopes these under their enum type; PyQt5 exposes them flat.
NO_BRUSH = _first(lambda: Qt.BrushStyle.NoBrush, lambda: Qt.NoBrush)
NO_PEN = _first(lambda: Qt.PenStyle.NoPen, lambda: Qt.NoPen)
DISPLAY_ROLE = _first(lambda: Qt.ItemDataRole.DisplayRole, lambda: Qt.DisplayRole)

BNG = QgsCoordinateReferenceSystem("EPSG:27700")
PROJECT = QgsProject.instance()

# Legend trees are referenced by the layouts but owned here, so they must
# outlive the building function or the legends render empty.
_keepalive = []

# Layer id -> the name the legend should show. The layers themselves keep the
# PREFIX in their name so teardown can still find them on a re-run.
DISPLAY = {}


def ramp():
    return QgsGradientColorRamp(QColor(RAMP_LOW), QColor(RAMP_HIGH))


def shown_as(layer, text):
    DISPLAY[layer.id()] = text
    return layer


# --------------------------------------------------------------------------
# Teardown of any previous run
# --------------------------------------------------------------------------


def free_path(path):
    """A writable path: *path* itself if it can be freed, else a numbered one.

    Removing a layer does not always make GDAL drop its file handle straight
    away, so a re-run can find last run's GeoTIFF still locked on Windows.
    Falling back to a new name keeps the rebuild working either way.
    """
    if not os.path.exists(path):
        return path
    try:
        os.remove(path)
        return path
    except OSError:
        pass
    stem, ext = os.path.splitext(path)
    for n in range(1, 100):
        candidate = f"{stem}_{n}{ext}"
        if not os.path.exists(candidate):
            return candidate
        try:
            os.remove(candidate)
            return candidate
        except OSError:
            continue
    raise RuntimeError(f"no writable path near {path}")


def teardown():
    manager = PROJECT.layoutManager()
    for layout in list(manager.printLayouts()):
        if layout.name().startswith("Fig "):
            manager.removeLayout(layout)

    doomed = [
        lyr.id() for lyr in PROJECT.mapLayers().values()
        if lyr.name().startswith(PREFIX)
    ]
    if doomed:
        PROJECT.removeMapLayers(doomed)

    root = PROJECT.layerTreeRoot()
    stale = root.findGroup(GROUP)
    if stale:
        root.removeChildNode(stale)

    # Removing a raster layer does not release its GDAL handle until the Qt
    # deleteLater queue and Python GC have run. Draining both here lets the
    # rebuild reuse the canonical idw_*.tif names instead of numbering upward
    # on every re-run.
    gc.collect()
    QgsApplication.processEvents()
    for path in glob.glob(os.path.join(PROCESSED, "idw_*.tif")):
        for target in (path, path + ".aux.xml"):
            if os.path.exists(target):
                try:
                    os.remove(target)
                except OSError:
                    pass  # still locked; free_path() will number around it


# --------------------------------------------------------------------------
# Layer loading. Layers live in an unchecked tree group so the canvas stays
# usable; every layout pins its own layer list, so visibility never affects
# what gets exported.
# --------------------------------------------------------------------------

_groups = {}


def figure_group(fig):
    root = PROJECT.layerTreeRoot()
    parent = root.findGroup(GROUP) or root.insertGroup(0, GROUP)
    parent.setExpanded(False)
    key = f"Fig {fig:02d}"
    if key not in _groups:
        group = parent.addGroup(key)
        group.setExpanded(False)
        group.setItemVisibilityChecked(False)
        _groups[key] = group
    return _groups[key]


def add_vector(fig, gpkg, layername, tag, subset=None):
    uri = f"{gpkg}|layername={layername}"
    layer = QgsVectorLayer(uri, f"{PREFIX}{fig:02d} {tag}", "ogr")
    if not layer.isValid():
        raise RuntimeError(f"invalid layer: {uri}")
    if subset:
        if not layer.setSubsetString(subset):
            raise RuntimeError(f"provider rejected subset '{subset}' on {layername}")
        if layer.featureCount() == 0:
            raise RuntimeError(f"subset '{subset}' matched nothing on {layername}")
    PROJECT.addMapLayer(layer, False)
    figure_group(fig).addLayer(layer)
    return layer


def add_raster(fig, path, tag):
    layer = QgsRasterLayer(path, f"{PREFIX}{fig:02d} {tag}")
    if not layer.isValid():
        raise RuntimeError(f"invalid raster: {path}")
    PROJECT.addMapLayer(layer, False)
    figure_group(fig).addLayer(layer)
    return layer


# --------------------------------------------------------------------------
# Symbol builders
# --------------------------------------------------------------------------


def outline_only(color, width_mm):
    """Polygon outline with no fill."""
    fill = QgsSimpleFillSymbolLayer(QColor(0, 0, 0, 0))
    fill.setBrushStyle(NO_BRUSH)
    fill.setStrokeColor(QColor(color))
    fill.setStrokeWidth(width_mm)
    fill.setStrokeWidthUnit(RENDER_MM)
    symbol = QgsFillSymbol()
    symbol.changeSymbolLayer(0, fill)
    return symbol


def hatch(fill_color=None, line_color=GREY, outline=GREY, angle=45.0):
    """Diagonal hatch, optionally over a solid fill."""
    symbol = QgsFillSymbol()
    base = QgsSimpleFillSymbolLayer(
        QColor(fill_color) if fill_color else QColor(0, 0, 0, 0)
    )
    if fill_color is None:
        base.setBrushStyle(NO_BRUSH)
    if outline:
        base.setStrokeColor(QColor(outline))
        base.setStrokeWidth(0.15)
        base.setStrokeWidthUnit(RENDER_MM)
    else:
        base.setStrokeStyle(NO_PEN)
    symbol.changeSymbolLayer(0, base)

    lines = QgsLinePatternFillSymbolLayer()
    lines.setColor(QColor(line_color))
    lines.setLineAngle(angle)
    lines.setDistance(2.0)
    lines.setDistanceUnit(RENDER_MM)
    lines.setLineWidth(0.2)
    lines.setLineWidthUnit(RENDER_MM)
    symbol.appendSymbolLayer(lines)
    return symbol


def solid_fill(color, alpha=255, stroke=GREY, stroke_width=0.15):
    col = QColor(color)
    col.setAlpha(alpha)
    fill = QgsSimpleFillSymbolLayer(col)
    if stroke:
        fill.setStrokeColor(QColor(stroke))
        fill.setStrokeWidth(stroke_width)
        fill.setStrokeWidthUnit(RENDER_MM)
    else:
        fill.setStrokeStyle(NO_PEN)
    symbol = QgsFillSymbol()
    symbol.changeSymbolLayer(0, fill)
    return symbol


def line_symbol(color, width_mm):
    line = QgsSimpleLineSymbolLayer(QColor(color))
    line.setWidth(width_mm)
    line.setWidthUnit(RENDER_MM)
    symbol = QgsLineSymbol()
    symbol.changeSymbolLayer(0, line)
    return symbol


def marker(shape, color, size_mm, stroke="white", stroke_width=0.3):
    if shape.startswith(("cross", "line")):
        # Cross and line markers have no interior: they are drawn with the
        # stroke, so coloring the fill leaves an invisible white symbol.
        stroke, stroke_width = color, max(stroke_width, 0.6)
    symbol = QgsMarkerSymbol.createSimple(
        {
            "name": shape,
            "color": color,
            "outline_color": stroke,
            "outline_width": str(stroke_width),
            "size": str(size_mm),
        }
    )
    symbol.setSizeUnit(RENDER_MM)
    return symbol


def centroid_marker(layer, symbol):
    """Draw a marker at each polygon centroid, via a geometry generator."""
    gen = QgsGeometryGeneratorSymbolLayer.create({})
    gen.setGeometryExpression("centroid($geometry)")
    gen.setSymbolType(SYMBOL_MARKER)
    gen.setSubSymbol(symbol)
    fill = QgsFillSymbol()
    fill.changeSymbolLayer(0, gen)
    layer.setRenderer(QgsSingleSymbolRenderer(fill))
    return layer


# --------------------------------------------------------------------------
# Labelling
# --------------------------------------------------------------------------


def label(layer, expression, size=7, color=INK, placement=None, buffer=True,
          color_expression=None, offset_mm=None):
    settings = QgsPalLayerSettings()
    settings.fieldName = expression
    settings.isExpression = True

    fmt = QgsTextFormat()
    fmt.setFont(QFont(FONT))
    fmt.setSize(size)
    fmt.setSizeUnit(RENDER_PT)
    fmt.setColor(QColor(color))
    if buffer:
        buf = QgsTextBufferSettings()
        buf.setEnabled(True)
        buf.setSize(0.7)
        buf.setSizeUnit(RENDER_MM)
        buf.setColor(QColor("white"))
        fmt.setBuffer(buf)
    settings.setFormat(fmt)
    settings.placement = placement or PLACEMENT_HORIZONTAL

    if offset_mm:
        settings.xOffset, settings.yOffset = offset_mm
        settings.offsetUnits = RENDER_MM

    if color_expression:
        settings.dataDefinedProperties().setProperty(
            LABEL_COLOR_PROP, QgsProperty.fromExpression(color_expression)
        )

    layer.setLabeling(QgsVectorLayerSimpleLabeling(settings))
    layer.setLabelsEnabled(True)
    return layer


# --------------------------------------------------------------------------
# Graduated renderers
# --------------------------------------------------------------------------


def graduated_manual(layer, field, breaks, labels=None):
    """Graduated renderer with exact class boundaries.

    Used wherever the class edges matter: integer fields, or a fixed scale the
    brief specifies. Natural breaks would invent its own edges.
    """
    colours = ramp()
    ranges = []
    n = len(breaks) - 1
    for i in range(n):
        lower, upper = breaks[i], breaks[i + 1]
        colour = colours.color(i / max(n - 1, 1))
        text = labels[i] if labels else f"{lower:g} to {upper:g}"
        ranges.append(
            QgsRendererRange(lower, upper, solid_fill(colour.name(), stroke=GREY), text)
        )
    renderer = QgsGraduatedSymbolRenderer(field, ranges)
    renderer.setSourceColorRamp(ramp())
    layer.setRenderer(renderer)
    return renderer


def graduated_jenks(layer, field, classes=5):
    """Natural breaks, as the brief asks for on the continuous fields."""
    renderer = QgsGraduatedSymbolRenderer(field, [])
    renderer.setClassificationMethod(QgsClassificationJenks())
    renderer.setSourceSymbol(solid_fill(RAMP_LOW, stroke=GREY))
    renderer.setSourceColorRamp(ramp())
    renderer.updateClasses(layer, classes)
    renderer.updateColorRamp(ramp())
    layer.setRenderer(renderer)
    return renderer


def relabel_ranges(renderer, formatter):
    """Rewrite auto-generated class labels as "low to high".

    QGIS writes "450 - 600"; the report style uses no dash as a connector, and
    the numbers should be formatted the same way as the on-map labels.
    """
    for i, item in enumerate(renderer.ranges()):
        renderer.updateRangeLabel(
            i, f"{formatter(item.lowerValue())} to {formatter(item.upperValue())}"
        )


def dark_from(renderer, index=3):
    """Lower bound of the first class dark enough to need white label text."""
    ranges = renderer.ranges()
    return ranges[index].lowerValue() if len(ranges) > index else ranges[-1].lowerValue()


def white_on_dark(field, threshold):
    return f"if(\"{field}\" >= {threshold}, '#ffffff', '{INK}')"


# --------------------------------------------------------------------------
# Interpolation surfaces for figures 4, 6 and 8
# --------------------------------------------------------------------------


def surveyed_centroids():
    """The 20 surveyed squares as points, carrying every metric field."""
    out = free_path(os.path.join(PROCESSED, "surveyed_centroids.gpkg"))
    extracted = processing.run(
        "native:extractbyexpression",
        {
            "INPUT": f"{RESULTS}|layername=results",
            "EXPRESSION": '"surveyed"',
            "OUTPUT": "TEMPORARY_OUTPUT",
        },
    )["OUTPUT"]
    return processing.run(
        "native:centroids",
        {"INPUT": extracted, "ALL_PARTS": False, "OUTPUT": out},
    )["OUTPUT"]


def idw_surface(points, field):
    """IDW over the surveyed points, clipped to the SSSI boundary.

    IDW rather than the Gaussian kernel the Python figures use: QGIS has no
    Gaussian smoother, so these surfaces are related but not identical.
    """
    boundary = QgsVectorLayer(f"{BOUNDARIES}|layername=sssi_boundary", "b", "ogr")
    extent = QgsRectangle(boundary.extent())
    extent.grow(80)

    raw = processing.run(
        "gdal:gridinversedistance",
        {
            "INPUT": points,
            "Z_FIELD": field,
            # Power 1.5 rather than 2: at 2 each sample point becomes a hard
            # bullseye, which reads as false precision on a 20-point sample.
            "POWER": 1.5,
            "SMOOTHING": 0.0,
            "RADIUS_1": 0.0,
            "RADIUS_2": 0.0,
            "ANGLE": 0.0,
            "MAX_POINTS": 0,
            "MIN_POINTS": 0,
            "NODATA": -9999.0,
            "EXTRA": (
                f"-txe {extent.xMinimum()} {extent.xMaximum()} "
                f"-tye {extent.yMinimum()} {extent.yMaximum()} -outsize 400 400"
            ),
            "OUTPUT": "TEMPORARY_OUTPUT",
        },
    )["OUTPUT"]

    clipped = free_path(os.path.join(PROCESSED, f"idw_{field}.tif"))
    processing.run(
        "gdal:cliprasterbymasklayer",
        {
            "INPUT": raw,
            "MASK": f"{BOUNDARIES}|layername=sssi_boundary",
            "SOURCE_CRS": BNG,
            "TARGET_CRS": BNG,
            "NODATA": -9999.0,
            "CROP_TO_CUTLINE": True,
            "KEEP_RESOLUTION": True,
            "OUTPUT": clipped,
        },
    )
    return clipped


def style_raster(layer, vmin, vmax):
    shader_fn = QgsColorRampShader(vmin, vmax, ramp(), SHADER_LINEAR)
    shader_fn.classifyColorRamp(classes=12)
    shader = QgsRasterShader()
    shader.setRasterShaderFunction(shader_fn)
    layer.setRenderer(
        QgsSingleBandPseudoColorRenderer(layer.dataProvider(), 1, shader)
    )
    return layer


# --------------------------------------------------------------------------
# Layout construction
# --------------------------------------------------------------------------


def build_layout(name, title, map_layers, legend_layers, extent):
    """One print layout: title, map, legend. No north arrow, no scale bar."""
    layout = QgsPrintLayout(PROJECT)
    layout.initializeDefaults()
    layout.setName(name)
    layout.setUnits(LAYOUT_MM)
    layout.pageCollection().pages()[0].setPageSize("A4", LANDSCAPE)

    heading = QgsLayoutItemLabel(layout)
    heading.setText(title)
    font = QFont(FONT, 13)
    font.setBold(True)
    heading.setFont(font)
    heading.setFontColor(QColor(INK))
    layout.addLayoutItem(heading)
    heading.attemptSetSceneRect(TITLE_RECT)

    map_item = QgsLayoutItemMap(layout)
    map_item.setCrs(BNG)
    layout.addLayoutItem(map_item)
    map_item.attemptSetSceneRect(MAP_RECT)
    map_item.setFrameEnabled(True)
    map_item.setFrameStrokeColor(QColor(GREY))
    map_item.setFrameStrokeWidth(QgsLayoutMeasurement(0.2, LAYOUT_MM))
    map_item.setBackgroundColor(QColor("white"))
    map_item.setBackgroundEnabled(True)
    # Pin the layer set, so an unchecked tree group still renders here.
    map_item.setFollowVisibilityPreset(False)
    map_item.setKeepLayerSet(True)
    map_item.setLayers(map_layers)
    map_item.zoomToExtent(extent)

    legend = QgsLayoutItemLegend(layout)
    legend.setLinkedMap(map_item)
    legend.setTitle("")
    legend.setAutoUpdateModel(False)
    layout.addLayoutItem(legend)

    tree = QgsLayerTree()
    for layer in legend_layers:
        node = tree.addLayer(layer)
        node.setName(DISPLAY.get(layer.id(), layer.name()))
    _keepalive.append(tree)
    legend.model().setRootGroup(tree)

    # A pseudocolour raster contributes a "Band 1 (Gray)" row above its ramp,
    # which is provider detail rather than anything a reader needs.
    for layer in legend_layers:
        if not isinstance(layer, QgsRasterLayer):
            continue
        node = tree.findLayer(layer)
        legend.model().refreshLayerLegend(node)
        nodes = legend.model().layerLegendNodes(node)
        keep = [
            i for i, item in enumerate(nodes)
            if "Band" not in str(item.data(DISPLAY_ROLE) or "")
        ]
        if len(keep) != len(nodes):
            QgsMapLayerLegendUtils.setLegendNodeOrder(node, keep)
            legend.model().refreshLayerLegend(node)

    legend.setSymbolWidth(6)
    legend.setSymbolHeight(3.5)
    legend.setBoxSpace(1.5)
    legend.setResizeToContents(True)
    legend.attemptSetSceneRect(LEGEND_RECT)

    PROJECT.layoutManager().addLayout(layout)
    return layout


def export(layout, filename):
    exporter = QgsLayoutExporter(layout)
    settings = QgsLayoutExporter.ImageExportSettings()
    settings.dpi = DPI
    path = os.path.join(OUT_DIR, filename)
    code = exporter.exportToImage(path, settings)
    if code != EXPORT_OK:
        raise RuntimeError(f"export failed for {layout.name()} (code {code})")
    return path


# ==========================================================================
# Build
# ==========================================================================

teardown()

# One shared extent, so the eleven maps can be flipped through without the
# site jumping around between them.
_plan = QgsVectorLayer(f"{SURVEY_PLAN}|layername=plan_cells", "p", "ogr")
EXTENT = QgsRectangle(_plan.extent())
EXTENT.grow(70)

basemap = next(
    (lyr for lyr in PROJECT.mapLayers().values() if lyr.name() == "OpenStreetMap"),
    None,
)

points = surveyed_centroids()
print("built surveyed centroids")

exported = []


def base_layers(fig):
    """The two base layers the brief puts on every map."""
    not_surveyed = add_vector(fig, SURVEY_PLAN, "plan_cells", "not surveyed",
                              "surveyed = 0")
    not_surveyed.setRenderer(QgsSingleSymbolRenderer(hatch()))
    shown_as(not_surveyed, "Not surveyed")

    bound = add_vector(fig, BOUNDARIES, "sssi_boundary", "sssi")
    bound.setRenderer(QgsSingleSymbolRenderer(outline_only("black", 0.6)))
    shown_as(bound, "SSSI boundary")
    return not_surveyed, bound


# --- Figure 1: coverage on a basemap -------------------------------------
f1_not, f1_bound = base_layers(1)

f1_done = add_vector(1, SURVEY_PLAN, "plan_cells", "surveyed", "surveyed = 1")
f1_done.setRenderer(
    QgsSingleSymbolRenderer(solid_fill(BLUE_FILL, alpha=140, stroke=GREY))
)
label(f1_done, '"label"', size=7)
shown_as(f1_done, "Surveyed square")

f1_cliff = add_vector(1, SURVEY_PLAN, "plan_cells", "cliff", "contains_cliff = 1")
f1_cliff.setRenderer(QgsSingleSymbolRenderer(outline_only(RED, 0.5)))
shown_as(f1_cliff, "Contains cliff")

# Filtered to the 20 walked. transect_lines holds all 49 PLANNED transects, so
# unfiltered it draws lines inside squares this same map hatches as "not
# surveyed", which reads as though all 49 were walked.
f1_lines = add_vector(1, SURVEY_PLAN, "transect_lines", "transects", "surveyed = 1")
f1_lines.setRenderer(QgsSingleSymbolRenderer(line_symbol(NAVY, 0.4)))
shown_as(f1_lines, "Transect walked")

lay = build_layout(
    "Fig 01 survey coverage basemap",
    "Figure 1. Survey coverage, Weston Big Wood SSSI",
    [f1_cliff, f1_lines, f1_bound, f1_done, f1_not] + ([basemap] if basemap else []),
    [f1_done, f1_not, f1_cliff, f1_lines, f1_bound],
    EXTENT,
)
exported.append(export(lay, "fig01_survey_coverage_basemap.png"))

# --- Figure 2: the same coverage, no basemap -----------------------------
f2_cells = add_vector(2, SURVEY_PLAN, "plan_cells", "coverage")
f2_cells.setRenderer(
    QgsCategorizedSymbolRenderer(
        "surveyed",
        [
            QgsRendererCategory(True, solid_fill(BLUE_FILL, stroke=GREY), "Surveyed"),
            QgsRendererCategory(False, hatch(fill_color="white"), "Not surveyed"),
        ],
    )
)
shown_as(f2_cells, "Survey coverage")

f2_lines = add_vector(2, SURVEY_PLAN, "transect_lines", "transects", "surveyed = 1")
f2_lines.setRenderer(QgsSingleSymbolRenderer(line_symbol(NAVY, 0.4)))
shown_as(f2_lines, "Transect walked")

f2_bound = add_vector(2, BOUNDARIES, "sssi_boundary", "sssi")
f2_bound.setRenderer(QgsSingleSymbolRenderer(outline_only("black", 0.6)))
shown_as(f2_bound, "SSSI boundary")

lay = build_layout(
    "Fig 02 survey coverage plain",
    "Figure 2. Survey coverage, 100 m sample squares",
    [f2_lines, f2_bound, f2_cells],
    [f2_cells, f2_lines, f2_bound],
    EXTENT,
)
exported.append(export(lay, "fig02_survey_coverage_plain.png"))


# --- Choropleths, figures 3, 5, 7 ---------------------------------------


def choropleth(fig, field, title, filename, legend_title, jenks=False,
               breaks=None, labels=None, label_expr=None, legend_format=None):
    not_surveyed, bound = base_layers(fig)
    data = add_vector(fig, RESULTS, "results", field, "surveyed = 1")

    if jenks:
        renderer = graduated_jenks(data, field, 5)
        relabel_ranges(renderer, legend_format or (lambda v: f"{v:g}"))
    else:
        renderer = graduated_manual(data, field, breaks, labels)
    label(
        data,
        label_expr or f'"{field}"',
        size=7,
        color_expression=white_on_dark(field, dark_from(renderer, 3)),
        buffer=False,
    )
    shown_as(data, legend_title)

    lay = build_layout(
        f"Fig {fig:02d} {field}", title,
        [bound, data, not_surveyed],
        [data, not_surveyed, bound],
        EXTENT,
    )
    return export(lay, filename)


exported.append(
    choropleth(
        3, "est_per_ha",
        "Figure 3. Established trees per hectare",
        "fig03_established_per_ha.png",
        "Established trees per hectare",
        jenks=True,
        label_expr='format_number("est_per_ha", 0)',
        legend_format=lambda v: f"{v:,.0f}",
    )
)

exported.append(
    choropleth(
        5, "shannon",
        "Figure 5. Species diversity of established trees (Shannon H')",
        "fig05_species_diversity.png",
        "Shannon H'",
        jenks=True,
        label_expr='format_number("shannon", 2)',
        legend_format=lambda v: f"{v:.2f}",
    )
)

# Manual classes on a fixed 3 to 7 scale. Natural breaks would flatten this:
# every surveyed square scores 5, 6 or 7. Half-value edges keep each integer in
# its own class, so the legend reads as counts rather than overlapping bands.
exported.append(
    choropleth(
        7, "n_classes",
        "Figure 7. Structural diversity: number of size classes present",
        "fig07_structural_diversity.png",
        "Size classes present",
        breaks=[2.5, 3.5, 4.5, 5.5, 6.5, 7.5],
        labels=["3", "4", "5", "6", "7"],
    )
)

# --- Figure 9: deadwood --------------------------------------------------
f9_not, f9_bound = base_layers(9)

f9_data = add_vector(9, RESULTS, "results", "dead_total", "surveyed = 1")
graduated_manual(f9_data, "dead_total", [0, 3, 6, 9, 12],
                 ["0 to 3", "3 to 6", "6 to 9", "9 to 12"])
shown_as(f9_data, "Deadwood records per transect")

# Q1 is the only transect with no deadwood at all, so it is called out.
f9_zero = add_vector(9, RESULTS, "results", "zero",
                     "surveyed = 1 AND dead_total = 0")
f9_zero.setRenderer(QgsSingleSymbolRenderer(outline_only(RED, 0.6)))
shown_as(f9_zero, "No deadwood recorded")

f9_standing = add_vector(9, RESULTS, "results", "standing", "dead_standing > 0")
centroid_marker(f9_standing, marker("triangle", RED, 3.2))
label(f9_standing, '"dead_standing"', size=7,
      placement=PLACEMENT_OVER_POINT, offset_mm=(0, -3.4))
shown_as(f9_standing, "Standing dead stems")

lay = build_layout(
    "Fig 09 deadwood",
    "Figure 9. Deadwood records per transect, with standing dead stems",
    [f9_standing, f9_zero, f9_bound, f9_data, f9_not],
    [f9_data, f9_standing, f9_zero, f9_not, f9_bound],
    EXTENT,
)
exported.append(export(lay, "fig09_deadwood.png"))

# --- Figure 10: lime and wild service -----------------------------------
f10_not, f10_bound = base_layers(10)

f10_data = add_vector(10, RESULTS, "results", "lime_est", "surveyed = 1")
graduated_manual(f10_data, "lime_est", [-0.5, 0.5, 1.5, 2.5, 3.5, 4.5],
                 ["0", "1", "2", "3", "4"])
shown_as(f10_data, "Established small-leaved lime")

f10_young = add_vector(10, RESULTS, "results", "lime_young", "lime_young > 0")
centroid_marker(f10_young, marker("circle", GREEN, 3.0))
label(f10_young, '"lime_young"', size=7,
      placement=PLACEMENT_OVER_POINT, offset_mm=(3.6, 0))
shown_as(f10_young, "Lime seedlings and saplings")

f10_ws = add_vector(10, RESULTS, "results", "wild_service", "wild_service > 0")
centroid_marker(f10_ws, marker("star", PURPLE, 4.2))
shown_as(f10_ws, "Wild service tree present")

lay = build_layout(
    "Fig 10 lime and wild service",
    "Figure 10. Small-leaved lime and wild service tree",
    [f10_ws, f10_young, f10_bound, f10_data, f10_not],
    [f10_data, f10_young, f10_ws, f10_not, f10_bound],
    EXTENT,
)
exported.append(export(lay, "fig10_lime_wild_service.png"))


# --- Figures 4, 6, 8: smoothed surfaces ----------------------------------


def surface(fig, field, vmin, vmax, title, filename, legend_title):
    raster = add_raster(fig, idw_surface(points, field), field)
    style_raster(raster, vmin, vmax)
    shown_as(raster, legend_title)

    bound = add_vector(fig, BOUNDARIES, "sssi_boundary", "sssi")
    bound.setRenderer(QgsSingleSymbolRenderer(outline_only("black", 0.6)))
    shown_as(bound, "SSSI boundary")

    dots = add_vector(fig, SURVEY_PLAN, "start_points", "samples", "surveyed = 1")
    dots.setRenderer(
        QgsSingleSymbolRenderer(
            marker("circle", "white", 2.2, stroke=INK, stroke_width=0.25)
        )
    )
    shown_as(dots, "Sample point")

    lay = build_layout(
        f"Fig {fig:02d} {field} surface", title,
        [dots, bound, raster],
        [raster, dots, bound],
        EXTENT,
    )
    return export(lay, filename)


exported.append(
    surface(4, "est_per_ha", 450, 1800,
            "Figure 4. Established trees per hectare, smoothed surface "
            "(indicative only)",
            "fig04_density_surface.png", "Trees per hectare")
)
exported.append(
    surface(6, "shannon", 0.66, 1.90,
            "Figure 6. Species diversity, smoothed surface (indicative only)",
            "fig06_diversity_surface.png", "Shannon H'")
)
exported.append(
    surface(8, "n_classes", 3, 7,
            "Figure 8. Structural diversity, smoothed surface "
            "(indicative only)",
            "fig08_structural_surface.png", "Size classes present")
)

# --- Figure 11: non-native trees by species -----------------------------
f11_not, f11_bound = base_layers(11)

f11_cells = add_vector(11, SURVEY_PLAN, "plan_cells", "surveyed", "surveyed = 1")
f11_cells.setRenderer(QgsSingleSymbolRenderer(solid_fill("#f2f5f9", stroke=GREY)))
shown_as(f11_cells, "Surveyed square")

SPECIES = [
    ("Sycamore", "circle", "#1f6fb4", "Sycamore"),
    ("Holm Oak", "square", "#e07b18", "Holm Oak"),
    ("Buddleia", "diamond", GREEN, "Buddleia"),
    ("Laurel", "cross2", RED, "Laurel (check for Cherry Laurel)"),
]
f11_points = add_vector(11, NON_NATIVES, "non_natives", "species")
f11_points.setRenderer(
    QgsCategorizedSymbolRenderer(
        "species",
        [
            QgsRendererCategory(
                value, marker(shape, colour, 3.2, stroke="white", stroke_width=0.25), text
            )
            for value, shape, colour, text in SPECIES
        ],
    )
)
label(f11_points, '"stems"', size=8,
      placement=PLACEMENT_OVER_POINT, offset_mm=(3.6, 0))
shown_as(f11_points, "Non-native species")

lay = build_layout(
    "Fig 11 non-native trees",
    "Figure 11. Non-native trees by species, stems per record",
    [f11_points, f11_bound, f11_cells, f11_not],
    [f11_points, f11_cells, f11_not, f11_bound],
    EXTENT,
)
exported.append(export(lay, "fig11_non_natives.png"))

# --------------------------------------------------------------------------

print(f"\nexported {len(exported)} figures to {OUT_DIR}")
for path in sorted(exported):
    print(f"  {os.path.basename(path):40} {os.path.getsize(path) // 1024:5} KB")
