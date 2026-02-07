"""Stroke comparison using DTW and geometric metrics.

Compares a user's stroke attempt to a reference stroke and
identifies specific deviations.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from rm_greg.models import NormalizedStroke
from rm_greg.preprocessing.normalize import stroke_to_array


@dataclass
class StrokeComparison:
    """Results of comparing a user stroke to a reference."""

    dtw_distance: float
    frechet_distance: float
    size_ratio: float  # user_size / reference_size
    curvature_deviation: float  # Difference in total curvature
    angle_deviation: float  # Difference in start/end angles
    proportion_error: float  # How far off the height/width ratio is

    @property
    def overall_similarity(self) -> float:
        """Compute an overall similarity score in [0, 1].

        Higher is better (more similar to reference).
        """
        # Weighted combination of normalized metrics
        # These weights can be tuned based on what matters most for Gregg
        dtw_score = max(0.0, 1.0 - self.dtw_distance)
        size_score = max(0.0, 1.0 - abs(1.0 - self.size_ratio))
        curve_score = max(0.0, 1.0 - self.curvature_deviation)
        angle_score = max(0.0, 1.0 - self.angle_deviation / np.pi)

        return 0.4 * dtw_score + 0.2 * size_score + 0.2 * curve_score + 0.2 * angle_score


def compare_strokes(
    user_stroke: NormalizedStroke,
    reference_stroke: NormalizedStroke,
) -> StrokeComparison:
    """Compare a user's stroke attempt to a reference stroke.

    Args:
        user_stroke: The user's stroke attempt.
        reference_stroke: The canonical reference stroke.

    Returns:
        StrokeComparison with detailed deviation metrics.
    """
    user_arr = stroke_to_array(user_stroke)[:, :2]  # x, y only
    ref_arr = stroke_to_array(reference_stroke)[:, :2]

    dtw_dist = _compute_dtw(user_arr, ref_arr)
    frechet_dist = _compute_frechet(user_arr, ref_arr)
    size_ratio = _compute_size_ratio(user_arr, ref_arr)
    curvature_dev = _compute_curvature_deviation(user_arr, ref_arr)
    angle_dev = _compute_angle_deviation(user_arr, ref_arr)
    proportion_err = _compute_proportion_error(user_arr, ref_arr)

    return StrokeComparison(
        dtw_distance=dtw_dist,
        frechet_distance=frechet_dist,
        size_ratio=size_ratio,
        curvature_deviation=curvature_dev,
        angle_deviation=angle_dev,
        proportion_error=proportion_err,
    )


def _compute_dtw(seq1: np.ndarray, seq2: np.ndarray) -> float:
    """Compute Dynamic Time Warping distance between two point sequences.

    Falls back to a simple numpy implementation if dtaidistance is not installed.
    """
    try:
        from dtaidistance import dtw

        # dtaidistance expects 1D sequences, so compute on x and y separately
        # and combine
        dist_x = dtw.distance(seq1[:, 0].astype(np.double), seq2[:, 0].astype(np.double))
        dist_y = dtw.distance(seq1[:, 1].astype(np.double), seq2[:, 1].astype(np.double))
        return float((dist_x**2 + dist_y**2) ** 0.5)
    except ImportError:
        return _simple_dtw(seq1, seq2)


def _simple_dtw(seq1: np.ndarray, seq2: np.ndarray) -> float:
    """Simple DTW implementation using numpy (no external dependencies)."""
    n, m = len(seq1), len(seq2)
    cost = np.full((n + 1, m + 1), np.inf)
    cost[0, 0] = 0.0

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            d = float(np.linalg.norm(seq1[i - 1] - seq2[j - 1]))
            cost[i, j] = d + min(cost[i - 1, j], cost[i, j - 1], cost[i - 1, j - 1])

    return float(cost[n, m])


def _compute_frechet(seq1: np.ndarray, seq2: np.ndarray) -> float:
    """Compute discrete Fréchet distance between two curves."""
    n, m = len(seq1), len(seq2)
    ca = np.full((n, m), -1.0)

    def _recurse(i: int, j: int) -> float:
        if ca[i, j] > -0.5:
            return ca[i, j]

        d = float(np.linalg.norm(seq1[i] - seq2[j]))

        if i == 0 and j == 0:
            ca[i, j] = d
        elif i > 0 and j == 0:
            ca[i, j] = max(_recurse(i - 1, 0), d)
        elif i == 0 and j > 0:
            ca[i, j] = max(_recurse(0, j - 1), d)
        else:
            ca[i, j] = max(
                min(_recurse(i - 1, j), _recurse(i - 1, j - 1), _recurse(i, j - 1)),
                d,
            )
        return ca[i, j]

    return _recurse(n - 1, m - 1)


def _compute_size_ratio(user: np.ndarray, ref: np.ndarray) -> float:
    """Compute the ratio of user stroke size to reference size."""
    user_size = np.linalg.norm(user.max(axis=0) - user.min(axis=0))
    ref_size = np.linalg.norm(ref.max(axis=0) - ref.min(axis=0))
    if ref_size < 1e-8:
        return 1.0
    return float(user_size / ref_size)


def _compute_curvature_deviation(user: np.ndarray, ref: np.ndarray) -> float:
    """Compute difference in total curvature between two strokes."""

    def total_curvature(pts: np.ndarray) -> float:
        if len(pts) < 3:
            return 0.0
        diffs = np.diff(pts, axis=0)
        angles = np.arctan2(diffs[:, 1], diffs[:, 0])
        angle_changes = np.diff(angles)
        angle_changes = (angle_changes + np.pi) % (2 * np.pi) - np.pi
        return float(np.abs(angle_changes).sum())

    return abs(total_curvature(user) - total_curvature(ref))


def _compute_angle_deviation(user: np.ndarray, ref: np.ndarray) -> float:
    """Compute difference in start/end angles."""

    def get_angles(pts: np.ndarray) -> tuple[float, float]:
        if len(pts) < 2:
            return 0.0, 0.0
        start = np.arctan2(pts[1, 1] - pts[0, 1], pts[1, 0] - pts[0, 0])
        end = np.arctan2(pts[-1, 1] - pts[-2, 1], pts[-1, 0] - pts[-2, 0])
        return float(start), float(end)

    u_start, u_end = get_angles(user)
    r_start, r_end = get_angles(ref)

    start_dev = abs((u_start - r_start + np.pi) % (2 * np.pi) - np.pi)
    end_dev = abs((u_end - r_end + np.pi) % (2 * np.pi) - np.pi)

    return (start_dev + end_dev) / 2


def _compute_proportion_error(user: np.ndarray, ref: np.ndarray) -> float:
    """Compute difference in height/width ratios."""

    def aspect_ratio(pts: np.ndarray) -> float:
        extents = pts.max(axis=0) - pts.min(axis=0)
        if extents[0] < 1e-8:
            return 0.0
        return float(extents[1] / extents[0])

    return abs(aspect_ratio(user) - aspect_ratio(ref))
