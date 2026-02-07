"""Stroke-level classifier for Gregg shorthand primitives.

Supports two approaches:
1. Classical ML (Random Forest, SVM) on geometric features
2. Neural network (LSTM, 1D-CNN) on raw stroke sequences

Start with the classical approach for fast iteration, then move
to neural when you have more data.
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import numpy as np

from rm_greg.models import NormalizedStroke
from rm_greg.preprocessing.features import extract_geometric_features
from rm_greg.training.dataset import StrokeDataset


class StrokeClassifier:
    """Classifies individual Gregg shorthand strokes.

    Wraps scikit-learn models with a consistent interface for
    training, prediction, and serialization.
    """

    def __init__(self, model_type: str = "rf") -> None:
        """Initialize the classifier.

        Args:
            model_type: One of "rf" (Random Forest), "svm" (SVM).
        """
        self.model_type = model_type
        self.model: Any = None
        self.label_encoder: Any = None
        self._build_model()

    def _build_model(self) -> None:
        """Instantiate the underlying scikit-learn model."""
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.preprocessing import LabelEncoder
            from sklearn.svm import SVC
        except ImportError as e:
            raise ImportError(
                "scikit-learn is required for classical ML models. "
                "Install with: pip install rm-greg[ml]"
            ) from e

        self.label_encoder = LabelEncoder()

        if self.model_type == "rf":
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
            )
        elif self.model_type == "svm":
            self.model = SVC(
                kernel="rbf",
                probability=True,
                random_state=42,
            )
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")

    def train(self, dataset: StrokeDataset) -> dict[str, float]:
        """Train the classifier on a dataset.

        Args:
            dataset: StrokeDataset with labeled strokes.

        Returns:
            Dictionary of training metrics.
        """
        from sklearn.model_selection import cross_val_score

        X, y_str = dataset.get_feature_matrix()
        y = self.label_encoder.fit_transform(y_str)

        # Cross-validation score
        scores = cross_val_score(self.model, X, y, cv=min(5, len(set(y))), scoring="accuracy")

        # Final fit on all data
        self.model.fit(X, y)

        return {
            "cv_accuracy_mean": float(scores.mean()),
            "cv_accuracy_std": float(scores.std()),
            "n_samples": len(y),
            "n_classes": len(set(y)),
        }

    def predict(self, stroke: NormalizedStroke) -> str:
        """Predict the Gregg primitive label for a single stroke.

        Args:
            stroke: A normalized stroke to classify.

        Returns:
            Predicted label string.
        """
        features = extract_geometric_features(stroke)
        X = features.to_array().reshape(1, -1)
        y_pred = self.model.predict(X)
        return str(self.label_encoder.inverse_transform(y_pred)[0])

    def predict_proba(self, stroke: NormalizedStroke) -> dict[str, float]:
        """Predict class probabilities for a stroke.

        Args:
            stroke: A normalized stroke to classify.

        Returns:
            Dictionary mapping label names to probabilities.
        """
        features = extract_geometric_features(stroke)
        X = features.to_array().reshape(1, -1)
        probs = self.model.predict_proba(X)[0]
        labels = self.label_encoder.inverse_transform(range(len(probs)))
        return dict(zip(labels, probs.tolist()))

    def save(self, path: Path) -> None:
        """Save the trained model to disk."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(
                {
                    "model_type": self.model_type,
                    "model": self.model,
                    "label_encoder": self.label_encoder,
                },
                f,
            )

    @classmethod
    def load(cls, path: Path) -> StrokeClassifier:
        """Load a trained model from disk."""
        with open(path, "rb") as f:
            data = pickle.load(f)  # noqa: S301

        classifier = cls.__new__(cls)
        classifier.model_type = data["model_type"]
        classifier.model = data["model"]
        classifier.label_encoder = data["label_encoder"]
        return classifier
