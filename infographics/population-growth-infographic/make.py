"""Draws the population growth infographic (1920 x 1080 px PNG and SVG).

Reads   the dataset population-central-south-asia (values for 2000 and 2025) and the analysis
        summary population-growth-2000-2025, so the picture matches the analysis.
Writes  outputs/infographic_en.png and outputs/infographic_en.svg

Run by the pipeline, or from the repository root:
    python infographics/population-growth-infographic/make.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))  # lets the script run directly as well as through the pipeline

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

from aab.analyses import EDGE, REGION_STYLE  # noqa: E402
from aab.datasets import read as read_dataset  # noqa: E402
from aab.infographics import load_infographic, read_summary  # noqa: E402

ANALYSIS = "population-growth-2000-2025"
DATASET = "population-central-south-asia"
INDICATOR = "SP.POP.TOTL"
START, END = 2000, 2025
DARK, MID = "#222222", "#444444"


def main() -> None:
    info = load_infographic(HERE)
    summary = read_summary(ANALYSIS)

    # The headline may only say that every country grew if the analysis agrees.
    if info.config["claim"] == "trend_found" and not summary["all_grew"]:
        raise SystemExit("The headline says every country grew, but the analysis finds that not all did. "
                         "Update infographic.yaml so the claim matches the analysis.")

    installed = {f.name for f in font_manager.fontManager.ttflist}
    plt.rcParams["font.family"] = next((f for f in ["Liberation Sans", "Arial", "DejaVu Sans"]
                                        if f in installed), "sans-serif")

    df = read_dataset(DATASET)
    df = df[df["indicator_code"] == INDICATOR]
    first = df[df["year"] == START].set_index("iso3")
    last = df[df["year"] == END].set_index("iso3")
    d = last[["country_name", "region"]].copy()
    d["start"] = first["value"]
    d["end"] = last["value"]
    d["pct"] = (d["end"] / d["start"] - 1) * 100
    d = d.sort_values("pct", ascending=True).reset_index(drop=True)  # largest drawn at the top
    span = float(d["pct"].max())

    fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
    fig.subplots_adjust(left=0.20, right=0.97, top=0.72, bottom=0.12)
    bars = ax.barh(d["country_name"], d["pct"], color=[REGION_STYLE[r][0] for r in d["region"]],
                   height=0.7, edgecolor=EDGE, linewidth=0.8)
    for bar, r in zip(bars, d["region"]):
        bar.set_hatch(REGION_STYLE[r][1])
    for y, row in d.iterrows():
        ax.text(row["pct"] + span * 0.01, y,
                f"+{row['pct']:.0f}%   ({row['start'] / 1e6:,.1f} to {row['end'] / 1e6:,.1f} million)",
                va="center", fontsize=18, color=DARK)
    ax.set_xlim(0, span * 1.75)
    ax.set_xticks([])
    ax.tick_params(axis="y", labelsize=20, colors=DARK, length=0)
    for side in ("top", "right", "bottom", "left"):
        ax.spines[side].set_visible(False)
    handles = [Patch(facecolor=REGION_STYLE[r][0], hatch=REGION_STYLE[r][1], edgecolor=EDGE, label=r)
               for r in sorted(d["region"].unique())]
    ax.legend(handles=handles, frameon=False, loc="lower right", fontsize=18)

    fig.text(0.02, 0.93, info.config["title"], fontsize=40, weight="bold", color=DARK)
    sub = fig.text(0.02, 0.87, info.config["headline"], fontsize=26, color=DARK)
    fig.text(0.02, 0.81, f"Each bar shows how much a country's population grew from {START} to {END}.",
             fontsize=20, color=MID)
    fig.text(0.02, 0.03, f"Source: UN World Population Prospects 2024, via World Bank WDI (SP.POP.TOTL). "
                         f"Licence CC BY 4.0. {END} is a projection.", fontsize=16, color=MID)
    fig.canvas.draw()
    bb = sub.get_window_extent()
    assert bb.x1 < fig.bbox.x1 - 20, f"headline overflows: {bb.x1} > {fig.bbox.x1}"

    out = info.png("en")
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    fig.savefig(info.svg("en"), format="svg", metadata={"Date": None})
    print(f"wrote {out.relative_to(HERE.parents[1]).as_posix()}")


if __name__ == "__main__":
    main()