"""Tests for the StrokeDataset class."""

from __future__ import annotations

from pathlib import Path

from rm_greg.models import NormalizedPoint, NormalizedStroke
from rm_greg.training.dataset import StrokeDataset


def _make_sample_stroke() -> NormalizedStroke:
    """Create a simple test stroke."""
    return NormalizedStroke(
        points=[
            NormalizedPoint(x=0.1, y=0.1, pressure=0.5),
            NormalizedPoint(x=0.2, y=0.2, pressure=0.6),
            NormalizedPoint(x=0.3, y=0.3, pressure=0.7),
        ]
    )


class TestStrokeDataset:
    def test_add_and_len(self) -> None:
        ds = StrokeDataset()
        assert len(ds) == 0
        ds.add_sample(_make_sample_stroke(), "a")
        assert len(ds) == 1

    def test_get_feature_matrix_shape(self) -> None:
        ds = StrokeDataset()
        for _ in range(5):
            ds.add_sample(_make_sample_stroke(), "a")
        for _ in range(5):
            ds.add_sample(_make_sample_stroke(), "t")

        X, y = ds.get_feature_matrix()
        assert X.shape[0] == 10
        assert X.shape[1] == 15  # Number of geometric features
        assert y.shape == (10,)

    def test_get_sequence_arrays_shape(self) -> None:
        ds = StrokeDataset()
        for _ in range(3):
            ds.add_sample(_make_sample_stroke(), "a")

        X, y = ds.get_sequence_arrays(target_length=32)
        assert X.shape == (3, 32, 6)
        assert y.shape == (3,)

    def test_save_and_load(self, tmp_path: Path) -> None:
        ds = StrokeDataset()
        ds.add_sample(_make_sample_stroke(), "a")
        ds.add_sample(_make_sample_stroke(), "t")

        save_path = tmp_path / "test_dataset.json"
        ds.save(save_path)

        loaded = StrokeDataset.load(save_path)
        assert len(loaded) == 2
        assert loaded.labels == ["a", "t"]
