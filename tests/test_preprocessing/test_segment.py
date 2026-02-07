"""Tests for stroke segmentation."""

from __future__ import annotations

from rm_greg.models import NormalizedPoint, NormalizedStroke
from rm_greg.preprocessing.segment import segment_by_grid, segment_glyphs


def _make_stroke(x_start: float, y_start: float, x_end: float, y_end: float) -> NormalizedStroke:
    """Helper to create a simple two-point stroke."""
    return NormalizedStroke(
        points=[
            NormalizedPoint(x=x_start, y=y_start),
            NormalizedPoint(x=x_end, y=y_end),
        ]
    )


class TestSegmentGlyphs:
    def test_empty_input(self) -> None:
        assert segment_glyphs([]) == []

    def test_single_stroke(self) -> None:
        stroke = _make_stroke(0.1, 0.1, 0.2, 0.2)
        result = segment_glyphs([stroke])
        assert len(result) == 1
        assert len(result[0]) == 1

    def test_close_strokes_grouped(self) -> None:
        s1 = _make_stroke(0.1, 0.1, 0.12, 0.12)
        s2 = _make_stroke(0.13, 0.13, 0.15, 0.15)
        result = segment_glyphs([s1, s2], gap_threshold=0.05)
        assert len(result) == 1
        assert len(result[0]) == 2

    def test_distant_strokes_separated(self) -> None:
        s1 = _make_stroke(0.1, 0.1, 0.12, 0.12)
        s2 = _make_stroke(0.5, 0.5, 0.52, 0.52)
        result = segment_glyphs([s1, s2], gap_threshold=0.05)
        assert len(result) == 2


class TestSegmentByGrid:
    def test_empty_input(self) -> None:
        result = segment_by_grid([], rows=2, cols=2)
        assert result == {}

    def test_assigns_to_correct_cell(self) -> None:
        # Stroke centered in top-left quadrant
        stroke = _make_stroke(0.1, 0.1, 0.2, 0.2)
        result = segment_by_grid([stroke], rows=2, cols=2)
        assert (0, 0) in result
        assert len(result[(0, 0)]) == 1
