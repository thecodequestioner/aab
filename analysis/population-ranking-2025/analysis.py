"""Total population by country, one reference year: a horizontal bar chart in millions.

The runner calls run(ctx) and writes the figure, table.csv, summary.json and results.md
from the Result returned here. Change the wording in this file, not the generated outputs.
"""
import textwrap

import pandas as pd

from aab.analyses import EDGE, MUTED, REGION_STYLE, TEXT, Result, _pyplot, _style_axes

DATASET = "population-central-south-asia"
INDICATOR = "SP.POP.TOTL"
REFERENCE_YEAR = 2025


def run(ctx) -> Result:
    plt = _pyplot()
    from matplotlib.patches import Patch

    cfg = ctx.dataset_config(DATASET)
    df = ctx.read(DATASET)
    sub = df[(df["indicator_code"] == INDICATOR) & (df["year"] == REFERENCE_YEAR)].copy()
    if sub.empty:
        raise ValueError(f"No rows for {INDICATOR} in {DATASET}")

    year = int(sub["year"].max())
    total = float(sub["value"].sum())
    sub["millions"] = sub["value"] / 1_000_000
    # barh draws the first row at the bottom, so sort ascending to put the largest country on top.
    sub = sub.sort_values("value", ascending=True).reset_index(drop=True)
    top = sub.iloc[-1]
    bottom = sub.iloc[0]
    share_top = 100 * float(top["value"]) / total

    table = pd.DataFrame({
        "country_name": sub["country_name"],
        "iso3": sub["iso3"],
        "region": sub["region"],
        "year": sub["year"],
        "population_millions": sub["millions"].round(2),
        "population": sub["value"].round(0).astype("int64"),
    }).sort_values("population", ascending=False).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(9, 0.45 * len(sub) + 2.4))
    bars = ax.barh(sub["country_name"], sub["millions"],
                   color=[REGION_STYLE[r][0] for r in sub["region"]], height=0.65,
                   edgecolor=EDGE, linewidth=0.6)
    for bar, r in zip(bars, sub["region"]):
        bar.set_hatch(REGION_STYLE[r][1])
    upper = float(sub["millions"].max()) * 1.18
    for y, val in enumerate(sub["millions"]):
        ax.text(val + upper * 0.01, y, f"{val:,.1f} million", va="center", fontsize=9, color=TEXT)
    ax.set_xlim(0, upper)
    ax.set_xlabel("Total population (millions of people)", color=TEXT)
    ax.set_title(textwrap.fill(f"Total population by country, {year}", 80),
                 loc="left", fontsize=12, fontweight="bold", color=TEXT)
    _style_axes(ax)
    handles = [Patch(facecolor=REGION_STYLE[r][0], hatch=REGION_STYLE[r][1], edgecolor=EDGE, label=r)
               for r in sorted(sub["region"].unique())]
    ax.legend(handles=handles, frameon=False, loc="lower right", fontsize=9)
    footnote = f"Source: {sub['attribution'].iloc[0]}. All values are for {year}."
    fig.text(0.01, 0.01, footnote, fontsize=8, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 1))

    rows = "\n".join(f"| {r.country_name} | {r.region} | {int(r.population):,} |"
                     for r in table.itertuples())
    body = (
        f"- Largest: {top['country_name']}, {float(top['value']) / 1e6:,.1f} million people ({year}). "
        f"This is {share_top:.0f}% of the total for the {len(sub)} countries.\n"
        f"- Smallest: {bottom['country_name']}, {float(bottom['value']) / 1e6:,.1f} million people ({year}).\n"
        f"- Total for the {len(sub)} countries: {total / 1e6:,.1f} million people ({year}).\n\n"
        "| Country | Sub-region | Population (people) |\n|---|---|---|\n" + rows
    )
    alt = (f"Horizontal bar chart of {len(sub)} countries ranked by total population in {year}. "
           f"{top['country_name']} is largest at {float(top['value']) / 1e6:,.1f} million people, "
           f"about {share_top:.0f}% of the group total. {bottom['country_name']} is smallest at "
           f"{float(bottom['value']) / 1e6:,.1f} million. Bars are coloured and hatched by sub-region.")
    summary = {
        "method": "custom", "dataset": DATASET, "indicator": INDICATOR, "unit": "people",
        "year": year, "n_countries": int(len(sub)),
        "largest": {"country": top["country_name"], "population": int(round(float(top["value"])))},
        "smallest": {"country": bottom["country_name"], "population": int(round(float(bottom["value"])))},
        "total_population": int(round(total)),
        "largest_share_percent": round(share_top, 1),
    }
    return Result(
        summary=summary, table=table, figure=fig, figure_stem="population_ranking_2025",
        alt_text=alt, body=body,
        method_note="Countries are ordered by total population in the reference year, largest first.",
        footnote=footnote,
    )
