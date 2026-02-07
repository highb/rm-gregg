"""Geometric feature extraction from strokes.

Extracts hand-crafted features for classical ML baselines (Random Forest, SVM).
These features capture the shape, size, and dynamics of Gregg shorthand strokes.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from rm_greg.models import NormalizedStroke
from rm_greg.preprocessing.normalize import stroke_to_array


@dataclass
class GeometricFeatures:
    """Hand-crafted geometric features for a single stroke."""

    # Bounding box
    bbox_width: float
    bbox_height: float
    bbox_aspect_ratio: float

    # Arc/path properties
    total_arc_length: float
    direct_distance: float  # Start to end, straight line
    straightness: float  # direct_distance / total_arc_length

    # Angular properties
    start_angle: float  # Angle of first segment
    end_angle: float  # Angle of last segment
    total_angle_change: float  # Sum of absolute angle changes
    mean_curvature: float

    # Size relative features
    stroke_height_ratio: float  # height / width
    n_points: int

    # Pressure/dynamics (if available)
    mean_pressure: float
    std_pressure: float
    mean_speed: float

    def to_array(self) -> np.ndarray:
        """Convert to a flat numpy array for ML input."""
        return np.array(
            [
                self.bbox_width,
                self.bbox_height,
                self.bbox_aspect_ratio,
                self.total_arc_length,
                self.direct_distance,
                self.straightness,
                self.start_angle,
                self.end_angle,
                self.total_angle_change,
                self.mean_curvature,
                self.stroke_height_ratio,
                self.n_points,
                self.mean_pressure,
                self.std_pressure,
                self.mean_speed,
            ],
            dtype=np.float32,
        )


def extract_geometric_features(stroke: NormalizedStroke) -> GeometricFeatures:
    """Extract geometric features from a normalized stroke.

    Args:
        stroke: A normalized stroke with points in [0, 1] coordinate space.

    Returns:
        GeometricFeatures dataclass with all computed features.

    Raises:
        ValueError: If the stroke has fewer than 2 points.
    """
    if len(stroke.points) < 2:
        raise ValueError("Stroke must have at least 2 points for feature extraction")

    arr = stroke_to_array(stroke)
    xy = arr[:, :2]  # x, y columns
    pressures = arr[:, 2]
    speeds = arr[:, 4]

    # Bounding box
    mins = xy.min(axis=0)
    maxs = xy.max(axis=0)
    bbox_width = maxs[0] - mins[0]
    bbox_height = maxs[1] - mins[1]
    bbox_aspect_ratio = bbox_width / bbox_height if bbox_height > 1e-8 else 0.0

    # Arc length (sum of segment lengths)
    diffs = np.diff(xy, axis=0)
    segment_lengths = np.linalg.norm(diffs, axis=1)
    total_arc_length = float(segment_lengths.sum())

    # Direct distance (start to end)
    direct_distance = float(np.linalg.norm(xy[-1] - xy[0]))
    straightness = direct_distance / total_arc_length if total_arc_length > 1e-8 else 1.0

    # Angles
    angles = np.arctan2(diffs[:, 1], diffs[:, 0])
    start_angle = float(angles[0])
    end_angle = float(angles[-1])

    # Angle changes (curvature proxy)
    angle_diffs = np.diff(angles)
    # Wrap to [-pi, pi]
    angle_diffs = (angle_diffs + np.pi) % (2 * np.pi) - np.pi
    total_angle_change = float(np.abs(angle_diffs).sum())
    mean_curvature = float(np.abs(angle_diffs).mean()) if len(angle_diffs) > 0 else 0.0

    # Height/width ratio
    stroke_height_ratio = bbox_height / bbox_width if bbox_width > 1e-8 else 0.0

    return GeometricFeatures(
        bbox_width=bbox_width,
        bbox_height=bbox_height,
        bbox_aspect_ratio=bbox_aspect_ratio,
        total_arc_length=total_arc_length,
        direct_distance=direct_distance,
        straightness=straightness,
        start_angle=start_angle,
        end_angle=end_angle,
        total_angle_change=total_angle_change,
        mean_curvature=mean_curvature,
        stroke_height_ratio=stroke_height_ratio,
        n_points=len(stroke.points),
        mean_pressure=float(pressures.mean()),
        std_pressure=float(pressures.std()),
        mean_speed=float(speeds.mean()),
    )
