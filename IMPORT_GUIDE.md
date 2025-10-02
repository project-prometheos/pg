# WeBWorK Problem Import Guide

This guide explains how to import problems from the Open Problem Library (OPL) into your local database.

## Quick Start

### Option 1: Automated Bootstrap (Recommended)

This will clone the OPL and import ~4,000 high-quality Tier 1 problems:

```bash
python scripts/bootstrap_opl.py
```

**What it does:**
1. Clones the Open Problem Library (~2.5 GB)
2. Imports FortLewis collection (~500 problems)
3. Imports Hope collection (~600 problems)
4. Imports TCNJ collection (~800 problems)
5. Imports UBC collection (~2,000 problems)
6. Optionally imports Tier 2 collections (Michigan, LoyolaChicago)

**Requirements:**
- Git installed
- ~3 GB free disk space
- Internet connection
- ~30-60 minutes for full import

### Option 2: Manual Import

Import specific collections:

```bash
# 1. Clone OPL (one time only)
git clone --depth 1 https://github.com/openwebwork/webwork-open-problem-library.git

# 2. Import a specific collection
python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/FortLewis

# 3. Import another collection
python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/Hope
```

### Option 3: Test Import (Small Sample)

Test with just 50 problems before doing a full import:

```bash
# Clone OPL
git clone --depth 1 https://github.com/openwebwork/webwork-open-problem-library.git

# Import just 50 problems from Hope collection
python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/Hope --limit 50
```

## Problem Collections

### Tier 1: Highest Quality (Recommended) ⭐⭐⭐

| Collection | Problems | Quality | Focus Areas |
|-----------|----------|---------|-------------|
| **FortLewis** | ~500 | Modern PGML, well-documented | Calculus, Linear Algebra |
| **Hope** | ~600 | Excellent examples | Calculus, Statistics |
| **TCNJ** | ~800 | High quality, diverse | Various subjects |
| **UBC** | ~2,000 | Modern, well-tested | Calculus, Statistics |

### Tier 2: Good Quality ⭐⭐

| Collection | Problems | Focus Areas |
|-----------|----------|-------------|
| **Michigan** | ~3,000 | Calculus, Differential Equations |
| **LoyolaChicago** | ~1,500 | Calculus, Precalculus |
| **NAU** | ~600 | College Algebra |

### Tier 3: Classic Collection ⭐

| Collection | Problems | Notes |
|-----------|----------|-------|
| **Rochester** | ~7,000 | Oldest collection, may need updates |

## Import Commands

### By Collection

```bash
# Tier 1 (Recommended)
python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/FortLewis
python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/Hope
python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/TCNJ
python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/UBC

# Tier 2
python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/Michigan
python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/LoyolaChicago

# Tier 3
python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/Rochester
```

### By Subject

```bash
# All Linear Algebra problems from Hope
python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/Hope/Linear_Algebra

# All Calculus problems from Michigan  
python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/Michigan/Chap1

# Statistics from UBC
python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/UBC/Statistics
```

### With Limits (Testing)

```bash
# Import only first 100 problems from Michigan
python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/Michigan --limit 100
```

## Database Statistics

View import statistics:

```bash
# After import, the script automatically shows:
# - Collections imported
# - Total problem count
# - Subject distribution
```

Or query directly:

```bash
# Using PowerShell (Windows)
sqlite3 problems.db "SELECT source_collection, COUNT(*) FROM problems GROUP BY source_collection"

# View total problems
sqlite3 problems.db "SELECT COUNT(*) FROM problems"

# View subjects
sqlite3 problems.db "SELECT DISTINCT json_extract(metadata, '$.subjects') FROM problems LIMIT 20"
```

## Metadata Extracted

The import script extracts the following from OPL problems:

- **Subject taxonomy** (Calculus, Algebra, etc.)
- **Chapter/Section** organization
- **Keywords** for search
- **Macros** used
- **Institution** and author
- **Difficulty level** (when available)
- **Description** text

## File Structure

After import:

```
d:/pg/
├── webwork-open-problem-library/    # Cloned OPL repository (~2.5 GB)
│   └── OpenProblemLibrary/
│       ├── FortLewis/
│       ├── Hope/
│       ├── TCNJ/
│       ├── UBC/
│       ├── Michigan/
│       └── ...
├── problems.db                       # SQLite database with imported problems
└── scripts/
    ├── import_opl.py                # OPL import script
    └── bootstrap_opl.py             # Automated bootstrap
```

## Troubleshooting

### "Database not found" Error

```bash
# Create initial database with tutorial problems:
python scripts/import_problems.py
```

### Git Clone Too Slow

Use shallow clone (already done in bootstrap):

```bash
git clone --depth 1 https://github.com/openwebwork/webwork-open-problem-library.git
```

### Out of Disk Space

Import collections incrementally:

```bash
# Import one collection at a time
python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/Hope

# Check database size
ls -lh problems.db  # Unix/Mac
Get-Item problems.db | Select-Object Length  # Windows PowerShell
```

### Unicode Encoding Errors (Windows)

The scripts now use ASCII-safe output. If you still see errors:

```powershell
# Set UTF-8 encoding in PowerShell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
```

## Performance

### Import Speed

| Collection | Size | Import Time (est.) |
|-----------|------|-------------------|
| Hope | ~600 problems | ~3 minutes |
| FortLewis | ~500 problems | ~2 minutes |
| TCNJ | ~800 problems | ~4 minutes |
| UBC | ~2,000 problems | ~10 minutes |
| Michigan | ~3,000 problems | ~15 minutes |
| **All Tier 1** | ~4,000 | **~20 minutes** |

### Database Size

| Import Level | Problem Count | DB Size |
|-------------|---------------|---------|
| Tutorial only | 161 | 2 MB |
| + Tier 1 | ~4,000 | 60 MB |
| + Tier 2 | ~9,000 | 150 MB |
| Full OPL | ~35,000 | 500 MB |

## Next Steps

After importing:

1. **Start the backend:**
   ```bash
   cd apps/backend
   python -m uvicorn app.main:app --reload
   ```

2. **Test the search API:**
   ```bash
   # View all problems
   curl http://localhost:8000/api/problems

   # Search for calculus problems
   curl http://localhost:8000/api/problems/search?q=calculus

   # Search by collection
   curl http://localhost:8000/api/problems/search?collection=OPL-Hope
   ```

3. **Use the web interface:**
   ```bash
   cd apps/web
   npm run dev
   # Visit http://localhost:5173
   ```

## Advanced Usage

### Custom Collection Name

```bash
python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/Hope MyCustomCollection
```

### Re-import (Update) Collection

The import script uses `INSERT OR REPLACE`, so re-running will update existing problems:

```bash
# Update Hope collection with latest from OPL
cd webwork-open-problem-library
git pull
cd ..
python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/Hope
```

### Import Multiple Collections in Parallel

```bash
# Import multiple collections simultaneously (PowerShell)
Start-Job { python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/Hope }
Start-Job { python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/TCNJ }
Start-Job { python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/FortLewis }

# Monitor jobs
Get-Job

# Wait for completion
Get-Job | Wait-Job
```

## Resources

- **OPL Browser:** https://webwork.maa.org/moodle/mod/data/view.php?id=3
- **OPL GitHub:** https://github.com/openwebwork/webwork-open-problem-library
- **Problem Sources:** See `PROBLEM_SOURCES.md`

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review `PROBLEM_SOURCES.md` for collection details
3. Ensure you have the latest version of the import scripts
4. For OPL-specific issues, check the [OPL GitHub Issues](https://github.com/openwebwork/webwork-open-problem-library/issues)

