"""Database problem rendering endpoints."""

from typing import Dict, Any
from fastapi import APIRouter, Query, HTTPException, Body

from ..db import ProblemDB
from ..services.pg_renderer_python import get_pg_render_service


router = APIRouter(prefix="/api/db", tags=["database", "rendering"])


def get_db() -> ProblemDB:
    """Get database instance."""
    return ProblemDB.get_instance()


@router.get("/{problem_id:path}/render")
def render_database_problem(
    problem_id: str,
    seed: int = Query(0, ge=0, description="Random seed for problem variation")
) -> Dict[str, Any]:
    """
    Render a database problem with the given seed using Python PG renderer.
    
    Example: /api/db/Algebra/AlgebraicFractionAnswer/render?seed=42
    
    Returns the rendered HTML, answer blanks, and correct values.
    """
    db = get_db()
    
    # Get problem from database
    problem = db.get_by_id(problem_id)
    if not problem:
        raise HTTPException(404, f"Problem not found: {problem_id}")
    
    # Render using Python renderer
    renderer = get_pg_render_service()
    rendered = renderer.render_problem(problem['pg_source'], seed=seed)
    
    return {
        'problem_id': problem_id,
        'name': problem['name'],
        'seed': seed,
        'statement_html': rendered['statement_html'],
        'inputs': rendered['inputs'],
        'answers': rendered['answers'],
        'solution_html': rendered['solution_html'],
        'warnings': rendered.get('warnings', []),
        'errors': rendered.get('errors', []),
        'metadata': problem['metadata']
    }


@router.post("/{problem_id:path}/check")
def check_database_problem_answers(
    problem_id: str,
    request_data: Dict[str, Any] = Body(...)
) -> Dict[str, Any]:
    """
    Check student answers for a database problem.
    
    Request body:
    {
        "seed": 0,
        "inputs": {"AnSwEr0001": "5", "AnSwEr0002": "10"}
    }
    """
    db = get_db()
    
    seed = request_data.get('seed', 0)
    inputs = request_data.get('inputs', {})
    
    # Get problem
    problem = db.get_by_id(problem_id)
    if not problem:
        raise HTTPException(404, f"Problem not found: {problem_id}")
    
    # Check answers using renderer
    renderer = get_pg_render_service()
    results = renderer.check_answers(problem['pg_source'], seed=seed, student_inputs=inputs)
    
    return results

