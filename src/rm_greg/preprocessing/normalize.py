"""Coordinate normalization for reMarkable stroke data.

The reMarkable has a fixed coordinate space of 1404x1872 pixels.
This module normalizes coordinates to [0, 1] for ML consumption.
"""

from __future__ import annotations

import numpy as np

from rm_greg.models import (
    NormalizedPoint,
    NormalizedStroke,
    PageData,
    Stroke,
)

# reMarkable display dimensions in device coordinates
RM_WIDTH = 1404.0
RM_HEIGHT = 1872.0


def normalize_point_coords(x: float, y: float) -> tuple[float, float]:
    """Normalize raw reMarkable coordinates to [0, 1] range."""
    return (
        max(0.0, min(1.0, x / RM_WIDTH)),
        max(0.0, min(1.0, y / RM_HEIGHT)),
    )


def normalize_stroke(stroke: Stroke) -> NormalizedStroke:
    """Normalize a single stroke's coordinates to [0, 1] range.

    Args:
        stroke: Raw stroke with device coordinates.

    Returns:
        NormalizedStroke with coordinates in [0, 1].
    """
    normalized_points = []
    for pt in stroke.points:
        nx, ny = normalize_point_coords(pt.x, pt.y)
        normalized_points.append(
            NormalizedPoint(
                x=nx,
                y=ny,
                pressure=pt.pressure,
                tilt=pt.tilt,
                speed=pt.speed,
                direction=pt.direction,
                timestamp=pt.timestamp,
            )
        )
    return NormalizedStroke(points=normalized_points)


def normalize_strokes(page: PageData) -> list[NormalizedStroke]:
    """Normalize all strokes in a page.

    Args:
        page: Raw page data from the extractor.

    Returns:
        List of normalized strokes.
    """
    return [normalize_stroke(s) for s in page.strokes]


def stroke_to_array(stroke: NormalizedStroke) -> np.ndarray:
    """Convert a normalized stroke to a numpy array.

    Returns an array of shape (N, 6) where columns are:
    [x, y, pressure, tilt, speed, direction]
    """
    return np.array(
        [
            [p.x, p.y, p.pressure, p.tilt, p.speed, p.direction]
            for p in stroke.points
        ],
        dtype=np.float32,
    )


def interpolate_stroke(
    stroke_array: np.ndarray,
    target_length: int = 64,
) -> np.ndarray:
    """Resample a stroke to a fixed number of points via linear interpolation.

    This is useful for feeding strokes into fixed-length neural network inputs.

    Args:
        stroke_array: Array of shape (N, D) where N is variable length.
        target_length: Desired output length.

    Returns:
        Array of shape (target_length, D).
    """
    n_points, n_features = stroke_array.shape
    if n_points == target_length:
        return stroke_array

    old_indices = np.linspace(0, 1, n_points)
    new_indices = np.linspace(0, 1, target_length)

    result = np.zeros((target_length, n_features), dtype=np.float32)
    for col in range(n_features):
        result[:, col] = np.interp(new_indices, old_indices, stroke_array[:, col])

    return result
