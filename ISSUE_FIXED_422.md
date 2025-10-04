# Fixed: 422 Unprocessable Entity Error

## Issue
Frontend was getting a 422 error when trying to load problems from `/api/problems/search?limit=200`

## Root Cause
The backend API endpoint had a maximum limit validation of 100, but the frontend was requesting 200 results.

**Error message from FastAPI:**
```json
{
  "detail": [{
    "type": "less_than_equal",
    "loc": ["query", "limit"],
    "msg": "Input should be less than or equal to 100",
    "input": "200",
    "ctx": {"le": 100}
  }]
}
```

## Solution

### 1. Increased Backend Limit
**File:** `apps/backend/app/routers/search.py:63`

Changed from:
```python
limit: int = Query(50, ge=1, le=100, description="Results per page")
```

To:
```python
limit: int = Query(50, ge=1, le=500, description="Results per page")
```

### 2. Frontend Already Requesting 200
**File:** `apps/web/src/pages/BrowsePage.tsx:47`

```typescript
params.set('limit', '200');  // API max is now 500
```

## Verification

Backend now returns all 182 problems:
```bash
$ curl "http://localhost:8000/api/problems/search?limit=200"
{
  "problems": [...],  # 182 items
  "total": 182,
  "limit": 200,
  "offset": 0
}
```

## Status: ✅ FIXED

The frontend should now load all problems successfully:
- Tutorial: 157 problems
- PS1: 25 problems
- **Total: 182 problems**

Reload your browser to see the changes!
