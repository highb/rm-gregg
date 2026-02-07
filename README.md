# rm-greg

A Gregg Shorthand learning system powered by reMarkable tablet stroke data and ML.

> **Note:** This project is under active development. APIs, data formats, and features are subject to change. See the [roadmap](#pipeline) for current status.

**[Documentation](https://highb.github.io/rm-greg/)** | **[Getting Started](https://highb.github.io/rm-greg/getting-started)** | **[Roadmap](https://highb.github.io/rm-greg/roadmap)**

## Overview

rm-greg extracts rich stroke data from reMarkable tablets and uses it to build a curriculum-aware Gregg shorthand practice system with AI-powered feedback. Unlike raster-based approaches, it leverages the tablet's online stroke data (coordinates, pressure, tilt, speed) for higher-accuracy recognition and more actionable feedback.

See [docs/PLAN.md](docs/PLAN.md) for the full investigation and pipeline plan, or visit the [documentation site](https://highb.github.io/rm-greg/) for guides and API reference.

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

## Current Status

The project is in **Cycle 0/1** -- the data foundation is complete and work on the first stroke-level classifier is underway. Core extraction, preprocessing, synthetic data generation, and feedback comparison metrics are implemented. The CLI and API endpoints are scaffolded but not yet fully wired up.

See the [full roadmap](https://highb.github.io/rm-greg/roadmap) for details on what's done and what's planned.

## Contributing

Contributions are welcome! See the [contributing guide](https://highb.github.io/rm-greg/contributing) for setup instructions and areas where help is most needed. Please open an issue before starting large changes.
