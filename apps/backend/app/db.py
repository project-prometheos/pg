"""Database access layer for WeBWorK problems."""

import sqlite3
import json
from typing import List, Dict, Any, Optional
from pathlib import Path


class ProblemDB:
    """Singleton database connection for problem queries."""
    
    _instance: Optional['ProblemDB'] = None
    
    def __init__(self, db_path: str = "problems.db"):
        """Initialize database connection."""
        # If relative path, look in project root (two levels up from app/)
        db_path_obj = Path(db_path)
        if not db_path_obj.is_absolute():
            # apps/backend/app/db.py -> go up 3 levels to project root
            project_root = Path(__file__).parent.parent.parent.parent
            self.db_path = project_root / db_path
        else:
            self.db_path = db_path_obj
        
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"Database not found: {self.db_path}\n"
                "Run: python scripts/import_problems.py"
            )
        
        self.conn = sqlite3.connect(
            str(self.db_path),
            check_same_thread=False,
            timeout=10.0
        )
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA query_only = OFF")
    
    @classmethod
    def get_instance(cls, db_path: str = "problems.db") -> 'ProblemDB':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls(db_path)
        return cls._instance
    
    def search(
        self,
        query: Optional[str] = None,
        types: Optional[List[str]] = None,
        subjects: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        collection: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Search problems with optional filters."""
        
        params: List[Any] = []
        
        if query:
            # Full-text search with FTS5
            sql = """
                SELECT p.*, bm25(problems_fts) as score
                FROM problems p
                JOIN problems_fts ON p.rowid = problems_fts.rowid
                WHERE problems_fts MATCH ?
            """
            params.append(query)
        else:
            # No query, just filtering
            sql = "SELECT *, 1.0 as score FROM problems WHERE 1=1"
        
        # Add filters
        if collection:
            sql += " AND source_collection = ?"
            params.append(collection)
        
        if types:
            placeholders = ','.join('?' * len(types))
            sql += f"""
                AND EXISTS (
                    SELECT 1 FROM json_each(metadata, '$.types')
                    WHERE value IN ({placeholders})
                )
            """
            params.extend(types)
        
        if subjects:
            placeholders = ','.join('?' * len(subjects))
            sql += f"""
                AND EXISTS (
                    SELECT 1 FROM json_each(metadata, '$.subjects')
                    WHERE value IN ({placeholders})
                )
            """
            params.extend(subjects)
        
        if categories:
            placeholders = ','.join('?' * len(categories))
            sql += f"""
                AND EXISTS (
                    SELECT 1 FROM json_each(metadata, '$.categories')
                    WHERE value IN ({placeholders})
                )
            """
            params.extend(categories)
        
        # Order and limit
        sql += " ORDER BY score DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        rows = self.conn.execute(sql, params).fetchall()
        return [self._row_to_dict(row) for row in rows]
    
    def get_by_id(self, problem_id: str) -> Optional[Dict[str, Any]]:
        """Get problem by ID."""
        row = self.conn.execute(
            "SELECT * FROM problems WHERE id = ?",
            (problem_id,)
        ).fetchone()
        
        return self._row_to_dict(row) if row else None
    
    def get_related(self, problem_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get related problems."""
        problem = self.get_by_id(problem_id)
        if not problem:
            return []
        
        related_ids = problem['metadata'].get('related', [])
        if not related_ids:
            return []
        
        # Get related problems
        placeholders = ','.join('?' * len(related_ids[:limit]))
        sql = f"SELECT * FROM problems WHERE id IN ({placeholders})"
        
        rows = self.conn.execute(sql, related_ids[:limit]).fetchall()
        return [self._row_to_dict(row) for row in rows]
    
    def get_facets(self, collection: Optional[str] = None) -> Dict[str, List[str]]:
        """Get all unique filter values."""
        facets = {
            'types': set(),
            'subjects': set(),
            'categories': set(),
            'collections': set()
        }
        
        where_clause = ""
        params = []
        if collection:
            where_clause = "WHERE source_collection = ?"
            params.append(collection)
        
        # Get metadata from all problems
        rows = self.conn.execute(
            f"SELECT metadata, source_collection FROM problems {where_clause}",
            params
        ).fetchall()
        
        for row in rows:
            meta = json.loads(row['metadata'])
            facets['types'].update(meta.get('types', []))
            facets['subjects'].update(meta.get('subjects', []))
            facets['categories'].update(meta.get('categories', []))
            facets['collections'].add(row['source_collection'])
        
        return {k: sorted(v) for k, v in facets.items()}
    
    def get_collections(self) -> List[Dict[str, Any]]:
        """Get all problem collections."""
        rows = self.conn.execute(
            "SELECT id, name, description, problem_count FROM collections ORDER BY name"
        ).fetchall()
        
        return [dict(row) for row in rows]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        stats = {}
        
        # Total problems
        cursor = self.conn.execute("SELECT COUNT(*) FROM problems")
        stats['total_problems'] = cursor.fetchone()[0]
        
        # Problems by collection
        cursor = self.conn.execute("""
            SELECT source_collection, COUNT(*) as count
            FROM problems
            GROUP BY source_collection
        """)
        stats['by_collection'] = {row[0]: row[1] for row in cursor}
        
        # Top subjects
        cursor = self.conn.execute("""
            SELECT json_each.value as subject, COUNT(*) as count
            FROM problems, json_each(metadata, '$.subjects')
            GROUP BY subject
            ORDER BY count DESC
            LIMIT 10
        """)
        stats['top_subjects'] = [(row[0], row[1]) for row in cursor]
        
        return stats
    
    def increment_view_count(self, problem_id: str):
        """Increment view count for a problem."""
        self.conn.execute("""
            INSERT INTO problem_stats (problem_id, view_count, last_accessed)
            VALUES (?, 1, unixepoch())
            ON CONFLICT(problem_id) DO UPDATE SET
                view_count = view_count + 1,
                last_accessed = unixepoch()
        """, (problem_id,))
        self.conn.commit()
    
    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
        """Convert SQLite row to dictionary."""
        d = dict(row)
        
        # Parse JSON metadata
        if d.get('metadata'):
            d['metadata'] = json.loads(d['metadata'])
        
        return d
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        """Cleanup on deletion."""
        self.close()
