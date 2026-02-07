"""Training module: stroke classifiers and word recognizers."""

from rm_greg.training.stroke_classifier import StrokeClassifier
from rm_greg.training.dataset import StrokeDataset

__all__ = ["StrokeClassifier", "StrokeDataset"]
