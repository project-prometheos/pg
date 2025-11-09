# Systematic Plan to Fix Sample PG Files for Python Implementation

## Overview
Fix the 157 tutorial sample problems in `tutorial/sample-problems/` to work correctly with the Python implementation (PGTranslator). Current baseline: ~36.9% success rate (58/157). Target: 100% or near-100%.

---

## Phase 1: Discovery & Analysis (Current State)

### 1.1 Run Full Test Suite to Identify Failures
```powershell
# Run the full test suite and capture failures
& "C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py" -v --tb=short 2>&1 | Select-String -Pattern "FAILED|SyntaxError|NameError|TypeError|AttributeError|ImportError" -Context 0,3 | Select-Object -First 200 | Tee-Object -FilePath "d:\pg\test_failures_initial.txt"
```

### 1.2 Run Slow Test for Error Categorization
```powershell
# Run batch rendering test to get error breakdown and categorization
& "C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py::test_tutorial_problems_batch_rendering" -v -s 2>&1 | Tee-Object -FilePath "d:\pg\batch_rendering_results.txt"
```

**Output:** 
- `test_failures_initial.txt` - Raw test failures
- `batch_rendering_results.txt` - Categorized errors (SyntaxError, NameError, AttributeError, etc.)

### 1.3 Categorize Errors
Parse the batch results to create error categories:
- **SyntaxError** - Malformed PG code
- **NameError** - Undefined variables/functions (missing macros)
- **AttributeError** - Missing methods/properties
- **TypeError** - Type mismatches
- **ImportError/ModuleNotFoundError** - Missing macro packages
- **Other** - Rendering/logic errors

**Deliverable:** `error_categories.json` or `error_categories.txt`

---

## Phase 2: Per-Problem Diagnosis

### 2.1 Create Diagnostic Script
For each failing problem:
1. Get filename from failing tests
2. Convert to Python with `pg-convert` (or PGTranslator)
3. Examine the generated Python code to understand the error
4. Identify the root cause in the original .pg file

**Script:** `scripts/diagnose_problem.py`
```
Input: problem_file.pg
Process:
  1. Translate problem using PGTranslator to get generated Python
  2. Show translation result (Python code)
  3. Show error message with context
  4. Show original .pg file section where error occurs
Output: diagnosis_report.txt with:
  - Problem name
  - Error type
  - Error message + traceback
  - Generated Python (relevant section)
  - Original PG code (relevant section)
  - Hypothesis for fix
```

### 2.2 Group Problems by Error Pattern
Instead of fixing each problem individually, identify common patterns:

**Example Groups:**
- **Group A:** Missing PGML/PGCORE macros → Need to add `loadMacros(...)` calls
- **Group B:** Using PG3 syntax → Need to adapt to Python implementation
- **Group C:** Missing answer checker setup → Need proper answer handling
- **Group D:** Complex random data structures → May need refactoring
- **Group E:** Graphics/special modules → May need different approach

---

## Phase 3: Systematic Fixing

### 3.1 Fix by Error Type (Priority Order)

**Priority 1: Quick Wins (SyntaxError, ImportError)**
- These are usually easy fixes: missing macros, typos, or incorrect function calls
- Should fix 20-30% of remaining issues quickly

**Priority 2: NameError (Undefined Functions/Variables)**
- Usually need to add macro loads or define variables
- Should fix another 20-30%

**Priority 3: AttributeError (Missing Methods)**
- Often related to object compatibility
- Requires understanding the object model

**Priority 4: TypeError (Type Issues)**
- More complex; may need refactoring
- Usually only 10-15% of problems

### 3.2 Fix Template Workflow

For each problem in the priority group:

```
1. READ: Original .pg file → understand intent
2. GENERATE: Python code via PGTranslator → see what it becomes
3. ERROR: Run test → capture error details
4. DIAGNOSE: Analyze generated code vs error
5. HYPOTHESIZE: What's the fix?
   - Add missing macro?
   - Fix function call signature?
   - Adapt algorithm to Python?
6. FIX: Modify original .pg file (or generated Python if direct fix is easier)
7. TEST: Verify fix works (run problem test again)
8. VALIDATE: Ensure rendering produces correct output
```

### 3.3 Create Fixes Documentation
For each fix, document:
```
Problem: filename.pg
Original Error: [error type] - [error message]
Root Cause: [explanation]
Fix Applied: [changes made]
Result: ✓ Fixed / ⚠ Partial / ✗ Unable to fix
Notes: [any gotchas or special considerations]
```

---

## Phase 4: Batch Processing & Automation

### 4.1 Create Batch Fix Script
```python
# scripts/batch_diagnose.py
# For each failing problem:
#   1. Run translator
#   2. Capture error
#   3. Generate report
#   4. Extract common patterns
# Output: prioritized fix list
```

### 4.2 Create Batch Testing Script
```python
# scripts/batch_test_fixes.py
# For each problem:
#   1. Run test
#   2. Check if passes
#   3. Collect statistics
# Output: progress_report.txt with:
#   - Success count (was X, now Y)
#   - Remaining issues by category
#   - Estimated effort for next batch
```

---

## Phase 5: Iteration & Refinement

### 5.1 Regression Testing
After each batch of fixes:
```powershell
# Run full test suite
& "C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py" -v --tb=line 2>&1 | Tee-Object -FilePath "d:\pg\test_results_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
```

### 5.2 Track Progress
Maintain a progress file:
```
Date        | Pass | Fail | % Success | Focus Area
2025-11-09  | 58   | 99   | 36.9%     | Initial state
2025-11-09  | 85   | 72   | 54.1%     | After Priority 1 fixes
2025-11-09  | 110  | 47   | 70.0%     | After Priority 2 fixes
...
```

---

## Phase 6: Special Cases & Stubborn Problems

### 6.1 Triage Unsolvable Problems
Some problems might be:
- Too complex for current Python translator
- Require features not yet implemented
- Need WeBWorK library features not ported

For these:
- Mark with `# TODO: Complex - requires [specific feature]`
- Consider creating wrapper or compatibility layer
- May need to skip or create alternative version

### 6.2 Create Compatibility Macros
As patterns emerge, create Python macro files:
```perl
# packages/pg_macros/compat_macros.pl
# Provides compatibility layers for:
# - Common PGML constructs
# - Answer checking patterns
# - Random data generation
```

---

## Implementation Tools

### Tool 1: Problem Translator with Diagnostics
**File:** `scripts/diagnose_problem.py`
```
Usage: python diagnose_problem.py tutorial/sample-problems/Algebra/Problem.pg
Output: Shows error, generated code, and suggested fix
```

### Tool 2: Batch Diagnostic Reporter
**File:** `scripts/batch_diagnose_all.py`
```
Usage: python batch_diagnose_all.py
Output: problems_diagnostic_report.json with all failures categorized
```

### Tool 3: Progress Tracker
**File:** `scripts/track_progress.py`
```
Usage: python track_progress.py
Output: Updates progress file, shows improvement metrics
```

### Tool 4: Quick Test Harness
**File:** `scripts/quick_test.py`
```
Usage: python quick_test.py tutorial/sample-problems/Algebra/Problem.pg
Output: Test this single problem without full pytest overhead
```

---

## Success Criteria

- [ ] All 157 problems successfully load and preprocess (0 SyntaxError, ImportError)
- [ ] All 157 problems successfully execute (0 NameError, AttributeError, TypeError)
- [ ] All 157 problems generate non-empty statement_html output
- [ ] No critical errors in result.errors for any problem
- [ ] Success rate ≥ 95% (≥151/157 passing)
- [ ] Tests pass in CI/CD pipeline

---

## Quick Start Checklist

```powershell
# 1. Run initial test sweep
& "C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py::test_tutorial_problems_batch_rendering" -v -s

# 2. Analyze results
# Review test_failures_initial.txt and batch_rendering_results.txt

# 3. Create diagnostic report
# Run: python scripts/batch_diagnose_all.py

# 4. Prioritize fixes
# Group problems by error type and complexity

# 5. Start fixing
# Pick first low-hanging fruit (SyntaxErrors, ImportErrors)

# 6. Track progress
# After each fix batch, re-run tests and log results
```

---

## Notes

- **Seed:** Use fixed seed (12345) for reproducibility during diagnosis
- **Isolation:** Test problems one at a time for easier debugging
- **Documentation:** Keep fixes documented for future reference
- **Reverting:** Keep git history clean; use branches for experimental fixes
- **Parallel Work:** Can work on different error categories in parallel
