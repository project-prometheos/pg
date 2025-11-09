# Sample Problems Fixing - Complete Guide

## Executive Summary

This guide provides a **systematic plan** to fix the 157 WeBWorK tutorial sample problems for the Python implementation. Current success rate: **36.9%** (58/157). Target: **95%+** (150+/157).

**Key Documents:**
- `PLAN_FIX_SAMPLE_PROBLEMS.md` - Strategic 6-phase plan
- `README_FIXES_WORKFLOW.md` - Practical workflow & commands
- `FIX_DOCUMENTATION_TEMPLATE.md` - How to document fixes
- This file - Complete overview

---

## Three-Step Quick Start

### Step 1: See What's Failing (5 minutes)
```powershell
cd d:\pg
# Run the batch test to see failures categorized by error type
& "C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest `
  "packages/pg_translator/tests/test_tutorial_sample_problems.py::test_tutorial_problems_batch_rendering" `
  -v -s 2>&1 | Tee-Object -FilePath "batch_results.txt"
```

**Output:** Shows how many pass/fail, breakdown by error type, sample errors

### Step 2: Understand Individual Problems (5 minutes each)
```powershell
# Diagnose a specific problem to see:
# - Original .pg file
# - Generated Python code  
# - Error message with suggestions
& "C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" `
  scripts/diagnose_problem.py "tutorial/sample-problems/Algebra/SimpleFactoring.pg"
```

**Output:** Shows what went wrong and suggested fixes

### Step 3: Fix & Test (1 minute per fix)
```powershell
# Edit the .pg file to fix the issue
# Then quick test:
& "C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" `
  scripts/quick_test.py "tutorial/sample-problems/Algebra/SimpleFactoring.pg"
```

**Output:** ✅ PASSED or ❌ FAILED + reason

---

## Available Tools

| Tool | Purpose | Runtime | Command |
|------|---------|---------|---------|
| **batch_diagnose_all.py** | Categorize all 157 problems by error type | ~30s | `python scripts/batch_diagnose_all.py` |
| **diagnose_problem.py** | Deep dive into a single problem | ~5s | `python scripts/diagnose_problem.py tutorial/.../Problem.pg` |
| **quick_test.py** | Fast test during development | ~2s | `python scripts/quick_test.py tutorial/.../Problem.pg` |
| **track_progress.py** | Record progress checkpoints | ~5 min | `python scripts/track_progress.py --note "Fixed batch 1"` |
| **pytest** | Full test suite | ~5 min | `pytest packages/pg_translator/tests/test_tutorial_sample_problems.py -v` |

---

## Systematic Fixing Strategy

### Phase 1: Quick Wins - SyntaxError (Est. 5-10 problems)
These are easiest - syntax issues, typos, formatting.

**Process:**
1. Run `batch_diagnose_all.py` to get list of SyntaxErrors
2. For each: `diagnose_problem.py` → fix → `quick_test.py`
3. Expected impact: +10-15 problems passing

### Phase 2: NameError Fixes (Est. 30-40 problems)  
Usually missing macros or undefined variables.

**Common fixes:**
- Add missing macro to `loadMacros()` call
- Example: `SimpleFactoring.pg` needed `PGbasicmacros.pl`

**Process:**
1. Get list of NameError problems
2. Most can be fixed by adding macro loads
3. Expected impact: +30-40 problems passing

### Phase 3: AttributeError Fixes (Est. 10-15 problems)
Object compatibility issues.

**Process:**
1. Understand what object/method is needed
2. Fix method call or find alternative
3. Expected impact: +10-15 problems passing

### Phase 4: TypeError & Other Complex Issues (Est. 10-20 problems)
Require more thought and potentially algorithm changes.

**Process:**
1. Understand the logic
2. Adapt to Python implementation
3. May need to modify problem structure
4. Expected impact: +10-20 problems passing

### Phase 5: Stubborn Problems (Est. 5-10 problems)
Problems that may need special handling or new features.

---

## Error Type Reference

### SyntaxError (20-25 problems)
**Root causes:**
- String escaping issues (LaTeX with backslashes)
- Perl vs Python syntax differences
- Malformed code

**Fix approach:**
- Fix escaping (use raw strings `r"..."`)
- Adapt Perl syntax to Python
- Correct operators/functions

**Example:**
```perl
# WRONG (Python treats \s as escape):
$latex = "\\sqrt{x}";

# FIXED (either):
$latex = r"\\sqrt{x}";  # or use macro that handles it
```

### NameError (35-45 problems)
**Root causes:**
- Missing macro in loadMacros()
- Undefined variable
- Wrong variable name

**Fix approach:**
- Add missing macro
- Define variable
- Check spelling

**Example:**
```perl
# WRONG:
loadMacros("PG.pl");  # Missing PGbasicmacros.pl
$ans = Formula("x^2");

# FIXED:
loadMacros("PG.pl", "PGbasicmacros.pl");
$ans = Formula("x^2");
```

### AttributeError (10-15 problems)
**Root causes:**
- Object missing method
- Renamed method
- Wrong object type

**Fix approach:**
- Find correct method name
- Check object initialization
- Use wrapper/compatibility layer

### TypeError (10-15 problems)
**Root causes:**
- Wrong argument type
- List vs scalar confusion
- Numeric vs string

**Fix approach:**
- Convert types as needed
- Fix function calls
- Adapt algorithm

### ImportError (5-10 problems)
**Root causes:**
- Macro path wrong
- Macro file missing
- Circular dependency

**Fix approach:**
- Verify macro exists
- Check path in loadMacros()
- Remove circular dependencies

---

## Workflow Summary

```
Discovery → Analysis → Prioritization → Fixing → Testing → Iteration

1. DISCOVERY
   ├─ Run: pytest batch rendering test
   ├─ Output: Which problems fail and why
   └─ Time: ~5 minutes

2. ANALYSIS
   ├─ Run: batch_diagnose_all.py
   ├─ Output: Problems grouped by error type
   ├─ Files: problems_diagnostic_report.txt, .json, by_error_type.txt
   └─ Time: ~30 seconds

3. PRIORITIZATION
   ├─ Focus on high-impact categories first
   ├─ Order: SyntaxError → NameError → AttributeError → ...
   └─ Expected: 80% of problems in first 3 categories

4. FIXING
   ├─ For each problem:
   │  ├─ diagnose_problem.py (see what's wrong)
   │  ├─ Edit the .pg file (apply fix)
   │  ├─ quick_test.py (verify it works)
   │  ├─ Document the fix (for reference)
   │  └─ Git commit (track changes)
   └─ Time: 1-5 minutes per problem

5. TESTING
   ├─ Quick: quick_test.py for individual problems
   ├─ Batch: pytest for full test suite
   └─ Track: track_progress.py to monitor improvement

6. ITERATION
   ├─ After fixing a batch (5-10 problems)
   ├─ Re-run full test to catch regressions
   ├─ Adjust strategy if needed
   └─ Move to next batch
```

---

## Expected Timeline

| Phase | Duration | Problems Fixed | Pass Rate |
|-------|----------|---|---|
| Initial | Day 1 Start | 58 | 36.9% |
| SyntaxError | Day 1 Afternoon | +15 | ~50% |
| NameError | Day 2 Morning | +35 | ~72% |
| AttributeError | Day 2 Afternoon | +12 | ~80% |
| TypeError | Day 3 Morning | +10 | ~86% |
| Complex/Stubborn | Day 3+ | +8 | ~95% |

---

## File Organization

```
d:\pg\
├── PLAN_FIX_SAMPLE_PROBLEMS.md
│   └─ 6-phase strategic plan (detailed)
│
├── README_FIXES_WORKFLOW.md
│   └─ Practical workflow guide (with commands)
│
├── FIX_DOCUMENTATION_TEMPLATE.md
│   └─ How to document each fix
│
├── THIS_FILE.md (COMPLETE_GUIDE.md)
│   └─ Overview (you are here)
│
├── scripts/
│   ├── diagnose_problem.py (detailed diagnosis)
│   ├── batch_diagnose_all.py (categorize all failures)
│   ├── quick_test.py (fast individual test)
│   └── track_progress.py (progress tracking)
│
├── tutorial/sample-problems/
│   ├── Algebra/ (e.g., SimpleFactoring.pg)
│   ├── Arithmetic/
│   ├── Complex/
│   ├── DiffCalc/
│   ├── DiffCalcMV/
│   ├── DiffEq/
│   ├── Geometry/
│   ├── IntegralCalc/
│   ├── LinearAlgebra/
│   ├── Misc/
│   ├── Parametric/
│   ├── ProblemTechniques/
│   ├── Sequences/
│   ├── Statistics/
│   ├── Trig/
│   └── VectorCalc/
│
├── Generated Reports (after running tools)
│   ├── batch_results.txt (from pytest)
│   ├── problems_diagnostic_report.txt
│   ├── problems_diagnostic_summary.json
│   ├── problems_by_error_type.txt
│   └── PROGRESS_FIXES.json (tracking)
│
└── packages/pg_translator/tests/
    └── test_tutorial_sample_problems.py (the tests)
```

---

## Example Scenario: Complete a Full Cycle

**Scenario:** Fix SimpleFactoring and 2 similar Algebra problems

### Step 1: Diagnosis (10 minutes)
```powershell
# See all failures
python scripts/batch_diagnose_all.py --limit 20

# Get details on SimpleFactoring
python scripts/diagnose_problem.py "tutorial/sample-problems/Algebra/SimpleFactoring.pg"

# Output shows: NameError - Formula not defined
# Root cause: loadMacros missing PGbasicmacros.pl
```

### Step 2: Fix (5 minutes)
```powershell
# Edit tutorial/sample-problems/Algebra/SimpleFactoring.pg
# Change: loadMacros("PG.pl", "PGcourse.pl");
# To: loadMacros("PG.pl", "PGbasicmacros.pl", "PGcourse.pl");

# Quick test
python scripts/quick_test.py "tutorial/sample-problems/Algebra/SimpleFactoring.pg"
# ✅ PASSED

# Apply same fix to similar problems
python scripts/quick_test.py "tutorial/sample-problems/Algebra/ExpandedPolynomial.pg"
# ✅ PASSED

# Document the fixes
# See FIX_DOCUMENTATION_TEMPLATE.md for format
```

### Step 3: Track (2 minutes)
```powershell
# Record progress
python scripts/track_progress.py --note "Fixed 3 Algebra NameErrors - all needed PGbasicmacros.pl"

# View progress
python scripts/track_progress.py --report
# Shows: Progress from 58 → 61 passing
```

### Step 4: Commit (2 minutes)
```powershell
git add tutorial/sample-problems/Algebra/*.pg
git commit -m "Fix: Add missing PGbasicmacros.pl to 3 Algebra problems

- SimpleFactoring.pg: NameError Formula not defined
- ExpandedPolynomial.pg: NameError Formula not defined  
- [third problem]: NameError Formula not defined

Fixes: 3 problems passing
Pass rate: 36.9% → 39.5%"
```

**Total Time:** ~20 minutes for 3 problems fixed

---

## Success Criteria

- [ ] **Syntax:** 0 SyntaxError failures
- [ ] **Names:** 0 NameError failures
- [ ] **Attributes:** 0 AttributeError failures
- [ ] **Render:** All problems produce non-empty statement_html
- [ ] **Rate:** ≥95% success rate (151+/157)
- [ ] **Documentation:** Each fix documented
- [ ] **Tests:** Full pytest suite passes

---

## Troubleshooting

### Problem: Diagnostic script won't run
**Solution:** The import warnings are expected - they're IDE warnings, not runtime errors

### Problem: Tests timeout
**Solution:** Use `--limit` flag: `python scripts/batch_diagnose_all.py --limit 10`

### Problem: Error message is confusing
**Solution:** Use `--show-full` flag to see complete error: `python scripts/diagnose_problem.py problem.pg --show-full`

### Problem: After fixing one error, a different error appears
**Solution:** This is normal - problems often have multiple issues. Fix iteratively until all errors resolved.

### Problem: Same error in many problems
**Solution:** This is good! It means you can create a batch fix. Document the pattern and apply to all similar problems.

---

## Tips for Efficiency

### Batch Fixes
Group problems by error type and apply same fix to multiple problems at once:
```powershell
# Fix all Algebra problems that need PGbasicmacros.pl
# Instead of: edit 1, test 1, edit 1, test 1
# Do: edit all 5, test all 5, commit all 5
```

### Use version control
```powershell
git checkout -b fix/syntax-errors-batch1
# Fix 5-10 problems
git commit -m "Fix: SyntaxError batch - string escaping (8 problems)"
# Then: git checkout -b fix/nameerror-batch1
```

### Keep diagnostic reports
Before starting a batch, save the diagnostic report for reference:
```powershell
python scripts/batch_diagnose_all.py > problems_to_fix.txt
```

### Document patterns
As you fix problems, note patterns:
```
Pattern 1: SyntaxError + backslashes in strings
  → Use r"..." raw strings (affects ~8 problems)

Pattern 2: NameError + Formula undefined
  → Add PGbasicmacros.pl (affects ~12 problems)

Pattern 3: NameError + random() undefined
  → Add PGrandom.pl (affects ~6 problems)
```

---

## Resources

### Documentation
- WeBWorK Problem Authoring: http://webwork.maa.org/wiki/Authors
- PG Language Reference: http://webwork.maa.org/wiki/PG
- Macro Documentation: See `macros/` directory

### Related Code
- `packages/pg_translator/` - Main translator
- `packages/pg_macros/` - Macro implementations
- `packages/pg_math/` - Math objects
- `packages/pg_renderer/` - Output rendering

### Test Infrastructure
- Test file: `packages/pg_translator/tests/test_tutorial_sample_problems.py`
- Runs all 157 tutorial problems
- Categorizes failures

---

## Next Actions

### To Start Right Now:
1. ✅ Read `README_FIXES_WORKFLOW.md` (15 min)
2. ✅ Run: `python scripts/batch_diagnose_all.py` (1 min)
3. ✅ Run: `python scripts/diagnose_problem.py tutorial/sample-problems/Algebra/SimpleFactoring.pg` (1 min)
4. ✅ Read a .pg file that's failing (2 min)
5. ✅ Make first fix and test it (5 min)
6. ✅ Record progress: `python scripts/track_progress.py --note "First fix complete"` (1 min)

**Total time to first fix:** ~25 minutes

### Then Iterate:
- Fix 5-10 problems per batch
- Test after each batch
- Track progress
- Document patterns as you find them

---

## Final Checklist

Before you start:
- [ ] Conda environment activated (`pytorch-5090`)
- [ ] Terminal at `d:\pg`
- [ ] Read `README_FIXES_WORKFLOW.md`
- [ ] Understand the 3-step quick start
- [ ] Know what tools are available

Ready to go? Start with:
```powershell
cd d:\pg
python scripts/batch_diagnose_all.py --limit 10
```

Good luck! 🚀

---

*Last updated: 2025-11-09*
*For detailed planning: See `PLAN_FIX_SAMPLE_PROBLEMS.md`*
*For practical workflow: See `README_FIXES_WORKFLOW.md`*
