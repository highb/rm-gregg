---
title: Roadmap
layout: default
nav_order: 5
---

# Roadmap

{: .note }
> rm-gregg follows an incremental development approach organized into cycles. The project is currently in **Cycle 0/1**, building the data foundation and first classifier.

## Development Cycles

### Cycle 0: Data Foundation

**Goal:** Extract stroke data from reMarkable `.rm` files and convert it to a normalized, ML-ready format.

| Task | Status |
|:-----|:-------|
| Build extraction pipeline using rmscene | Done |
| Normalize coordinates to [0, 1] range | Done |
| Implement stroke segmentation (gap-based and grid-based) | Done |
| Define data schema with Pydantic models | Done |
| Build synthetic stroke generator for Gregg primitives | Done |
| Feature extraction (15 geometric features) | Done |

---

### Cycle 1: Stroke-Level Classifier (Unit 1)

**Goal:** Classify individual Gregg strokes from Unit 1 with >90% accuracy on held-out test data.

| Task | Status |
|:-----|:-------|
| Define Unit 1 stroke vocabulary (~10-15 classes) | Done |
| Create training data (synthetic + handwritten) | In Progress |
| Implement Random Forest / SVM classifiers | Done |
| Implement sequence model (1D CNN or LSTM) | Planned |
| Evaluate with k-fold cross-validation | Planned |
| Implement stroke-to-label prediction API | Planned |

---

### Cycle 2: Word-Level Recognition

**Goal:** Map a sequence of strokes to an English word from the current unit's vocabulary (top-3 accuracy >85%).

| Task | Status |
|:-----|:-------|
| Word-level segmentation from page data | Planned |
| Sequence classification (CTC or holistic) | Planned |
| Vocabulary-constrained decoder per unit | Planned |
| Integrate Gregg-1916 dataset for transfer learning | Planned |

---

### Cycle 3: Feedback Engine

**Goal:** Compare user strokes to references and produce actionable feedback.

| Task | Status |
|:-----|:-------|
| Define canonical reference strokes | Planned |
| DTW-based stroke alignment and comparison | Done |
| Frechet distance computation | Done |
| Proportional analysis (relative sizing) | Done |
| Natural language feedback generation | In Progress |
| Scoring rubric per unit | Planned |

---

### Cycle 4: App Integration

**Goal:** End-to-end workflow from reMarkable practice to web-based feedback.

| Task | Status |
|:-----|:-------|
| PDF practice sheet template generator | Planned |
| File upload and processing pipeline | Planned |
| Web frontend (rendered strokes + feedback) | Planned |
| Progress tracking per unit | Planned |
| Export model to ONNX for serving | Planned |

## Data Strategy

The project bootstraps from zero real data through four phases:

1. **Synthetic only** (current) -- Parameterized Gregg primitives with controlled variation
2. **Self-play** -- The developer's own practice data, labeled by intent
3. **Additional writers** -- A second writer's data for generalization
4. **Community** -- Open-source contributions from the r/shorthand community

## How to Contribute

See the [Contributing]({% link contributing.md %}) guide for ways to help move the roadmap forward.
