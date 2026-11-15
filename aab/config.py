"""Paths, YAML loading and discovery. Every other module gets its paths from here."""
from pathlib import Path

import yaml

PACKAGE_DIR = Path(__file__).resolve().parent
ROOT = PACKAGE_DIR.parent
DATA_DIR = ROOT / "data"
SOURCES_DIR = DATA_DIR / "sources"
DATASETS_DIR = DATA_DIR / "datasets"
ANALYSES_DIR = ROOT / "analysis"
INFOGRAPHICS_DIR = ROOT / "infographics"
TEMPLATES_DIR = PACKAGE_DIR / "templates"

# Each kind of item is one folder per id, holding one descriptor file.
DESCRIPTORS = {
    "source": (SOURCES_DIR, "source.yaml"),
    "dataset": (DATASETS_DIR, "dataset.yaml"),
    "analysis": (ANALYSES_DIR, "analysis.yaml"),
    "infographic": (INFOGRAPHICS_DIR, "infographic.yaml"),
}


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_project() -> dict:
    return load_yaml(ROOT / "project.yaml")


def folder_for(kind: str) -> Path:
    return DESCRIPTORS[kind][0]


def discover(kind: str) -> list[Path]:
    """Return the folder of every item of this kind. Folders starting with '_' are templates and are skipped."""
    base, descriptor = DESCRIPTORS[kind]
    return sorted(p.parent for p in base.glob(f"*/{descriptor}")
                  if not p.parent.name.startswith("_"))


def rel(path: Path) -> str:
    """Repository-relative path with forward slashes, for messages and generated links."""
    return path.relative_to(ROOT).as_posix()
