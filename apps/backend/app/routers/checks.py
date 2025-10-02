"""Answer checking endpoints returning stubbed responses for now."""
from __future__ import annotations

from fastapi import APIRouter

from ..schemas.check import CheckRequest, CheckResponse

router = APIRouter(prefix="/api")


@router.post("/check", response_model=CheckResponse)
def check_answer(payload: CheckRequest) -> CheckResponse:
    """Placeholder checker returning deterministic mock feedback."""

    is_correct = payload.inputs.get("ans", "").strip() != ""
    return CheckResponse(
        correct=is_correct,
        score=1.0 if is_correct else 0.0,
        feedback=["Sample feedback" if not is_correct else "Great work!"],
        canonical="Not yet implemented",
    )
