"""FastAPI application entry-point for the problem generator backend."""
from __future__ import annotations

from fastapi import FastAPI

from .routers import checks, health, problems, solutions

app = FastAPI(title="Problem Generator API", version="0.1.0")
app.include_router(health.router)
app.include_router(problems.router, prefix="/api/problems", tags=["problems"])
app.include_router(checks.router, tags=["checking"])
app.include_router(solutions.router, tags=["solutions"])


@app.get("/api/health", tags=["health"])
def healthcheck() -> dict[str, str]:
    """Simple health endpoint used for readiness checks."""
    return {"status": "ok"}
