"""Data ingestion module: extract stroke data from reMarkable .rm files."""

from rm_greg.ingest.extractor import extract_page, extract_notebook

__all__ = ["extract_page", "extract_notebook"]
