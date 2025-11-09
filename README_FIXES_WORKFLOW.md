# Sample Problems Fixing Workflow

A systematic approach to fix and improve the 157 tutorial PG sample problems for the Python implementation.

## Quick Start

### 1. Initial Diagnosis
Get an overview of what's failing:

```powershell
# Run batch test to see all problems and categorize errors
& "C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py::test_tutorial_problems_batch_rendering" -v -s 2>&1 | Tee-Object -FilePath "d:\pg\batch_results_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
```

This shows:
- How many problems pass/fail
- Error breakdown by type
- Sample errors for each category

### 2. Get Detailed Diagnostic Report
```powershell
# Generate detailed diagnostics for all problems
cd d:\pg
& "C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" scripts/batch_diagnose_all.py

# Output files created:
# - problems_diagnostic_report.txt (detailed findings)
# - problems_diagnostic_summary.json (structured data)
# - problems_by_error_type.txt (quick reference by error type)
```

### 3. Diagnose a Single Problem
```powershell
# Understand why a specific problem fails
& "C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" scripts/diagnose_problem.py "tutorial/sample-problems/Algebra/SimpleFactoring.pg"

# Shows:
# - Original .pg file (first 20 lines)
# - Generated Python code
# - Error message with suggestions
# - Recommended fixes
```

### 4. Quick Test During Development
```powershell
# Fast test of a single problem while fixing
& "C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" scripts/quick_test.py "tutorial/sample-problems/Algebra/SimpleFactoring.pg"

# Shows: ✅ PASSED or ❌ FAILED + error
```

### 5. Track Progress
```powershell
# Run tests and record checkpoint
& "C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" scripts/track_progress.py --note "Fixed Priority 1 NameErrors"

# View progress history
& "C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" scripts/track_progress.py --report
```

---

## Fixing Strategy

### Phase 1: Low-Hanging Fruit (SyntaxError, ImportError)
These are usually the easiest to fix - syntax errors, missing macros, typos.

**Process:**
```
1. Get list of problems with SyntaxError/ImportError from diagnostic report
2. For each problem:
   a. diagnose_problem.py to see the error
   b. Read the problem .pg file
   c. Fix the syntax issue in the .pg file
   d. Run quick_test.py to verify
3. Track progress with track_progress.py
```

**Example fixes:**
- Add missing `loadMacros()` calls
- Fix incorrect function calls
- Correct variable names

### Phase 2: NameError (Undefined Functions/Variables)
Usually need to add macro loads or set up missing objects.

**Process:**
1. Identify which function/variable is undefined
2. Determine which macro provides it
3. Add the macro to `loadMacros()` call
4. Test

### Phase 3: AttributeError (Missing Methods/Properties)
Object compatibility issues - usually require understanding the object model.

**Process:**
1. Understand what object is being used
2. Check if method name changed in Python version
3. Update call if needed
4. Or find alternative approach

### Phase 4: TypeError (Type Mismatches)
More complex - may require refactoring the logic.

**Process:**
1. Understand what types are expected vs provided
2. Adapt algorithm if needed
3. May need to modify the problem logic

---

## Key Files

### Planning & Documentation
- `PLAN_FIX_SAMPLE_PROBLEMS.md` - Full strategic plan
- `README_FIXES_WORKFLOW.md` - This file

### Diagnostic Tools
- `scripts/diagnose_problem.py` - Detailed diagnosis of a single problem
- `scripts/batch_diagnose_all.py` - Batch analysis of all problems
- `scripts/quick_test.py` - Fast test during development
- `scripts/track_progress.py` - Progress tracking and reporting

### Generated Reports
- `batch_rendering_results.txt` - Test batch output
- `problems_diagnostic_report.txt` - Detailed findings
- `problems_diagnostic_summary.json` - Structured data
- `problems_by_error_type.txt` - Quick reference
- `PROGRESS_FIXES.json` - Progress history

### Original Problems
- `tutorial/sample-problems/*/` - 157 .pg files organized by category:
  - `Algebra/` - Algebraic problems
  - `Arithmetic/` - Basic arithmetic
  - `DiffCalc/` - Differential calculus
  - `IntegralCalc/` - Integral calculus
  - `Trig/` - Trigonometry
  - `LinearAlgebra/` - Linear algebra
  - And 11 more categories...

---

## Example Workflow

### Scenario: Fix a NameError

```powershell
# 1. See what's failing
cd d:\pg
& "C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" scripts/batch_diagnose_all.py --limit 5

# 2. Find a NameError problem
# Output shows: LinearInterpolation.pg has "NameError: name 'DispatchList' is not defined"

# 3. Diagnose it
& "C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" scripts/diagnose_problem.py "tutorial/sample-problems/Misc/LinearInterpolation.pg"

# 4. Read the original problem file
# Look at tutorial/sample-problems/Misc/LinearInterpolation.pg

# 5. See what loadMacros it has
# Might be missing the macro that defines DispatchList

# 6. Add the macro to the loadMacros() call:
# loadMacros("PG.pl", "PGbasicmacros.pl", "PGanswergroup.pl", ...)

# 7. Test the fix
& "C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" scripts/quick_test.py "tutorial/sample-problems/Misc/LinearInterpolation.pg"

# 8. If it passes, commit the change
# If not, diagnose further and repeat

# 9. Track progress
& "C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" scripts/track_progress.py --note "Fixed LinearInterpolation NameError"
```

---

## Understanding the Generated Python

### View Generated Code
When diagnosing, the generated Python code helps understand what's happening:

```
Original .pg:
    $a = Formula("x^2");

Generated Python:
    a = Formula("x**2")  # Note: PG ^ becomes Python **
```

### Common Patterns
- PG's `^` (power) becomes Python's `**`
- PG's `$var` becomes Python's `var` (variable access)
- PG macros generate Python function calls
- Answer checking is handled differently

---

## Testing Best Practices

### Run Full Test Suite
```powershell
& "C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py" -v --tb=short
```

### Test Single Problem
```powershell
& "C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py::test_tutorial_problem_renders[SimpleFactoring]" -v
```

### Run Batch Test with Progress
```powershell
& "C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py::test_tutorial_problems_batch_rendering" -v -s
```

---

## Git Workflow for Fixes

Each fix should ideally be:
1. **Small, focused** - Fix one or a few related problems per commit
2. **Testable** - Each commit should show test improvement
3. **Documented** - Commit message explains the fix

```powershell
# Create fix branch
git checkout -b fix/sample-problems-batch1

# Make changes to .pg files

# Test locally
& "C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" scripts/quick_test.py "tutorial/sample-problems/..."

# Commit
git commit -m "Fix: SimpleFactoring - add missing PGbasicmacros macro"

# After fixing a batch
git commit -m "Fix: NameError batch (5 problems fixed)"

# Track progress
& "C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" scripts/track_progress.py --note "Batch 1 complete - 8 problems fixed"

# Push when ready
git push origin fix/sample-problems-batch1
```

---

## Troubleshooting

### Diagnostic Script Not Running
```
Issue: "Import pg_translator could not be resolved"
Solution: This is just an IDE warning - the script will work at runtime
```

### Tests Timeout
```
Issue: Batch test takes very long
Solution: Use --limit flag to test subset:
  python batch_diagnose_all.py --limit 10
```

### Can't Understand Error Message
```
Solution: Use --show-full flag:
  python diagnose_problem.py problem.pg --show-full
```

### Problem Still Fails After Fix
```
Process:
1. Make note of the problem
2. Run diagnose_problem.py again to see new error
3. May be a different error revealed after fixing the first one
4. Fix iteratively until all errors are resolved
```

---

## Success Metrics

**Current Baseline (2025-11-09):**
- Passing: 58/157 (36.9%)
- Failing: 99/157

**Goals:**
- Phase 1 (after 1 day): 80/157 (51%)
- Phase 2 (after 2 days): 110/157 (70%)
- Phase 3 (after 3 days): 140/157 (89%)
- Final (after 5 days): 155+/157 (98%+)

---

## References

- **Test File:** `packages/pg_translator/tests/test_tutorial_sample_problems.py`
- **Translator:** `packages/pg_translator/` (PGTranslator class)
- **Macro Packages:** `packages/pg_macros/`
- **Math Objects:** `packages/pg_math/`
- **Tutorial Problems:** `tutorial/sample-problems/`

---

## Contributing

When fixing problems:
1. Keep fixes atomic (one conceptual fix per commit)
2. Add comments explaining non-obvious changes
3. Update progress tracking
4. Share findings with team via commit messages and tracking file

---

*For detailed strategic planning, see `PLAN_FIX_SAMPLE_PROBLEMS.md`*
