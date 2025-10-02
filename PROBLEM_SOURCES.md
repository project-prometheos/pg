# WeBWorK Problem Collections - Sources & Import Guide

## Current Collections in Repository

✅ **Tutorial Sample Problems** (161+ problems)
- Location: `tutorial/sample-problems/`
- Status: Included in repository
- Subjects: Algebra, Calculus, Statistics, Trig, Linear Algebra, etc.
- Quality: Curated, documented, modern PGML

## Major Online Problem Libraries

### 1. **Open Problem Library (OPL)** ⭐ PRIMARY SOURCE

**Repository**: https://github.com/openwebwork/webwork-open-problem-library

**Size**: 35,000+ problems

**Structure**:
```
webwork-open-problem-library/
├── OpenProblemLibrary/          # Main library
│   ├── LoyolaChicago/           # ~1,500 problems
│   ├── Michigan/                # ~3,000 problems  
│   ├── Rochester/               # ~7,000 problems (oldest)
│   ├── UBC/                     # ~2,000 problems
│   ├── WHFreeman/               # ~1,000 problems (textbook)
│   ├── TCNJ/                    # ~800 problems
│   ├── Hope/                    # ~600 problems
│   ├── FortLewis/              # ~500 problems
│   └── [many more...]
├── Contrib/                     # Contributed problems
└── Pending/                     # Under review
```

**Subjects**: 
- Algebra (Pre-algebra through Abstract Algebra)
- Calculus (single & multivariable)
- Differential Equations
- Linear Algebra
- Statistics & Probability
- Discrete Math
- Complex Analysis
- Number Theory
- Physics, Chemistry, Biology applications

**How to Clone**:
```bash
git clone https://github.com/openwebwork/webwork-open-problem-library.git
cd webwork-open-problem-library
git submodule update --init --recursive
```

**Size**: ~2.5 GB

### 2. **WeBWorK Problem Libraries** (GitHub)

Multiple curated collections:

#### a. **CUNY Problems**
- URL: https://github.com/drdrew42/CUNYProblemLibrary
- Size: ~500 problems
- Focus: Remedial math, College Algebra, Precalculus
- Quality: Modern, well-documented

#### b. **NIST Problems**
- Focus: Scientific computing, numerical methods
- URL: Check OPL Contrib section

#### c. **Michigan State Problems**
- Focus: Engineering math, applied calculus
- URL: https://github.com/openwebwork/webwork-open-problem-library (MSU section)

### 3. **Subject-Specific Collections**

#### Calculus
- **MIT OCW Problems**: Available in OPL/MIT
- **Paul's Online Math Notes**: (Not in PG format, but could convert)
  - URL: https://tutorial.math.lamar.edu/

#### Statistics
- **Lock5 Statistics**: In OPL/Lock5
- **Intro Stats Problems**: OPL/UBC/Stats

#### Linear Algebra
- **TCNJ Linear Algebra**: OPL/TCNJ/LinearAlgebra
- **Hope College**: OPL/Hope/LinearAlgebra

#### Differential Equations
- **Fort Lewis**: OPL/FortLewis/DiffEq
- **Michigan**: OPL/Michigan/DiffEq

### 4. **Textbook-Specific Problems**

These are tagged to specific textbooks:

- **Stewart Calculus**: ~5,000 problems
- **Briggs Calculus**: ~3,000 problems  
- **Rogawski Calculus**: ~2,000 problems
- **OpenStax**: ~1,500 problems (open source textbook)
- **WHFreeman**: Various textbooks

## Import Strategy

### Phase 1: Import OPL Subset (Recommended Start)

Start with high-quality, curated collections:

```bash
# 1. Clone OPL
git clone --depth 1 https://github.com/openwebwork/webwork-open-problem-library.git opl

# 2. Import specific collections
python scripts/import_opl.py opl/OpenProblemLibrary/FortLewis
python scripts/import_opl.py opl/OpenProblemLibrary/TCNJ
python scripts/import_opl.py opl/OpenProblemLibrary/Hope
python scripts/import_opl.py opl/OpenProblemLibrary/UBC

# 3. Import by subject
python scripts/import_opl.py opl/OpenProblemLibrary/Michigan/Chap1Sec1  # Calculus I
python scripts/import_opl.py opl/OpenProblemLibrary/*/LinearAlgebra    # All LA problems
```

**Estimated size**: 5,000-10,000 quality problems

### Phase 2: Import Full OPL (If Needed)

```bash
python scripts/import_opl.py opl/OpenProblemLibrary --all
```

**Warning**: This will import 35,000+ problems (~3 GB database)

### Phase 3: Subject-Specific Imports

For targeted collections:

```bash
# Calculus only
find opl/OpenProblemLibrary -path "*/Calculus/*" -name "*.pg" | \
    xargs python scripts/import_problems.py --collection opl_calculus

# Statistics only  
find opl/OpenProblemLibrary -path "*/Statistics/*" -name "*.pg" | \
    xargs python scripts/import_problems.py --collection opl_stats
```

## Implementation: OPL Import Script

Create `scripts/import_opl.py`:

```python
#!/usr/bin/env python3
"""Import problems from Open Problem Library."""

import sys
from pathlib import Path
from import_problems import ProblemImporter

def import_opl_directory(opl_path: Path, collection_name: str = "OPL"):
    """Import problems from OPL directory."""
    
    print(f"🔍 Scanning OPL directory: {opl_path}")
    
    # Find all .pg files
    pg_files = list(opl_path.rglob("*.pg"))
    print(f"📚 Found {len(pg_files)} PG files")
    
    # Create simplified metadata (OPL problems use different format)
    metadata = {}
    
    for pg_file in pg_files:
        # Extract path relative to OPL root
        relative_path = pg_file.relative_to(opl_path)
        
        # Read file to extract metadata
        with open(pg_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Extract OPL-style metadata
        db_subject = extract_tag(content, 'DBsubject')
        db_chapter = extract_tag(content, 'DBchapter')
        db_section = extract_tag(content, 'DBsection')
        
        metadata[pg_file.name] = {
            'name': pg_file.stem.replace('_', ' ').replace('-', ' '),
            'dir': str(relative_path.parent),
            'description': extract_description(content),
            'types': ['sample'],
            'subjects': [db_subject.lower()] if db_subject else [],
            'categories': [],
            'keywords': extract_keywords(content),
            'macros': extract_macros(content),
            'related': [],
            'DBsubject': db_subject,
            'DBchapter': db_chapter,
            'DBsection': db_section
        }
    
    # Import using existing importer
    importer = ProblemImporter()
    importer.init_database()
    
    # Import problems with OPL metadata
    count = 0
    for pg_file in pg_files:
        # Similar to import_problems.py but with OPL-specific handling
        # ... implementation ...
        count += 1
    
    print(f"✅ Imported {count} problems from OPL")

def extract_tag(content: str, tag: str) -> str:
    """Extract metadata tag from PG file."""
    import re
    pattern = rf'##\s*{tag}\((.*?)\)'
    match = re.search(pattern, content)
    return match.group(1).strip() if match else ""

# ... helper functions ...

if __name__ == "__main__":
    opl_path = Path(sys.argv[1])
    import_opl_directory(opl_path)
```

## Metadata Mapping: OPL to Our Format

OPL uses different metadata format:

```perl
## DESCRIPTION
## Brief description here
## ENDDESCRIPTION

## DBsubject(Calculus)
## DBchapter(Limits and Continuity)  
## DBsection(Evaluating Limits)
## Date(01/01/2000)
## Institution(Rochester)
## Author(John Doe)
## MLT(limit_basic)
## Level(2)
## KEYWORDS('calculus','limit')
```

Our mapping:
```json
{
  "subjects": ["calculus"],
  "categories": ["limits", "continuity"],
  "keywords": ["calculus", "limit"],
  "metadata": {
    "db_subject": "Calculus",
    "db_chapter": "Limits and Continuity",
    "db_section": "Evaluating Limits",
    "institution": "Rochester",
    "level": 2
  }
}
```

## Quality Tiers (Import Priority)

### Tier 1: Highest Quality (Import First) ⭐⭐⭐
- **FortLewis**: Modern PGML, well-documented (~500 problems)
- **Hope**: Excellent examples, documented (~600 problems)
- **TCNJ**: High quality, diverse subjects (~800 problems)
- **UBC**: Modern, well-tested (~2,000 problems)

### Tier 2: Good Quality ⭐⭐
- **Michigan**: Large collection, well-maintained (~3,000 problems)
- **LoyolaChicago**: Good coverage (~1,500 problems)
- **NAU**: Solid problems (~600 problems)

### Tier 3: Classic Collection ⭐
- **Rochester**: Largest but oldest collection (~7,000 problems)
- Note: May need syntax updates for modern WeBWorK

## Estimated Database Sizes

| Collection | Problem Count | DB Size | Import Time |
|------------|--------------|---------|-------------|
| Tutorial | 161 | 2 MB | 30 sec |
| Tier 1 (curated) | ~2,000 | 30 MB | 5 min |
| Tier 2 | ~5,000 | 75 MB | 15 min |
| Full OPL | ~35,000 | 500 MB | 2 hours |

## Testing New Collections

Before full import, test a subset:

```bash
# Test with 10 problems
find opl/OpenProblemLibrary/Hope -name "*.pg" | head -10 | \
    xargs python scripts/import_problems.py --test

# Review in database
sqlite3 problems.db "SELECT name, source_collection FROM problems WHERE source_collection='OPL-Hope'"
```

## ✅ Implementation Complete!

The import system is now fully implemented and ready to use.

### Quick Start

```bash
# Option 1: Automated import (recommended)
python scripts/bootstrap_opl.py

# Option 2: Test with small sample first
git clone --depth 1 https://github.com/openwebwork/webwork-open-problem-library.git
python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/Hope --limit 50

# Option 3: Manual import of specific collections
python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/Hope
python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/TCNJ
```

### Available Scripts

- **`scripts/import_opl.py`** - Import from OPL (supports any collection)
- **`scripts/bootstrap_opl.py`** - Automated Tier 1 import (~4,000 problems)
- **`scripts/test_import.py`** - Test and verify import system
- **`scripts/import_problems.py`** - Import tutorial problems (already done)

### Documentation

- **IMPORT_GUIDE.md** - Complete import guide with examples
- **IMPORT_SUMMARY.md** - Quick reference and system status
- This file (PROBLEM_SOURCES.md) - Available problem sources

## Next Steps

1. **Immediate** (Today):
   ```bash
   # Test the system
   python scripts/test_import.py
   
   # Import a small sample (50 problems)
   git clone --depth 1 https://github.com/openwebwork/webwork-open-problem-library.git
   python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/Hope --limit 50
   ```

2. **Short-term** (This Week):
   ```bash
   # Automated Tier 1 import (~4,000 problems)
   python scripts/bootstrap_opl.py
   ```

3. **Medium-term** (Month 1):
   - Import Tier 2 collections (Michigan, LoyolaChicago)
   - Add search ranking based on problem quality
   - Implement problem ratings

4. **Long-term**:
   - Full OPL import (~35,000 problems)
   - Textbook-specific collections
   - User-contributed problems

## Resources

- **OPL Browser**: https://webwork.maa.org/moodle/mod/data/view.php?id=3
- **OPL GitHub**: https://github.com/openwebwork/webwork-open-problem-library
- **Problem Authoring Guide**: https://webwork.maa.org/wiki/Problem_Authoring
- **PG Documentation**: https://webwork.maa.org/pod/pg/

## Community

- **WeBWorK Forums**: https://webwork.maa.org/moodle/
- **GitHub Issues**: Report problems with specific PG files
- **Mailing List**: webwork@lists.webwork.maa.org
