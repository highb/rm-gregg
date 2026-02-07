"""Tests for coordinate normalization."""

from __future__ import annotations

import numpy as np
import pytest

from rm_greg.models import NormalizedPoint, NormalizedStroke, PageData, Point, Stroke
from rm_greg.preprocessing.normalize import (
    RM_HEIGHT,
    RM_WIDTH,
    interpolate_stroke,
    normalize_point_coords,
    normalize_stroke,
    normalize_strokes,
    stroke_to_array,
)


class TestNormalizePointCoords:
    def test_origin(self) -> None:
        x, y = normalize_point_coords(0.0, 0.0)
        assert x == 0.0
        assert y == 0.0

    def test_max_coords(self) -> None:
        x, y = normalize_point_coords(RM_WIDTH, RM_HEIGHT)
        assert x == pytest.approx(1.0)
        assert y == pytest.approx(1.0)

    def test_midpoint(self) -> None:
        x, y = normalize_point_coords(RM_WIDTH / 2, RM_HEIGHT / 2)
        assert x == pytest.approx(0.5)
        assert y == pytest.approx(0.5)

    def test_clamps_above_max(self) -> None:
        x, y = normalize_point_coords(RM_WIDTH * 2, RM_HEIGHT * 2)
        assert x == 1.0
        assert y == 1.0

    def test_clamps_below_zero(self) -> None:
        x, y = normalize_point_coords(-100.0, -100.0)
        assert x == 0.0
        assert y == 0.0


class TestNormalizeStroke:
    def test_normalizes_all_points(self) -> None:
        stroke = Stroke(
            points=[
                Point(x=0.0, y=0.0, pressure=0.5),
                Point(x=RM_WIDTH, y=RM_HEIGHT, pressure=1.0),
            ]
        )
        result = normalize_stroke(stroke)
        assert len(result.points) == 2
        assert result.points[0].x == 0.0
        assert result.points[0].y == 0.0
        assert result.points[1].x == pytest.approx(1.0)
        assert result.points[1].y == pytest.approx(1.0)

    def test_preserves_pressure(self) -> None:
        stroke = Stroke(points=[Point(x=0.0, y=0.0, pressure=0.75)])
        result = normalize_stroke(stroke)
        assert result.points[0].pressure == 0.75


class TestStrokeToArray:
    def test_shape(self) -> None:
        stroke = NormalizedStroke(
            points=[
                NormalizedPoint(x=0.1, y=0.2, pressure=0.5),
                NormalizedPoint(x=0.3, y=0.4, pressure=0.6),
                NormalizedPoint(x=0.5, y=0.6, pressure=0.7),
            ]
        )
        arr = stroke_to_array(stroke)
        assert arr.shape == (3, 6)
        assert arr.dtype == np.float32

    def test_values(self) -> None:
        stroke = NormalizedStroke(
            points=[NormalizedPoint(x=0.1, y=0.2, pressure=0.5)]
        )
        arr = stroke_to_array(stroke)
        assert arr[0, 0] == pytest.approx(0.1)
        assert arr[0, 1] == pytest.approx(0.2)
        assert arr[0, 2] == pytest.approx(0.5)


class TestInterpolateStroke:
    def test_output_length(self) -> None:
        arr = np.random.rand(10, 6).astype(np.float32)
        result = interpolate_stroke(arr, target_length=32)
        assert result.shape == (32, 6)

    def test_identity_when_same_length(self) -> None:
        arr = np.random.rand(64, 6).astype(np.float32)
        result = interpolate_stroke(arr, target_length=64)
        np.testing.assert_array_equal(result, arr)

    def test_preserves_endpoints(self) -> None:
        arr = np.array(
            [[0.0, 0.0, 0.5, 0.0, 0.0, 0.0], [1.0, 1.0, 1.0, 0.0, 0.0, 0.0]],
            dtype=np.float32,
        )
        result = interpolate_stroke(arr, target_length=10)
        assert result[0, 0] == pytest.approx(0.0)
        assert result[-1, 0] == pytest.approx(1.0)
