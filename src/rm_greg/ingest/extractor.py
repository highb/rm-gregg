"""Extract stroke data from reMarkable .rm (v6) files using rmscene.

This module reads the binary .rm files produced by the reMarkable tablet
and converts them into our internal Stroke/Point data model.
"""

from __future__ import annotations

from pathlib import Path

from rm_greg.models import PageData, Point, Stroke, StrokeColor, PenType


def extract_page(rm_file: Path) -> PageData:
    """Extract all stroke data from a single .rm file.

    Args:
        rm_file: Path to a .rm binary file (v6 format).

    Returns:
        PageData containing all strokes and points from the page.

    Raises:
        FileNotFoundError: If the .rm file doesn't exist.
        ValueError: If the file format is not supported.
    """
    try:
        from rmscene import read_blocks, SceneLineItemBlock
    except ImportError as e:
        raise ImportError(
            "rmscene is required for .rm file extraction. "
            "Install it with: pip install rmscene"
        ) from e

    if not rm_file.exists():
        raise FileNotFoundError(f"File not found: {rm_file}")

    strokes: list[Stroke] = []

    with open(rm_file, "rb") as f:
        for block in read_blocks(f):
            if not isinstance(block, SceneLineItemBlock):
                continue

            item = block.item
            if item is None or item.value is None:
                continue

            line = item.value
            points: list[Point] = []
            for pt in line.points:
                points.append(
                    Point(
                        x=pt.x,
                        y=pt.y,
                        speed=pt.speed,
                        direction=pt.direction,
                        width=pt.width,
                        pressure=pt.pressure,
                        tilt=pt.tilt,
                    )
                )

            if points:
                strokes.append(
                    Stroke(
                        points=points,
                        color=_map_color(line.color),
                        brush_size=line.thickness_scale,
                    )
                )

    page_id = rm_file.stem
    return PageData(page_id=page_id, strokes=strokes)


def extract_notebook(notebook_dir: Path) -> list[PageData]:
    """Extract stroke data from all pages in a reMarkable notebook directory.

    Args:
        notebook_dir: Path to the notebook directory containing .rm files.

    Returns:
        List of PageData, one per page.
    """
    if not notebook_dir.is_dir():
        raise NotADirectoryError(f"Not a directory: {notebook_dir}")

    pages = []
    for rm_file in sorted(notebook_dir.glob("*.rm")):
        pages.append(extract_page(rm_file))
    return pages


def _map_color(color_value: int) -> StrokeColor:
    """Map rmscene color integer to our StrokeColor enum."""
    color_map = {
        0: StrokeColor.BLACK,
        1: StrokeColor.GREY,
        2: StrokeColor.WHITE,
    }
    return color_map.get(color_value, StrokeColor.BLACK)
