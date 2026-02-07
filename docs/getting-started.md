---
title: Getting Started
layout: default
nav_order: 2
---

# Getting Started

{: .warning }
> **This project is under active development.** Installation steps and CLI commands may change.

## Prerequisites

- Python 3.11 or later
- A reMarkable tablet (for real stroke data; synthetic data works without one)

## Installation

rm-greg uses a modular dependency system. Install only what you need:

```bash
# Core only (extraction + preprocessing)
pip install -e .

# With ML support (classification, training)
pip install -e ".[ml]"

# With API server
pip install -e ".[api]"

# With feedback engine
pip install -e ".[feedback]"

# Everything (ML, API, feedback, visualization, PDF, dev tools)
pip install -e ".[all]"
```

## Basic Usage

### Extract stroke data from a .rm file

```bash
rm-greg extract notebook.rm -o strokes.json
```

This parses the reMarkable binary format and outputs structured stroke data as JSON, including per-point coordinates, pressure, tilt, speed, and direction.

### Generate synthetic training data

```bash
rm-greg synthetic --unit 1 --count 100 -o data/synthetic/
```

Generates parameterized Gregg shorthand primitives (circles, lines, curves) with realistic variation for training without a tablet.

### Train a stroke classifier

```bash
rm-greg train data/synthetic/ --unit 1 --model rf -o models/unit1.pkl
```

Trains a Random Forest or SVM classifier on extracted features from stroke data.

### Start the API server

```bash
rm-greg serve --port 8000
```

Launches a FastAPI server for stroke classification and feedback.

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

## What's Next

See the [Architecture]({% link architecture.md %}) page for details on how the pipeline works, or the [Roadmap]({% link roadmap.md %}) for planned development.
