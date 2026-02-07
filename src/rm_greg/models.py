"""Core data models for rm-greg.

Defines the Pydantic models used throughout the pipeline for representing
stroke data, points, and practice sessions.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class PenType(str, Enum):
    """reMarkable pen types."""

    BALLPOINT = "ballpoint"
    MARKER = "marker"
    FINELINER = "fineliner"
    PENCIL = "pencil"
    MECHANICAL_PENCIL = "mechanical_pencil"
    BRUSH = "brush"
    HIGHLIGHTER = "highlighter"
    ERASER = "eraser"
    CALLIGRAPHY = "calligraphy"


class StrokeColor(str, Enum):
    """reMarkable stroke colors."""

    BLACK = "black"
    GREY = "grey"
    WHITE = "white"


class Point(BaseModel):
    """A single point in a stroke, with all reMarkable sensor data."""

    x: float = Field(description="Horizontal coordinate (raw: 0-1404)")
    y: float = Field(description="Vertical coordinate (raw: 0-1872)")
    pressure: float = Field(default=0.0, ge=0.0, le=1.0, description="Pen pressure")
    tilt: float = Field(default=0.0, description="Stylus tilt angle in radians")
    speed: float = Field(default=0.0, description="Stylus velocity")
    direction: float = Field(default=0.0, description="Tangent angle in radians")
    width: float = Field(default=0.0, description="Effective brush width")
    timestamp: float = Field(default=0.0, description="Time offset from stroke start in seconds")


class Stroke(BaseModel):
    """A continuous pen-down sequence of points."""

    points: list[Point] = Field(default_factory=list)
    pen_type: PenType = Field(default=PenType.FINELINER)
    color: StrokeColor = Field(default=StrokeColor.BLACK)
    brush_size: float = Field(default=1.0, description="Base brush size")


class NormalizedPoint(BaseModel):
    """A point with coordinates normalized to [0, 1] range."""

    x: float = Field(ge=0.0, le=1.0)
    y: float = Field(ge=0.0, le=1.0)
    pressure: float = Field(default=0.0, ge=0.0, le=1.0)
    tilt: float = Field(default=0.0)
    speed: float = Field(default=0.0)
    direction: float = Field(default=0.0)
    timestamp: float = Field(default=0.0)


class NormalizedStroke(BaseModel):
    """A stroke with normalized coordinates."""

    points: list[NormalizedPoint] = Field(default_factory=list)
    label: str | None = Field(default=None, description="Gregg shorthand label if known")


class PageData(BaseModel):
    """All stroke data from a single reMarkable page."""

    page_id: str = Field(description="UUID of the page")
    strokes: list[Stroke] = Field(default_factory=list)
    layer: int = Field(default=0, description="Layer index (0-4)")


class PracticeSession(BaseModel):
    """A labeled practice session with metadata."""

    session_id: str
    unit: int = Field(description="Gregg curriculum unit number")
    lesson: int = Field(default=1, description="Lesson within the unit")
    target_words: list[str] = Field(
        default_factory=list,
        description="Expected words for this practice session",
    )
    pages: list[PageData] = Field(default_factory=list)


class GreggPrimitive(str, Enum):
    """Gregg shorthand stroke primitives (Unit 1)."""

    # Circles (vowels)
    A = "a"  # Small circle
    E = "e"  # Small circle (same as A, context-dependent)
    O = "o"  # Large circle (deep hook)

    # Straight lines
    T = "t"  # Short forward straight
    D = "d"  # Long forward straight
    N = "n"  # Short curved line
    M = "m"  # Long curved line

    # Curves
    R = "r"  # Short forward curve
    L = "l"  # Long forward curve
    K = "k"  # Short backward curve
    G = "g"  # Long backward curve

    # Special
    S = "s"  # Small comma-shaped curve
    P = "p"  # Short backward straight
    B = "b"  # Long backward straight
    F = "f"  # Short curved (left motion)
    V = "v"  # Long curved (left motion)
