# Implementation Plan: Portable Problem Database for WeBWorK PG

## Executive Summary

**Goal**: Create a portable, searchable database of PG problems that integrates seamlessly with existing WeBWorK infrastructure while maintaining simplicity and developer ergonomics.

**Key Insight**: The existing Perl infrastructure (`SampleProblemParser.pm`) is **already functional**. Instead of rewriting everything, we should:
1. **Leverage existing Perl parser** for one-time migration
2. **Build minimal Python layer** for API/search
3. **Keep PG source as source-of-truth** (don't parse on-the-fly)

## Current State (Strengths to Preserve)

✅ **161+ Sample Problems** in `tutorial/sample-problems/`
- Already have rich metadata
- Proven PGML structure
- Documentation embedded

✅ **SampleProblemParser.pm** (Perl)
- Production-ready metadata extraction
- Handles all edge cases
- Generates HTML documentation

✅ **FastAPI Backend** (Python)
- Modern, fast, typed
- Problem generation via `problemkit`

✅ **React Frontend**
- Component-based
- Already has problem rendering

## Architecture Decision: Hybrid Approach

### Philosophy: "Don't Rewrite What Works"

```
┌─────────────────────────────────────────────────────────────┐
│  ONE-TIME MIGRATION (Use existing Perl)                     │
│  SampleProblemParser.pm → problems.db                       │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  RUNTIME (Pure Python + SQLite)                             │
│  problems.db → FastAPI → React                              │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Strategy

### Phase 1: One-Time Migration (Use Perl Parser)

**Why**: The Perl parser is battle-tested and handles all edge cases.

```perl
#!/usr/bin/env perl
# scripts/export_problems_to_json.pl

use strict;
use warnings;
use JSON::PP;
use lib 'lib';
use SampleProblemParser qw(generateMetadata);

my $metadata = generateMetadata('tutorial/sample-problems', verbose => 1);

# Export to JSON for Python consumption
open my $fh, '>:encoding(UTF-8)', 'problems_metadata.json';
print $fh encode_json($metadata);
close $fh;

print "Exported ", scalar(keys %$metadata), " problems to problems_metadata.json\n";
```

**Benefit**: 
- ✅ Reuses 100+ LOC of proven parsing logic
- ✅ No need to replicate regex patterns in Python
- ✅ One-time operation, performance doesn't matter

### Phase 2: Minimal SQLite Schema

**Design Principle**: Store parsed data, not raw PG (for search speed)

```sql
-- Minimal schema for runtime performance
CREATE TABLE problems (
    id TEXT PRIMARY KEY,              -- "Algebra/LinearInequality"
    name TEXT NOT NULL,               -- "Linear Inequality"
    description TEXT,
    pg_source TEXT NOT NULL,          -- Full PG file content
    file_path TEXT NOT NULL,          -- Relative path
    
    -- Metadata as JSON (SQLite 3.38+ has excellent JSON support)
    metadata JSON NOT NULL,           -- { types, subjects, categories, keywords, macros, related, ... }
    
    created_at INTEGER DEFAULT (unixepoch()),
    updated_at INTEGER DEFAULT (unixepoch())
);

-- Full-text search (built-in FTS5)
CREATE VIRTUAL TABLE problems_fts USING fts5(
    id UNINDEXED,
    name,
    description,
    keywords,
    content='problems',
    content_rowid='rowid'
);

-- Triggers for FTS sync
CREATE TRIGGER problems_fts_insert AFTER INSERT ON problems BEGIN
    INSERT INTO problems_fts(rowid, id, name, description, keywords)
    SELECT new.rowid, new.id, new.name, new.description, 
           json_extract(new.metadata, '$.keywords');
END;

-- JSON indexes for fast filtering (SQLite 3.9+)
CREATE INDEX idx_types ON problems(json_extract(metadata, '$.types'));
CREATE INDEX idx_subjects ON problems(json_extract(metadata, '$.subjects'));
```

**Why this schema?**
- ✅ **Portable**: No extensions, pure SQLite
- ✅ **Fast**: JSON indexes are performant enough
- ✅ **Simple**: 3 tables total (problems + FTS + triggers)
- ✅ **Flexible**: Easy to add metadata fields without migrations

### Phase 3: Import Script (Python calls Perl)

```python
#!/usr/bin/env python3
# scripts/import_problems.py

import json
import sqlite3
import subprocess
from pathlib import Path

def run_perl_parser():
    """Use existing Perl parser to extract metadata."""
    print("📦 Running Perl parser...")
    subprocess.run([
        'perl', 
        'scripts/export_problems_to_json.pl'
    ], check=True)
    
    with open('problems_metadata.json') as f:
        return json.load(f)

def init_database(db_path='problems.db'):
    """Initialize SQLite database."""
    conn = sqlite3.connect(db_path)
    
    # Load schema
    with open('scripts/schema.sql') as f:
        conn.executescript(f.read())
    
    return conn

def import_problems(metadata, conn):
    """Import parsed problems into SQLite."""
    problems_dir = Path('tutorial/sample-problems')
    count = 0
    
    for filename, meta in metadata.items():
        pg_file = problems_dir / meta['dir'] / filename
        
        if not pg_file.exists():
            print(f"⚠️  Skipping {filename} (file not found)")
            continue
        
        with open(pg_file, 'r', encoding='utf-8') as f:
            pg_source = f.read()
        
        # Prepare metadata JSON
        metadata_json = json.dumps({
            'types': meta.get('types', []),
            'subjects': meta.get('subjects', []),
            'categories': meta.get('categories', []),
            'keywords': [k.lower() for k in meta.get('keywords', [])],
            'macros': meta.get('macros', []),
            'related': meta.get('related', [])
        })
        
        # Insert into database
        conn.execute("""
            INSERT INTO problems (id, name, description, pg_source, file_path, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            f"{meta['dir']}/{filename}".replace('.pg', ''),
            meta['name'],
            meta.get('description', ''),
            pg_source,
            f"{meta['dir']}/{filename}",
            metadata_json
        ))
        
        count += 1
        print(f"✓ {meta['name']}")
    
    conn.commit()
    return count

if __name__ == '__main__':
    print("🚀 WeBWorK Problem Database Import\n")
    
    # Step 1: Parse using Perl
    metadata = run_perl_parser()
    print(f"📊 Found {len(metadata)} problems\n")
    
    # Step 2: Initialize database
    conn = init_database()
    print("✓ Database initialized\n")
    
    # Step 3: Import problems
    count = import_problems(metadata, conn)
    
    print(f"\n✅ Successfully imported {count} problems")
    print(f"📂 Database: problems.db")
    
    conn.close()
```

**One-command setup:**
```bash
python scripts/import_problems.py
```

### Phase 4: Minimal Backend (Repository + Service)

```python
# app/db.py (Database access - 80 LOC)
import sqlite3
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

class ProblemDB:
    """Singleton database connection."""
    _instance = None
    
    def __init__(self, db_path: str = "problems.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
    
    @classmethod
    def get(cls) -> 'ProblemDB':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def search(self, query: str = None, types: List[str] = None,
               subjects: List[str] = None, limit: int = 50) -> List[Dict]:
        """Search problems with optional filters."""
        
        if query:
            # Full-text search
            sql = """
                SELECT p.*, bm25(problems_fts) as score
                FROM problems p
                JOIN problems_fts ON p.rowid = problems_fts.rowid
                WHERE problems_fts MATCH ?
            """
            params = [query]
        else:
            sql = "SELECT *, 1.0 as score FROM problems WHERE 1=1"
            params = []
        
        # Add filters
        if types:
            sql += " AND EXISTS (SELECT 1 FROM json_each(metadata, '$.types') WHERE value IN (" + ','.join('?' * len(types)) + "))"
            params.extend(types)
        
        if subjects:
            sql += " AND EXISTS (SELECT 1 FROM json_each(metadata, '$.subjects') WHERE value IN (" + ','.join('?' * len(subjects)) + "))"
            params.extend(subjects)
        
        sql += f" ORDER BY score LIMIT {limit}"
        
        rows = self.conn.execute(sql, params).fetchall()
        return [self._row_to_dict(r) for r in rows]
    
    def get_by_id(self, problem_id: str) -> Optional[Dict]:
        """Get problem by ID."""
        row = self.conn.execute("SELECT * FROM problems WHERE id = ?", (problem_id,)).fetchone()
        return self._row_to_dict(row) if row else None
    
    def get_facets(self) -> Dict[str, List[str]]:
        """Get all unique filter values."""
        facets = {'types': set(), 'subjects': set(), 'categories': set()}
        
        rows = self.conn.execute("SELECT metadata FROM problems").fetchall()
        for row in rows:
            meta = json.loads(row['metadata'])
            facets['types'].update(meta.get('types', []))
            facets['subjects'].update(meta.get('subjects', []))
            facets['categories'].update(meta.get('categories', []))
        
        return {k: sorted(v) for k, v in facets.items()}
    
    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
        d = dict(row)
        if d.get('metadata'):
            d['metadata'] = json.loads(d['metadata'])
        return d
```

```python
# app/api.py (FastAPI routes - 60 LOC)
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from .db import ProblemDB

router = APIRouter(prefix="/api/problems")

class ProblemSummary(BaseModel):
    id: str
    name: str
    description: str
    metadata: dict

class SearchResponse(BaseModel):
    problems: List[ProblemSummary]
    total: int
    facets: dict

@router.get("/search")
def search_problems(
    q: Optional[str] = None,
    types: Optional[str] = None,
    subjects: Optional[str] = None,
    limit: int = Query(50, le=100)
) -> SearchResponse:
    """Search problems."""
    db = ProblemDB.get()
    
    results = db.search(
        query=q,
        types=types.split(',') if types else None,
        subjects=subjects.split(',') if subjects else None,
        limit=limit
    )
    
    return SearchResponse(
        problems=[ProblemSummary(**r) for r in results],
        total=len(results),
        facets=db.get_facets()
    )

@router.get("/{problem_id}")
def get_problem(problem_id: str) -> ProblemSummary:
    """Get problem details including PG source."""
    db = ProblemDB.get()
    problem = db.get_by_id(problem_id)
    
    if not problem:
        raise HTTPException(404, "Problem not found")
    
    return ProblemSummary(**problem)
```

### Phase 5: Integration with Existing Problem System

```python
# app/services/problem_loader.py
from typing import Optional
from ..db import ProblemDB
from .problems import ProblemService  # Existing service

class HybridProblemService(ProblemService):
    """
    Extends existing ProblemService to load from database.
    Falls back to registry if not in database.
    """
    
    def __init__(self):
        super().__init__()
        self.db = ProblemDB.get()
    
    def generate_problem(self, problem_id: str, seed: int):
        """
        1. Try to load from database (sample problems)
        2. Fall back to registry (programmatic problems)
        """
        
        # Try database first (for sample problems)
        db_problem = self.db.get_by_id(problem_id)
        
        if db_problem:
            # TODO: Render PG source with seed
            # For now, return metadata + source
            return {
                'problem_id': problem_id,
                'seed': seed,
                'name': db_problem['name'],
                'pg_source': db_problem['pg_source'],
                'metadata': db_problem['metadata']
            }
        
        # Fall back to existing registry-based generation
        return super().generate_problem(problem_id, seed)
    
    def list_problems(self) -> list:
        """List all available problems (database + registry)."""
        db_problems = self.db.search(limit=1000)
        registry_problems = super().list_problems()
        
        return db_problems + registry_problems
```

### Phase 6: Frontend Search Component (Reuse existing)

```typescript
// apps/web/src/pages/SearchPage.tsx
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';

interface SearchFilters {
  query?: string;
  types?: string[];
  subjects?: string[];
}

export default function SearchPage() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState<SearchFilters>({});
  
  const { data, isLoading } = useQuery({
    queryKey: ['problems', filters],
    queryFn: () => fetch(`/api/problems/search?${new URLSearchParams({
      q: filters.query || '',
      types: filters.types?.join(',') || '',
      subjects: filters.subjects?.join(',') || ''
    })}`).then(r => r.json())
  });
  
  return (
    <div className="max-w-7xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Problem Library</h1>
      
      {/* Search bar */}
      <input
        type="text"
        placeholder="Search problems..."
        onChange={(e) => setFilters({ ...filters, query: e.target.value })}
        className="w-full p-3 border rounded-lg mb-6"
      />
      
      {/* Facets (types, subjects) */}
      <div className="grid grid-cols-4 gap-6">
        <div className="col-span-1">
          <h3 className="font-semibold mb-2">Subjects</h3>
          {data?.facets.subjects.map((s: string) => (
            <label key={s} className="block">
              <input
                type="checkbox"
                onChange={(e) => {
                  const subjects = e.target.checked
                    ? [...(filters.subjects || []), s]
                    : filters.subjects?.filter(x => x !== s);
                  setFilters({ ...filters, subjects });
                }}
              /> {s}
            </label>
          ))}
        </div>
        
        {/* Results */}
        <div className="col-span-3">
          {isLoading ? 'Loading...' : (
            data?.problems.map((p: any) => (
              <div
                key={p.id}
                onClick={() => navigate(`/p/${p.id}`)}
                className="p-4 border rounded-lg mb-2 cursor-pointer hover:bg-gray-50"
              >
                <h3 className="font-semibold">{p.name}</h3>
                <p className="text-sm text-gray-600">{p.description}</p>
                <div className="flex gap-2 mt-2">
                  {p.metadata.subjects?.map((s: string) => (
                    <span key={s} className="text-xs bg-blue-100 px-2 py-1 rounded">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
```

## File Structure (Minimal)

```
pg/
├── scripts/
│   ├── export_problems_to_json.pl    # Perl: Export metadata (30 LOC)
│   ├── import_problems.py            # Python: Import to SQLite (80 LOC)
│   └── schema.sql                    # SQLite schema (50 LOC)
│
├── apps/backend/app/
│   ├── db.py                         # Database access (80 LOC)
│   ├── api.py                        # FastAPI routes (60 LOC)
│   └── services/
│       └── problem_loader.py         # Hybrid loader (40 LOC)
│
├── apps/web/src/
│   └── pages/
│       └── SearchPage.tsx            # Search UI (100 LOC)
│
├── problems.db                       # SQLite database (generated)
└── problems_metadata.json            # Intermediate (generated)
```

**Total new code: ~440 LOC**

## Setup & Usage

### One-Time Setup
```bash
# 1. Import problems (calls Perl parser → SQLite)
python scripts/import_problems.py

# 2. Start backend (FastAPI auto-detects problems.db)
cd apps/backend
uvicorn app.main:app --reload

# 3. Start frontend
cd apps/web
npm run dev
```

### Usage
```bash
# Search API
curl "http://localhost:8000/api/problems/search?q=derivative"
curl "http://localhost:8000/api/problems/search?subjects=calculus&types=sample"

# Get problem
curl "http://localhost:8000/api/problems/Algebra/LinearInequality"

# Frontend
open http://localhost:3000/search
```

## Benefits of This Approach

### ✅ Portability
- **Pure SQLite**: No extensions, works everywhere
- **Single file**: `problems.db` is portable
- **No Perl runtime dependency**: Only needed for one-time import

### ✅ Developer Experience
- **One command**: `python scripts/import_problems.py`
- **Fast iteration**: Database persists, no re-parsing
- **Familiar tools**: SQLite, FastAPI, React

### ✅ Simplicity
- **~440 LOC** of new code
- **Reuses existing**: Perl parser, React components
- **No ORM complexity**: Direct SQLite queries

### ✅ SOLID Principles
- **Single Responsibility**: DB layer, API layer, UI layer
- **Open/Closed**: Easy to extend search without modifying core
- **Dependency Inversion**: HybridProblemService extends existing

### ✅ Integration
- **Non-breaking**: Existing problem generation still works
- **Gradual migration**: Database problems supplement registry
- **Fallback**: Registry-based problems as backup

## Migration Path

### Day 1: Setup Database
```bash
python scripts/import_problems.py
```

### Day 2: Add Search API
- Copy `app/db.py` and `app/api.py`
- Add routes to `main.py`

### Day 3: Add Frontend
- Copy `SearchPage.tsx`
- Add route to `App.tsx`

### Day 4+: Iterate
- Improve search ranking
- Add filters
- Enhance UI

## Future Enhancements (Optional)

### Phase 7: Better Search Ranking
```sql
-- Add relevance scoring
CREATE TABLE problem_stats (
    problem_id TEXT PRIMARY KEY,
    views INTEGER DEFAULT 0,
    uses INTEGER DEFAULT 0,
    avg_rating REAL,
    FOREIGN KEY (problem_id) REFERENCES problems(id)
);
```

### Phase 8: Problem Collections
```sql
-- User-curated problem sets
CREATE TABLE collections (
    id TEXT PRIMARY KEY,
    name TEXT,
    problem_ids JSON  -- ["prob1", "prob2", ...]
);
```

### Phase 9: Vector Search (Optional)
If needed later, add embeddings table:
```sql
CREATE TABLE problem_embeddings (
    problem_id TEXT PRIMARY KEY,
    embedding BLOB,  -- 768-dim vector
    FOREIGN KEY (problem_id) REFERENCES problems(id)
);
```

## Comparison: Hybrid vs Pure Rewrite

| Aspect | Hybrid (This Plan) | Pure Rewrite (Original) |
|--------|-------------------|------------------------|
| **LOC** | 440 | 2000+ |
| **Setup** | 1 command | 6+ steps |
| **Dependencies** | 0 runtime | sqlite-vec, alembic |
| **Perl reuse** | ✅ Yes | ❌ Duplicate in Python |
| **Risk** | Low (proven parser) | High (new regex) |
| **Time to MVP** | 1 day | 1-2 weeks |
| **Portability** | ✅ Perfect | ⚠️ Needs extension |

## Conclusion

This plan achieves all requirements with:
1. **Minimal code**: 440 LOC vs 2000+
2. **Reuse**: Leverages battle-tested Perl parser
3. **Portability**: Pure SQLite, no extensions
4. **Integration**: Works with existing system
5. **SOLID**: Clean separation of concerns
6. **DX**: One-command setup

The key insight: **Don't rewrite what works**. Use Perl for one-time migration, Python for runtime performance.

