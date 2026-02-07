"""FastAPI application for the Gregg shorthand practice feedback API.

Provides endpoints for:
- Uploading .rm files for analysis
- Getting stroke classification results
- Getting practice feedback
- Generating practice sheet PDFs
"""

from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile

from pydantic import BaseModel, Field

try:
    from fastapi import FastAPI, HTTPException, UploadFile
except ImportError as e:
    raise ImportError(
        "FastAPI is required for the API server. Install with: pip install rm-gregg[api]"
    ) from e

from rm_greg.models import NormalizedStroke, NormalizedPoint

app = FastAPI(
    title="rm-gregg",
    description="Gregg Shorthand Practice Feedback API",
    version="0.1.0",
)


class StrokeInput(BaseModel):
    """A stroke submitted for classification or feedback."""

    points: list[dict[str, float]] = Field(
        description="List of points with x, y, pressure, etc."
    )
    label: str | None = Field(default=None, description="Expected label if known")


class ClassificationResult(BaseModel):
    """Result of classifying a stroke."""

    predicted_label: str
    confidence: float
    probabilities: dict[str, float]


class FeedbackResult(BaseModel):
    """Feedback for a practice attempt."""

    label: str
    score: float
    grade: str
    feedback: list[str]


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/api/v1/classify", response_model=ClassificationResult)
async def classify_stroke(stroke_input: StrokeInput) -> ClassificationResult:
    """Classify a single stroke as a Gregg shorthand primitive.

    Accepts a stroke as a list of points and returns the predicted
    Gregg primitive label with confidence scores.
    """
    # TODO: Load model and classify
    raise HTTPException(status_code=501, detail="Classification not yet implemented")


@app.post("/api/v1/feedback", response_model=FeedbackResult)
async def get_feedback(stroke_input: StrokeInput) -> FeedbackResult:
    """Get practice feedback for a stroke attempt.

    Compares the submitted stroke to the reference for the expected label
    and returns detailed feedback.
    """
    if stroke_input.label is None:
        raise HTTPException(
            status_code=400,
            detail="Label is required for feedback. Provide the expected Gregg primitive.",
        )

    # TODO: Load reference strokes and compare
    raise HTTPException(status_code=501, detail="Feedback not yet implemented")


@app.post("/api/v1/upload")
async def upload_rm_file(file: UploadFile) -> dict[str, str]:
    """Upload a .rm file for batch analysis.

    Extracts strokes from the uploaded file and queues them for
    classification and feedback.
    """
    if not file.filename or not file.filename.endswith(".rm"):
        raise HTTPException(status_code=400, detail="Only .rm files are accepted")

    # Save to temp file and process
    with NamedTemporaryFile(suffix=".rm", delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    # TODO: Process the uploaded file
    return {"status": "uploaded", "filename": file.filename, "path": str(tmp_path)}


@app.get("/api/v1/curriculum/{unit}")
async def get_unit_vocabulary(unit: int) -> dict[str, list[str]]:
    """Get the vocabulary (primitives and words) for a curriculum unit.

    Args:
        unit: The curriculum unit number (1-based).

    Returns:
        Dictionary with primitives and words for the unit.
    """
    # TODO: Load curriculum data
    if unit != 1:
        raise HTTPException(status_code=404, detail=f"Unit {unit} not yet available")

    return {
        "unit": [str(unit)],
        "primitives": ["a", "e", "o", "t", "d", "n", "m", "r", "l", "k", "g", "s", "p", "b"],
        "words": [],  # TODO: Add Unit 1 vocabulary
    }
