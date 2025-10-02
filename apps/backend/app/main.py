"""FastAPI application entry-point for the problem generator backend."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import checks, health, problems, solutions

# Try to import search router if database is available
try:
    from .routers import search
    SEARCH_AVAILABLE = True
except ImportError as e:
    print(f"Search not available: {e}")
    SEARCH_AVAILABLE = False

# Try to import database rendering router
try:
    import sys
    print(f"[DEBUG] Python path: {sys.executable}")
    print(f"[DEBUG] sys.path entries: {len(sys.path)}")
    
    from .routers import database_problems
    DATABASE_RENDERING_AVAILABLE = True
    print("[SUCCESS] Database rendering router loaded!")
except ImportError as e:
    print(f"[ERROR] Database rendering not available: {e}")
    print(f"[DEBUG] Trying to import pg_renderer directly...")
    try:
        import pg_renderer
        print(f"[INFO] pg_renderer can be imported directly from: {pg_renderer.__file__}")
    except ImportError as e2:
        print(f"[ERROR] Cannot import pg_renderer at all: {e2}")
    DATABASE_RENDERING_AVAILABLE = False

app = FastAPI(
    title="WeBWorK PG API",
    version="0.2.0",
    description="Problem generation and search API for WeBWorK PG"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)

# Include search router (separate from /api/problems/{id} to avoid conflicts)
if SEARCH_AVAILABLE:
    app.include_router(search.router)

# Include database rendering router (separate prefix)
if DATABASE_RENDERING_AVAILABLE:
    app.include_router(database_problems.router)

app.include_router(problems.router, prefix="/api/problems", tags=["problems"])
app.include_router(checks.router, tags=["checking"])
app.include_router(solutions.router, tags=["solutions"])


@app.get("/api/health", tags=["health"])
def healthcheck() -> dict[str, str]:
    """Simple health endpoint used for readiness checks."""
    return {"status": "ok"}
