"""Draw a regional map of the 13 Central and South Asian countries.

Natural Earth geometry is used only to draw the map. Names and sub-regions come
from the declared population dataset.
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.patches import Polygon as MapPolygon  # noqa: E402

from aab.analyses import EDGE, REGION_STYLE  # noqa: E402
from aab.datasets import read as read_dataset  # noqa: E402
from aab.infographics import load_infographic  # noqa: E402

BOUNDARIES = ROOT / "data/sources/natural-earth-countries/ne_50m_admin_0_countries.geojson"
INDICATOR = "SP.POP.TOTL"

# A simple regional map projection: scale longitude at the middle of the map.
COS_LAT = math.cos(math.radians(27))
LON_MIN, LON_MAX = 42, 102
LAT_MIN, LAT_MAX = -2, 58


DARK = "#222222"
MID = "#555555"
LAND = "#E8EDF1"
OCEAN = "#F5F8FA"


def exterior_rings(feature):
    """Return the outer rings for a GeoJSON Polygon or MultiPolygon."""
    geometry = feature.get("geometry") or {}
    kind = geometry.get("type")
    coords = geometry.get("coordinates", [])

    if kind == "Polygon":
        return [polygon[0] for polygon in [coords] if polygon]
    if kind == "MultiPolygon":
        return [polygon[0] for polygon in coords if polygon]
    return []


def bounds(rings):
    """Return longitude and latitude bounds for a set of rings."""
    points = [point for ring in rings for point in ring]
    if not points:
        return None
    return (
        min(point[0] for point in points),
        max(point[0] for point in points),
        min(point[1] for point in points),
        max(point[1] for point in points),
    )


def add_feature(ax, feature, facecolor, hatch=None, zorder=1, linewidth=0.45):
    """Draw a feature's outer polygon rings."""
    for ring in exterior_rings(feature):
        xy = [(point[0] * COS_LAT, point[1]) for point in ring]
        if len(xy) >= 3:
            ax.add_patch(MapPolygon(
                xy,
                closed=True,
                facecolor=facecolor,
                edgecolor="white",
                linewidth=linewidth,
                hatch=hatch,
                zorder=zorder,
            ))


def main():
    info = load_infographic(HERE)

    if not BOUNDARIES.exists():
        raise SystemExit(f"Boundary file not found: {BOUNDARIES}")

    with BOUNDARIES.open(encoding="utf-8") as file:
        geojson = json.load(file)

    df = read_dataset(info.datasets[0])
    data = df[df["indicator_code"] == INDICATOR].copy()
    year = int(data["year"].max())
    countries = data[data["year"] == year].drop_duplicates("iso3")

    names_regions = {
        row["iso3"]: {
            "name": row["country_name"],
            "region": row["region"],
        }
        for _, row in countries.iterrows()
    }
    target_codes = set(names_regions)

    features = geojson["features"]
    map_features = {}
    for feature in features:
        code = (feature.get("properties") or {}).get("ADM0_A3")
        if code in target_codes:
            map_features[code] = feature

    missing = sorted(target_codes - set(map_features))
    if missing:
        raise SystemExit(f"Boundary file is missing these country codes: {', '.join(missing)}")

    installed_fonts = {font.name for font in font_manager.fontManager.ttflist}
    plt.rcParams["font.family"] = next(
        (font for font in ["Liberation Sans", "Arial", "DejaVu Sans"] if font in installed_fonts),
        "sans-serif",
    )

    fig = plt.figure(figsize=(19.2, 10.8), dpi=100, facecolor="white")
    ax = fig.add_axes([0.035, 0.13, 0.49, 0.65])
    ax.set_facecolor(OCEAN)

    # Draw nearby countries in a quiet neutral colour for geographic context.
    for feature in features:
        code = (feature.get("properties") or {}).get("ADM0_A3")
        if code in target_codes:
            continue
        rings = exterior_rings(feature)
        box = bounds(rings)
        if box is None:
            continue
        west, east, south, north = box
        if east < LON_MIN or west > LON_MAX or north < LAT_MIN or south > LAT_MAX:
            continue
        add_feature(ax, feature, LAND, zorder=1)

    # Highlight the 13 countries, coloured by sub-region.
    for code, feature in map_features.items():
        region = names_regions[code]["region"]
        colour, hatch = REGION_STYLE[region]
        add_feature(ax, feature, colour, hatch=hatch, zorder=3, linewidth=0.7)

    ax.set_xlim(LON_MIN * COS_LAT, LON_MAX * COS_LAT)
    ax.set_ylim(LAT_MIN, LAT_MAX)
    ax.set_aspect("equal")
    ax.set_axis_off()

    # The Maldives is a very small island chain at this scale. Mark its location
    # and call it out rather than implying the marker is its boundary.
    maldives_style = REGION_STYLE[names_regions["MDV"]["region"]]
    mdv_x, mdv_y = 73.5 * COS_LAT, 3.2
    ax.scatter(
        [mdv_x], [mdv_y], s=100, color=maldives_style[0],
        edgecolor="white", linewidth=1.5, zorder=6,
    )
    ax.annotate(
        "Maldives",
        xy=(mdv_x, mdv_y),
        xytext=(68 * COS_LAT, 8),
        fontsize=12,
        color=DARK,
        bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#D0D7DE"),
        arrowprops=dict(arrowstyle="-", color=MID, linewidth=1),
        zorder=7,
    )

    fig.text(0.04, 0.94, info.config["title"], fontsize=36, weight="bold", color=DARK)
    fig.text(0.04, 0.885, info.config["headline"], fontsize=24, color=DARK)
    fig.text(
        0.04, 0.845,
        "Highlighted countries are listed by sub-region. Colours show Central Asia and South Asia.",
        fontsize=17, color=MID,
    )

    # Country key. Each heading uses the same colour as its region on the map.
    panel_x = 0.57
    fig.text(panel_x, 0.80, f"13 countries · population data year {year}",
             fontsize=20, weight="bold", color=DARK)

    y = 0.735
    for region in ["Central Asia", "South Asia"]:
        colour, _ = REGION_STYLE[region]
        fig.text(panel_x, y, region, fontsize=18, weight="bold", color=colour)
        y -= 0.045
        names = sorted(
            row["name"] for row in names_regions.values()
            if row["region"] == region
        )
        for name in names:
            fig.text(panel_x + 0.01, y, name, fontsize=16, color=DARK)
            y -= 0.037
        y -= 0.025

    fig.text(
        panel_x, 0.13,
        "Maldives marker shows location only;\nits island chain is too small at this scale.",
        fontsize=13, color=MID,
    )
    fig.text(
        0.04, 0.035,
        "Map boundaries: Natural Earth 1:50m, public domain. Generalized boundaries; "
        "not an authority on disputed borders.",
        fontsize=13, color=MID,
    )

    out = info.png("en")
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Wrote {out.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
