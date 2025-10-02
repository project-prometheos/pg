"""Solution retrieval endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..services import problems as problem_service

router = APIRouter(prefix="/api")


@router.get("/solution/{variant_id}")
def get_solution(variant_id: str) -> dict[str, str]:
    """Return the stored solution for a variant.

    For the initial scaffold we recompute the problem by decoding the variant id.
    This keeps the implementation simple while illustrating the hexagonal layering.
    """

    try:
        problem_id, seed = problem_service.registry_decode_variant(variant_id)
    except ValueError as exc:  # pragma: no cover - guard clause
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    problem = problem_service.generate_problem(problem_id=problem_id, seed=seed)
    return {"solutionTex": problem.solution_tex}
