"""Stroke segmentation: split page-level data into individual glyph attempts.

Segmentation strategies:
1. Gap-based: Split where there's a spatial gap between strokes (word boundaries)
2. Temporal: Use timing gaps between strokes (if timestamp data available)
3. Grid-based: If practice sheet has predefined grid zones, use those
"""

from __future__ import annotations

from rm_greg.models import NormalizedStroke


def segment_glyphs(
    strokes: list[NormalizedStroke],
    gap_threshold: float = 0.05,
) -> list[list[NormalizedStroke]]:
    """Segment a list of strokes into individual glyph attempts.

    Uses a gap-based heuristic: strokes that are spatially close together
    are grouped as a single glyph attempt.

    Args:
        strokes: List of normalized strokes from a page.
        gap_threshold: Minimum normalized distance between stroke groups
            to consider them separate glyphs. Default 0.05 (5% of page width).

    Returns:
        List of glyph groups, where each group is a list of strokes
        forming a single glyph attempt.
    """
    if not strokes:
        return []

    groups: list[list[NormalizedStroke]] = [[strokes[0]]]

    for stroke in strokes[1:]:
        if not stroke.points:
            continue

        prev_group = groups[-1]
        prev_stroke = prev_group[-1]

        if not prev_stroke.points:
            groups.append([stroke])
            continue

        # Calculate minimum distance between end of previous stroke
        # and start of current stroke
        prev_end = prev_stroke.points[-1]
        curr_start = stroke.points[0]

        dx = curr_start.x - prev_end.x
        dy = curr_start.y - prev_end.y
        distance = (dx**2 + dy**2) ** 0.5

        if distance > gap_threshold:
            groups.append([stroke])
        else:
            prev_group.append(stroke)

    return groups


def segment_by_grid(
    strokes: list[NormalizedStroke],
    rows: int = 4,
    cols: int = 4,
) -> dict[tuple[int, int], list[NormalizedStroke]]:
    """Segment strokes into a grid of cells.

    Useful when practice sheets have a predefined grid layout.

    Args:
        strokes: Normalized strokes from a page.
        rows: Number of grid rows.
        cols: Number of grid columns.

    Returns:
        Dictionary mapping (row, col) to strokes in that cell.
    """
    grid: dict[tuple[int, int], list[NormalizedStroke]] = {}

    row_height = 1.0 / rows
    col_width = 1.0 / cols

    for stroke in strokes:
        if not stroke.points:
            continue

        # Use the centroid of the stroke to assign it to a grid cell
        xs = [p.x for p in stroke.points]
        ys = [p.y for p in stroke.points]
        cx = sum(xs) / len(xs)
        cy = sum(ys) / len(ys)

        row = min(int(cy / row_height), rows - 1)
        col = min(int(cx / col_width), cols - 1)

        key = (row, col)
        if key not in grid:
            grid[key] = []
        grid[key].append(stroke)

    return grid
