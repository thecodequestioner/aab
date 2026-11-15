"""Country registry (ISO 3166-1 alpha-3) with project sub-regions and group tags.

A dataset selects countries by group tag, for example `countries.group: central_asia`.
To add a country or a group, edit aab/countries.csv only.
"""
import csv
from functools import lru_cache

from .config import PACKAGE_DIR
from . import ProjectError

REGISTRY_FILE = PACKAGE_DIR / "countries.csv"


@lru_cache(maxsize=None)
def load_registry() -> dict:
    with REGISTRY_FILE.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for row in rows:
        row["groups"] = [g for g in row["groups"].split(";") if g]
    return {row["iso3"]: row for row in rows}


def known_groups() -> list[str]:
    return sorted({g for row in load_registry().values() for g in row["groups"]})


def select(group: str) -> list[dict]:
    rows = [r for r in load_registry().values() if group in r["groups"]]
    if not rows:
        raise ProjectError(f"No countries in group '{group}'. Known groups: {known_groups()}")
    return sorted(rows, key=lambda r: (r["subregion"], r["name"]))
