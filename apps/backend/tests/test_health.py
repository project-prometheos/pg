"""Smoke tests for the FastAPI application."""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_problem_roundtrip() -> None:
    client = TestClient(app)
    response = client.get("/api/problems/calc.product_rule.v1", params={"seed": 42})
    assert response.status_code == 200
    payload = response.json()
    assert payload["variant_id"]
    assert payload["problem_id"] == "calc.product_rule.v1"
    assert payload["seed"] == 42
    assert "statement_tex" in payload
