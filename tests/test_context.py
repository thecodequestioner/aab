"""Checks the rule that an analysis reads only the datasets it declares, including several at once."""
from pathlib import Path

import pytest

from aab import ProjectError
from aab.analyses import Analysis, Context
from aab.datasets import load_all as load_datasets


def _analysis(dataset_ids: list[str]) -> Analysis:
    config = {
        "id": "multi-dataset-check",
        "title": "Check: several declared datasets",
        "question": "Can a custom analysis read every dataset it declares?",
        "version": "0.1.0",
        "status": "draft",
        "themes": ["water-access"],
        "inputs": {"datasets": dataset_ids},
        "method": "custom",
    }
    return Analysis(id="multi-dataset-check", path=Path("analysis/multi-dataset-check"), config=config)


def test_custom_analysis_reads_every_declared_dataset():
    ids = ["drinking-water-access", "afghanistan-precipitation"]
    ctx = Context(_analysis(ids), load_datasets())
    for dataset_id in ids:
        table = ctx.read(dataset_id)
        assert len(table) > 0
        assert ctx.dataset_config(dataset_id)["id"] == dataset_id


def test_custom_analysis_cannot_read_an_undeclared_dataset():
    ctx = Context(_analysis(["afghanistan-precipitation"]), load_datasets())
    with pytest.raises(ProjectError):
        ctx.read("drinking-water-access")
