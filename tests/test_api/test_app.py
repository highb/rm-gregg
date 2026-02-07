"""Tests for the FastAPI application."""

from __future__ import annotations

import pytest

try:
    from fastapi.testclient import TestClient

    from rm_greg.api.app import app

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

pytestmark = pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not installed")


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class TestHealthCheck:
    def test_health_returns_ok(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestCurriculumEndpoint:
    def test_unit_1_returns_primitives(self, client: TestClient) -> None:
        response = client.get("/api/v1/curriculum/1")
        assert response.status_code == 200
        data = response.json()
        assert "primitives" in data
        assert len(data["primitives"]) > 0

    def test_unknown_unit_returns_404(self, client: TestClient) -> None:
        response = client.get("/api/v1/curriculum/99")
        assert response.status_code == 404
