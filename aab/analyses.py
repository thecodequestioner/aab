"""Analyses: question-driven work that reads one or more datasets and reports findings.

analysis.yaml names the question, the input datasets and a method. Built-in methods:

  ranking  rank countries on one indicator, using each country's latest year
  trend    annual series with a 10-year rolling mean, Sen's slope (95% interval),
           and a Mann-Kendall test

For anything else, set `method: custom` and add analysis.py with run(ctx) -> Result.
A custom analysis can read several datasets with ctx.read("<dataset-id>").

Generated outputs go to analysis/<id>/outputs/ and are never edited by hand:
  figures/<stem>.png and .svg   PNG for slides, SVG for print and the web
  table.csv                     the numbers behind the figure
  summary.json                  machine-readable results (infographics read this)
  results.md                    readable results, with alt text and input checksums
Hand-written findings belong in analysis/<id>/README.md.
"""
import json
import re
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import pandas as pd

from . import ProjectError
from .config import discover, load_yaml, rel
from .countries import load_registry, select
from .datasets import Dataset, get as get_dataset, load_all as load_datasets, read as read_dataset
from .provenance import sha256_file
from .stats import mann_kendall, sen_slope

# Okabe-Ito colour-blind-safe palette, plus a hatch so region is never shown by colour alone.
OKABE_ITO = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00", "#F0E442", "#000000"]
REGION_STYLE = {"Central Asia": ("#0072B2", ""), "South Asia": ("#E69F00", "//")}
EDGE = "#333333"
TEXT = "#222222"
MUTED = "#555555"


@dataclass
class Result:
    """What a method returns. The runner writes every output file from it."""
    summary: dict
    table: pd.DataFrame
    figure: object                # matplotlib Figure
    figure_stem: str
    alt_text: str
    body: str                     # Markdown: key results and tables
    method_note: str = ""
    footnote: str = ""
    extra: dict = field(default_factory=dict)


@dataclass
class Analysis:
    id: str
    path: Path
    config: dict

    @property
    def method(self) -> str:
        return self.config["method"]

    @property
    def parameters(self) -> dict:
        return self.config.get("parameters") or {}

    @property
    def dataset_ids(self) -> list[str]:
        return list(self.config["inputs"]["datasets"])

    @property
    def outputs(self) -> Path:
        return self.path / "outputs"

    @property
    def figures(self) -> Path:
        return self.outputs / "figures"

    @property
    def readme(self) -> Path:
        return self.path / "README.md"

    @property
    def custom_script(self) -> Path:
        return self.path / "analysis.py"


class Context:
    """Gives a custom analysis access to its declared datasets, and nothing else."""

    def __init__(self, analysis: Analysis, datasets: dict[str, Dataset]):
        self.analysis = analysis
        self._datasets = datasets

    def read(self, dataset_id: str) -> pd.DataFrame:
        if dataset_id not in self.analysis.dataset_ids:
            raise ProjectError(f"{self.analysis.id}: dataset '{dataset_id}' is not listed in inputs.datasets")
        return read_dataset(dataset_id)

    def dataset_config(self, dataset_id: str) -> dict:
        return get_dataset(self._datasets, dataset_id).config


def load_analysis(path: Path) -> Analysis:
    descriptor = path / "analysis.yaml"
    config = load_yaml(descriptor)
    for key in ("id", "title", "question", "version", "status", "themes", "inputs", "method"):
        if key not in config:
            raise ProjectError(f"{rel(descriptor)}: missing key '{key}'")
    if config["id"] != path.name:
        raise ProjectError(f"{rel(descriptor)}: id '{config['id']}' must equal the folder name '{path.name}'")
    if not config["inputs"].get("datasets"):
        raise ProjectError(f"{rel(descriptor)}: inputs.datasets must list at least one dataset")
    if config["method"] not in METHODS and config["method"] != "custom":
        raise ProjectError(f"{rel(descriptor)}: unknown method '{config['method']}'. "
                           f"Use one of {sorted(METHODS)} or 'custom'.")
    return Analysis(id=config["id"], path=path, config=config)


def load_all() -> dict[str, Analysis]:
    return {a.id: a for a in (load_analysis(p) for p in discover("analysis"))}


# ---------------------------------------------------------------- helpers

def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def _indicator(dataset_config: dict, code: str) -> dict:
    for ind in dataset_config["indicators"]:
        if ind["code"] == code:
            return ind
    raise ProjectError(f"Indicator {code} is not listed in dataset '{dataset_config['id']}'")


FONT_PREFERENCE = ["Liberation Sans", "Arial", "DejaVu Sans"]


def _pyplot():
    """pyplot with the Agg backend and the first installed font from FONT_PREFERENCE."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    installed = {f.name for f in font_manager.fontManager.ttflist}
    plt.rcParams["font.family"] = next((f for f in FONT_PREFERENCE if f in installed), "sans-serif")
    # A fixed salt makes SVG element ids the same on every build (matplotlib otherwise picks a random one).
    # Fixed seed for SVG element IDs. Keep it unchanged, or every SVG figure changes.
    plt.rcParams["svg.hashsalt"] = "cas-water"
    return plt


def _style_axes(ax) -> None:
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


# ---------------------------------------------------------------- methods

def ranking(ctx: Context, dataset: str, indicator: str) -> Result:
    """Rank countries on one indicator, using each country's latest available year."""
    plt = _pyplot()
    from matplotlib.patches import Patch

    cfg = ctx.dataset_config(dataset)
    ind = _indicator(cfg, indicator)
    df = ctx.read(dataset)
    sub = df[df["indicator_code"] == indicator]
    if sub.empty:
        raise ProjectError(f"No rows for {indicator} in {dataset}")
    latest = (sub.sort_values("year").groupby("iso3").tail(1)
                 .sort_values("value").reset_index(drop=True))

    group = [r["iso3"] for r in select(cfg["coverage"]["countries"])]
    registry = load_registry()
    without = [registry[i]["name"] for i in group if i not in set(latest["iso3"])]

    unit = ind["unit"]
    upper = 110 if unit == "percent of population" else float(latest["value"].max()) * 1.2
    regions = sorted(latest["region"].unique())
    fallback = iter(OKABE_ITO)
    style = {r: REGION_STYLE.get(r, (next(fallback), "")) for r in regions}
    top, bottom = latest.iloc[-1], latest.iloc[0]
    attribution = sub["attribution"].iloc[0]

    fig, ax = plt.subplots(figsize=(9, 0.45 * len(latest) + 2.4))
    bars = ax.barh(latest["country_name"], latest["value"],
                   color=[style[r][0] for r in latest["region"]], height=0.65,
                   edgecolor=EDGE, linewidth=0.6)
    for bar, r in zip(bars, latest["region"]):
        bar.set_hatch(style[r][1])
    for y, (val, yr) in enumerate(zip(latest["value"], latest["year"])):
        ax.text(val + upper * 0.01, y, f"{val:.1f} ({yr})", va="center", fontsize=9, color=TEXT)
    ax.set_xlim(0, upper)
    ax.set_xlabel(textwrap.fill(f"{ind['name']} ({unit})", 80), color=TEXT)
    ax.set_title(textwrap.fill(f"{ind['name']}: latest available year", 80),
                 loc="left", fontsize=12, fontweight="bold", color=TEXT)
    _style_axes(ax)
    handles = [Patch(facecolor=style[r][0], hatch=style[r][1], edgecolor=EDGE, label=r) for r in regions]
    ax.legend(handles=handles, frameon=False, loc="lower right", fontsize=9)
    footnote = f"Source: {attribution}. Latest year can differ by country."
    if without:
        footnote += f" No value for: {', '.join(without)}."
    fig.text(0.01, 0.01, footnote, fontsize=8, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 1))

    means = latest.groupby("region")["value"].mean().round(1)
    means_text = ", ".join(f"{k} {v:.1f}" for k, v in means.items())
    table = pd.DataFrame({
        "country_name": latest["country_name"], "iso3": latest["iso3"], "region": latest["region"],
        "latest_year": latest["year"], "value": latest["value"], "unit": unit,
    }).sort_values("value", ascending=False).reset_index(drop=True)
    md_table = "\n".join(f"| {r.country_name} | {r.region} | {r.latest_year} | {r.value:.1f} |"
                         for r in table.itertuples())
    without_text = (f"- No value for this indicator: {', '.join(without)}. "
                    f"These countries are in the group but absent from the source for this indicator.\n"
                    if without else "")
    body = f"""- Highest: {top.country_name} at {top.value:.1f} ({top.year}).
- Lowest: {bottom.country_name} at {bottom.value:.1f} ({bottom.year}).
- Gap between highest and lowest: {top.value - bottom.value:.1f} points.
- Unweighted sub-region averages: {means_text}. These are simple averages of countries, not population-weighted.
{without_text}
| Country | Sub-region | Latest year | Value ({unit}) |
|---|---|---|---|
{md_table}
"""
    alt = (f"Horizontal bar chart of {len(latest)} countries ranked by {ind['name'].lower()} "
           f"in each country's latest year, from {bottom.country_name} ({bottom.value:.1f}) to "
           f"{top.country_name} ({top.value:.1f}). Bars are coloured and hatched by sub-region.")
    summary = {
        "method": "ranking", "dataset": dataset, "indicator": indicator, "unit": unit,
        "n_countries": int(len(latest)),
        "highest": {"country": top.country_name, "value": round(float(top.value), 1), "year": int(top.year)},
        "lowest": {"country": bottom.country_name, "value": round(float(bottom.value), 1), "year": int(bottom.year)},
        "gap_points": round(float(top.value - bottom.value), 1),
        "subregion_means": {k: float(v) for k, v in means.items()},
        "without_value": without,
    }
    return Result(summary=summary, table=table, figure=fig, figure_stem=f"ranking_{_slug(indicator)}",
                  alt_text=alt, body=body,
                  method_note="Countries are ranked on their latest available value. Each value shows its year.",
                  footnote=footnote)


def trend(ctx: Context, dataset: str, indicator: str) -> Result:
    """Annual series with a 10-year rolling mean, Sen's slope (95% interval) and a Mann-Kendall test."""
    plt = _pyplot()
    cfg = ctx.dataset_config(dataset)
    ind = _indicator(cfg, indicator)
    df = ctx.read(dataset)
    sub = df[df["indicator_code"] == indicator].sort_values("year").reset_index(drop=True)
    if len(sub) < 10:
        raise ProjectError(f"Need at least 10 years for a trend; found {len(sub)} for {dataset}")
    t = sub["year"].to_numpy(dtype=float)
    x = sub["value"].to_numpy(dtype=float)
    n = len(x)
    attribution = sub["attribution"].iloc[0]

    mk = mann_kendall(x)
    sen = sen_slope(t, x)
    unit = ind["unit"]
    base = unit.split(" per ")[0] if " per " in unit else unit
    per_decade = sen.slope * 10
    low10, high10 = sen.lower * 10, sen.upper * 10
    mean_value = float(x.mean())
    change_total = sen.slope * (t[-1] - t[0])
    pct_per_decade = 100 * per_decade / mean_value if mean_value else float("nan")
    significant = mk.p_value < 0.05
    direction = "increasing" if sen.slope > 0 else "decreasing" if sen.slope < 0 else "flat"
    verdict = ("statistically significant at the 5% level" if significant
               else "not statistically significant at the 5% level")

    rolling = pd.Series(x).rolling(10, center=True, min_periods=5).mean().to_numpy()
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(t, x, color="#B8C4CE", width=0.8, label="Annual value")
    ax.plot(t, rolling, color="#0072B2", linewidth=2.4, label="10-year rolling mean")
    ax.plot(t, sen.intercept + sen.slope * t, color="#D55E00", linestyle="--", linewidth=1.8,
            label=f"Sen's trend line: {per_decade:+.1f} {base} per decade")
    ax.set_xlabel("Year", color=TEXT)
    ax.set_ylabel(ind["name"], color=TEXT)
    ax.set_title(textwrap.fill(f"{ind['name']}: trend, {int(t[0])}-{int(t[-1])}", 80),
                 loc="left", fontsize=12, fontweight="bold", color=TEXT)
    _style_axes(ax)
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    footnote = f"Source: {attribution}. Gridded estimates; station coverage and data quality vary across the record."
    fig.text(0.01, 0.01, footnote, fontsize=8, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 1))

    grouped = sub.assign(decade=(sub["year"] // 10 * 10).astype(int)).groupby("decade")["value"]
    rows = []
    for decade, mean, count in zip(grouped.mean().index, grouped.mean(), grouped.count()):
        label = f"{decade}s" + (" (partial decade)" if count < 10 else "")
        rows.append(f"| {label} | {mean:.1f} | {count} |")
    decade_table = "\n".join(rows)

    wettest = sub.loc[sub["value"].idxmax()]
    driest = sub.loc[sub["value"].idxmin()]
    body = f"""- Direction: {direction}. Sen's slope says the value changes by {per_decade:+.2f} {base} per decade, with a 95% interval of {low10:+.2f} to {high10:+.2f}.
- Change implied by the slope over the period: {change_total:+.1f} {base} between the first and last year, about {pct_per_decade:+.1f}% of the mean per decade.
- Mean over the period: {mean_value:.1f} {unit}.
- Wettest year: {int(wettest['year'])} ({wettest['value']:.1f}). Driest year: {int(driest['year'])} ({driest['value']:.1f}).
- Mann-Kendall test: S = {mk.s:.0f}, z = {mk.z:.2f}, p = {mk.p_value:.3f}. The trend is {verdict}.

**Decadal means**

| Decade | Mean ({unit}) | Years |
|---|---|---|
{decade_table}
"""
    alt = (f"Bar chart of {ind['name'].lower()} from {int(t[0])} to {int(t[-1])}, with a 10-year rolling "
           f"mean and a dashed trend line. The trend is {direction}, at {per_decade:+.1f} {base} per decade, "
           f"and it is {'statistically significant' if significant else 'not statistically significant'} "
           f"at the 5% level.")
    summary = {
        "method": "trend", "dataset": dataset, "indicator": indicator, "unit": unit,
        "first_year": int(t[0]), "last_year": int(t[-1]), "n_years": int(n),
        "direction": direction,
        "sen_slope_per_decade": round(per_decade, 3),
        "ci95_per_decade": [round(low10, 3), round(high10, 3)],
        "mann_kendall_s": float(mk.s), "mann_kendall_z": round(mk.z, 3),
        "p_value": round(mk.p_value, 4),
        "significant_5pct": bool(significant),
        "mean": round(mean_value, 2),
        "wettest": {"year": int(wettest["year"]), "value": round(float(wettest["value"]), 1)},
        "driest": {"year": int(driest["year"]), "value": round(float(driest["value"]), 1)},
    }
    table = pd.DataFrame({"year": sub["year"], "value": sub["value"], "unit": unit,
                          "rolling_mean_10y": pd.Series(rolling).round(2)})
    return Result(summary=summary, table=table, figure=fig, figure_stem=f"trend_{_slug(indicator)}",
                  alt_text=alt, body=body,
                  method_note=("Sen's slope is a robust estimate of the trend. The conventional Mann-Kendall "
                               "test asks whether the trend is larger than year-to-year variation would explain, "
                               "but its p-value does not adjust for serial correlation or changing data quality."),
                  footnote=footnote)


METHODS: dict[str, Callable[..., Result]] = {"ranking": ranking, "trend": trend}


# ---------------------------------------------------------------- running

def _results_md(analysis: Analysis, result: Result, datasets: dict[str, Dataset]) -> str:
    cfg = analysis.config
    lines = [f"# {cfg['title']}: results", "",
             "*Generated by `python -m aab build`. Do not edit by hand. "
             "The numbers depend only on the input datasets, so the file is the same on every rebuild.*",
             "",
             f"**Question:** {cfg['question']}",
             f"**Method:** `{analysis.method}`. {result.method_note}".rstrip(),
             "",
             "**Input datasets**", ""]
    for dsid in analysis.dataset_ids:
        ds = get_dataset(datasets, dsid)
        lines.append(f"- `{dsid}` version {ds.config['version']}, "
                     f"file checksum (SHA-256) `{sha256_file(ds.processed_csv)}`")
    lines += ["", "## Key results", "", result.body.rstrip(), "",
              f"![{result.alt_text}](figures/{result.figure_stem}.png)", "",
              result.footnote, ""]
    return "\n".join(lines)


def run(analysis: Analysis, datasets: dict[str, Dataset]) -> Result:
    """Run one analysis and write its outputs. Returns the Result."""
    analysis.figures.mkdir(parents=True, exist_ok=True)
    ctx = Context(analysis, datasets)
    if analysis.method == "custom":
        if not analysis.custom_script.exists():
            raise ProjectError(f"{rel(analysis.path)}: method 'custom' needs analysis.py with run(ctx)")
        result = _load_custom(analysis).run(ctx)
    else:
        result = METHODS[analysis.method](ctx, **analysis.parameters)

    stem = result.figure_stem
    result.figure.savefig(analysis.figures / f"{stem}.png", dpi=200)
    result.figure.savefig(analysis.figures / f"{stem}.svg", metadata={"Date": None})
    _pyplot().close(result.figure)
    result.table.to_csv(analysis.outputs / "table.csv", index=False, encoding="utf-8", lineterminator="\n")
    (analysis.outputs / "summary.json").write_text(
        json.dumps(result.summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (analysis.outputs / "results.md").write_text(_results_md(analysis, result, datasets), encoding="utf-8")
    return result


def _load_custom(analysis: Analysis):
    import importlib.util
    spec = importlib.util.spec_from_file_location(f"analysis_{analysis.id.replace('-', '_')}",
                                                  analysis.custom_script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "run"):
        raise ProjectError(f"{rel(analysis.custom_script)} must define run(ctx)")
    return module


def run_all(ids: list[str] | None = None) -> None:
    datasets = load_datasets()
    for analysis in load_all().values():
        if ids and analysis.id not in ids:
            continue
        run(analysis, datasets)
        print(f"  analysis {analysis.id}: wrote figure, table, summary and results")
