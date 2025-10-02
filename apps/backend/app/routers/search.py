"""Dedicated search API endpoints."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Query
from pydantic import BaseModel

from ..db import ProblemDB


router = APIRouter(prefix="/api", tags=["search"])


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
        extra = "allow"


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


class SearchResponse(BaseModel):
    """Search response with results and metadata."""
    problems: List[ProblemSummary]
    total: int
    limit: int
    offset: int
    query: Optional[str] = None
    facets: Dict[str, List[str]]


def get_db() -> ProblemDB:
    """Get database instance."""
    return ProblemDB.get_instance()


@router.get("/problems/search", response_model=SearchResponse)
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
    
    This endpoint is separate from /api/problems/{id} to avoid routing conflicts.
    
    Examples:
    - /api/problems/search?q=derivative
    - /api/problems/search?subjects=calculus&types=sample
    - /api/problems/search?limit=20
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


@router.get("/problems/facets", response_model=Dict[str, List[str]])
def get_all_facets(
    collection: Optional[str] = Query(None, description="Filter by collection")
) -> Dict[str, List[str]]:
    """Get all available facet values for filtering."""
    db = get_db()
    return db.get_facets(collection=collection)
