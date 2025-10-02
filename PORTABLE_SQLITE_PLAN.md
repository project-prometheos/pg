# Portable SQLite-Based Problem Database Plan

## Overview

This plan implements a portable, SQLite-based problem database system for WeBWorK PG with vector search capabilities using sqlite-vec, SQLAlchemy ORM, and Alembic migrations.

## Technology Stack

- **Database**: SQLite with sqlite-vec extension for vector search
- **ORM**: SQLAlchemy with async support
- **Migrations**: Alembic for database schema management
- **Vector Search**: sqlite-vec for semantic search capabilities
- **Backend**: FastAPI with search endpoints
- **Frontend**: React with search interface
- **Portability**: Single SQLite file, no external dependencies

## Key Features

### 1. **Rich Metadata System**
- Problem types: `sample`, `technique`, `snippet`
- Subjects: `algebra`, `calculus`, `statistics`, `trigonometry`, etc.
- Categories: `inequality`, `proof`, `draggable`, `images`, etc.
- Keywords: Searchable tags from PG files
- Macros: Required macro dependencies
- Documentation: Structured sections (preamble, setup, statement, solution)

### 2. **Advanced Search Capabilities**
- **Vector Search**: Semantic similarity using sqlite-vec
- **Full-Text Search**: SQLite FTS5 for keyword matching
- **Filtered Search**: By type, subject, category, keywords, macros
- **Related Problems**: Cross-references via metadata
- **Faceted Search**: Browse by available categories/subjects

### 3. **Portable Database**
- Single SQLite file (`problems.db`)
- No external database server required
- Easy backup and deployment
- Cross-platform compatibility

## Implementation Structure

### Database Schema
```sql
-- Core tables
problems                    -- Main problem data
problem_metadata           -- Key-value metadata
problem_types             -- Problem types
problem_subjects          -- Subject areas
problem_categories        -- Categories
problem_keywords          -- Keywords/tags
problem_macros            -- Required macros
problem_relations         -- Related problems
problem_documentation     -- Documentation sections
problem_embeddings        -- Vector embeddings

-- Search indexes
problems_fts              -- FTS5 full-text search
problems_search_content   -- Search content view
```

### Backend Components
- **Models**: SQLAlchemy ORM models (`app/models/database.py`)
- **Search Service**: Vector and traditional search (`app/services/search.py`)
- **API Endpoints**: RESTful search API (`app/routers/search.py`)
- **Migration Script**: Parse PG files and populate database (`scripts/migrate_sample_problems.py`)
- **Database Service**: Load problems from database (`app/services/database_problems.py`)

### Frontend Components
- **Search Page**: Advanced search interface (`apps/web/src/pages/SearchPage.tsx`)
- **Search API**: Frontend API service (`apps/web/src/services/searchApi.ts`)
- **Types**: TypeScript definitions (`apps/web/src/types.ts`)

## Setup Instructions

### 1. **Install Dependencies**
```bash
# Backend dependencies
cd apps/backend
pip install -e .

# Optional: Install sqlite-vec for vector search
pip install sqlite-vec
```

### 2. **Initialize Database**
```bash
# Run the setup script
python setup_database.py

# Or manually:
cd apps/backend
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
python scripts/migrate_sample_problems.py
```

### 3. **Start Services**
```bash
# Backend
cd apps/backend
python -m uvicorn app.main:app --reload

# Frontend
cd apps/web
npm run dev
```

### 4. **Access Search Interface**
Visit `http://localhost:3000/search` to explore the problem database.

## API Endpoints

### Search Endpoints
- `POST /api/search` - Advanced search with filters
- `GET /api/search` - Search with query parameters
- `GET /api/fts` - Full-text search
- `GET /api/by-category/{category}` - Problems by category
- `GET /api/by-subject/{subject}` - Problems by subject
- `GET /api/by-macro/{macro}` - Problems using specific macro
- `GET /api/related/{problem_id}` - Related problems
- `GET /api/facets` - Available search facets
- `GET /api/problem/{problem_id}` - Problem details

### Example Usage
```bash
# Search for calculus problems
curl "http://localhost:8000/api/search?q=derivative&subjects=calculus"

# Get problems by category
curl "http://localhost:8000/api/by-category/proof"

# Full-text search
curl "http://localhost:8000/api/fts?q=trigonometric identity"
```

## Migration Process

### 1. **Parse Sample Problems**
The migration script (`scripts/migrate_sample_problems.py`) automatically:
- Scans `tutorial/sample-problems/` directory
- Parses PG files for metadata using regex patterns
- Extracts documentation sections
- Identifies macro dependencies
- Populates database with structured data

### 2. **Generate Embeddings**
Vector embeddings are generated for:
- Problem statements
- Solutions
- Descriptions
- Full text content

### 3. **Create Search Indexes**
- FTS5 full-text search index
- Vector similarity indexes
- Metadata indexes for filtering

## Search Features

### 1. **Text Search**
- **Query**: Natural language search across all content
- **Vector Search**: Semantic similarity using embeddings
- **Full-Text**: Keyword matching with SQLite FTS5

### 2. **Filtered Search**
- **Types**: sample, technique, snippet
- **Subjects**: algebra, calculus, statistics, etc.
- **Categories**: inequality, proof, draggable, etc.
- **Keywords**: Tags from PG files
- **Macros**: Required macro dependencies

### 3. **Browse Interface**
- **Faceted Navigation**: Filter by available categories/subjects
- **Related Problems**: Cross-references
- **Problem Details**: Full metadata and documentation

## Benefits

### 1. **Portability**
- Single SQLite file
- No external dependencies
- Easy deployment and backup
- Cross-platform compatibility

### 2. **Performance**
- Indexed searches
- Vector similarity
- Efficient filtering
- Pagination support

### 3. **Extensibility**
- Easy to add new metadata fields
- Flexible search criteria
- Plugin architecture for embeddings
- RESTful API design

### 4. **Integration**
- Compatible with existing WeBWorK PG system
- Fallback to registry-based problems
- Maintains existing problem generation
- Seamless frontend integration

## Future Enhancements

### 1. **Advanced Vector Search**
- Integration with OpenAI embeddings
- Sentence transformer models
- Multi-language support
- Custom embedding models

### 2. **Enhanced Metadata**
- Difficulty ratings
- Learning objectives
- Prerequisites
- Usage statistics

### 3. **Collaborative Features**
- User ratings and reviews
- Problem collections
- Sharing and export
- Version control

### 4. **Analytics**
- Search analytics
- Popular problems
- Usage patterns
- Performance metrics

## File Structure

```
apps/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   └── database.py          # SQLAlchemy models
│   │   ├── routers/
│   │   │   └── search.py            # Search API endpoints
│   │   ├── services/
│   │   │   ├── search.py            # Search service
│   │   │   └── database_problems.py # Database problem loading
│   │   └── main.py                  # FastAPI app
│   ├── alembic/                     # Database migrations
│   ├── scripts/
│   │   └── migrate_sample_problems.py # Migration script
│   └── pyproject.toml               # Dependencies
├── web/
│   └── src/
│       ├── pages/
│       │   └── SearchPage.tsx       # Search interface
│       ├── services/
│       │   └── searchApi.ts         # Frontend API
│       └── types.ts                 # TypeScript types
└── database_schema.sql              # Database schema
```

This implementation provides a comprehensive, portable solution for searching and discovering WeBWorK PG problems with modern vector search capabilities while maintaining compatibility with the existing system.
