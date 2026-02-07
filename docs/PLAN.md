# Gregg Shorthand Practice App: Investigation & Pipeline Plan

## 1. reMarkable Stroke Data Format

### What You're Working With

The reMarkable stores drawings in `.rm` binary files (currently v6 format since firmware 3.0, late 2022). Each notebook page gets its own `.rm` file, stored at `/home/root/.local/share/remarkable/xochitl/<UUID>/<page-UUID>.rm`.

**Per-point data available:**

| Field     | Type  | Range   | Notes                                              |
|-----------|-------|---------|----------------------------------------------------|
| x         | float | 0–1404  | Horizontal coordinate                              |
| y         | float | 0–1872  | Vertical coordinate                                |
| speed     | float | varies  | Stylus velocity across surface                     |
| direction | float | radians | Tangent angle between consecutive points           |
| width     | float | varies  | Effective brush width (accounts for tilt/pressure) |
| pressure  | float | 0.0–1.0 | Pen-to-surface pressure                            |
| tilt      | float | radians | Stylus angle to surface (0–π/2 and 3π/2–2π)       |

Points are grouped into **strokes** (continuous pen-down sequences), which belong to **layers** (up to 5 per page). Each stroke has metadata: pen type, color (black/grey/white), and base brush size.

This is *vastly* richer than raster image data. You get the temporal sequence of strokes, pressure dynamics, and pen angle — essentially the same signal space as "online handwriting recognition," which is a much more tractable problem than offline OCR.

### Key Python Libraries for Parsing

| Library              | Format   | Status       | Notes                                                                              |
|----------------------|----------|--------------|------------------------------------------------------------------------------------|
| **rmscene**          | v6 (.rm) | Active       | Best option for current firmware. Reads stroke data, text, layers. By Rick Lupton. |
| **rmc**              | v6 (.rm) | Active       | CLI converter built on rmscene. Exports to SVG, PDF, Markdown.                     |
| **remarkable-layers** | v3/v5   | Unmaintained | Python API for older format.                                                       |
| **rmtool**           | v3/v5    | Active       | Go library, also has Cloud API client.                                             |

**rmscene** (`pip install rmscene`) is the clear winner for our use case. It gives direct access to the stroke/point data structures in Python, which can then be fed into the ML pipeline.

**Extraction workflow:**

```
reMarkable tablet → SSH/Cloud API → .rm files → rmscene → [(x, y, pressure, tilt, speed, direction), ...] per stroke
```

### Getting Files Off the Tablet

Three paths, all well-documented by the community:

1. **SSH** (direct USB or WiFi): `scp root@10.11.99.1:/home/root/.local/share/remarkable/xochitl/<UUID>/*.rm ./`
2. **Cloud API**: Use rmapi or the REST API to sync files programmatically
3. **Export as PDF/SVG**: Loses stroke-level data — avoid for training

### Kaitai Struct Spec

Barry Van Tassell reverse-engineered the v6 format and published a full Kaitai Struct spec at `github.com/YakBarber/remarkable_file_format`. This is useful if you need to build tooling in languages other than Python, since Kaitai generates parsers for dozens of languages.

---

## 2. Prior Art: Gregg Shorthand Recognition

There is more prior work here than you might expect. The field is small but active.

### Datasets

| Dataset                | Size                   | Type             | Source                                                   | Notes                                                                                                     |
|------------------------|------------------------|------------------|----------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| **Gregg-1916**         | ~15,700 word images    | Offline (raster) | Extracted from 1916 Gregg Shorthand Dictionary           | Publicly available at `github.com/anonimously/Gregg1916-Recognition`. Printed shorthand, not handwritten. |
| **LION**               | Line-level stenography | Offline (raster) | Astrid Lindgren manuscripts (Melin shorthand, not Gregg) | Published 2024, available on Zenodo. First handwritten stenography HTR dataset.                           |
| **StenogrApp dataset** | 48 images              | Offline (raster) | 48 basic Gregg brief forms                               | Very small, proof-of-concept only.                                                                        |

**Critical gap:** No existing dataset has **online** (stroke-level) Gregg shorthand data. Every dataset is raster images from scanned printed or handwritten sources. Our reMarkable pipeline would produce the first online Gregg shorthand dataset, which is a genuinely novel contribution.

### Published Research

**Zhai et al. (2018)** — "A Dataset and a Novel Neural Approach for Optical Gregg Shorthand Recognition" (TSD 2018, Springer)

- Created Gregg-1916 dataset from the 1916 dictionary
- CNN feature extractor → bidirectional RNN decoder → word retrieval module
- Key insight: Gregg is pronunciation-based, not spelling-based, so the mapping from shorthand to English is many-to-many
- Code available at the GitHub repo above

**Padilla et al. (2020)** — "Deep Learning Approach in Gregg Shorthand Word to English-Word Conversion"

- Used Inception-v3 (transfer learning) on 135 legal terms in Gregg shorthand
- TensorFlow-based, word-level classification approach

**StenogrApp (2024)** — "E-Learning Android Application in Recognition of Basic Gregg Shorthand using Machine Learning" (ICETT 2024)

- **Most relevant to our concept:** an e-learning app for Gregg shorthand using ML
- Used k-Nearest Neighbors on 48 brief forms, achieved 86% precision
- Android app with API for cross-platform use
- Limited scope (only brief forms), but validates the educational app concept

**Heil & Breznik (2024)** — "Handwritten stenography recognition and the LION dataset" (IJDAR)

- First baseline for handwritten stenography recognition
- CER of ~25%, WER of ~45-48% with stenography-specific encodings + pretraining
- Key finding: integrating domain knowledge (stenographic theory) into target sequence encoding significantly improves results
- Not Gregg (it's Melin/Swedish), but the methodology transfers

**Rajasekaran & Ramar (2012)** — "Handwritten Gregg Shorthand Recognition"

- Earlier work using PCA + Logistic Regression, also explored CANN and backpropagation
- Focused on both character-level and word-level recognition

### Practice Apps (Non-Shorthand)

No dedicated shorthand practice app with AI feedback exists. General handwriting practice apps:

- **Writey** (iOS): Real-time feedback on handwriting with Apple Pencil. Closest analog to what we're building, but for standard alphabets.
- **Kaligo** (tablets): AI-powered handwriting for kids, uses on-device stroke analysis
- **MyScript Notes / Nebo**: Best-in-class handwriting recognition (66 languages), but recognition not training
- **Handwriting Success**: Getty-Dubay curriculum on iPad with stylus practice

None of these handle shorthand, and none integrate with the reMarkable specifically.

---

## 3. Feasibility Assessment

### Why This Is More Tractable Than It Looks

1. **Online vs. Offline**: We have stroke data, not raster images. Online handwriting recognition is substantially easier — you get temporal ordering, stroke segmentation for free, and rich per-point features.
2. **Curriculum-constrained recognition**: We don't need a general Gregg recognizer. Unit 1 has ~10-15 distinct strokes. Unit 2 adds a handful more. At any given lesson, the classification space is tiny.
3. **Known vocabulary per lesson**: Each unit introduces specific words. We can constrain the decoder to only output words from the current unit's vocabulary — a massive reduction in search space.
4. **Synthetic data generation**: Gregg strokes are well-defined geometric primitives (arcs, lines, circles, hooks). We can parameterize them and generate thousands of synthetic training examples with controlled variation.

### Where It Gets Hard

1. **Proportional strokes**: The same curve shape at different sizes means different letters. This requires the model to learn relative sizing, not just shape.
2. **Contextual joining**: Later units introduce blends where strokes flow into each other. Segmenting these requires understanding stroke boundaries in continuous writing.
3. **Writer variation**: Even with stroke data, everyone's "a" circle will be slightly different. Need sufficient examples per writer to generalize.
4. **Feedback quality**: Recognizing what someone *wrote* is easier than telling them *how to improve*. The feedback mechanism needs careful design.

---

## 4. Training Pipeline Design

### Architecture Overview

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

### Cycle 0: Data Foundation

**Deliverable:** A Python package that extracts stroke data from reMarkable `.rm` files and converts it to a normalized, ML-ready format.

**Tasks:**

- Build extraction pipeline using `rmscene`: `.rm` → list of strokes → list of (x, y, pressure, tilt, speed, time) tuples
- Normalize coordinates to [0, 1] range (dividing by 1404 and 1872)
- Implement stroke segmentation (split page-level data into individual glyph attempts)
- Define data schema (probably a simple JSON or Parquet format per practice session)
- Build a synthetic stroke generator that creates parameterized Gregg primitives:
  - Circles (vowels: a, e, o) at varying sizes
  - Straight lines (consonants: t, d, n, m) at varying lengths/angles
  - Curves (r, l, k, g) with controlled curvature
  - Add realistic noise: jitter, pressure variation, speed variation
- Validate by rendering synthetic strokes back to SVG and visually confirming they look like Gregg

**Open Source Tools:**

- `rmscene` — .rm file parsing
- `numpy` — numerical operations
- `svgwrite` or `matplotlib` — rendering/validation
- `pydantic` — data schema validation

### Cycle 1: Stroke-Level Classifier (Unit 1)

**Deliverable:** A model that classifies individual Gregg strokes from Unit 1 with >90% accuracy on held-out test data.

**Tasks:**

- Define Unit 1 stroke vocabulary from the greggshorthand.github.io curriculum (~10-15 classes)
- Create training data: mix of synthetic strokes + handwritten samples on reMarkable
- Implement feature extraction from stroke sequences:
  - **Geometric features**: total arc length, bounding box aspect ratio, start/end angles, curvature statistics, stroke height/width ratio
  - **Raw sequence features**: padded/interpolated (x, y, pressure) sequences for neural network input
- Train two parallel approaches and compare:
  1. **Classical ML baseline**: Extract geometric features → Random Forest or SVM (scikit-learn). Fast to iterate, good baseline.
  2. **Sequence model**: 1D CNN or small LSTM on interpolated point sequences (PyTorch). Better ceiling.
- Evaluate with k-fold cross-validation (small dataset, so need to be careful about splits)
- Implement stroke-to-label prediction API

**Open Source Tools:**

- `scikit-learn` — classical ML baseline
- `PyTorch` — neural network models
- `wandb` or `mlflow` — experiment tracking

### Cycle 2: Word-Level Recognition

**Deliverable:** A model that maps a sequence of strokes to an English word from the current unit's vocabulary, with top-3 accuracy >85%.

**Tasks:**

- Implement word-level segmentation: given a page of practice, identify individual word attempts (likely gap-based heuristic on x-coordinates between strokes)
- Build word recognition as sequence classification:
  - Input: ordered sequence of stroke classifications from Cycle 1
  - Output: English word from unit vocabulary
  - Approach: CTC loss over stroke sequence → word, constrained to unit vocabulary
- Alternatively (simpler): treat each word attempt as a single stroke sequence and classify holistically
- Integrate the Gregg-1916 dataset as supplementary training data:
  - These are raster images, so use a CNN to extract features
  - Use as a transfer learning source: pretrain on Gregg-1916, fine-tune on online stroke data
- Build vocabulary constraint: given a unit number, restrict output space to only valid words for that unit

**Open Source Tools:**

- `PyTorch` — CTC loss, sequence models
- `torchvision` — for Gregg-1916 raster image preprocessing
- `Pillow` / `OpenCV` — image processing for raster data

### Cycle 3: Feedback Engine

**Deliverable:** A system that compares a user's stroke to a reference and produces actionable feedback (e.g., "your 'a' circle is too large relative to the 'n' curve").

**Tasks:**

- Define reference strokes: canonical representations of each Gregg primitive with acceptable tolerance bands
- Implement comparison metrics:
  - **Dynamic Time Warping (DTW)**: Align user stroke to reference, identify where deviation is largest
  - **Fréchet distance**: Overall shape similarity
  - **Proportional analysis**: Compare stroke sizes relative to each other (critical for Gregg)
- Generate natural language feedback from metric deviations:
  - Size too large/small → "Make your [stroke] about 2/3 the height of your [other stroke]"
  - Curvature wrong → "This curve should be more/less pronounced"
  - Angle off → "The starting angle should be steeper"
- Build a scoring rubric per unit that weights different aspects of stroke quality
- Could also use an LLM to generate more nuanced feedback from structured metric data — this is where a Claude API call per evaluation could add real value

**Open Source Tools:**

- `dtaidistance` or `tslearn` — DTW implementation
- `scipy` — Fréchet distance, curve analysis
- `jinja2` — feedback template rendering

### Cycle 4: App Integration

**Deliverable:** End-to-end workflow: practice on reMarkable → export → get feedback in web UI.

**Tasks:**

- Build PDF template generator for practice sheets (guided lines, reference strokes, practice areas)
- Implement file upload/processing pipeline:
  - User exports `.rm` file (or syncs via cloud)
  - Server parses with rmscene
  - Runs through recognition + feedback pipeline
  - Returns results via web UI
- Build a simple web frontend (could be a React app) showing:
  - Rendered version of what user drew
  - Side-by-side with reference
  - Feedback annotations
  - Progress tracking per unit
- Package model for serving: export to ONNX for fast inference

**Open Source Tools:**

- `FastAPI` — API server
- `reportlab` or `fpdf2` — PDF template generation
- `onnxruntime` — model serving
- React / Next.js — web frontend

---

## 5. Data Strategy: Bootstrapping from Nothing

The cold start problem is real but solvable. Here's the progression:

**Phase 1 — Synthetic only** (0 real samples needed):
Parameterize each Gregg primitive mathematically. Generate 1,000+ examples per stroke class with controlled variation. Train initial model. This gets you a working prototype.

**Phase 2 — Self-play** (~50-100 real samples per class):
As you practice on the reMarkable, feed your own writing through the pipeline. Label it (you know what you were trying to write). Fine-tune from synthetic baseline.

**Phase 3 — Additional writers** (~50-100 real samples per class):
A second writer's data dramatically improves generalization. If another practitioner is willing to write a few pages of practice forms, that's invaluable.

**Phase 4 — Community** (if the tool gains traction):
If open-sourced, the r/shorthand community + Gregg enthusiasts could contribute labeled samples. The curriculum structure means you can crowdsource labels cheaply ("I was practicing Unit 3, here are my .rm files").

---

## 6. Key Risks & Mitigations

| Risk                                          | Likelihood | Impact | Mitigation                                                                                                                   |
|-----------------------------------------------|------------|--------|------------------------------------------------------------------------------------------------------------------------------|
| reMarkable firmware update breaks .rm format  | Medium     | High   | Pin to rmscene library, which tracks format changes. The community has adapted to every format change so far (v3→v5→v6).     |
| Insufficient training data for generalization | High       | Medium | Synthetic data + curriculum constraints drastically reduce data requirements. Start with Unit 1 (tiny classification space). |
| Proportional stroke discrimination too hard   | Medium     | High   | Use relative features (ratios) rather than absolute sizes. The reMarkable's consistent DPI helps here.                       |
| Feedback quality feels unhelpful              | Medium     | Medium | Start with simple pass/fail + DTW visualization. Iterate based on your own experience using it.                              |
| reMarkable restricts cloud API access         | Low        | Medium | SSH extraction always works (they've committed to keeping SSH access). Community has survived multiple API changes.           |

---

## 7. Recommended Tech Stack Summary

| Component           | Tool                                        | Why                                                   |
|---------------------|---------------------------------------------|-------------------------------------------------------|
| .rm parsing         | rmscene (Python)                            | Best maintained v6 parser                             |
| ML framework        | PyTorch                                     | Best ecosystem for sequence models, good ONNX export  |
| Classical ML        | scikit-learn                                | Fast iteration for baselines                          |
| Experiment tracking | Weights & Biases or MLflow                  | Track training runs                                   |
| Sequence alignment  | dtaidistance / tslearn                      | DTW for feedback                                      |
| API server          | FastAPI                                     | Fast, typed, async                                    |
| Model serving       | ONNX Runtime                                | Cross-platform, fast inference                        |
| PDF generation      | fpdf2 or reportlab                          | Practice template generation                          |
| Data storage        | Parquet (training data), SQLite (app state) | Efficient columnar storage for stroke data            |
| Frontend            | React + Tailwind                            | Standard, or even a simple Gradio app for prototyping |

---

## 8. Summary

This project is feasible and genuinely novel — nobody has built a curriculum-aware shorthand practice app with AI feedback using online stroke data. The reMarkable's rich stroke format is a massive advantage over raster-based approaches. The Gregg-1916 dataset and StenogrApp paper validate that ML-based shorthand recognition works, and the curriculum structure of the greggshorthand.github.io course gives a natural way to constrain the problem to tractable sub-problems.

The biggest risk is scope creep. Start with Cycle 0 (data extraction) and Cycle 1 (stroke classification for Unit 1 only). If those work, everything else follows incrementally.
