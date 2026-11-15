"""Infographics: communication products built from datasets and analyses.

Each infographic has infographic.yaml (question, headline, audience, alt text, inputs)
and make.py, which draws outputs/infographic_<lang>.png. The claim in infographic.yaml is
checked against the analysis summary by that make.py, so the picture cannot state a result the
analysis does not show. The generic pipeline does not yet read the claim field itself.
"""
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from . import ProjectError
from .config import ANALYSES_DIR, ROOT, discover, load_yaml, rel

REQUIRED_KEYS = ["id", "title", "question", "headline", "version", "status", "themes",
                 "audience", "languages", "alt_text", "inputs"]


@dataclass
class Infographic:
    id: str
    path: Path
    config: dict

    @property
    def analyses(self) -> list[str]:
        return list(self.config["inputs"].get("analyses") or [])

    @property
    def datasets(self) -> list[str]:
        return list(self.config["inputs"].get("datasets") or [])

    @property
    def outputs(self) -> Path:
        return self.path / "outputs"

    @property
    def make_script(self) -> Path:
        return self.path / "make.py"

    @property
    def notes(self) -> Path:
        return self.path / "README.md"

    def png(self, lang: str = "en") -> Path:
        return self.outputs / f"infographic_{lang}.png"


def load_infographic(path: Path) -> Infographic:
    descriptor = path / "infographic.yaml"
    config = load_yaml(descriptor)
    missing = [k for k in REQUIRED_KEYS if k not in config]
    if missing:
        raise ProjectError(f"{rel(descriptor)}: missing keys {missing}")
    if config["id"] != path.name:
        raise ProjectError(f"{rel(descriptor)}: id '{config['id']}' must equal the folder name '{path.name}'")
    if not (config["inputs"].get("analyses") or config["inputs"].get("datasets")):
        raise ProjectError(f"{rel(descriptor)}: inputs must list at least one analysis or dataset")
    return Infographic(id=config["id"], path=path, config=config)


def load_all() -> dict[str, Infographic]:
    return {i.id: i for i in (load_infographic(p) for p in discover("infographic"))}


def read_summary(analysis_id: str) -> dict:
    """The machine-readable result of an analysis, for infographics to check their claims against."""
    path = ANALYSES_DIR / analysis_id / "outputs" / "summary.json"
    if not path.exists():
        raise ProjectError(f"{rel(path)} is missing. Build the analysis first.")
    return json.loads(path.read_text(encoding="utf-8"))


def run(infographic: Infographic) -> None:
    """Run make.py from the repository root, with aab importable."""
    if not infographic.make_script.exists():
        raise ProjectError(f"{rel(infographic.path)}: make.py is missing")
    infographic.outputs.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [str(ROOT), env.get("PYTHONPATH", "")]))
    result = subprocess.run([sys.executable, str(infographic.make_script)], cwd=ROOT, env=env)
    if result.returncode != 0:
        raise ProjectError(f"{infographic.id}: make.py failed (see messages above)")
