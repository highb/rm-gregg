"""Scoring rubric for Gregg shorthand practice attempts.

Assigns a structured score to a practice attempt based on
multiple quality dimensions.
"""

from __future__ import annotations

from dataclasses import dataclass

from rm_greg.feedback.comparison import StrokeComparison


@dataclass
class AttemptScore:
    """Scored result for a single glyph attempt."""

    shape_score: float  # 0-1, based on DTW/Frechet
    size_score: float  # 0-1, based on proportional accuracy
    angle_score: float  # 0-1, based on start/end angles
    smoothness_score: float  # 0-1, based on curvature consistency
    overall_score: float  # 0-1, weighted combination

    @property
    def grade(self) -> str:
        """Convert overall score to a letter grade."""
        if self.overall_score >= 0.9:
            return "A"
        if self.overall_score >= 0.8:
            return "B"
        if self.overall_score >= 0.7:
            return "C"
        if self.overall_score >= 0.6:
            return "D"
        return "F"


def score_attempt(comparison: StrokeComparison) -> AttemptScore:
    """Score a practice attempt based on its comparison to the reference.

    Args:
        comparison: StrokeComparison from comparing user stroke to reference.

    Returns:
        AttemptScore with individual and overall scores.
    """
    # Shape score: based on DTW distance (lower = better)
    # Normalize DTW to [0, 1] using a sigmoid-like function
    shape_score = max(0.0, 1.0 - comparison.dtw_distance * 2.0)

    # Size score: how close the size ratio is to 1.0
    size_score = max(0.0, 1.0 - abs(1.0 - comparison.size_ratio))

    # Angle score: based on angular deviation
    angle_score = max(0.0, 1.0 - comparison.angle_deviation / 1.0)

    # Smoothness: based on curvature deviation
    smoothness_score = max(0.0, 1.0 - comparison.curvature_deviation * 0.5)

    # Weighted overall (shape matters most for Gregg)
    overall_score = (
        0.40 * shape_score
        + 0.25 * size_score
        + 0.20 * angle_score
        + 0.15 * smoothness_score
    )

    return AttemptScore(
        shape_score=shape_score,
        size_score=size_score,
        angle_score=angle_score,
        smoothness_score=smoothness_score,
        overall_score=overall_score,
    )
