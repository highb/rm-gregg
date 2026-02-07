---
title: Architecture
layout: default
nav_order: 3
---

# Architecture

{: .note }
> This document describes the current and planned architecture. Components marked as **planned** are not yet implemented.

## Pipeline Overview

rm-greg follows a four-stage pipeline:

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐    ┌─────────────┐
│ Data Ingest  │───▶│ Preprocessing │───▶│  Training     │───▶│  Serving    │
│              │    │              │    │              │    │             │
│ • rmscene    │    │ • Normalize  │    │ • Per-unit   │    │ • FastAPI   │
│ • Synthetic  │    │ • Segment    │    │   models     │    │ • ONNX      │
│   generator  │    │ • Augment    │    │ • Transfer   │    │ • Feedback  │
│ • Gregg-1916 │    │ • Feature    │    │   learning   │    │   engine    │
│   (raster)   │    │   extract    │    │              │    │             │
└─────────────┘    └──────────────┘    └──────────────┘    └─────────────┘
```

## Data Ingest

The ingest layer handles two data sources:

### reMarkable .rm Files

The reMarkable stores drawings in `.rm` binary files (v6 format). Each page gets its own file containing strokes grouped into layers. Per-point data includes:

| Field     | Type  | Description                     |
|:----------|:------|:--------------------------------|
| x, y      | float | Coordinates (0-1404 x 0-1872)  |
| pressure  | float | Pen-to-surface pressure (0-1)  |
| tilt      | float | Stylus angle to surface         |
| speed     | float | Stylus velocity                 |
| direction | float | Tangent angle between points    |
| width     | float | Effective brush width           |

Extraction uses the [rmscene](https://github.com/ricklupton/rmscene) library.

### Synthetic Data Generator

Gregg shorthand strokes are well-defined geometric primitives. The synthetic generator creates parameterized training examples:

- **Circles** (vowels: a, e, o) at varying sizes
- **Straight lines** (consonants: t, d, n, m) at varying lengths and angles
- **Curves** (r, l, k, g) with controlled curvature

Each synthetic stroke includes realistic variation: jitter, pressure dynamics, and speed profiles. Generation is deterministic with seeds for reproducibility.

## Preprocessing

### Normalization

Raw coordinates are normalized to a [0, 1] range. Strokes are optionally interpolated to a fixed number of points for sequence model input.

### Segmentation

Two segmentation strategies:

- **Gap-based**: Splits strokes into individual glyph attempts based on spatial gaps
- **Grid-based**: For structured practice sheets, segments by grid cell position

### Feature Extraction

15 geometric features are extracted per stroke:

- Bounding box dimensions and aspect ratio
- Total arc length
- Start and end angles
- Curvature statistics (mean, max, standard deviation)
- Pressure and speed profiles
- Stroke height/width ratio

## Training

### Classical ML Baseline

Random Forest and SVM classifiers trained on geometric features via scikit-learn. Fast to iterate and provides a strong baseline.

### Sequence Models (Planned)

1D CNN or LSTM on interpolated point sequences via PyTorch for higher accuracy ceiling.

### Curriculum Constraints

Models are trained per-unit. Each unit introduces a small set of new strokes (~10-15 for Unit 1), keeping the classification space manageable even with limited training data.

## Feedback Engine

### Stroke Comparison

User strokes are compared against reference strokes using:

- **Dynamic Time Warping (DTW)**: Aligns strokes temporally to find where deviation is largest
- **Frechet distance**: Overall shape similarity
- **Proportional analysis**: Relative stroke sizes (critical for Gregg, where size encodes meaning)
- **Curvature and angle deviation**: Shape quality metrics

### Feedback Generation

Metric deviations are translated into natural language feedback, e.g.:

- "Make your 'a' circle about 2/3 the height of your 'n' curve"
- "This curve should be more pronounced"
- "The starting angle should be steeper"

## API Layer

A FastAPI server exposes the pipeline via REST endpoints:

| Endpoint | Description | Status |
|:---------|:------------|:-------|
| `GET /health` | Health check | Done |
| `POST /api/v1/classify` | Stroke classification | Planned |
| `POST /api/v1/feedback` | Feedback generation | Planned |
| `POST /api/v1/upload` | .rm file upload | Planned |
| `GET /api/v1/curriculum/{unit}` | Unit vocabulary | Partial |

## Tech Stack

| Component | Tool | Purpose |
|:----------|:-----|:--------|
| .rm parsing | rmscene | reMarkable v6 format parsing |
| Data models | Pydantic | Validation and serialization |
| Numerical | NumPy | Array operations |
| Classical ML | scikit-learn | Baseline classifiers |
| Deep learning | PyTorch | Sequence models |
| Serving | ONNX Runtime | Fast inference |
| API | FastAPI | REST endpoints |
| Alignment | dtaidistance | DTW computation |
| Feedback | Jinja2 | Template rendering |
