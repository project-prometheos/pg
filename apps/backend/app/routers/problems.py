"""Problem endpoints bridging FastAPI and the domain core."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from ..schemas.problem import ProblemResponse
from ..services import problems as problem_service

router = APIRouter()


@router.get("/{problem_id:path}", response_model=ProblemResponse)
def read_problem(problem_id: str, seed: int = Query(..., ge=0)) -> ProblemResponse:
    """Return a deterministic problem variant for the requested seed."""
    try:
        problem = problem_service.generate_problem(
            problem_id=problem_id, seed=seed)
    except problem_service.ProblemNotFoundError as exc:  # pragma: no cover - guard clause
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return problem
