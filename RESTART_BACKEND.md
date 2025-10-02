# Restart Backend to Activate Problem Rendering

## Issue
The database problem rendering endpoints (`/api/db/{problem_id}/render`) are not loading because the backend server needs to be restarted after installing the `pg-renderer` package.

## Solution: Restart Backend Server

### Step 1: Stop Current Backend
Find the terminal running the backend and press `Ctrl+C` to stop it.

### Step 2: Restart Backend
```bash
cd apps/backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Verify Routes Are Loaded
Open: http://localhost:8000/docs

You should see these new endpoints:
- `GET /api/db/{problem_id}/render` - Render a database problem
- `POST /api/db/{problem_id}/check` - Check student answers

### Step 4: Test
```bash
curl "http://localhost:8000/api/db/Algebra/AlgebraicFractionAnswer/render?seed=42"
```

You should get a JSON response with `statement_html`, `inputs`, and `answers`.

## Alternative: Quick Test Without Restart

If you can't restart the backend, you can test the renderer directly:

```python
# Test the renderer
python -c "
from pg_renderer import PGRenderer
import sqlite3

conn = sqlite3.connect('problems.db')
row = conn.execute('SELECT pg_source FROM problems LIMIT 1').fetchone()
renderer = PGRenderer()
result = renderer.render(row[0], seed=0)
print('✓ Renderer works!')
print(f'Inputs: {result[\"inputs\"]}')
print(f'Errors: {len(result[\"errors\"])}')
"
```

## What Gets Fixed

After restarting, clicking on problems in the browse page will:
✅ Show the rendered problem with LaTeX math
✅ Display answer input boxes
✅ Allow you to check your answers
✅ Support seed-based problem variations

## Files Involved

- `packages/pg_renderer/` - Pure Python PG renderer (installed)
- `apps/backend/app/routers/database_problems.py` - API endpoints
- `apps/backend/app/services/pg_renderer_python.py` - Service wrapper
- `apps/web/src/pages/DatabaseProblemPage.tsx` - Frontend component

## Current Status

✅ Package installed: `pg-renderer`
✅ Routes created: `/api/db/`
✅ Frontend ready: `DatabaseProblemPage`
🔄 **Need to restart backend to activate**

After restart, everything will work!

