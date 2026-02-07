"""Dataset management for training stroke classifiers.

Handles loading, splitting, and batching of stroke data for both
classical ML and neural network training.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from rm_greg.models import GreggPrimitive, NormalizedPoint, NormalizedStroke
from rm_greg.preprocessing.features import GeometricFeatures, extract_geometric_features
from rm_greg.preprocessing.normalize import interpolate_stroke, stroke_to_array


class StrokeDataset:
    """A dataset of labeled strokes for training.

    Stores strokes with their labels and provides methods to convert
    to numpy arrays suitable for scikit-learn or PyTorch.
    """

    def __init__(self) -> None:
        self.strokes: list[NormalizedStroke] = []
        self.labels: list[str] = []

    def add_sample(self, stroke: NormalizedStroke, label: str) -> None:
        """Add a labeled stroke to the dataset."""
        self.strokes.append(stroke)
        self.labels.append(label)

    def __len__(self) -> int:
        return len(self.strokes)

    def get_feature_matrix(self) -> tuple[np.ndarray, np.ndarray]:
        """Extract geometric features for all strokes.

        Returns:
            Tuple of (X, y) where X is (n_samples, n_features) and
            y is (n_samples,) of string labels.
        """
        features = []
        valid_labels = []

        for stroke, label in zip(self.strokes, self.labels):
            if len(stroke.points) < 2:
                continue
            feat = extract_geometric_features(stroke)
            features.append(feat.to_array())
            valid_labels.append(label)

        return np.stack(features), np.array(valid_labels)

    def get_sequence_arrays(
        self, target_length: int = 64
    ) -> tuple[np.ndarray, np.ndarray]:
        """Get interpolated stroke sequences for neural network input.

        Args:
            target_length: Fixed sequence length for all strokes.

        Returns:
            Tuple of (X, y) where X is (n_samples, target_length, n_features)
            and y is (n_samples,) of string labels.
        """
        sequences = []
        valid_labels = []

        for stroke, label in zip(self.strokes, self.labels):
            if len(stroke.points) < 2:
                continue
            arr = stroke_to_array(stroke)
            interp = interpolate_stroke(arr, target_length)
            sequences.append(interp)
            valid_labels.append(label)

        return np.stack(sequences), np.array(valid_labels)

    def save(self, path: Path) -> None:
        """Save dataset to JSON."""
        data = {
            "samples": [
                {
                    "label": label,
                    "points": [p.model_dump() for p in stroke.points],
                }
                for stroke, label in zip(self.strokes, self.labels)
            ]
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, path: Path) -> StrokeDataset:
        """Load dataset from JSON."""
        with open(path) as f:
            data = json.load(f)

        dataset = cls()
        for sample in data["samples"]:
            points = [NormalizedPoint(**p) for p in sample["points"]]
            stroke = NormalizedStroke(points=points, label=sample["label"])
            dataset.add_sample(stroke, sample["label"])

        return dataset
