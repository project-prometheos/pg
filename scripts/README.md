# WeBWorK Problem Import Scripts

This directory contains scripts for importing WeBWorK problems into the local SQLite database.

## Quick Reference

### Test the System

```bash
python scripts/test_import.py
```

### Import Tutorial Problems

```bash
python scripts/import_problems.py
```

### Import from Open Problem Library

#### Automated (Recommended)

Import ~4,000 high-quality problems automatically:

```bash
python scripts/bootstrap_opl.py
```

#### Manual Import

Import specific collections:

```bash
# 1. Clone OPL (one time)
git clone --depth 1 https://github.com/openwebwork/webwork-open-problem-library.git

# 2. Import collection
python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/Hope

# 3. Or test with limited sample
python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/Hope --limit 50
```

## Scripts

### `test_import.py`

Test and verify the import system.

**Usage:**
```bash
python scripts/test_import.py
```

**What it does:**
- Checks database exists and has valid schema
- Shows current problem counts
- Lists collections and subjects
- Tests search functionality
- Verifies all import scripts are present

### `import_problems.py`

Import tutorial problems from `tutorial/sample-problems/`.

**Usage:**
```bash
python scripts/import_problems.py [database_path]
```

**Example:**
```bash
python scripts/import_problems.py              # Uses problems.db
python scripts/import_problems.py custom.db    # Custom database
```

**What it does:**
- Runs Perl parser to extract metadata
- Imports ~161 tutorial problems
- Creates/updates database schema
- Shows statistics

### `import_opl.py`

Import problems from Open Problem Library.

**Usage:**
```bash
python scripts/import_opl.py <opl_directory> [collection_name] [--limit N]
```

**Examples:**
```bash
# Import Hope collection
python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/Hope

# Import with custom collection name
python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/Hope MyHopeProblems

# Test with 50 problems
python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/Hope --limit 50

# Import specific subject
python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/Hope/Linear_Algebra
```

**What it does:**
- Scans directory for `.pg` files
- Extracts OPL-style metadata (DBsubject, DBchapter, etc.)
- Categorizes problems by subject
- Imports into database
- Shows progress and statistics

### `bootstrap_opl.py`

Automated import of Tier 1 OPL collections.

**Usage:**
```bash
python scripts/bootstrap_opl.py
```

**What it does:**
1. Checks/creates database
2. Clones OPL repository (~2.5 GB)
3. Imports FortLewis (~500 problems)
4. Imports Hope (~600 problems)
5. Imports TCNJ (~800 problems)
6. Imports UBC (~2,000 problems)
7. Optionally imports Tier 2 (Michigan, LoyolaChicago)

**Time:** 30-60 minutes  
**Space:** ~3 GB  
**Result:** ~4,000 problems

### `export_problems_to_json.pl`

Perl script to extract metadata from PG files.

**Usage:**
```bash
perl scripts/export_problems_to_json.pl [problem_directory] [output_file]
```

**Example:**
```bash
perl scripts/export_problems_to_json.pl tutorial/sample-problems problems_metadata.json
```

**Note:** This is called automatically by `import_problems.py`.

## Problem Collections

### Tier 1: Highest Quality ⭐⭐⭐

| Collection | Problems | Command |
|-----------|----------|---------|
| FortLewis | ~500 | `python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/FortLewis` |
| Hope | ~600 | `python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/Hope` |
| TCNJ | ~800 | `python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/TCNJ` |
| UBC | ~2,000 | `python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/UBC` |

### Tier 2: Good Quality ⭐⭐

| Collection | Problems | Command |
|-----------|----------|---------|
| Michigan | ~3,000 | `python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/Michigan` |
| LoyolaChicago | ~1,500 | `python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/LoyolaChicago` |

## Database Schema

```sql
-- Main problems table
CREATE TABLE problems (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    pg_source TEXT NOT NULL,
    file_path TEXT,
    source_collection TEXT,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Collections table
CREATE TABLE collections (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    problem_count INTEGER DEFAULT 0
);

-- Full-text search index
CREATE VIRTUAL TABLE problems_fts USING fts5(
    name, description, pg_source, content=problems
);
```

## Metadata Format

OPL problems use this metadata format:

```
## DESCRIPTION
## Brief description here
## ENDDESCRIPTION

## DBsubject(Calculus)
## DBchapter(Limits and Continuity)
## DBsection(Evaluating Limits)
## Date(01/01/2000)
## Institution(Hope College)
## Author(Paul Pearson)
## Level(2)
## KEYWORDS('calculus','limit')
```

Imported as:

```json
{
  "subjects": ["calculus"],
  "categories": ["limits", "continuity"],
  "keywords": ["calculus", "limit"],
  "db_subject": "Calculus",
  "db_chapter": "Limits and Continuity",
  "db_section": "Evaluating Limits",
  "institution": "Hope College",
  "author": "Paul Pearson",
  "level": "2"
}
```

## Troubleshooting

### Database Not Found

```bash
# Create database with tutorial problems
python scripts/import_problems.py
```

### OPL Repository Not Found

```bash
# Clone OPL
git clone --depth 1 https://github.com/openwebwork/webwork-open-problem-library.git
```

### Import Errors

The import scripts handle errors gracefully:
- Duplicate problems are skipped
- First 5 errors are shown
- Import continues on errors

To see full details, check the output.

### Reset Database

```bash
# Backup first!
cp problems.db problems.db.backup

# Delete and recreate
rm problems.db
python scripts/import_problems.py
```

## Performance

### Import Speed

| Collection | Problems | Time |
|-----------|----------|------|
| Tutorial | 161 | 30 sec |
| Hope | ~600 | 3 min |
| UBC | ~2,000 | 10 min |
| Tier 1 All | ~4,000 | 20 min |

### Database Size

| Import Level | Problems | DB Size |
|-------------|----------|---------|
| Tutorial | 161 | 2 MB |
| + Tier 1 | ~4,000 | 60 MB |
| Full OPL | ~35,000 | 500 MB |

## Documentation

- **IMPORT_GUIDE.md** - Complete import guide
- **IMPORT_SUMMARY.md** - System status and quick reference
- **PROBLEM_SOURCES.md** - Available problem sources and collections

## Resources

- **OPL GitHub:** https://github.com/openwebwork/webwork-open-problem-library
- **OPL Browser:** https://webwork.maa.org/moodle/mod/data/view.php?id=3
- **PG Documentation:** https://webwork.maa.org/pod/pg/

## Next Steps

1. **Test the system:**
   ```bash
   python scripts/test_import.py
   ```

2. **Import problems:**
   ```bash
   python scripts/bootstrap_opl.py
   ```

3. **Start the backend:**
   ```bash
   cd apps/backend
   python -m uvicorn app.main:app --reload
   ```

4. **Use the API:**
   ```bash
   curl http://localhost:8000/api/problems/search?q=calculus
   ```

