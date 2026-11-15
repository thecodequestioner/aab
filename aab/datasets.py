"""Datasets: cleaned, documented, versioned tables built from one or more sources.

A dataset folder holds its configuration (dataset.yaml), its documentation (README.md),
its generated table (<id>.csv) and its generated schema (datapackage.json).

Two ways to build a table:
  1. Generic: indicators from a World Bank source are filtered to the countries and years
     named in dataset.yaml. No code is needed.
  2. transform.py: a script with build(dataset, sources) -> DataFrame, for any other source.
"""
import importlib.util
import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from . import ProjectError
from .config import DATASETS_DIR, discover, load_project, load_yaml, rel
from .countries import load_registry, select
from .sources import Source, get as get_source, read_worldbank
from .tidy import PRIMARY_KEY, STANDARD_COLUMNS, STANDARD_FIELDS, write_csv

REQUIRED_KEYS = ["id", "title", "description", "version", "status", "themes", "inputs", "coverage", "indicators"]


@dataclass
class Dataset:
    id: str
    path: Path
    config: dict

    @property
    def processed_csv(self) -> Path:
        return self.path / f"{self.id}.csv"

    @property
    def datapackage(self) -> Path:
        return self.path / "datapackage.json"

    @property
    def readme(self) -> Path:
        return self.path / "README.md"

    @property
    def transform(self) -> Path:
        return self.path / "transform.py"

    @property
    def source_ids(self) -> list[str]:
        return list(self.config["inputs"]["sources"])

    @property
    def years(self) -> tuple[int, int]:
        y = self.config["coverage"]["years"]
        return int(y["start"]), int(y["end"])

    @property
    def countries_group(self) -> str:
        return self.config["coverage"]["countries"]


def load_dataset(path: Path) -> Dataset:
    descriptor = path / "dataset.yaml"
    config = load_yaml(descriptor)
    missing = [k for k in REQUIRED_KEYS if k not in config]
    if missing:
        raise ProjectError(f"{rel(descriptor)}: missing keys {missing}")
    if config["id"] != path.name:
        raise ProjectError(f"{rel(descriptor)}: id '{config['id']}' must equal the folder name '{path.name}'")
    for ind in config["indicators"]:
        for key in ("code", "name", "unit"):
            if key not in ind:
                raise ProjectError(f"{rel(descriptor)}: every indicator needs '{key}'")
    return Dataset(id=config["id"], path=path, config=config)


def load_all() -> dict[str, Dataset]:
    return {d.id: d for d in (load_dataset(p) for p in discover("dataset"))}


def get(datasets: dict[str, Dataset], dataset_id: str) -> Dataset:
    if dataset_id not in datasets:
        raise ProjectError(f"Unknown dataset '{dataset_id}'. Known datasets: {sorted(datasets)}")
    return datasets[dataset_id]


def build(ds: Dataset, sources: dict[str, Source]) -> pd.DataFrame:
    """Return the tidy table for one dataset. Does not write files."""
    if ds.transform.exists():
        df = _load_transform(ds).build(ds, sources)
    else:
        df = _build_worldbank(ds, sources)
    missing = [c for c in STANDARD_COLUMNS if c not in df.columns]
    if missing:
        raise ProjectError(f"{ds.id}: built table is missing columns {missing}")
    return df.sort_values(["region", "iso3", "indicator_code", "year"]).reset_index(drop=True)


def _load_transform(ds: Dataset):
    spec = importlib.util.spec_from_file_location(f"transform_{ds.id.replace('-', '_')}", ds.transform)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "build"):
        raise ProjectError(f"{rel(ds.transform)} must define build(dataset, sources)")
    return module


def _build_worldbank(ds: Dataset, sources: dict[str, Source]) -> pd.DataFrame:
    registry = load_registry()
    selected = {r["iso3"] for r in select(ds.countries_group)}
    y0, y1 = ds.years
    records = []
    for ind in ds.config["indicators"]:
        source_id = ind.get("source") or (ds.source_ids[0] if len(ds.source_ids) == 1 else None)
        if source_id is None or source_id not in ds.source_ids:
            raise ProjectError(f"{ds.id}: indicator {ind['code']} needs 'source:' set to one of {ds.source_ids}")
        source = get_source(sources, source_id)
        if source.access_type != "worldbank":
            raise ProjectError(f"{ds.id}: source '{source_id}' has no World Bank connector. Add transform.py.")
        listed = {i["code"] for i in source.config["access"]["indicators"]}
        if ind["code"] not in listed:
            raise ProjectError(f"{ind['code']} is not listed in data/sources/{source_id}/source.yaml")
        decimals = ind.get("decimals", 2)
        for r in read_worldbank(source, ind["code"]):
            iso3 = r.get("countryiso3code")
            if r.get("value") is None or iso3 not in selected:
                continue
            year = int(r["date"])
            if not y0 <= year <= y1:
                continue
            country = registry[iso3]
            records.append({
                "iso3": iso3,
                "country_name": country["name"],
                "region": country["subregion"],
                "year": year,
                "indicator_code": ind["code"],
                "indicator_name": ind["name"],
                "value": round(float(r["value"]), decimals),
                "unit": ind["unit"],
                "attribution": source.config["attribution"],
            })
    return pd.DataFrame(records, columns=STANDARD_COLUMNS)


def datapackage(ds: Dataset, sources: dict[str, Source]) -> dict:
    """Frictionless Data Package descriptor. Generated from dataset.yaml, never hand-edited."""
    project = load_project()
    cfg = ds.config
    fields = [dict(f) for f in STANDARD_FIELDS] + [dict(f) for f in cfg.get("extra_fields") or []]
    package = {
        "name": cfg["id"],
        "title": cfg["title"],
        "description": cfg["description"],
        "version": str(cfg["version"]),
        "keywords": cfg.get("tags", []),
        "contributors": [{"title": project["author"], "role": "author"}],
        "sources": [{"title": get_source(sources, s).config["title"],
                     "path": get_source(sources, s).config["url"]} for s in ds.source_ids],
        "resources": [{
            "name": cfg["id"],
            "title": cfg["title"],
            "path": f"{cfg['id']}.csv",
            "format": "csv",
            "mediatype": "text/csv",
            "encoding": "utf-8",
            "schema": {"fields": fields, "primaryKey": PRIMARY_KEY},
        }],
    }
    if not cfg.get("license_review_required", False):
        package["licenses"] = [project["licences"]["data"]]
    return package


def datapackage_text(ds: Dataset, sources: dict[str, Source]) -> str:
    return json.dumps(datapackage(ds, sources), indent=2, ensure_ascii=False) + "\n"


def write(ds: Dataset, df: pd.DataFrame, sources: dict[str, Source]) -> None:
    write_csv(df, ds.processed_csv)
    ds.datapackage.write_text(datapackage_text(ds, sources), encoding="utf-8")


def read(dataset_id: str) -> pd.DataFrame:
    """Read a built dataset. Analyses and infographics use this, never the raw files."""
    ds = get(load_all(), dataset_id)
    if not ds.processed_csv.exists():
        raise ProjectError(f"{rel(ds.processed_csv)} is missing. Run: python -m aab build --dataset {dataset_id}")
    return pd.read_csv(ds.processed_csv, dtype={"iso3": str, "indicator_code": str})
