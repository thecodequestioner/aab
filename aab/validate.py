"""Checks on everything in the repository. Errors fail the build. Warnings are reported only.

What is checked
  project     required settings; one version number across project.yaml, CITATION.cff, codemeta.json;
              no template placeholders left in the public metadata
  sources     descriptor complete; every raw file matches its logged SHA-256 checksum
  datasets    tidy-format rules (types, patterns, ranges, primary key, units, years);
              coverage per indicator; datapackage.json and CSV current; README sections present
  analyses    inputs exist; outputs exist and are current; every figure has alt text
  infographics inputs exist; PNG exists at slide size; alt text present; notes present
  catalogue   CATALOG.md is current
"""
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from . import ProjectError
from .analyses import load_all as load_analyses
from .catalog import write_text as catalog_text
from .config import ROOT, load_project, rel
from .countries import select
from .datasets import datapackage_text, load_all as load_datasets
from .infographics import load_all as load_infographics
from .provenance import latest_checksum, sha256_file
from .sources import load_all as load_sources
from .tidy import PRIMARY_KEY, STANDARD_COLUMNS

UNIT_RULES = {"percent of population": (0, 100)}
PLACEHOLDERS = ["your_first_name", "your_last_name", "your_github_username", "TEMPLATE_ID"]
DATASET_README_SECTIONS = {"source": "Source", "method": "Method", "caveat": "Caveat", "cite": "Cite"}
IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, where: str, msg: str) -> None:
        self.errors.append(f"{where}: {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append(f"{where}: {msg}")

    @property
    def ok(self) -> bool:
        return not self.errors


def _guard(report: Report, where: str, fn):
    try:
        return fn()
    except ProjectError as exc:
        report.error(where, str(exc))
        return None


def check_project(report: Report) -> None:
    where = "project.yaml"
    project = load_project()
    for key in ("name", "title", "author", "version", "repository_url", "licences", "themes"):
        if key not in project:
            report.error(where, f"missing key '{key}'")
    if "your-org" in str(project.get("repository_url", "")):
        report.warn(where, "repository_url is a placeholder; the citation and links are wrong until it is replaced")
    version = str(project.get("version", ""))
    citation = _load_yaml_safe(ROOT / "CITATION.cff")
    if citation and str(citation.get("version")) != version:
        report.error("CITATION.cff", f"version {citation.get('version')} differs from project.yaml ({version})")
    codemeta = _load_json_safe(ROOT / "codemeta.json")
    if codemeta and str(codemeta.get("version")) != version:
        report.error("codemeta.json", f"version {codemeta.get('version')} differs from project.yaml ({version})")
    for name in ("project.yaml", "CITATION.cff", "codemeta.json", "LICENSE"):
        text = (ROOT / name).read_text(encoding="utf-8") if (ROOT / name).exists() else ""
        for token in PLACEHOLDERS:
            if token in text:
                report.error(name, f"placeholder '{token}' is still present")


def _load_yaml_safe(path: Path):
    import yaml
    return yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else None


def _load_json_safe(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def check_sources(report: Report, sources: dict) -> None:
    for s in sources.values():
        where = f"data/sources/{s.id}"
        if not (s.path / "README.md").exists():
            report.error(where, "README.md is missing (how to obtain the data, licence, citation)")
        if s.access_type == "worldbank":
            for ind in s.config["access"]["indicators"]:
                if not s.worldbank_file(ind["code"]).exists():
                    report.error(where, f"raw file for {ind['code']} is missing. Run: python -m aab build --refresh")
        files = s.raw_files()
        if s.access_type == "manual" and not files:
            report.error(where, "no raw file present. See the steps in its README.md")
        for f in files:
            logged = latest_checksum(s.raw_dir, f.name)
            actual = sha256_file(f)
            if logged is None:
                report.error(where, f"{f.name} is not in RETRIEVAL_LOG.csv")
            elif logged != actual:
                msg = (f"{f.name} does not match its logged checksum (log {logged[:12]}..., file {actual[:12]}...). "
                       "Raw files must not change. Re-download, or record the issue in known_issues.")
                if s.known_issues:
                    report.warn(where, "known issue: " + msg)
                else:
                    report.error(where, msg)


def check_dataset(report: Report, ds, sources: dict, project_themes: set) -> None:
    where = f"data/datasets/{ds.id}"
    cfg = ds.config
    for sid in ds.source_ids:
        if sid not in sources:
            report.error(where, f"input source '{sid}' does not exist in data/sources/")
    for t in cfg["themes"]:
        if t not in project_themes:
            report.error(where, f"theme '{t}' is not listed in project.yaml")
    if not ds.processed_csv.exists():
        report.error(where, f"{rel(ds.processed_csv)} is missing. Run: python -m aab build --dataset {ds.id}")
        return
    readme = ds.readme.read_text(encoding="utf-8") if ds.readme.exists() else ""
    headings = [h.lower() for h in re.findall(r"^##\s+(.+)$", readme, flags=re.M)]
    for key, label in DATASET_README_SECTIONS.items():
        if not any(key in h for h in headings):
            report.error(where, f"README.md needs a '## {label}' section")

    expected_text = datapackage_text(ds, sources)
    if not ds.datapackage.exists() or ds.datapackage.read_text(encoding="utf-8") != expected_text:
        report.error(where, "datapackage.json is out of date. Run: python -m aab build --dataset " + ds.id)

    df = pd.read_csv(ds.processed_csv, dtype={"iso3": str, "indicator_code": str})
    fields = [f["name"] for f in json.loads(expected_text)["resources"][0]["schema"]["fields"]]
    if list(df.columns) != fields:
        report.error(where, f"columns {list(df.columns)} do not match the datapackage {fields}")
        return
    if list(df.columns[:len(STANDARD_COLUMNS)]) != STANDARD_COLUMNS:
        report.error(where, "standard columns are missing or out of order")
    _check_values(report, where, df, json.loads(expected_text)["resources"][0]["schema"]["fields"])
    y0, y1 = ds.years
    outside = int(((df["year"] < y0) | (df["year"] > y1)).sum())
    if outside:
        report.error(where, f"{outside} row(s) outside years {y0}-{y1}")

    members = {r["iso3"] for r in select(ds.countries_group)}
    for ind in cfg["indicators"]:
        sub = df[df["indicator_code"] == ind["code"]]
        if sub.empty:
            report.warn(where, f"no rows for indicator {ind['code']}")
            continue
        absent = sorted(members - set(sub["iso3"]))
        if absent:
            report.warn(where, f"{ind['code']} has no values for: {', '.join(absent)}. "
                               "Say so in the dataset README and in any figure footnote.")


def _check_values(report: Report, where: str, df: pd.DataFrame, fields: list[dict]) -> None:
    pk = PRIMARY_KEY
    for f in fields:
        name, c, t = f["name"], f.get("constraints", {}), f["type"]
        col = df[name]
        if c.get("required") and col.isna().any():
            report.error(where, f"{name}: {int(col.isna().sum())} missing value(s)")
        non = col.dropna()
        if t in ("number", "integer"):
            num = pd.to_numeric(non, errors="coerce")
            if num.isna().any():
                report.error(where, f"{name}: non-numeric values")
                continue
            if t == "integer" and (num % 1 != 0).any():
                report.error(where, f"{name}: non-integer values")
            non = num
        if "pattern" in c and (~non.astype(str).str.match(c["pattern"])).any():
            report.error(where, f"{name}: values do not match pattern {c['pattern']}")
        if "minimum" in c and (non < c["minimum"]).any():
            report.error(where, f"{name}: value below {c['minimum']}")
        if "maximum" in c and (non > c["maximum"]).any():
            report.error(where, f"{name}: value above {c['maximum']}")
    dupes = int(df.duplicated(pk).sum())
    if dupes:
        report.error(where, f"{dupes} duplicate primary key(s) on {pk}")
    values = pd.to_numeric(df["value"], errors="coerce")
    for unit, (lo, hi) in UNIT_RULES.items():
        bad = (df["unit"] == unit) & ((values < lo) | (values > hi))
        if bad.any():
            report.error(where, f"{int(bad.sum())} value(s) outside {lo}-{hi} for unit '{unit}'")


def _check_images(report: Report, where: str, text: str, base: Path, required: bool) -> None:
    images = IMAGE.findall(text)
    if required and not images:
        report.error(where, "no figure with alt text found")
    for alt, target in images:
        if not alt.strip():
            report.error(where, f"figure '{target}' has empty alt text")
        if not target.startswith("http") and not (base / target).exists():
            report.error(where, f"figure '{target}' does not exist")


def check_analysis(report: Report, a, datasets: dict, project_themes: set) -> None:
    where = f"analysis/{a.id}"
    cfg = a.config
    for dsid in a.dataset_ids:
        if dsid not in datasets:
            report.error(where, f"input dataset '{dsid}' does not exist")
    for t in cfg["themes"]:
        if t not in project_themes:
            report.error(where, f"theme '{t}' is not listed in project.yaml")
    if a.method == "custom" and not a.custom_script.exists():
        report.error(where, "method is 'custom' but analysis.py is missing")
    if not a.readme.exists():
        report.error(where, "README.md is missing (findings and method)")
    else:
        _check_images(report, where, a.readme.read_text(encoding="utf-8"), a.path, required=True)
    for name in ("summary.json", "table.csv", "results.md"):
        if not (a.outputs / name).exists():
            report.error(where, f"outputs/{name} is missing. Run: python -m aab build --analysis {a.id}")
    results = a.outputs / "results.md"
    if results.exists():
        _check_images(report, where, results.read_text(encoding="utf-8"), a.outputs, required=True)


def check_infographic(report: Report, info, analyses: dict, datasets: dict, project_themes: set) -> None:
    where = f"infographics/{info.id}"
    cfg = info.config
    for aid in info.analyses:
        if aid not in analyses:
            report.error(where, f"input analysis '{aid}' does not exist")
    for dsid in info.datasets:
        if dsid not in datasets:
            report.error(where, f"input dataset '{dsid}' does not exist")
    for t in cfg["themes"]:
        if t not in project_themes:
            report.error(where, f"theme '{t}' is not listed in project.yaml")
    if len(str(cfg["alt_text"]).split()) < 12:
        report.error(where, "alt_text is too short to describe the finding in plain words")
    if not info.notes.exists():
        report.error(where, "README.md is missing (teacher or companion notes, with alt text)")
    png = info.png("en")
    if not png.exists():
        report.error(where, f"{rel(png)} is missing. Run: python -m aab build --infographic {info.id}")
    else:
        from PIL import Image
        with Image.open(png) as im:
            if im.size != (1920, 1080):
                report.warn(where, f"PNG is {im.size[0]}x{im.size[1]}; slides are 1920x1080")


def run(strict_catalog: bool = True) -> Report:
    report = Report()
    check_project(report)
    project_themes = set(load_project().get("themes", []))
    sources = _guard(report, "sources", load_sources) or {}
    datasets = _guard(report, "datasets", load_datasets) or {}
    analyses = _guard(report, "analyses", load_analyses) or {}
    infographics = _guard(report, "infographics", load_infographics) or {}
    check_sources(report, sources)
    for ds in datasets.values():
        check_dataset(report, ds, sources, project_themes)
    for a in analyses.values():
        check_analysis(report, a, datasets, project_themes)
    for info in infographics.values():
        check_infographic(report, info, analyses, datasets, project_themes)
    if strict_catalog:
        catalog = ROOT / "CATALOG.md"
        if not catalog.exists() or catalog.read_text(encoding="utf-8") != catalog_text():
            report.error("CATALOG.md", "is out of date. Run: python -m aab catalog")
    return report


def print_report(report: Report) -> None:
    for w in report.warnings:
        print(f"  warning: {w}")
    for e in report.errors:
        print(f"  ERROR: {e}")
    print("Validation passed." if report.ok else f"Validation failed with {len(report.errors)} error(s).")
