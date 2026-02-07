---
title: Home
layout: home
nav_order: 1
---

# rm-gregg

**A Gregg Shorthand learning system powered by reMarkable tablet stroke data and ML.**

{: .warning }
> **This project is under active development.** APIs, data formats, and features are subject to change. Contributions and feedback are welcome, but expect breaking changes.

## What is rm-gregg?

rm-gregg extracts rich stroke data from [reMarkable tablets](https://remarkable.com/) and uses it to build a curriculum-aware Gregg shorthand practice system with AI-powered feedback.

Unlike raster-based approaches, rm-gregg leverages the tablet's **online stroke data** -- coordinates, pressure, tilt, and speed -- for higher-accuracy recognition and more actionable feedback.

## Why this project?

- **No existing tool** provides AI-powered feedback for Gregg shorthand practice
- **Online stroke data** from the reMarkable is vastly richer than scanned images
- **Curriculum-constrained recognition** makes the ML problem tractable even with limited training data
- **This would produce the first online Gregg shorthand dataset**, a genuinely novel contribution

## Key Features (Planned & In Progress)

| Feature | Status |
|:--------|:-------|
| `.rm` file extraction via rmscene | Done |
| Stroke normalization & preprocessing | Done |
| Geometric feature extraction | Done |
| Synthetic training data generation | Done |
| Stroke-level classification (Unit 1) | In Progress |
| DTW-based feedback comparison | Done |
| Natural language feedback generation | In Progress |
| FastAPI server | Scaffolded |
| Web UI for feedback review | Planned |
| PDF practice sheet generation | Planned |

## How It Works

```
reMarkable tablet
    ↓ SSH / Cloud sync
.rm binary files
    ↓ rmscene parsing
Stroke data (x, y, pressure, tilt, speed)
    ↓ Normalization & feature extraction
ML classification → Feedback engine
    ↓
Actionable practice feedback
```

## Quick Start

```bash
pip install -e ".[all]"
```

See the [Getting Started]({% link getting-started.md %}) guide for detailed setup instructions.
