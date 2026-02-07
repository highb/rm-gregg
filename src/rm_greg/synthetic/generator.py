"""Synthetic stroke generator for Gregg shorthand primitives.

Generates parameterized Gregg strokes with controlled variation for
training data bootstrapping. Each Gregg primitive is defined as a
geometric template (arc, line, circle, hook) with parameters that
can be varied to simulate natural handwriting variation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from rm_greg.models import GreggPrimitive, NormalizedPoint, NormalizedStroke
from rm_greg.training.dataset import StrokeDataset


@dataclass
class StrokeTemplate:
    """Parameterized template for a Gregg shorthand primitive."""

    primitive: GreggPrimitive
    generator_fn: str  # Name of the generator method
    base_params: dict[str, float]  # Default parameters


class SyntheticGenerator:
    """Generates synthetic training data for Gregg shorthand primitives.

    Each primitive is parameterized as a geometric shape (circle, line, arc)
    with controllable variation in size, position, angle, and noise.
    """

    def __init__(self, seed: int = 42) -> None:
        self.rng = np.random.default_rng(seed)

    def generate_dataset(
        self,
        primitives: list[GreggPrimitive] | None = None,
        samples_per_class: int = 100,
    ) -> StrokeDataset:
        """Generate a full dataset of synthetic strokes.

        Args:
            primitives: Which primitives to generate. Defaults to all.
            samples_per_class: Number of samples per primitive class.

        Returns:
            StrokeDataset with labeled synthetic strokes.
        """
        if primitives is None:
            primitives = list(GreggPrimitive)

        dataset = StrokeDataset()

        for primitive in primitives:
            for _ in range(samples_per_class):
                stroke = self._generate_primitive(primitive)
                dataset.add_sample(stroke, primitive.value)

        return dataset

    def _generate_primitive(self, primitive: GreggPrimitive) -> NormalizedStroke:
        """Generate a single synthetic stroke for a primitive."""
        generators = {
            GreggPrimitive.A: self._gen_small_circle,
            GreggPrimitive.E: self._gen_small_circle,
            GreggPrimitive.O: self._gen_large_circle,
            GreggPrimitive.T: lambda: self._gen_line(length=0.05),
            GreggPrimitive.D: lambda: self._gen_line(length=0.10),
            GreggPrimitive.N: lambda: self._gen_curve(length=0.05, curvature=0.3),
            GreggPrimitive.M: lambda: self._gen_curve(length=0.10, curvature=0.3),
            GreggPrimitive.R: lambda: self._gen_curve(length=0.05, curvature=0.6),
            GreggPrimitive.L: lambda: self._gen_curve(length=0.10, curvature=0.6),
            GreggPrimitive.K: lambda: self._gen_curve(length=0.05, curvature=-0.6),
            GreggPrimitive.G: lambda: self._gen_curve(length=0.10, curvature=-0.6),
            GreggPrimitive.S: self._gen_s_curve,
            GreggPrimitive.P: lambda: self._gen_line(length=0.05, angle=-0.5),
            GreggPrimitive.B: lambda: self._gen_line(length=0.10, angle=-0.5),
            GreggPrimitive.F: lambda: self._gen_curve(length=0.05, curvature=0.4),
            GreggPrimitive.V: lambda: self._gen_curve(length=0.10, curvature=0.4),
        }

        gen_fn = generators.get(primitive, self._gen_small_circle)
        return gen_fn()

    def _gen_small_circle(self) -> NormalizedStroke:
        """Generate a small circle (vowels a, e)."""
        return self._gen_circle(radius=0.015)

    def _gen_large_circle(self) -> NormalizedStroke:
        """Generate a large circle (vowel o)."""
        return self._gen_circle(radius=0.03)

    def _gen_circle(self, radius: float = 0.02) -> NormalizedStroke:
        """Generate a circle with controlled variation."""
        # Add variation
        radius *= 1.0 + self.rng.normal(0, 0.15)
        center_x = self.rng.uniform(0.2, 0.8)
        center_y = self.rng.uniform(0.2, 0.8)
        n_points = self.rng.integers(20, 40)

        angles = np.linspace(0, 2 * math.pi, n_points)
        # Add slight eccentricity
        eccentricity = 1.0 + self.rng.normal(0, 0.1)

        points = []
        for i, angle in enumerate(angles):
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * eccentricity * math.sin(angle)

            # Add jitter
            x += self.rng.normal(0, radius * 0.05)
            y += self.rng.normal(0, radius * 0.05)

            # Clamp to [0, 1]
            x = max(0.0, min(1.0, x))
            y = max(0.0, min(1.0, y))

            pressure = max(0.0, min(1.0, 0.5 + self.rng.normal(0, 0.1)))
            speed = max(0.0, abs(self.rng.normal(0.5, 0.15)))

            points.append(
                NormalizedPoint(
                    x=x,
                    y=y,
                    pressure=pressure,
                    speed=speed,
                    timestamp=float(i) / n_points,
                )
            )

        return NormalizedStroke(points=points)

    def _gen_line(
        self, length: float = 0.08, angle: float = 0.0
    ) -> NormalizedStroke:
        """Generate a straight line with variation."""
        length *= 1.0 + self.rng.normal(0, 0.15)
        angle += self.rng.normal(0, 0.1)

        start_x = self.rng.uniform(0.2, 0.6)
        start_y = self.rng.uniform(0.3, 0.7)
        n_points = self.rng.integers(15, 30)

        points = []
        for i in range(n_points):
            t = i / (n_points - 1)
            x = start_x + t * length * math.cos(angle)
            y = start_y + t * length * math.sin(angle)

            # Add jitter (less than circles)
            x += self.rng.normal(0, length * 0.02)
            y += self.rng.normal(0, length * 0.02)

            x = max(0.0, min(1.0, x))
            y = max(0.0, min(1.0, y))

            pressure = max(0.0, min(1.0, 0.5 + self.rng.normal(0, 0.1)))
            speed = max(0.0, abs(self.rng.normal(0.6, 0.1)))

            points.append(
                NormalizedPoint(
                    x=x,
                    y=y,
                    pressure=pressure,
                    speed=speed,
                    timestamp=t,
                )
            )

        return NormalizedStroke(points=points)

    def _gen_curve(
        self,
        length: float = 0.08,
        curvature: float = 0.5,
    ) -> NormalizedStroke:
        """Generate a curved stroke (arcs for r, l, k, g, n, m, etc.)."""
        length *= 1.0 + self.rng.normal(0, 0.15)
        curvature *= 1.0 + self.rng.normal(0, 0.2)

        start_x = self.rng.uniform(0.2, 0.6)
        start_y = self.rng.uniform(0.3, 0.7)
        base_angle = self.rng.normal(0, 0.15)
        n_points = self.rng.integers(20, 40)

        points = []
        for i in range(n_points):
            t = i / (n_points - 1)
            # Parametric curve: line + sinusoidal deviation
            x = start_x + t * length * math.cos(base_angle)
            y = start_y + t * length * math.sin(base_angle)

            # Add curvature (perpendicular displacement)
            perp_x = -math.sin(base_angle)
            perp_y = math.cos(base_angle)
            curve_amount = curvature * length * math.sin(math.pi * t)
            x += perp_x * curve_amount
            y += perp_y * curve_amount

            # Add jitter
            x += self.rng.normal(0, length * 0.02)
            y += self.rng.normal(0, length * 0.02)

            x = max(0.0, min(1.0, x))
            y = max(0.0, min(1.0, y))

            pressure = max(0.0, min(1.0, 0.5 + self.rng.normal(0, 0.1)))
            speed = max(0.0, abs(self.rng.normal(0.5, 0.15)))

            points.append(
                NormalizedPoint(
                    x=x,
                    y=y,
                    pressure=pressure,
                    speed=speed,
                    timestamp=t,
                )
            )

        return NormalizedStroke(points=points)

    def _gen_s_curve(self) -> NormalizedStroke:
        """Generate an S-shaped curve (for 's' primitive)."""
        length = 0.04 * (1.0 + self.rng.normal(0, 0.15))
        start_x = self.rng.uniform(0.3, 0.7)
        start_y = self.rng.uniform(0.3, 0.7)
        n_points = self.rng.integers(20, 35)

        points = []
        for i in range(n_points):
            t = i / (n_points - 1)
            x = start_x + t * length
            # S-curve: two half-sine waves
            y = start_y + length * 0.3 * math.sin(2 * math.pi * t)

            x += self.rng.normal(0, length * 0.03)
            y += self.rng.normal(0, length * 0.03)

            x = max(0.0, min(1.0, x))
            y = max(0.0, min(1.0, y))

            pressure = max(0.0, min(1.0, 0.5 + self.rng.normal(0, 0.1)))

            points.append(
                NormalizedPoint(
                    x=x,
                    y=y,
                    pressure=pressure,
                    timestamp=t,
                )
            )

        return NormalizedStroke(points=points)
