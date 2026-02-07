"""Tests for synthetic data generation."""

from __future__ import annotations

from rm_greg.models import GreggPrimitive
from rm_greg.synthetic.generator import SyntheticGenerator


class TestSyntheticGenerator:
    def test_generates_correct_count(self) -> None:
        gen = SyntheticGenerator(seed=42)
        dataset = gen.generate_dataset(
            primitives=[GreggPrimitive.A, GreggPrimitive.T],
            samples_per_class=10,
        )
        assert len(dataset) == 20

    def test_all_primitives(self) -> None:
        gen = SyntheticGenerator(seed=42)
        dataset = gen.generate_dataset(samples_per_class=5)
        assert len(dataset) == 5 * len(GreggPrimitive)

    def test_strokes_have_valid_coordinates(self) -> None:
        gen = SyntheticGenerator(seed=42)
        dataset = gen.generate_dataset(
            primitives=[GreggPrimitive.A],
            samples_per_class=10,
        )
        for stroke in dataset.strokes:
            for point in stroke.points:
                assert 0.0 <= point.x <= 1.0
                assert 0.0 <= point.y <= 1.0
                assert 0.0 <= point.pressure <= 1.0

    def test_deterministic_with_seed(self) -> None:
        gen1 = SyntheticGenerator(seed=123)
        gen2 = SyntheticGenerator(seed=123)

        ds1 = gen1.generate_dataset(
            primitives=[GreggPrimitive.T],
            samples_per_class=5,
        )
        ds2 = gen2.generate_dataset(
            primitives=[GreggPrimitive.T],
            samples_per_class=5,
        )

        for s1, s2 in zip(ds1.strokes, ds2.strokes):
            for p1, p2 in zip(s1.points, s2.points):
                assert p1.x == p2.x
                assert p1.y == p2.y

    def test_strokes_have_multiple_points(self) -> None:
        gen = SyntheticGenerator(seed=42)
        dataset = gen.generate_dataset(
            primitives=[GreggPrimitive.R],
            samples_per_class=5,
        )
        for stroke in dataset.strokes:
            assert len(stroke.points) >= 10
