-- Enable sqlite-vec extension for vector search
.load sqlite-vec

-- Core problems table
CREATE TABLE problems (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    description TEXT,
    pg_source TEXT NOT NULL,
    file_path VARCHAR(500), -- Original file path for reference
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Problem metadata (key-value pairs for flexible metadata)
CREATE TABLE problem_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id VARCHAR(255) REFERENCES problems(id) ON DELETE CASCADE,
    key VARCHAR(100) NOT NULL,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Problem types (sample, technique, snippet)
CREATE TABLE problem_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id VARCHAR(255) REFERENCES problems(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(problem_id, type)
);

-- Problem subjects (algebra, calculus, etc.)
CREATE TABLE problem_subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id VARCHAR(255) REFERENCES problems(id) ON DELETE CASCADE,
    subject VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(problem_id, subject)
);

-- Problem categories (inequality, proof, etc.)
CREATE TABLE problem_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id VARCHAR(255) REFERENCES problems(id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(problem_id, category)
);

-- Problem keywords/tags
CREATE TABLE problem_keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id VARCHAR(255) REFERENCES problems(id) ON DELETE CASCADE,
    keyword VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(problem_id, keyword)
);

-- Required macros for each problem
CREATE TABLE problem_macros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id VARCHAR(255) REFERENCES problems(id) ON DELETE CASCADE,
    macro VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(problem_id, macro)
);

-- Related problems
CREATE TABLE problem_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id VARCHAR(255) REFERENCES problems(id) ON DELETE CASCADE,
    related_problem_id VARCHAR(255) REFERENCES problems(id) ON DELETE CASCADE,
    relation_type VARCHAR(50) DEFAULT 'see_also',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(problem_id, related_problem_id, relation_type)
);

-- Problem documentation sections
CREATE TABLE problem_documentation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id VARCHAR(255) REFERENCES problems(id) ON DELETE CASCADE,
    section VARCHAR(50) NOT NULL, -- preamble, setup, statement, solution
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(problem_id, section)
);

-- Vector embeddings for semantic search
CREATE TABLE problem_embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id VARCHAR(255) REFERENCES problems(id) ON DELETE CASCADE,
    content_type VARCHAR(50) NOT NULL, -- 'statement', 'solution', 'description', 'full_text'
    embedding BLOB NOT NULL, -- Vector embedding stored as blob
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(problem_id, content_type)
);

-- Search indexes for performance
CREATE INDEX idx_problems_name ON problems(name);
CREATE INDEX idx_problems_file_path ON problems(file_path);
CREATE INDEX idx_problem_metadata_key ON problem_metadata(key);
CREATE INDEX idx_problem_types_type ON problem_types(type);
CREATE INDEX idx_problem_subjects_subject ON problem_subjects(subject);
CREATE INDEX idx_problem_categories_category ON problem_categories(category);
CREATE INDEX idx_problem_keywords_keyword ON problem_keywords(keyword);
CREATE INDEX idx_problem_macros_macro ON problem_macros(macro);
CREATE INDEX idx_problem_documentation_section ON problem_documentation(section);

-- Full-text search index for SQLite FTS5
CREATE VIRTUAL TABLE problems_fts USING fts5(
    problem_id,
    name,
    description,
    content,
    keywords,
    subjects,
    categories,
    content='problems_search_content',
    content_rowid='rowid'
);

-- View to populate FTS5 content
CREATE VIEW problems_search_content AS
SELECT 
    p.rowid,
    p.id as problem_id,
    p.name,
    p.description,
    GROUP_CONCAT(DISTINCT pd.content, ' ') as content,
    GROUP_CONCAT(DISTINCT pk.keyword, ' ') as keywords,
    GROUP_CONCAT(DISTINCT ps.subject, ' ') as subjects,
    GROUP_CONCAT(DISTINCT pc.category, ' ') as categories
FROM problems p
LEFT JOIN problem_documentation pd ON p.id = pd.problem_id
LEFT JOIN problem_keywords pk ON p.id = pk.problem_id
LEFT JOIN problem_subjects ps ON p.id = ps.problem_id
LEFT JOIN problem_categories pc ON p.id = pc.problem_id
GROUP BY p.id;

-- Triggers to maintain FTS5 index
CREATE TRIGGER problems_fts_insert AFTER INSERT ON problems BEGIN
    INSERT INTO problems_fts(problem_id, name, description, content, keywords, subjects, categories)
    SELECT problem_id, name, description, content, keywords, subjects, categories
    FROM problems_search_content WHERE problem_id = NEW.id;
END;

CREATE TRIGGER problems_fts_delete AFTER DELETE ON problems BEGIN
    DELETE FROM problems_fts WHERE problem_id = OLD.id;
END;

CREATE TRIGGER problems_fts_update AFTER UPDATE ON problems BEGIN
    DELETE FROM problems_fts WHERE problem_id = OLD.id;
    INSERT INTO problems_fts(problem_id, name, description, content, keywords, subjects, categories)
    SELECT problem_id, name, description, content, keywords, subjects, categories
    FROM problems_search_content WHERE problem_id = NEW.id;
END;
