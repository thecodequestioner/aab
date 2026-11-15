"""Builds the Afghanistan precipitation table from the manually downloaded CCKP/CRU file.

Reads   data/sources/cru-ts-precipitation/cckp_cru_pr_annual_AFG.json unchanged
        (legacy CSV/XLSX downloads are also recognized)
Returns the standard tidy table (see aab/tidy.py).

The layout of the download is detected, not hard-coded: the script looks for a header row
containing 'Year', an optional country column, and one value column. If it cannot decide,
it stops and says what it found.
"""
import csv
import json
import math
import re
import sys
from pathlib import Path

import pandas as pd

from aab import ProjectError
from aab.countries import load_registry

ISO3 = "AFG"
VALUE_HINTS = ("precip", "rain", "value", "mean", "sum", "mm")
FILE_NAMES = ("cckp_cru_pr_annual_AFG.json", "cckp_cru_pr_annual_AFG.csv", "cckp_cru_pr_annual_AFG.xlsx")


def find_file(raw_dir: Path) -> Path:
    for name in FILE_NAMES:
        path = raw_dir / name
        if path.exists():
            return path
    raise ProjectError(f"Raw file missing in {raw_dir}. See data/sources/cru-ts-precipitation/README.md.")


def read_raw(path: Path) -> pd.DataFrame:
    """Read the supplied CCKP JSON response or a legacy CSV/XLSX download."""
    if path.suffix.lower() == ".json":
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ProjectError(f"Could not read CCKP JSON response {path.name}: {exc}") from exc
        if payload.get("metadata", {}).get("status") != "success":
            raise ProjectError("CCKP JSON response metadata.status is not 'success'.")
        series = payload.get("data", {}).get(ISO3)
        if not isinstance(series, dict) or not series:
            raise ProjectError(f"CCKP JSON response has no annual series for {ISO3}.")
        rows = []
        for key, value in series.items():
            match = re.fullmatch(r"(\d{4})-07", str(key))
            if not match:
                raise ProjectError(f"Unexpected annual date key {key!r}; expected YYYY-07.")
            try:
                number = float(value)
            except (TypeError, ValueError) as exc:
                raise ProjectError(f"Non-numeric precipitation value for {key}: {value!r}.") from exc
            if not math.isfinite(number):
                raise ProjectError(f"Non-finite precipitation value for {key}.")
            rows.append({"Year": int(match.group(1)), "Precipitation (mm per year)": number})
        frame = pd.DataFrame(rows).sort_values("Year").reset_index(drop=True)
        if frame["Year"].duplicated().any():
            raise ProjectError("CCKP JSON response contains duplicate annual years.")
        if frame["Year"].tolist() != list(range(1901, 2026)):
            raise ProjectError("Expected one annual CCKP value for every year from 1901 through 2025.")
        return frame
    if path.suffix.lower() == ".xlsx":
        return pd.read_excel(path, header=None, dtype=object)
    with path.open(newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.reader(fh))
    width = max((len(r) for r in rows), default=0)
    return pd.DataFrame([r + [None] * (width - len(r)) for r in rows], dtype=object)


def locate_header(raw: pd.DataFrame) -> int:
    for i in range(min(60, len(raw))):
        cells = [str(c).strip().lower() for c in raw.iloc[i].tolist() if pd.notna(c)]
        if any(c.startswith("year") for c in cells):
            return i
    raise ProjectError("No header row containing 'Year' was found in the first 60 lines.")


def to_frame(raw: pd.DataFrame, header_row: int) -> pd.DataFrame:
    names = [str(c).strip() if pd.notna(c) else f"col{j}" for j, c in enumerate(raw.iloc[header_row])]
    body = raw.iloc[header_row + 1:].copy()
    body.columns = names
    return body.dropna(how="all")


def filter_country(body: pd.DataFrame) -> pd.DataFrame:
    for col in body.columns:
        low = col.lower()
        if "iso" in low or "country" in low:
            values = body[col].astype(str).str.strip()
            if values.nunique() > 1:
                return body[values.isin([ISO3, "AFG", "Afghanistan"])]
    return body


def find_value_column(body: pd.DataFrame, year_col: str) -> str:
    others = [c for c in body.columns if c != year_col and "iso" not in c.lower() and "country" not in c.lower()]
    named = [c for c in others if any(h in c.lower() for h in VALUE_HINTS)]
    numeric = [c for c in others if pd.to_numeric(body[c], errors="coerce").notna().mean() > 0.9]
    for pool in (named, numeric):
        if len(pool) == 1:
            return pool[0]
        if len(pool) > 1:
            raise ProjectError(f"Several possible value columns {pool}. Check the header line of the file.")
    raise ProjectError(f"No value column found. Columns are: {list(body.columns)}")


def build(dataset, sources) -> pd.DataFrame:
    cfg = dataset.config
    indicator = cfg["indicators"][0]
    source = sources[indicator["source"]]
    raw_path = find_file(source.raw_dir)
    raw = read_raw(raw_path)
    if raw_path.suffix.lower() == ".json":
        body = raw
    else:
        body = filter_country(to_frame(raw, locate_header(raw)))
    year_col = next(c for c in body.columns if c.lower().startswith("year"))
    value_col = find_value_column(body, year_col)

    years = pd.to_numeric(body[year_col], errors="coerce")
    if years.isna().all():
        years = pd.to_numeric(body[year_col].astype(str).str[:4], errors="coerce")
    values = pd.to_numeric(body[value_col], errors="coerce")

    df = pd.DataFrame({"year": years, "value": values}).dropna()
    df["year"] = df["year"].astype(int)
    y0, y1 = dataset.years
    df = df[(df["year"] >= y0) & (df["year"] <= y1)]
    if df.empty:
        raise ProjectError("No rows fall inside the configured years. Check coverage.years in dataset.yaml.")
    if df["year"].duplicated().any():
        raise ProjectError("The file has more than one value for some years. Check the download settings.")

    country = load_registry()[ISO3]
    return pd.DataFrame({
        "iso3": ISO3,
        "country_name": country["name"],
        "region": country["subregion"],
        "year": df["year"].to_numpy(),
        "indicator_code": indicator["code"],
        "indicator_name": indicator["name"],
        "value": df["value"].round(indicator.get("decimals", 1)).to_numpy(),
        "unit": indicator["unit"],
        "attribution": sources[indicator["source"]].config["attribution"],
    }).sort_values("year").reset_index(drop=True)
