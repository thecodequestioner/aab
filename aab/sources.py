"""Upstream sources: where raw data comes from, how it is fetched or checked, and how it is read.

A source is one provider's data, kept unchanged in data/sources/<id>/. Several datasets can
use the same source, so raw data is stored once, here, and never edited by hand.

Two access types are supported:
  worldbank  downloaded from the World Bank API (WDI indicators). Fetched by the pipeline.
  manual     a file that someone downloads by hand (for example from a portal that
             generates links per request). The pipeline checks and logs it.
"""
import json
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from . import ProjectError
from .config import SOURCES_DIR, discover, load_yaml, rel
from .countries import select
from .provenance import LOG_NAME, latest_checksum, log_download, log_existing_file, sha256_file

API = "https://api.worldbank.org/v2"
USER_AGENT = "aab/0.5 (open data pipeline; see repository)"
REQUIRED_KEYS = ["id", "title", "attribution", "url", "licence", "access"]
ACCESS_TYPES = {"worldbank", "manual"}


@dataclass
class Source:
    id: str
    path: Path
    config: dict

    @property
    def raw_dir(self) -> Path:
        """Raw files sit in the source folder itself, next to source.yaml and README.md."""
        return self.path

    @property
    def access_type(self) -> str:
        return self.config["access"]["type"]

    @property
    def known_issues(self) -> list[str]:
        return self.config.get("known_issues") or []

    def raw_files(self) -> list[Path]:
        """Raw data files, excluding the retrieval log."""
        if not self.raw_dir.exists():
            return []
        return sorted(p for p in self.raw_dir.iterdir()
                      if p.is_file() and p.name != LOG_NAME and p.suffix not in {".yaml", ".md"}
                      and not p.name.startswith("."))

    def worldbank_file(self, code: str) -> Path:
        return self.raw_dir / f"worldbank_{code}.json"


def load_source(path: Path) -> Source:
    descriptor = path / "source.yaml"
    config = load_yaml(descriptor)
    missing = [k for k in REQUIRED_KEYS if k not in config]
    if missing:
        raise ProjectError(f"{rel(descriptor)}: missing keys {missing}")
    if config["id"] != path.name:
        raise ProjectError(f"{rel(descriptor)}: id '{config['id']}' must equal the folder name '{path.name}'")
    access = config["access"]
    if access.get("type") not in ACCESS_TYPES:
        raise ProjectError(f"{rel(descriptor)}: access.type must be one of {sorted(ACCESS_TYPES)}")
    if access["type"] == "worldbank":
        for key in ("countries", "years", "indicators"):
            if not access.get(key):
                raise ProjectError(f"{rel(descriptor)}: worldbank access needs '{key}'")
    return Source(id=config["id"], path=path, config=config)


def load_all() -> dict[str, Source]:
    return {s.id: s for s in (load_source(p) for p in discover("source"))}


def get(sources: dict[str, Source], source_id: str) -> Source:
    if source_id not in sources:
        raise ProjectError(f"Unknown source '{source_id}'. Known sources: {sorted(sources)}")
    return sources[source_id]


def fetch(source: Source, refresh: bool = False) -> None:
    """Download (worldbank) or check (manual) the raw files for one source."""
    if source.access_type == "worldbank":
        _fetch_worldbank(source, refresh)
    else:
        _check_manual(source)


def _download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def _fetch_worldbank(source: Source, refresh: bool) -> None:
    access = source.config["access"]
    codes = [r["iso3"] for r in select(access["countries"])]
    years = access["years"]
    source.raw_dir.mkdir(parents=True, exist_ok=True)
    for ind in access["indicators"]:
        out = source.worldbank_file(ind["code"])
        if out.exists() and not refresh:
            print(f"  skip  {out.name} (exists; use --refresh to update)")
            continue
        url = (f"{API}/country/{';'.join(codes)}/indicator/{ind['code']}"
               f"?format=json&per_page=20000&date={years['start']}:{years['end']}")
        body = _download(url)
        payload = json.loads(body)
        if not isinstance(payload, list) or len(payload) < 2 or not payload[1]:
            raise ProjectError(f"{source.id}: unexpected API response for {ind['code']}: {str(payload)[:200]}")
        if int(payload[0].get("pages", 1)) > 1:
            raise ProjectError(f"{source.id}: {ind['code']} has several pages; pagination is not implemented")
        out.write_bytes(body)
        log_download(source.raw_dir, out.name, url, body)
        print(f"  saved {out.name} ({len(payload[1])} records)")


def _check_manual(source: Source) -> None:
    files = source.raw_files()
    if not files:
        raise ProjectError(f"{source.id}: no raw file in {rel(source.raw_dir)}. "
                           f"Follow the steps in data/sources/{source.id}/README.md.")
    for f in files:
        if latest_checksum(source.raw_dir, f.name) is None:
            log_existing_file(source.raw_dir, f, source.config["url"])
            print(f"  logged {f.name} (first time)")
        elif latest_checksum(source.raw_dir, f.name) == sha256_file(f):
            print(f"  checked {f.name} (matches log)")
        else:
            # Never re-log a changed file silently. The validator reports this.
            print(f"  WARNING {f.name} differs from its logged checksum; see the validator output")


def read_worldbank(source: Source, code: str) -> list[dict]:
    path = source.worldbank_file(code)
    if not path.exists():
        raise ProjectError(f"{rel(path)} is missing. Run: python -m aab build --refresh")
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload[1]
