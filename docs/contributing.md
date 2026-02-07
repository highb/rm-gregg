---
title: Contributing
layout: default
nav_order: 6
---

# Contributing

{: .warning }
> rm-gregg is in early active development. The architecture and APIs are still evolving. Contributions are welcome, but please open an issue to discuss before starting large changes.

## Getting Set Up

```bash
# Clone the repository
git clone https://github.com/highb/rm-gregg.git
cd rm-gregg

# Install all dependencies (including dev tools)
pip install -e ".[all]"

# Verify everything works
pytest
ruff check src/ tests/
mypy src/
```

## Development Workflow

### Running Tests

```bash
pytest
```

Tests live in the `tests/` directory and cover the synthetic data generation, preprocessing, feature extraction, and feedback comparison modules.

### Linting

```bash
ruff check src/ tests/
```

The project uses [ruff](https://docs.astral.sh/ruff/) targeting Python 3.11+ with a 100-character line length.

### Type Checking

```bash
mypy src/
```

All functions must have type annotations (`disallow_untyped_defs = true`).

## Where to Help

Areas where contributions would be most valuable:

- **Training data**: If you have a reMarkable tablet and practice Gregg shorthand, your `.rm` files would be invaluable for training
- **Unit vocabulary**: Help define the stroke vocabulary for Units 2+ from the greggshorthand.github.io curriculum
- **Sequence models**: Implement PyTorch-based classifiers (1D CNN, LSTM) for the stroke sequences
- **Feedback quality**: Test the feedback engine and suggest improvements to the generated feedback text
- **Documentation**: Improve these docs, add examples, fix errors

## Code Style

- Python 3.11+ with type annotations on all functions
- Pydantic models for data validation
- Google-style docstrings
- Ruff for linting (E, F, I, N, W, UP, B, SIM, RUF rules)
- 100-character line length

## Reporting Issues

Please open issues on [GitHub](https://github.com/highb/rm-gregg/issues) for:

- Bug reports
- Feature requests
- Questions about the architecture or approach
