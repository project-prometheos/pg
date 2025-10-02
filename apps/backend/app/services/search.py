"""Search service with vector search capabilities using sqlite-vec."""
from __future__ import annotations

import json
import numpy as np
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, or_

from app.models.database import (
    Problem, ProblemType, ProblemSubject, ProblemCategory, 
    ProblemKeyword, ProblemMacro, ProblemDocumentation
)


@dataclass
class SearchFilters:
    """Search filters for problem queries."""
    query: Optional[str] = None
    types: Optional[List[str]] = None
    subjects: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    macros: Optional[List[str]] = None
    limit: int = 50
    offset: int = 0


@dataclass
class SearchResult:
    """Search result with problem data and relevance score."""
    problem: Problem
    score: float
    matched_fields: List[str]


class VectorSearchService:
    """Service for vector-based semantic search."""
    
    def __init__(self, session: Session):
        self.session = session
        
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using a simple hash-based approach.
        
        In production, you would use a proper embedding model like:
        - OpenAI embeddings
        - Sentence transformers
        - Local embedding models
        """
        # Simple hash-based embedding for demo purposes
        # In production, replace with actual embedding model
        words = text.lower().split()
        embedding = [0.0] * 128  # 128-dimensional embedding
        
        for i, word in enumerate(words):
            hash_val = hash(word) % 128
            embedding[hash_val] += 1.0 / len(words)
            
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = [x / norm for x in embedding]
            
        return embedding
    
    def store_embedding(self, problem_id: str, content_type: str, text: str):
        """Store embedding for problem content."""
        embedding = self.generate_embedding(text)
        embedding_json = json.dumps(embedding)
        
        # Insert or update embedding
        self.session.execute(text("""
            INSERT OR REPLACE INTO problem_embeddings 
            (problem_id, content_type, embedding) 
            VALUES (:problem_id, :content_type, :embedding)
        """), {
            "problem_id": problem_id,
            "content_type": content_type,
            "embedding": embedding_json
        })
    
    def vector_search(self, query: str, content_type: str = "full_text", limit: int = 10) -> List[Tuple[str, float]]:
        """Perform vector similarity search."""
        query_embedding = self.generate_embedding(query)
        query_embedding_json = json.dumps(query_embedding)
        
        # Use sqlite-vec for similarity search
        results = self.session.execute(text("""
            SELECT problem_id, 
                   vec_distance_cosine(embedding, :query_embedding) as distance
            FROM problem_embeddings 
            WHERE content_type = :content_type
            ORDER BY distance ASC
            LIMIT :limit
        """), {
            "query_embedding": query_embedding_json,
            "content_type": content_type,
            "limit": limit
        }).fetchall()
        
        return [(row.problem_id, 1.0 - row.distance) for row in results]


class ProblemSearchService:
    """Main search service combining vector search with traditional filtering."""
    
    def __init__(self, session: Session):
        self.session = session
        self.vector_service = VectorSearchService(session)
    
    def search_problems(self, filters: SearchFilters) -> List[SearchResult]:
        """Search problems with filters and optional vector search."""
        query = self.session.query(Problem)
        
        # Apply filters
        if filters.types:
            query = query.join(ProblemType).filter(ProblemType.type.in_(filters.types))
            
        if filters.subjects:
            query = query.join(ProblemSubject).filter(ProblemSubject.subject.in_(filters.subjects))
            
        if filters.categories:
            query = query.join(ProblemCategory).filter(ProblemCategory.category.in_(filters.categories))
            
        if filters.keywords:
            query = query.join(ProblemKeyword).filter(ProblemKeyword.keyword.in_(filters.keywords))
            
        if filters.macros:
            query = query.join(ProblemMacro).filter(ProblemMacro.macro.in_(filters.macros))
        
        # Apply pagination
        query = query.offset(filters.offset).limit(filters.limit)
        
        problems = query.all()
        
        # If text query provided, perform vector search and reorder results
        if filters.query:
            vector_results = self.vector_search_with_filters(filters.query, filters)
            return self._combine_search_results(problems, vector_results, filters.query)
        else:
            return [SearchResult(problem=p, score=1.0, matched_fields=[]) for p in problems]
    
    def vector_search_with_filters(self, query: str, filters: SearchFilters) -> List[Tuple[str, float]]:
        """Perform vector search with additional filters."""
        # Build filter conditions for vector search
        filter_conditions = []
        params = {"query_embedding": json.dumps(self.vector_service.generate_embedding(query))}
        
        if filters.types:
            filter_conditions.append("problem_id IN (SELECT problem_id FROM problem_types WHERE type IN :types)")
            params["types"] = tuple(filters.types)
            
        if filters.subjects:
            filter_conditions.append("problem_id IN (SELECT problem_id FROM problem_subjects WHERE subject IN :subjects)")
            params["subjects"] = tuple(filters.subjects)
            
        if filters.categories:
            filter_conditions.append("problem_id IN (SELECT problem_id FROM problem_categories WHERE category IN :categories)")
            params["categories"] = tuple(filters.categories)
        
        where_clause = " AND ".join(filter_conditions) if filter_conditions else "1=1"
        
        sql = f"""
            SELECT problem_id, 
                   1.0 - vec_distance_cosine(embedding, :query_embedding) as score
            FROM problem_embeddings 
            WHERE content_type = 'full_text' AND {where_clause}
            ORDER BY score DESC
            LIMIT :limit
        """
        
        params["limit"] = filters.limit
        
        results = self.session.execute(text(sql), params).fetchall()
        return [(row.problem_id, row.score) for row in results]
    
    def _combine_search_results(self, problems: List[Problem], vector_results: List[Tuple[str, float]], query: str) -> List[SearchResult]:
        """Combine traditional search results with vector search scores."""
        # Create a map of problem_id to vector score
        vector_scores = {pid: score for pid, score in vector_results}
        
        results = []
        for problem in problems:
            score = vector_scores.get(problem.id, 0.0)
            matched_fields = self._find_matched_fields(problem, query)
            
            # Boost score if query matches in specific fields
            if matched_fields:
                score += 0.2 * len(matched_fields)
            
            results.append(SearchResult(
                problem=problem,
                score=min(score, 1.0),
                matched_fields=matched_fields
            ))
        
        # Sort by score descending
        results.sort(key=lambda x: x.score, reverse=True)
        return results
    
    def _find_matched_fields(self, problem: Problem, query: str) -> List[str]:
        """Find which fields match the query."""
        matched_fields = []
        query_lower = query.lower()
        
        if query_lower in problem.name.lower():
            matched_fields.append("name")
            
        if problem.description and query_lower in problem.description.lower():
            matched_fields.append("description")
            
        # Check keywords
        for keyword in problem.keywords:
            if query_lower in keyword.keyword.lower():
                matched_fields.append("keywords")
                break
                
        # Check subjects
        for subject in problem.subjects:
            if query_lower in subject.subject.lower():
                matched_fields.append("subjects")
                break
                
        return matched_fields
    
    def full_text_search(self, query: str, limit: int = 50) -> List[SearchResult]:
        """Perform full-text search using SQLite FTS5."""
        # Use FTS5 for full-text search
        fts_query = self.session.execute(text("""
            SELECT problem_id, 
                   bm25(problems_fts) as score
            FROM problems_fts 
            WHERE problems_fts MATCH :query
            ORDER BY bm25(problems_fts)
            LIMIT :limit
        """), {"query": query, "limit": limit}).fetchall()
        
        # Get full problem objects
        problem_ids = [row.problem_id for row in fts_query]
        problems = self.session.query(Problem).filter(Problem.id.in_(problem_ids)).all()
        
        # Create results with scores
        problem_map = {p.id: p for p in problems}
        results = []
        
        for row in fts_query:
            if row.problem_id in problem_map:
                results.append(SearchResult(
                    problem=problem_map[row.problem_id],
                    score=max(0.0, 1.0 - row.score / 100.0),  # Normalize BM25 score
                    matched_fields=["full_text"]
                ))
        
        return results
    
    def get_problems_by_category(self, category: str, limit: int = 50) -> List[Problem]:
        """Get problems by category."""
        return self.session.query(Problem).join(ProblemCategory).filter(
            ProblemCategory.category == category.lower()
        ).limit(limit).all()
    
    def get_problems_by_subject(self, subject: str, limit: int = 50) -> List[Problem]:
        """Get problems by subject."""
        return self.session.query(Problem).join(ProblemSubject).filter(
            ProblemSubject.subject == subject.lower()
        ).limit(limit).all()
    
    def get_problems_by_macro(self, macro: str, limit: int = 50) -> List[Problem]:
        """Get problems that use a specific macro."""
        return self.session.query(Problem).join(ProblemMacro).filter(
            ProblemMacro.macro == macro
        ).limit(limit).all()
    
    def get_related_problems(self, problem_id: str, limit: int = 10) -> List[Problem]:
        """Get related problems."""
        related_ids = self.session.execute(text("""
            SELECT related_problem_id 
            FROM problem_relations 
            WHERE problem_id = :problem_id
            LIMIT :limit
        """), {"problem_id": problem_id, "limit": limit}).fetchall()
        
        if not related_ids:
            return []
            
        related_problem_ids = [row.related_problem_id for row in related_ids]
        return self.session.query(Problem).filter(Problem.id.in_(related_problem_ids)).all()
    
    def get_all_categories(self) -> List[str]:
        """Get all available categories."""
        results = self.session.query(ProblemCategory.category).distinct().all()
        return [row.category for row in results]
    
    def get_all_subjects(self) -> List[str]:
        """Get all available subjects."""
        results = self.session.query(ProblemSubject.subject).distinct().all()
        return [row.subject for row in results]
    
    def get_all_types(self) -> List[str]:
        """Get all available types."""
        results = self.session.query(ProblemType.type).distinct().all()
        return [row.type for row in results]
    
    def get_all_macros(self) -> List[str]:
        """Get all available macros."""
        results = self.session.query(ProblemMacro.macro).distinct().all()
        return [row.macro for row in results]
