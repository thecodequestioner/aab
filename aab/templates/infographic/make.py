"""Draws the infographic PNG (1920 x 1080 px) and SVG. Copy and adapt; keep the claim check.

Run by the pipeline, or from the repository root:
    python infographics/TEMPLATE_ID/make.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from aab.datasets import read as read_dataset  # noqa: E402
from aab.infographics import load_infographic, read_summary  # noqa: E402


def main() -> None:
    info = load_infographic(HERE)
    summary = read_summary(info.analyses[0])
    if info.config["claim"] == "no_clear_trend" and summary["significant_5pct"]:
        raise SystemExit("The headline claims no clear trend, but the analysis finds a significant one.")
    df = read_dataset(info.datasets[0])  # replace with the data you need
    fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
    ax.set_title(info.config["title"], fontsize=40, loc="left")
    fig.text(0.08, 0.02, info.config["headline"], fontsize=24)
    out = info.png("en")
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    fig.savefig(info.svg("en"), format="svg", metadata={"Date": None})


if __name__ == "__main__":
    main()
