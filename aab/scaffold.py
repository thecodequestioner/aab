"""Creates a new source, dataset, analysis or infographic from the templates in aab/templates/."""
import re
import shutil

from . import ProjectError
from .config import DESCRIPTORS, TEMPLATES_DIR, folder_for, rel

KINDS = sorted(DESCRIPTORS)
TEXT_SUFFIXES = {".yaml", ".yml", ".md", ".py"}


def new(kind: str, slug: str) -> str:
    if kind not in DESCRIPTORS:
        raise ProjectError(f"kind must be one of {KINDS}")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
        raise ProjectError("slug must be lowercase letters and digits joined by hyphens, e.g. sanitation-access")
    template = TEMPLATES_DIR / kind
    target = folder_for(kind) / slug
    if target.exists():
        raise ProjectError(f"{rel(target)} already exists")
    shutil.copytree(template, target)
    for f in target.rglob("*"):
        if f.is_file() and f.suffix in TEXT_SUFFIXES:
            f.write_text(f.read_text(encoding="utf-8").replace("TEMPLATE_ID", slug), encoding="utf-8")
    return rel(target)
