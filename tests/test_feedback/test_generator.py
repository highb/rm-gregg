"""Tests for feedback generation."""

from __future__ import annotations

from rm_greg.feedback.comparison import StrokeComparison
from rm_greg.feedback.generator import generate_feedback
from rm_greg.feedback.scoring import AttemptScore, score_attempt


class TestGenerateFeedback:
    def test_good_attempt_gets_positive_feedback(self) -> None:
        comparison = StrokeComparison(
            dtw_distance=0.01,
            frechet_distance=0.01,
            size_ratio=1.0,
            curvature_deviation=0.05,
            angle_deviation=0.05,
            proportion_error=0.05,
        )
        feedback = generate_feedback(comparison, label="a")
        assert len(feedback) >= 1
        assert "good" in feedback[0].lower() or "recognizable" in feedback[0].lower()

    def test_oversized_stroke_gets_size_feedback(self) -> None:
        comparison = StrokeComparison(
            dtw_distance=0.1,
            frechet_distance=0.1,
            size_ratio=1.5,
            curvature_deviation=0.1,
            angle_deviation=0.1,
            proportion_error=0.1,
        )
        feedback = generate_feedback(comparison, label="a")
        size_feedback = [f for f in feedback if "large" in f.lower() or "smaller" in f.lower()]
        assert len(size_feedback) > 0

    def test_poor_attempt_gets_multiple_feedback(self) -> None:
        comparison = StrokeComparison(
            dtw_distance=0.8,
            frechet_distance=0.8,
            size_ratio=2.0,
            curvature_deviation=1.5,
            angle_deviation=1.0,
            proportion_error=1.0,
        )
        feedback = generate_feedback(comparison, label="t")
        assert len(feedback) >= 3  # Should have multiple pieces of advice
