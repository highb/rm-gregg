# rm-greg

A Gregg Shorthand learning system powered by reMarkable tablet stroke data and ML.

## Overview

rm-greg extracts rich stroke data from reMarkable tablets and uses it to build a curriculum-aware Gregg shorthand practice system with AI-powered feedback. Unlike raster-based approaches, it leverages the tablet's online stroke data (coordinates, pressure, tilt, speed) for higher-accuracy recognition and more actionable feedback.

See [docs/PLAN.md](docs/PLAN.md) for the full investigation and pipeline plan.

## Project Structure

```
src/rm_greg/
├── models.py          # Core data models (Stroke, Point, etc.)
├── cli.py             # Command-line interface
├── ingest/            # Extract stroke data from .rm files
├── preprocessing/     # Normalize, segment, extract features
├── training/          # Stroke classifiers and datasets
├── feedback/          # DTW comparison, scoring, feedback generation
├── api/               # FastAPI server
└── synthetic/         # Synthetic training data generation
```

## Setup

```bash
# Install core dependencies
pip install -e .

# Install with ML support
pip install -e ".[ml]"

# Install everything (ML, API, feedback, visualization, dev tools)
pip install -e ".[all]"
```

## Usage

```bash
# Extract stroke data from a .rm file
rm-greg extract notebook.rm -o strokes.json

# Generate synthetic training data
rm-greg synthetic --unit 1 --count 100 -o data/synthetic/

# Train a stroke classifier
rm-greg train data/synthetic/ --unit 1 --model rf -o models/unit1.pkl

# Start the API server
rm-greg serve --port 8000
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

## Pipeline

The project follows an incremental cycle approach:

- **Cycle 0**: Data foundation — .rm extraction + synthetic data generation
- **Cycle 1**: Stroke-level classifier for Unit 1 primitives
- **Cycle 2**: Word-level recognition with vocabulary constraints
- **Cycle 3**: Feedback engine with DTW comparison and scoring
- **Cycle 4**: End-to-end app integration with web UI
