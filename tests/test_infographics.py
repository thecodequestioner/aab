"""Checks that infographic output paths follow the project's naming convention."""
from pathlib import Path

from aab.infographics import Infographic


def test_infographic_png_and_svg_paths():
    info = Infographic(
        id="example",
        path=Path("infographics/example"),
        config={},
    )

    assert info.png() == Path(
        "infographics/example/outputs/infographic_en.png"
    )
    assert info.svg() == Path(
        "infographics/example/outputs/infographic_en.svg"
    )