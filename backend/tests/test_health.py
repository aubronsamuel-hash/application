"""Smoke tests for the health endpoint."""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.app.main import app


def test_health_endpoint_returns_ok_status() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
