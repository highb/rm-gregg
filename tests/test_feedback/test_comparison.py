"""Tests for stroke comparison metrics."""

from __future__ import annotations

import pytest

from rm_greg.models import NormalizedPoint, NormalizedStroke
from rm_greg.feedback.comparison import compare_strokes, StrokeComparison


def _make_line(
    x_start: float, y_start: float, x_end: float, y_end: float, n: int = 10
) -> NormalizedStroke:
    points = []
    for i in range(n):
        t = i / (n - 1)
        points.append(
            NormalizedPoint(
                x=x_start + t * (x_end - x_start),
                y=y_start + t * (y_end - y_start),
            )
        )
    return NormalizedStroke(points=points)


class TestCompareStrokes:
    def test_identical_strokes_have_zero_distance(self) -> None:
        stroke = _make_line(0.1, 0.1, 0.5, 0.5)
        result = compare_strokes(stroke, stroke)

        assert result.dtw_distance == pytest.approx(0.0, abs=0.01)
        assert result.size_ratio == pytest.approx(1.0, abs=0.01)
        assert result.curvature_deviation == pytest.approx(0.0, abs=0.01)

    def test_different_size_strokes(self) -> None:
        small = _make_line(0.4, 0.4, 0.5, 0.5)
        large = _make_line(0.1, 0.1, 0.9, 0.9)
        result = compare_strokes(small, large)

        assert result.size_ratio < 1.0  # small / large < 1

    def test_overall_similarity_in_range(self) -> None:
        s1 = _make_line(0.1, 0.1, 0.5, 0.5)
        s2 = _make_line(0.1, 0.1, 0.6, 0.6)
        result = compare_strokes(s1, s2)

        assert 0.0 <= result.overall_similarity <= 1.0
