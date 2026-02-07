"""Natural language feedback generation from stroke comparison metrics.

Translates numerical deviations into actionable practice advice.
"""

from __future__ import annotations

from rm_greg.feedback.comparison import StrokeComparison
from rm_greg.feedback.scoring import AttemptScore, score_attempt


def generate_feedback(
    comparison: StrokeComparison,
    label: str,
    score: AttemptScore | None = None,
) -> list[str]:
    """Generate natural language feedback for a practice attempt.

    Args:
        comparison: Detailed stroke comparison metrics.
        label: The Gregg primitive label (e.g., "a", "t", "r").
        score: Optional pre-computed score. Will be computed if not provided.

    Returns:
        List of feedback strings, most important first.
    """
    if score is None:
        score = score_attempt(comparison)

    feedback: list[str] = []

    # Overall assessment
    if score.overall_score >= 0.9:
        feedback.append(f"Your '{label}' stroke looks good.")
    elif score.overall_score >= 0.7:
        feedback.append(f"Your '{label}' is recognizable but could be improved.")
    else:
        feedback.append(f"Your '{label}' needs more practice. Here's what to focus on:")

    # Size feedback
    if comparison.size_ratio > 1.3:
        feedback.append(
            f"Your '{label}' is too large — try making it about "
            f"{comparison.size_ratio:.0%} smaller."
        )
    elif comparison.size_ratio < 0.7:
        feedback.append(
            f"Your '{label}' is too small — try making it about "
            f"{1 / comparison.size_ratio:.0%} larger."
        )

    # Angle feedback
    if comparison.angle_deviation > 0.3:
        feedback.append(
            "The starting angle is off — check the reference and "
            "try to match the entry direction."
        )

    # Curvature feedback
    if comparison.curvature_deviation > 0.5:
        if comparison.curvature_deviation > 0:
            feedback.append(
                "The curve should be smoother — try to maintain a consistent arc."
            )

    # Proportion feedback
    if comparison.proportion_error > 0.3:
        feedback.append(
            "The height-to-width ratio doesn't match the reference. "
            "Pay attention to the proportions."
        )

    # Shape feedback (DTW)
    if score.shape_score < 0.6:
        feedback.append(
            "The overall shape is quite different from the reference. "
            "Try tracing the reference stroke a few times first."
        )

    return feedback
