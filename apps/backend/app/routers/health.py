"""Health router exposing readiness checks."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/ping")
def ping() -> dict[str, str]:
    """Ping endpoint for smoke tests."""
    return {"status": "ok"}
