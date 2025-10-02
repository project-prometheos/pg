-- WeBWorK Problem Database Schema
-- Portable SQLite with FTS5 for full-text search

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- Main problems table
CREATE TABLE IF NOT EXISTS problems (
    id TEXT PRIMARY KEY,              -- e.g., "Algebra/LinearInequality"
    name TEXT NOT NULL,               -- Human-readable name
    description TEXT,                 -- Short description
    pg_source TEXT NOT NULL,          -- Full PG file content
    file_path TEXT NOT NULL,          -- Original file path
    source_collection TEXT,           -- e.g., "OPL", "tutorial", "custom"
    
    -- Metadata as JSON for flexibility
    metadata JSON NOT NULL,           -- { types, subjects, categories, keywords, macros, related, ... }
    
    created_at INTEGER DEFAULT (unixepoch()),
    updated_at INTEGER DEFAULT (unixepoch())
);

-- Full-text search index (built-in FTS5)
CREATE VIRTUAL TABLE IF NOT EXISTS problems_fts USING fts5(
    id UNINDEXED,
    name,
    description,
    keywords,
    subjects,
    categories,
    content='problems',
    content_rowid='rowid',
    tokenize='porter unicode61'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS problems_fts_insert AFTER INSERT ON problems BEGIN
    INSERT INTO problems_fts(rowid, id, name, description, keywords, subjects, categories)
    VALUES (
        new.rowid,
        new.id,
        new.name,
        new.description,
        json_extract(new.metadata, '$.keywords'),
        json_extract(new.metadata, '$.subjects'),
        json_extract(new.metadata, '$.categories')
    );
END;

CREATE TRIGGER IF NOT EXISTS problems_fts_delete AFTER DELETE ON problems BEGIN
    DELETE FROM problems_fts WHERE rowid = old.rowid;
END;

CREATE TRIGGER IF NOT EXISTS problems_fts_update AFTER UPDATE ON problems BEGIN
    DELETE FROM problems_fts WHERE rowid = old.rowid;
    INSERT INTO problems_fts(rowid, id, name, description, keywords, subjects, categories)
    VALUES (
        new.rowid,
        new.id,
        new.name,
        new.description,
        json_extract(new.metadata, '$.keywords'),
        json_extract(new.metadata, '$.subjects'),
        json_extract(new.metadata, '$.categories')
    );
END;

-- Indexes for filtering performance
CREATE INDEX IF NOT EXISTS idx_problems_source ON problems(source_collection);
CREATE INDEX IF NOT EXISTS idx_problems_types ON problems(json_extract(metadata, '$.types'));
CREATE INDEX IF NOT EXISTS idx_problems_subjects ON problems(json_extract(metadata, '$.subjects'));
CREATE INDEX IF NOT EXISTS idx_problems_created ON problems(created_at DESC);

-- Problem collections/libraries
CREATE TABLE IF NOT EXISTS collections (
    id TEXT PRIMARY KEY,              -- e.g., "OPL", "tutorial", "calc1-final"
    name TEXT NOT NULL,               -- Display name
    description TEXT,
    source_url TEXT,                  -- Original source if imported
    problem_count INTEGER DEFAULT 0,
    created_at INTEGER DEFAULT (unixepoch()),
    updated_at INTEGER DEFAULT (unixepoch())
);

-- Problem usage statistics (optional, for future)
CREATE TABLE IF NOT EXISTS problem_stats (
    problem_id TEXT PRIMARY KEY,
    view_count INTEGER DEFAULT 0,
    use_count INTEGER DEFAULT 0,
    last_accessed INTEGER,
    FOREIGN KEY (problem_id) REFERENCES problems(id) ON DELETE CASCADE
);

-- User-created problem sets (optional, for future)
CREATE TABLE IF NOT EXISTS problem_sets (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    problem_ids JSON NOT NULL,       -- ["prob1", "prob2", ...]
    created_by TEXT,
    created_at INTEGER DEFAULT (unixepoch()),
    updated_at INTEGER DEFAULT (unixepoch())
);

-- Initial collections
INSERT OR IGNORE INTO collections (id, name, description) VALUES
    ('tutorial', 'Tutorial Sample Problems', 'Sample problems from PG tutorial'),
    ('OPL', 'Open Problem Library', 'Problems from WeBWorK OPL'),
    ('custom', 'Custom Problems', 'User-created problems');
