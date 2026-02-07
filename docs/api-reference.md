---
title: API Reference
layout: default
nav_order: 4
---

# API Reference

{: .warning }
> **The API is under active development.** Endpoints, request/response formats, and behavior will change. This page documents the planned API surface.

## Overview

rm-gregg exposes a REST API via FastAPI for stroke classification, feedback generation, and file management.

**Base URL**: `http://localhost:8000`

## Endpoints

### Health Check

```
GET /health
```

Returns server health status.

**Response:**
```json
{
  "status": "healthy"
}
```

---

### Classify Strokes

```
POST /api/v1/classify
```

{: .important }
> Not yet implemented.

Classify a set of strokes against the current unit's vocabulary.

**Request Body:**
```json
{
  "strokes": [
    {
      "points": [
        {"x": 0.1, "y": 0.2, "pressure": 0.5, "tilt": 0.0, "speed": 1.0}
      ]
    }
  ],
  "unit": 1
}
```

**Response:**
```json
{
  "classifications": [
    {
      "label": "a_circle",
      "confidence": 0.92,
      "alternatives": [
        {"label": "e_circle", "confidence": 0.06}
      ]
    }
  ]
}
```

---

### Generate Feedback

```
POST /api/v1/feedback
```

{: .important }
> Not yet implemented.

Compare user strokes against reference strokes and generate feedback.

**Request Body:**
```json
{
  "strokes": [...],
  "target_word": "day",
  "unit": 1
}
```

**Response:**
```json
{
  "score": 0.78,
  "grade": "B",
  "feedback": [
    "Your 'd' stroke is well-formed.",
    "The 'a' circle should be smaller relative to the 'd' curve."
  ],
  "metrics": {
    "dtw_distance": 0.15,
    "frechet_distance": 0.22,
    "size_ratio": 1.3,
    "curvature_deviation": 0.08
  }
}
```

---

### Upload .rm File

```
POST /api/v1/upload
```

{: .important }
> Not yet implemented.

Upload a reMarkable `.rm` file for processing.

**Request:**
- Content-Type: `multipart/form-data`
- Field: `file` (binary `.rm` file)

**Response:**
```json
{
  "session_id": "abc123",
  "pages": 1,
  "strokes_extracted": 42
}
```

---

### Get Unit Curriculum

```
GET /api/v1/curriculum/{unit}
```

Returns the vocabulary and stroke primitives for a given unit.

**Response:**
```json
{
  "unit": 1,
  "primitives": ["a_circle", "e_circle", "t_line", "d_line", ...],
  "words": ["day", "date", "aid", ...]
}
```

## Data Models

### Point

| Field | Type | Description |
|:------|:-----|:------------|
| x | float | Normalized x coordinate (0-1) |
| y | float | Normalized y coordinate (0-1) |
| pressure | float | Pen pressure (0-1) |
| tilt | float | Stylus tilt angle (radians) |
| speed | float | Stylus velocity |
| direction | float | Tangent angle |
| width | float | Effective brush width |

### Stroke

| Field | Type | Description |
|:------|:-----|:------------|
| points | list[Point] | Ordered sequence of points |
| pen_type | string | Pen tool used |
| color | string | Stroke color |

### PracticeSession

| Field | Type | Description |
|:------|:-----|:------------|
| pages | list[PageData] | Pages in the session |
| unit | int | Curriculum unit number |
| timestamp | datetime | When the session was recorded |

## Error Responses

All endpoints return standard error responses:

```json
{
  "detail": "Description of what went wrong"
}
```

| Status Code | Meaning |
|:------------|:--------|
| 400 | Invalid request (malformed data) |
| 404 | Resource not found |
| 422 | Validation error (wrong types/values) |
| 500 | Internal server error |
