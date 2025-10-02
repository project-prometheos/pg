"""Schemas used by the check endpoint."""
from __future__ import annotations

from typing import Dict

from pydantic import BaseModel, Field


class CheckRequest(BaseModel):
    variant_id: str
    inputs: Dict[str, str]


class CheckResponse(BaseModel):
    correct: bool
    score: float = Field(ge=0, le=1)
    feedback: list[str] = Field(default_factory=list)
    canonical: str | None = None
