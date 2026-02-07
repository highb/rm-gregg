"""Feedback engine: compare user strokes to references and generate actionable feedback."""

from rm_greg.feedback.comparison import compare_strokes, StrokeComparison
from rm_greg.feedback.scoring import score_attempt
from rm_greg.feedback.generator import generate_feedback

__all__ = ["compare_strokes", "StrokeComparison", "score_attempt", "generate_feedback"]
