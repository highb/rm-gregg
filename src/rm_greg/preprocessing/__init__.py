"""Preprocessing module: normalize, segment, augment, and extract features from stroke data."""

from rm_greg.preprocessing.normalize import normalize_strokes
from rm_greg.preprocessing.segment import segment_glyphs
from rm_greg.preprocessing.features import extract_geometric_features

__all__ = ["normalize_strokes", "segment_glyphs", "extract_geometric_features"]
