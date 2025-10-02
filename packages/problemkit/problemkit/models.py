"""Pydantic models representing authored problem instances."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class InputSpec(BaseModel):
    """Description of a single learner input widget."""

    name: str
    type: str
    label: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)


class ProblemInstance(BaseModel):
    """Immutable representation of an authored problem variant."""

    statement_tex: str
    inputs: list[InputSpec]
    answers: dict[str, Any]
    solution_tex: str
    meta: dict[str, Any] = Field(default_factory=dict)
