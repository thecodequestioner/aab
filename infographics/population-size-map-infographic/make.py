"""Draw a choropleth map of the 13 Central and South Asian countries, shaded by 2025 population.

Population values and country names come from the declared dataset. The 2025 year and the
largest country are checked against the declared analysis. Natural Earth geometry is used only
to draw the map shapes.
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
from matplotlib.patches import Polygon as MapPolygon, Rectangle  # noqa: E402

from aab.datasets import read as read_dataset  # noqa: E402
from aab.infographics import load_infographic, read_summary  # noqa: E402

BOUNDARIES = ROOT / "data/sources/natural-earth-countries/ne_50m_admin_0_countries.geojson"
INDICATOR = "SP.POP.TOTL"

# Fixed class limits in millions, dark (most people) to light (fewest). Fixed limits keep the
# classes readable; a linear scale would squeeze 10 of 13 countries into the lightest 7% of the range.
# Each entry: (lower limit in millions, label, colour). Colours run dark to light and keep their
# order in greyscale. Each class also has a text label in the key, so colour is not the only cue.
CLASSES = [
    (100, "100 million or more", "#0B3954"),
    (20, "20 to under 100 million", "#1F5F7A"),
    (10, "10 to under 20 million", "#3F8FA8"),
    (1, "1 to under 10 million", "#9CCBDA"),
    (0, "under 1 million", "#D4EAF2"),
]

# A simple regional projection: scale longitude at the middle latitude of the map.
COS_LAT = math.cos(math.radians(27))
LON_MIN, LON_MAX = 42, 102
LAT_MIN, LAT_MAX = -2, 58

DARK = "#222222"
MID = "#555555"
NEIGHBOUR = "#F2F2F2"   # neighbouring countries, drawn for context only
OCEAN = "#FFFFFF"
TARGET_EDGE = "#444444"


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


def add_feature(ax, feature, facecolor, zorder=1, edgecolor="white", linewidth=0.45):
    """Draw a feature's outer polygon rings."""
    for ring in exterior_rings(feature):
        xy = [(point[0] * COS_LAT, point[1]) for point in ring]
        if len(xy) >= 3:
            ax.add_patch(MapPolygon(
                xy, closed=True, facecolor=facecolor, edgecolor=edgecolor,
                linewidth=linewidth, zorder=zorder,
            ))


def class_index(population_millions):
    """Return the index in CLASSES for a population given in millions."""
    for index, (lower, _, _) in enumerate(CLASSES):
        if population_millions >= lower:
            return index
    raise ValueError(f"Negative population: {population_millions}")


def main():
    info = load_infographic(HERE)

    if not BOUNDARIES.exists():
        raise SystemExit(f"Boundary file not found: {BOUNDARIES}")
    with BOUNDARIES.open(encoding="utf-8") as file:
        geojson = json.load(file)

    df = read_dataset(info.datasets[0])
    data = df[df["indicator_code"] == INDICATOR].copy()
    year = int(data["year"].max())
    latest = data[data["year"] == year].drop_duplicates("iso3")

    # Check the claims in the headline against the declared analysis and the data.
    summary = read_summary(info.analyses[0])
    if int(summary["year"]) != year:
        raise SystemExit(f"Analysis year {summary['year']} differs from dataset year {year}.")
    countries = {
        row["iso3"]: {
            "name": row["country_name"],
            "region": row["region"],
            "millions": row["value"] / 1e6,
        }
        for _, row in latest.iterrows()
    }
    if summary["largest"]["country"] != max(countries.values(), key=lambda c: c["millions"])["name"]:
        raise SystemExit("The largest country differs between the analysis and the dataset.")
    over_100m = sorted(c["name"] for c in countries.values() if c["millions"] >= 100)
    under_1m = sorted(c["name"] for c in countries.values() if c["millions"] < 1)
    if over_100m != ["Bangladesh", "India", "Pakistan"]:
        raise SystemExit(f"The headline names the wrong countries over 100 million: {over_100m}")
    if under_1m != ["Bhutan", "Maldives"]:
        raise SystemExit(f"The headline names the wrong countries under 1 million: {under_1m}")

    features = geojson["features"]
    map_features = {}
    for feature in features:
        code = (feature.get("properties") or {}).get("ADM0_A3")
        if code in countries:
            map_features[code] = feature
    missing = sorted(set(countries) - set(map_features))
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

    # Neighbouring countries: quiet neutral fill for geographic context.
    for feature in features:
        code = (feature.get("properties") or {}).get("ADM0_A3")
        if code in countries:
            continue
        box = bounds(exterior_rings(feature))
        if box is None:
            continue
        west, east, south, north = box
        if east < LON_MIN or west > LON_MAX or north < LAT_MIN or south > LAT_MAX:
            continue
        add_feature(ax, feature, NEIGHBOUR, zorder=1)

    # The 13 countries, shaded by population class.
    for code, feature in map_features.items():
        colour = CLASSES[class_index(countries[code]["millions"])][2]
        add_feature(ax, feature, colour, zorder=3, edgecolor=TARGET_EDGE, linewidth=0.6)

    ax.set_xlim(LON_MIN * COS_LAT, LON_MAX * COS_LAT)
    ax.set_ylim(LAT_MIN, LAT_MAX)
    ax.set_aspect("equal")
    ax.set_axis_off()

    # The Maldives is too small to show at this scale. Mark its location and call it out.
    mdv_colour = CLASSES[class_index(countries["MDV"]["millions"])][2]
    mdv_x, mdv_y = 73.5 * COS_LAT, 3.2
    ax.scatter([mdv_x], [mdv_y], s=110, color=mdv_colour, edgecolor=DARK,
               linewidth=1.2, zorder=6)
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
    fig.text(0.04, 0.885, info.config["headline"], fontsize=22, color=DARK)
    fig.text(
        0.04, 0.845,
        "Darker countries have more people. Population is for 2025, in millions.",
        fontsize=17, color=MID,
    )

    # Key and country list. Each class has a swatch, a text label and the countries with values.
    panel_x = 0.57
    fig.text(panel_x, 0.80, f"Population, {year}", fontsize=20, weight="bold", color=DARK)

    y = 0.755
    for index, (lower, label, colour) in enumerate(CLASSES):
        fig.patches.append(Rectangle(
            (panel_x, y - 0.006), 0.018, 0.026, transform=fig.transFigure,
            facecolor=colour, edgecolor="#333333", linewidth=0.8, figure=fig,
        ))
        fig.text(panel_x + 0.03, y, label, fontsize=16, weight="bold", color=DARK)
        y -= 0.031
        members = sorted(
            (c for c in countries.values() if class_index(c["millions"]) == index),
            key=lambda c: -c["millions"],
        )
        for member in members:
            fig.text(
                panel_x + 0.03, y,
                f"{member['name']}: {member['millions']:,.1f} million",
                fontsize=14, color=DARK,
            )
            y -= 0.026
        y -= 0.014

    fig.text(
        panel_x, 0.105,
        "Maldives marker shows location only;\nits island chain is too small at this scale.",
        fontsize=13, color=MID,
    )
    fig.text(
        0.04, 0.035,
        "Population: World Bank WDI, based on UN World Population Prospects 2024. "
        "Map boundaries: Natural Earth 1:50m, public domain; generalized, not an authority on disputed borders.",
        fontsize=13, color=MID,
    )

    out = info.png("en")
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Wrote {out.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()