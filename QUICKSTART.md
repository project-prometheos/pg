# Quick Start Guide: WeBWorK Problem Database

## Installation (< 5 minutes)

### Prerequisites
- Python 3.8+
- Perl 5.x (already installed if you have WeBWorK PG)
- Node.js 18+ (for frontend)

### Step 1: Import Sample Problems

```bash
# Make import script executable
chmod +x scripts/import_problems.py

# Run import (creates problems.db)
python scripts/import_problems.py
```

**Expected output**:
```
🚀 WeBWorK Problem Database Import
==================================================

📦 Running Perl parser to extract metadata...
Found 161 problems

📊 Initializing database...
✓ Database initialized: /path/to/pg/problems.db

📚 Importing problems from collection: tutorial
  ✓ Linear Inequality
  ✓ Mean and Standard Deviation
  ✓ Draggable Trigonometry Identity
  ...

✅ Imported 161 problems

📊 Database Statistics
==================================================
  tutorial: 161 problems

  Total: 161 problems

📚 Subject Distribution (top 10)
  algebra: 45 problems
  calculus: 38 problems
  statistics: 22 problems
  ...

✅ Import completed successfully!
```

### Step 2: Start Backend

```bash
cd apps/backend

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Start Frontend (Optional)

```bash
cd apps/web

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

### Step 4: Test the API

```bash
# Search for calculus problems
curl "http://localhost:8000/api/problems/search?q=derivative"

# Search with filters
curl "http://localhost:8000/api/problems/search?subjects=algebra&types=sample"

# Get specific problem
curl "http://localhost:8000/api/problems/Algebra/LinearInequality"

# Get database stats
curl "http://localhost:8000/api/problems/stats"

# Get available filters
curl "http://localhost:8000/api/problems/facets/all"
```

## API Examples

### 1. **Basic Search**
```bash
curl "http://localhost:8000/api/problems/search?q=derivative"
```

Response:
```json
{
  "problems": [
    {
      "id": "Calculus/DerivativeBasic",
      "name": "Basic Derivative Problem",
      "description": "Find the derivative using power rule",
      "source_collection": "tutorial",
      "metadata": {
        "types": ["sample"],
        "subjects": ["calculus"],
        "keywords": ["derivative", "power rule"]
      },
      "score": 0.95
    }
  ],
  "total": 1,
  "query": "derivative",
  "facets": {
    "subjects": ["algebra", "calculus", "statistics"],
    "types": ["sample", "technique"]
  }
}
```

### 2. **Filtered Search**
```bash
curl "http://localhost:8000/api/problems/search?subjects=calculus,algebra&limit=10"
```

### 3. **Get Problem Details**
```bash
curl "http://localhost:8000/api/problems/Algebra/LinearInequality"
```

Response includes full PG source:
```json
{
  "id": "Algebra/LinearInequality",
  "name": "Linear Inequality",
  "pg_source": "DOCUMENT();\nloadMacros('PGstandard.pl', ...);\n...",
  "metadata": { ... }
}
```

### 4. **Get Related Problems**
```bash
curl "http://localhost:8000/api/problems/Algebra/LinearInequality/related"
```

### 5. **Browse by Subject**
```bash
# Get facets first
curl "http://localhost:8000/api/problems/facets/all"

# Then filter by subject
curl "http://localhost:8000/api/problems/search?subjects=statistics"
```

## Python SDK Usage

```python
import requests

BASE_URL = "http://localhost:8000"

# Search problems
response = requests.get(f"{BASE_URL}/api/problems/search", params={
    "q": "derivative",
    "subjects": "calculus",
    "limit": 20
})
problems = response.json()['problems']

for problem in problems:
    print(f"{problem['name']} - {problem['id']}")

# Get specific problem
problem_id = "Algebra/LinearInequality"
response = requests.get(f"{BASE_URL}/api/problems/{problem_id}")
problem = response.json()

print(f"Name: {problem['name']}")
print(f"PG Source:\n{problem['pg_source']}")
```

## Frontend Usage

1. Open browser: http://localhost:3000
2. Navigate to: http://localhost:3000/search
3. Use search interface to browse problems

## Directory Structure

```
pg/
├── problems.db              # SQLite database (created by import)
├── problems_metadata.json   # Intermediate JSON (created by Perl parser)
│
├── scripts/
│   ├── schema.sql           # Database schema
│   ├── export_problems_to_json.pl   # Perl parser wrapper
│   └── import_problems.py   # Main import script
│
├── apps/backend/
│   └── app/
│       ├── db.py            # Database access layer
│       └── routers/
│           └── problems_search.py   # Search API
│
└── tutorial/sample-problems/   # Source PG files (161 problems)
```

## Common Issues

### Issue: "Database not found"
**Solution**: Run `python scripts/import_problems.py` first

### Issue: "Perl parser failed"
**Solution**: Make sure you're in the PG root directory and have Perl installed
```bash
# Check Perl
perl --version

# Check if SampleProblemParser.pm exists
ls lib/SampleProblemParser.pm
```

### Issue: "Module 'JSON::PP' not found"
**Solution**: Install Perl JSON module
```bash
cpan JSON::PP
# or
cpanm JSON::PP
```

### Issue: "Port 8000 already in use"
**Solution**: Use different port
```bash
uvicorn app.main:app --reload --port 8001
```

## Next Steps

### Import More Problems (OPL)

```bash
# Clone Open Problem Library
git clone --depth 1 https://github.com/openwebwork/webwork-open-problem-library.git

# Import a specific collection (e.g., FortLewis)
# First, create import_opl.py script (see PROBLEM_SOURCES.md)
python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/FortLewis
```

### Integrate with Existing Problem System

The search API can coexist with existing problem generation:

```python
# apps/backend/app/services/hybrid_loader.py
from ..db import ProblemDB

def load_problem(problem_id: str, seed: int):
    """Load from database or registry."""
    
    # Try database first
    db = ProblemDB.get_instance()
    problem = db.get_by_id(problem_id)
    
    if problem:
        # Render PG source with seed
        return render_pg_problem(problem['pg_source'], seed)
    
    # Fall back to existing registry
    return generate_from_registry(problem_id, seed)
```

### Add Frontend Search Page

See `apps/web/src/pages/SearchPage.tsx` for React implementation.

## Performance Tips

### Database Optimization

```sql
-- Enable query optimization
PRAGMA optimize;

-- Check database size
SELECT page_count * page_size / 1024.0 / 1024.0 as 'Size (MB)' 
FROM pragma_page_count(), pragma_page_size();

-- Analyze tables for better query planning
ANALYZE;
```

### Caching (Optional)

Add Redis caching for frequently accessed problems:

```python
import redis
import json

cache = redis.Redis(host='localhost', port=6379, db=0)

def get_problem_cached(problem_id: str):
    # Try cache first
    cached = cache.get(f"problem:{problem_id}")
    if cached:
        return json.loads(cached)
    
    # Query database
    problem = db.get_by_id(problem_id)
    
    # Cache for 1 hour
    cache.setex(f"problem:{problem_id}", 3600, json.dumps(problem))
    
    return problem
```

## Database Queries

### Direct SQLite Access

```bash
# Open database
sqlite3 problems.db

# List all collections
SELECT id, name, problem_count FROM collections;

# Search problems
SELECT id, name FROM problems WHERE name LIKE '%derivative%';

# Subject distribution
SELECT json_each.value as subject, COUNT(*) 
FROM problems, json_each(metadata, '$.subjects')
GROUP BY subject
ORDER BY COUNT(*) DESC;

# Full-text search
SELECT id, name, bm25(problems_fts) as score
FROM problems 
JOIN problems_fts ON problems.rowid = problems_fts.rowid
WHERE problems_fts MATCH 'calculus limit'
ORDER BY score
LIMIT 10;
```

## Monitoring

### Check Database Health

```bash
# Database size
ls -lh problems.db

# Number of problems
sqlite3 problems.db "SELECT COUNT(*) FROM problems"

# Check indexes
sqlite3 problems.db ".indexes"

# Check FTS table
sqlite3 problems.db "SELECT COUNT(*) FROM problems_fts"
```

## Support

- **Documentation**: See `IMPLEMENTATION_PLAN.md` and `PROBLEM_SOURCES.md`
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Issues**: GitHub Issues
- **WeBWorK Community**: https://webwork.maa.org/

## Summary

✅ **Import**: `python scripts/import_problems.py` (30 seconds)
✅ **Start API**: `uvicorn app.main:app --reload` 
✅ **Test**: `curl http://localhost:8000/api/problems/search?q=calculus`
✅ **Browse**: http://localhost:8000/docs

**Result**: Searchable database of 161+ WeBWorK problems with full-text search, filtering, and metadata!
