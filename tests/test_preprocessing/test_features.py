"""Tests for geometric feature extraction."""

from __future__ import annotations

import math

import numpy as np
import pytest

from rm_greg.models import NormalizedPoint, NormalizedStroke
from rm_greg.preprocessing.features import extract_geometric_features


def _make_line_stroke(
    x_start: float, y_start: float, x_end: float, y_end: float, n_points: int = 10
) -> NormalizedStroke:
    """Create a straight-line stroke."""
    points = []
    for i in range(n_points):
        t = i / (n_points - 1)
        points.append(
            NormalizedPoint(
                x=x_start + t * (x_end - x_start),
                y=y_start + t * (y_end - y_start),
                pressure=0.5,
            )
        )
    return NormalizedStroke(points=points)


class TestExtractGeometricFeatures:
    def test_rejects_single_point(self) -> None:
        stroke = NormalizedStroke(points=[NormalizedPoint(x=0.5, y=0.5)])
        with pytest.raises(ValueError, match="at least 2 points"):
            extract_geometric_features(stroke)

    def test_horizontal_line(self) -> None:
        stroke = _make_line_stroke(0.1, 0.5, 0.9, 0.5)
        features = extract_geometric_features(stroke)

        assert features.bbox_width == pytest.approx(0.8, abs=0.01)
        assert features.bbox_height == pytest.approx(0.0, abs=0.01)
        assert features.straightness == pytest.approx(1.0, abs=0.01)
        assert features.n_points == 10

    def test_vertical_line(self) -> None:
        stroke = _make_line_stroke(0.5, 0.1, 0.5, 0.9)
        features = extract_geometric_features(stroke)

        assert features.bbox_height == pytest.approx(0.8, abs=0.01)
        assert features.bbox_width == pytest.approx(0.0, abs=0.01)
        assert features.straightness == pytest.approx(1.0, abs=0.01)

    def test_diagonal_line_has_nonzero_angle(self) -> None:
        stroke = _make_line_stroke(0.1, 0.1, 0.9, 0.9)
        features = extract_geometric_features(stroke)

        assert features.start_angle == pytest.approx(math.pi / 4, abs=0.1)
        assert features.straightness == pytest.approx(1.0, abs=0.01)

    def test_feature_array_length(self) -> None:
        stroke = _make_line_stroke(0.1, 0.1, 0.9, 0.9)
        features = extract_geometric_features(stroke)
        arr = features.to_array()

        assert arr.shape == (15,)
        assert arr.dtype == np.float32
