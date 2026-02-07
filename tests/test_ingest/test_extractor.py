"""Tests for the .rm file extraction pipeline."""

from __future__ import annotations

from pathlib import Path

import pytest

from rm_greg.models import PageData


class TestExtractPage:
    """Tests for extract_page function."""

    def test_file_not_found_raises(self) -> None:
        from rm_greg.ingest.extractor import extract_page

        with pytest.raises(FileNotFoundError):
            extract_page(Path("/nonexistent/file.rm"))

    def test_returns_page_data(self, tmp_path: Path) -> None:
        """Extraction of a valid .rm file returns PageData.

        Note: This test requires rmscene and a valid .rm fixture file.
        Skip if not available.
        """
        pytest.skip("Requires .rm fixture file — add real fixture to tests/fixtures/")
