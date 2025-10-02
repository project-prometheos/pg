"""Search API endpoints for WeBWorK problems."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Query, HTTPException, Body
from pydantic import BaseModel, Field

from ..db import ProblemDB
from ..services.pg_renderer_python import get_pg_render_service


router = APIRouter(prefix="/api/problems", tags=["problems"])


class ProblemMetadata(BaseModel):
    """Problem metadata structure."""
    types: List[str] = []
    subjects: List[str] = []
    categories: List[str] = []
    keywords: List[str] = []
    macros: List[str] = []
    related: List[str] = []
    db_subjects: List[str] = []
    db_chapter: List[str] = []
    db_section: List[str] = []
    
    class Config:
        extra = "allow"  # Allow extra fields from database


class ProblemSummary(BaseModel):
    """Problem summary for search results."""
    id: str
    name: str
    description: str
    file_path: str
    source_collection: str
    metadata: ProblemMetadata
    created_at: int
    score: Optional[float] = None


class ProblemDetail(ProblemSummary):
    """Full problem details including source."""
    pg_source: str


class SearchResponse(BaseModel):
    """Search response with results and metadata."""
    problems: List[ProblemSummary]
    total: int
    limit: int
    offset: int
    query: Optional[str] = None
    facets: dict


class FacetsResponse(BaseModel):
    """Available facets for filtering."""
    types: List[str]
    subjects: List[str]
    categories: List[str]
    collections: List[str]


class CollectionInfo(BaseModel):
    """Problem collection information."""
    id: str
    name: str
    description: Optional[str]
    problem_count: int


class StatsResponse(BaseModel):
    """Database statistics."""
    total_problems: int
    by_collection: dict
    top_subjects: List[tuple]


# Dependency
def get_db() -> ProblemDB:
    """Get database instance."""
    return ProblemDB.get_instance()


@router.get("/search", response_model=SearchResponse)
def search_problems(
    q: Optional[str] = Query(None, description="Search query"),
    types: Optional[str] = Query(None, description="Comma-separated problem types"),
    subjects: Optional[str] = Query(None, description="Comma-separated subjects"),
    categories: Optional[str] = Query(None, description="Comma-separated categories"),
    collection: Optional[str] = Query(None, description="Filter by collection"),
    limit: int = Query(50, ge=1, le=100, description="Results per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
) -> SearchResponse:
    """
    Search problems with optional filters.
    
    Examples:
    - /api/problems/search?q=derivative
    - /api/problems/search?subjects=calculus&types=sample
    - /api/problems/search?q=limit&subjects=calculus,algebra&limit=20
    """
    db = get_db()
    
    # Parse comma-separated filters
    types_list = types.split(',') if types else None
    subjects_list = subjects.split(',') if subjects else None
    categories_list = categories.split(',') if categories else None
    
    # Search
    results = db.search(
        query=q,
        types=types_list,
        subjects=subjects_list,
        categories=categories_list,
        collection=collection,
        limit=limit,
        offset=offset
    )
    
    # Get facets for current search
    facets = db.get_facets(collection=collection)
    
    # Convert to response models
    problems = []
    for r in results:
        problems.append(ProblemSummary(
            id=r['id'],
            name=r['name'],
            description=r['description'],
            file_path=r['file_path'],
            source_collection=r['source_collection'],
            metadata=ProblemMetadata(**r['metadata']),
            created_at=r['created_at'],
            score=r.get('score')
        ))
    
    return SearchResponse(
        problems=problems,
        total=len(problems),
        limit=limit,
        offset=offset,
        query=q,
        facets=facets
    )


@router.get("/{problem_id:path}", response_model=ProblemDetail)
def get_problem(problem_id: str) -> ProblemDetail:
    """
    Get full problem details including PG source.
    
    Example: /api/problems/Algebra/LinearInequality
    """
    db = get_db()
    
    problem = db.get_by_id(problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail=f"Problem not found: {problem_id}")
    
    # Increment view count
    db.increment_view_count(problem_id)
    
    return ProblemDetail(
        id=problem['id'],
        name=problem['name'],
        description=problem['description'],
        file_path=problem['file_path'],
        source_collection=problem['source_collection'],
        metadata=ProblemMetadata(**problem['metadata']),
        created_at=problem['created_at'],
        pg_source=problem['pg_source']
    )


@router.get("/{problem_id:path}/related", response_model=List[ProblemSummary])
def get_related_problems(
    problem_id: str,
    limit: int = Query(10, ge=1, le=50)
) -> List[ProblemSummary]:
    """Get related problems."""
    db = get_db()
    
    related = db.get_related(problem_id, limit=limit)
    
    return [
        ProblemSummary(
            id=r['id'],
            name=r['name'],
            description=r['description'],
            file_path=r['file_path'],
            source_collection=r['source_collection'],
            metadata=ProblemMetadata(**r['metadata']),
            created_at=r['created_at']
        )
        for r in related
    ]


@router.get("/facets/all", response_model=FacetsResponse)
def get_facets(
    collection: Optional[str] = Query(None, description="Filter by collection")
) -> FacetsResponse:
    """Get available filter options."""
    db = get_db()
    facets = db.get_facets(collection=collection)
    
    return FacetsResponse(**facets)


@router.get("/collections/list", response_model=List[CollectionInfo])
def list_collections() -> List[CollectionInfo]:
    """List all problem collections."""
    db = get_db()
    collections = db.get_collections()
    
    return [CollectionInfo(**c) for c in collections]


@router.get("/stats", response_model=StatsResponse)
def get_statistics() -> StatsResponse:
    """Get database statistics."""
    db = get_db()
    stats = db.get_stats()
    
    return StatsResponse(**stats)


# ============================================================================
# Database Problem Rendering Endpoints (Python PG Renderer)
# ============================================================================

@router.get("/db/{problem_id:path}/render", tags=["database", "rendering"])
def render_database_problem(
    problem_id: str,
    seed: int = Query(0, ge=0, description="Random seed for problem variation")
) -> Dict[str, Any]:
    """
    Render a database problem with the given seed using Python PG renderer.
    
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


@router.post("/db/{problem_id:path}/check", tags=["database", "checking"])
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
