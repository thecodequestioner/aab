"""Population change by country, 2000 to 2025: sorted horizontal bars of percentage change.

The runner calls run(ctx) and writes the figure, table.csv, summary.json and results.md
from the Result returned here. Change the wording in this file, not the generated outputs.
"""
import textwrap

import pandas as pd

from aab.analyses import EDGE, MUTED, REGION_STYLE, TEXT, Result, _pyplot, _style_axes

DATASET = "population-central-south-asia"
INDICATOR = "SP.POP.TOTL"
START, END = 2000, 2025


def run(ctx) -> Result:
    plt = _pyplot()
    from matplotlib.patches import Patch

    df = ctx.read(DATASET)
    sub = df[df["indicator_code"] == INDICATOR]
    last = sub[sub["year"] == END][["iso3", "country_name", "region", "value", "attribution"]]
    last = last.rename(columns={"value": "end_value"})
    first = sub[sub["year"] == START][["iso3", "value"]].rename(columns={"value": "start_value"})
    table = last.merge(first, on="iso3", how="inner")
    if table.empty:
        raise ValueError(f"{DATASET} needs values for {START} and {END}")

    attribution = table["attribution"].iloc[0]
    table = table.drop(columns=["attribution"])
    table["change_people"] = table["end_value"] - table["start_value"]
    table["change_percent"] = (table["end_value"] / table["start_value"] - 1) * 100
    table["average_yearly_percent"] = ((table["end_value"] / table["start_value"]) ** (1 / (END - START)) - 1) * 100
    table = table.sort_values("change_percent", ascending=False).reset_index(drop=True)

    n = len(table)
    grew = int((table["change_people"] > 0).sum())
    top = table.iloc[0]
    bottom = table.iloc[-1]
    median_avg = float(table["average_yearly_percent"].median())

    table["start_value"] = table["start_value"].round(0).astype("int64")
    table["end_value"] = table["end_value"].round(0).astype("int64")
    table["change_people"] = table["change_people"].round(0).astype("int64")
    table["change_percent"] = table["change_percent"].round(2)
    table["average_yearly_percent"] = table["average_yearly_percent"].round(2)
    table = table[["country_name", "iso3", "region", "start_value", "end_value",
                   "change_people", "change_percent", "average_yearly_percent"]]

    plot = table.sort_values("change_percent", ascending=True).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(9, 0.45 * n + 2.4))
    bars = ax.barh(plot["country_name"], plot["change_percent"],
                   color=[REGION_STYLE[r][0] for r in plot["region"]], height=0.65,
                   edgecolor=EDGE, linewidth=0.6)
    for bar, r in zip(bars, plot["region"]):
        bar.set_hatch(REGION_STYLE[r][1])
    lo = min(0.0, float(plot["change_percent"].min()))
    hi = max(0.0, float(plot["change_percent"].max()))
    span = hi - lo
    for y, row in plot.iterrows():
        x = float(row["change_percent"])
        label = (f"{x:+.0f}%  ({row['start_value'] / 1e6:,.1f} to "
                 f"{row['end_value'] / 1e6:,.1f} million)")
        ax.text(max(x, 0) + span * 0.01, y, label, va="center", fontsize=9, color=TEXT)
    ax.set_xlim(lo - span * 0.02, hi + span * 0.9)
    ax.axvline(0, color=EDGE, linewidth=0.8)
    ax.set_xlabel(f"Change in total population, {START} to {END} (%)", color=TEXT)
    ax.set_title(textwrap.fill(f"Population change by country, {START} to {END}", 80),
                 loc="left", fontsize=12, fontweight="bold", color=TEXT)
    _style_axes(ax)
    handles = [Patch(facecolor=REGION_STYLE[r][0], hatch=REGION_STYLE[r][1], edgecolor=EDGE, label=r)
               for r in sorted(table["region"].unique())]
    ax.legend(handles=handles, frameon=False, loc="lower right", fontsize=9)
    footnote = (f"Source: {attribution}. Change = population in {END} divided by population in {START}, "
                f"minus 1. {END} is a projection.")
    fig.text(0.01, 0.01, footnote, fontsize=8, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 1))

    rows = "\n".join(
        f"| {r['country_name']} | {r['region']} | {r['change_percent']:+.1f} | "
        f"{r['average_yearly_percent']:+.2f} |" for _, r in table.iterrows())
    body = (
        f"- Countries whose population grew from {START} to {END}: {grew} of {n}.\n"
        f"- Largest rise: {top['country_name']}, {top['change_percent']:+.1f}% "
        f"({top['start_value'] / 1e6:,.1f} million to {top['end_value'] / 1e6:,.1f} million).\n"
        f"- Smallest change: {bottom['country_name']}, {bottom['change_percent']:+.1f}% "
        f"({bottom['start_value'] / 1e6:,.1f} million to {bottom['end_value'] / 1e6:,.1f} million).\n"
        f"- Median average yearly change across the {n} countries: {median_avg:.2f}% per year.\n\n"
        "| Country | Sub-region | Change (%) | Average yearly change (%) |\n|---|---|---|---|\n" + rows
    )
    alt = (f"Horizontal bar chart of {n} countries sorted by population change from {START} to {END}. "
           f"{grew} of {n} countries grew. {top['country_name']} rose most, by "
           f"{top['change_percent']:.0f}%, and {bottom['country_name']} changed least, at "
           f"{bottom['change_percent']:+.0f}%. Bars are coloured and hatched by sub-region.")
    summary = {
        "method": "custom", "dataset": DATASET, "indicator": INDICATOR, "unit": "percent",
        "first_year": START, "last_year": END, "n_countries": n,
        "countries_grew": grew, "all_grew": bool(grew == n),
        "largest_rise": {"country": top["country_name"], "change_percent": float(top["change_percent"])},
        "smallest_change": {"country": bottom["country_name"], "change_percent": float(bottom["change_percent"])},
        "median_average_yearly_percent": round(median_avg, 2),
    }
    return Result(
        summary=summary, table=table, figure=fig, figure_stem="population_growth_2000_2025",
        alt_text=alt, body=body,
        method_note="Each country's population in the first and last year is compared. Countries are ordered from largest to smallest change.",
        footnote=footnote,
    )
