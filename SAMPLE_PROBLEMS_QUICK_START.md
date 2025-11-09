# Sample Problems Fix - Quick Start Guide

This guide helps you start fixing the 57 failing sample problems systematically.

## Prerequisites

```powershell
# Activate Python environment
conda activate pytorch-5090

# Install dependencies (if needed)
python -m pip install -e packages/pg_translator[dev]
```

## Quick Start (5 minutes)

### 1. Generate Error Analysis Report

```powershell
# Run analysis (takes ~2-3 minutes)
python tools/analyze_sample_errors.py --run

# View the report
code ERROR_ANALYSIS.md
```

This creates a comprehensive report showing:
- All 57 failing problems categorized by error type
- Common patterns (assignment in condition, string issues, etc.)
- Fix priority ranking
- Recommended actions

### 2. Analyze a Specific Problem

```powershell
# Example: Analyze NoSolution.pg
python tools/fix_sample_problem.py --analyze NoSolution
```

This shows:
- Full error message
- First 50 lines of preprocessed Python code
- Helps identify the root cause

### 3. Convert Problem to Python

```powershell
# Convert NoSolution.pg to NoSolution.pypg
python tools/fix_sample_problem.py --convert NoSolution

# View the generated Python
code tutorial/sample-problems/Algebra/NoSolution.pypg
```

Now you can see exactly what Python code was generated from the PG file.

### 4. Test Your Fix

```powershell
# After making a fix, test just that problem
python tools/fix_sample_problem.py --test NoSolution
```

## Common Workflows

### Workflow 1: Fix a Preprocessor Issue

Example: Fix "assignment in condition" errors

1. **Identify the pattern:**
   ```powershell
   python tools/fix_sample_problem.py --analyze NoSolution
   ```

2. **Check the preprocessed code:**
   ```powershell
   python tools/fix_sample_problem.py --convert NoSolution
   code tutorial/sample-problems/Algebra/NoSolution.pypg
   ```
   
   You might see:
   ```python
   # Line 36 - SyntaxError
   if (x = 5)  # ← Python doesn't allow assignment in if condition
   ```

3. **Fix the preprocessor:**
   
   Edit `packages/pg_translator/pg_translator/pg_preprocessor_pygment.py`:
   
   ```python
   # Find the section handling conditional statements
   # Add conversion for assignment in condition:
   
   # Before: if ($x = value)
   # After: x = value; if x
   # Or: if (x := value)  # Python walrus operator
   ```

4. **Test the fix:**
   ```powershell
   # Test this specific problem
   python tools/fix_sample_problem.py --test NoSolution
   
   # Test all to check for regressions
   python -m pytest packages/pg_translator/tests/test_tutorial_sample_problems.py -v
   ```

### Workflow 2: Fix a Missing Context Type

Example: Fix "NameError: name 'String' is not defined"

1. **Identify what's missing:**
   ```powershell
   python tools/fix_sample_problem.py --analyze StringOrOtherType
   ```
   
   Shows: `NameError: name 'String' is not defined`

2. **Check where it's used:**
   ```powershell
   python tools/fix_sample_problem.py --convert StringOrOtherType
   code tutorial/sample-problems/Algebra/StringOrOtherType.pypg
   ```

3. **Add the Context type:**
   
   Option A: Fix in preprocessor to auto-detect and inject
   
   Edit `packages/pg_translator/pg_translator/pg_preprocessor_pygment.py`:
   ```python
   def detect_required_contexts(code: str) -> set[str]:
       """Detect which Context types are needed."""
       contexts = set()
       if re.search(r'\bString\b', code):
           contexts.add('String')
       # Add other types...
       return contexts
   ```
   
   Option B: Add to macro that's already loaded
   
   Check if problem uses `loadMacros()` and add String support there.

4. **Test:**
   ```powershell
   python tools/fix_sample_problem.py --test StringOrOtherType
   ```

### Workflow 3: Fix Individual Problem

Some problems need custom fixes:

1. **Deep dive:**
   ```powershell
   # Get full analysis
   python tools/fix_sample_problem.py --analyze TriangleGraphTool
   
   # Look at original PG
   code tutorial/sample-problems/Geometry/TriangleGraphTool.pg
   
   # Look at generated Python
   python tools/fix_sample_problem.py --convert TriangleGraphTool
   code tutorial/sample-problems/Geometry/TriangleGraphTool.pypg
   ```

2. **Identify root cause:**
   - Missing variable declaration?
   - Wrong syntax conversion?
   - Missing feature in MathObjects?

3. **Apply fix:**
   - If preprocessor bug: fix in `pg_preprocessor_pygment.py`
   - If missing feature: add to `packages/pg_math/`
   - If .pg file issue: carefully edit the .pg file

4. **Test and document:**
   ```powershell
   python tools/fix_sample_problem.py --test TriangleGraphTool
   
   # Document in git commit
   git add .
   git commit -m "fix(tutorial): Fix TriangleGraphTool - undefined variable x3"
   ```

## Batch Operations

### Convert All Problems to Python

Useful for pattern analysis:

```powershell
python tools/fix_sample_problem.py --batch-convert
```

Creates `.pypg` files next to each `.pg` file.

### List All Failing Problems

```powershell
python tools/fix_sample_problem.py --list-failing
```

Shows simple list of problem names.

### Run Full Test Suite

```powershell
# All problems
python -m pytest packages/pg_translator/tests/test_tutorial_sample_problems.py -v

# Just count pass/fail
python -m pytest packages/pg_translator/tests/test_tutorial_sample_problems.py -v --tb=line | Select-String "passed|failed"

# Stop on first failure (for debugging)
python -m pytest packages/pg_translator/tests/test_tutorial_sample_problems.py -x -v

# Run with coverage
python -m pytest packages/pg_translator/tests/test_tutorial_sample_problems.py --cov=pg_translator --cov-report=html
```

## Tips & Tricks

### Tip 1: Focus on High-Impact Patterns

From ERROR_ANALYSIS.md, identify patterns that affect many problems:
- Assignment in condition: ~8 problems
- String issues: ~3 problems  
- Type errors: ~5 problems

Fixing one preprocessor pattern can fix multiple problems at once!

### Tip 2: Use Git Branches

```powershell
# Create branch for each major fix category
git checkout -b fix/sample-problems-syntax
# ... make fixes ...
git commit -am "fix: Resolve assignment in condition errors"

git checkout -b fix/sample-problems-context
# ... make fixes ...
git commit -am "fix: Add missing Context types"
```

### Tip 3: Test Incrementally

Don't fix everything at once. After each fix:

```powershell
# Quick smoke test (first failure)
python -m pytest packages/pg_translator/tests/test_tutorial_sample_problems.py -x

# Full validation
python -m pytest packages/pg_translator/tests/test_tutorial_sample_problems.py -v
```

### Tip 4: Look for Similar Problems

If you fix one problem, check for similar patterns:

```powershell
# Search for similar code patterns
rg "if.*=" tutorial/sample-problems/**/*.pg

# Find problems using same macros
rg "loadMacros.*String" tutorial/sample-problems/**/*.pg
```

### Tip 5: Don't Modify .pg Files Unless Necessary

Priority order for fixes:
1. **Best:** Fix in preprocessor (fixes all similar problems)
2. **Good:** Fix in MathObjects/Context (adds missing feature)
3. **Last resort:** Edit .pg file (only if truly necessary)

## Progress Tracking

### Check Current Status

```powershell
# Run full suite and count
python -m pytest packages/pg_translator/tests/test_tutorial_sample_problems.py -v --tb=line | Select-String "passed.*failed"
```

### Update Documentation

As you fix problems, update these files:
- `ERROR_ANALYSIS.md` - Regenerate after each batch of fixes
- `SAMPLE_PROBLEMS_FIX_PLAN.md` - Check off completed items
- Create `SAMPLE_PROBLEMS_FIX_LOG.md` - Record what you fixed

Example log entry:

```markdown
## 2025-11-09: Fixed Assignment in Condition Errors

**Problems Fixed:** 8
- NoSolution
- LineSegmentGraphTool
- QuadrilateralGraphTool
- LinearApprox
- (5 more...)

**Root Cause:** Preprocessor was directly translating Perl `if ($x = value)` 
to Python `if (x = value)` which is a syntax error.

**Fix:** Modified `pg_preprocessor_pygment.py` line 1234 to convert to walrus 
operator when assignment detected in condition.

**Test Results:** All 8 problems now pass. No regressions in other tests.

**Commit:** abc1234
```

## Getting Help

If stuck:

1. **Check existing patterns:**
   ```powershell
   rg "similar pattern" packages/pg_translator/tests/
   ```

2. **Look at working examples:**
   - Find a passing problem similar to your failing one
   - Compare the .pg files
   - Compare the .pypg files

3. **Review documentation:**
   - `AGENTS.md` - Project structure
   - `GRAMMAR_FEATURE_REFERENCE.md` - PG syntax reference
   - `IMPORT_GUIDE.md` - How imports work

## Next Steps

1. **Start with ERROR_ANALYSIS.md:**
   ```powershell
   python tools/analyze_sample_errors.py --run
   code ERROR_ANALYSIS.md
   ```

2. **Pick a high-impact pattern** from Priority 1

3. **Fix 2-3 problems** to validate your approach

4. **Iterate** until all 57 problems pass!

---

**Goal:** 90%+ pass rate (142/157 problems passing)

**Current:** 64% (100/157 problems passing)

**Gap:** Fix 42+ problems

Good luck! 🚀
