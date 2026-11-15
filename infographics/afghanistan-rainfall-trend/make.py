"""Draws the teaching infographic (1920 x 1080 px PNG) for the Afghanistan rainfall analysis.

Reads   the processed dataset (afghanistan-precipitation) and the analysis summary
        (afghanistan-rainfall-trend), so the picture always matches the data.
Writes  outputs/infographic_en.png

Run by the pipeline, or from the repository root:
    python infographics/afghanistan-rainfall-trend/make.py
"""
import sys
from pathlib import Path
from statistics import median

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))  # lets the script run directly as well as through the pipeline

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

from aab.datasets import read as read_dataset  # noqa: E402
from aab.infographics import load_infographic, read_summary  # noqa: E402

BLUE, GREY, DARK, MID = "#0072B2", "#B8C4CE", "#222222", "#444444"  # Okabe-Ito blue; neutral greys
ANALYSIS = "afghanistan-rainfall-trend"


def main() -> None:
    info = load_infographic(HERE)
    summary = read_summary(ANALYSIS)

    # Keep the stated headline direction aligned with the generated full-period result.
    if info.config["claim"] == "no_clear_trend" and summary["significant_5pct"]:
        raise SystemExit("The infographic says there is no clear trend, but the analysis finds a significant one.")
    if info.config["claim"] == "trend_found" and not summary["significant_5pct"]:
        raise SystemExit("The infographic claims a trend, but the analysis does not find one at 5%.")

    installed = {f.name for f in font_manager.fontManager.ttflist}
    plt.rcParams["font.family"] = next((f for f in ["Liberation Sans", "Arial", "DejaVu Sans"] if f in installed),
                                       "sans-serif")

    d = read_dataset("afghanistan-precipitation").sort_values("year")
    years, values = d["year"], d["value"]
    rolling = values.rolling(10, center=True, min_periods=5).mean()
    mean = summary["mean"]
    wet, dry = summary["wettest"], summary["driest"]
    y0, y1 = summary["first_year"], summary["last_year"]

    fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
    fig.subplots_adjust(left=0.08, right=0.97, top=0.63, bottom=0.14)
    ax.bar(years, values, color=GREY, width=0.8, label="Annual rainfall")
    ax.plot(years, rolling, color=BLUE, linewidth=4, label="10-year rolling mean")
    slope_per_year = summary["sen_slope_per_decade"] / 10
    intercept = median([v - slope_per_year * y for y, v in zip(years, values)])
    ax.plot(years, intercept + slope_per_year * years, color="#D55E00", linestyle="--", linewidth=3,
            label=f"Sen's trend: {summary['sen_slope_per_decade']:+.1f} mm/decade")
    ax.axhline(mean, color=DARK, linestyle=":", linewidth=2, label=f"Full-period average: {mean:.0f} mm")
    ax.annotate(f"Wettest year: {wet['year']}", xy=(wet["year"], wet["value"]),
                xytext=(wet["year"] - 8, wet["value"] + 12), fontsize=22, color=DARK,
                arrowprops=dict(arrowstyle="-", color=DARK, lw=1.5))
    ax.annotate(f"Driest year: {dry['year']}", xy=(dry["year"], dry["value"]),
                xytext=(dry["year"] + 3, dry["value"] - 22), fontsize=22, color=DARK,
                arrowprops=dict(arrowstyle="-", color=DARK, lw=1.5))
    # Bars start at zero so their relative heights are not exaggerated by a truncated axis.
    ax.set_ylim(0, float(values.max()) * 1.12)
    ax.set_xlim(years.min() - 1, years.max() + 1)
    ax.set_ylabel("Rain per year (mm)", fontsize=24, color=DARK)
    ax.tick_params(labelsize=22, colors=DARK)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    handles, labels = ax.get_legend_handles_labels()

    fig.text(0.08, 0.92, info.config["title"], fontsize=44, weight="bold", color=DARK)
    sub = fig.text(0.08, 0.85, info.config["headline"], fontsize=24, color=DARK)
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.52, 0.72),
               fontsize=15, frameon=False, ncol=4)
    fig.text(0.08, 0.075,
             f"Full-period Mann-Kendall p = {summary['p_value']:.3f}; not adjusted for serial correlation. "
             "Data quality varies over the record; interpret the result as exploratory.",
             fontsize=16, color=MID)
    fig.text(0.08, 0.035,
             f"Source: World Bank CCKP; CRU TS 4.10, {y0}-{y1}. CC BY 4.0; World Bank terms apply.",
             fontsize=15, color=MID)
    fig.canvas.draw()
    bb = sub.get_window_extent()
    assert bb.x1 < fig.bbox.x1 - 20, f"subtitle overflows: {bb.x1} > {fig.bbox.x1}"

    out = info.png("en")
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    print(f"wrote {out.relative_to(HERE.parents[1]).as_posix()}")


if __name__ == "__main__":
    main()
