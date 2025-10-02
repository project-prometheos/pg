"""Pydantic models exchanged across the FastAPI boundary."""
from __future__ import annotations

from pydantic import BaseModel, Field


class InputSpec(BaseModel):
    """Minimal representation of an input widget expected by the frontend."""

    name: str
    type: str
    label: str | None = None
    meta: dict[str, object] | None = None


class ProblemInstance(BaseModel):
    """Shape returned by the domain layer for a single problem variant."""

    statement_tex: str
    inputs: list[InputSpec]
    solution_tex: str
    meta: dict[str, object] = Field(default_factory=dict)


class ProblemResponse(ProblemInstance):
    """HTTP response containing a fully resolved problem instance."""

    variant_id: str
    problem_id: str
    seed: int


class ProblemRequest(BaseModel):
    """Incoming parameters from the HTTP layer."""

    seed: int = Field(ge=0)
