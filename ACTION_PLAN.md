# FIXING ACTION PLAN

## Start Here

You now have a **complete systematic plan** to fix the 157 sample PG problems. Here's what to do right now:

### Step 1: Understand the Plan (10 minutes)

```powershell
# Read the complete overview
Get-Content d:\pg\COMPLETE_GUIDE_FIX_SAMPLE_PROBLEMS.md | less

# Or read the practical workflow
Get-Content d:\pg\README_FIXES_WORKFLOW.md | less
```

### Step 2: See What's Failing (5 minutes)

```powershell
cd d:\pg

# Run comprehensive diagnosis
python implement_fixes.py --start

# Then run the actual diagnostic scan
python scripts/batch_diagnose_all.py
```

This creates:
- `problems_diagnostic_report.txt` - Full details
- `problems_diagnostic_summary.json` - Structured data  
- `problems_by_error_type.txt` - Quick reference by error type

### Step 3: Understand the Strategy (10 minutes)

```powershell
# See complete 5-phase strategy
python implement_fixes.py --strategy

# See Phase 1 in detail
python implement_fixes.py --phase-1

# See Phase 2 in detail
python implement_fixes.py --phase-2

# See implementation checklist
python implement_fixes.py --checklist
```

### Step 4: Start Fixing (begins immediately)

**Phase 1: SyntaxError (easiest, ~1-2 hours)**
```powershell
# Pick one problem with SyntaxError
python scripts/diagnose_problem.py "tutorial/sample-problems/Algebra/SimpleFactoring.pg"

# Edit the .pg file to fix it
# (Your favorite editor)

# Test the fix
python scripts/quick_test.py "tutorial/sample-problems/Algebra/SimpleFactoring.pg"

# Track progress
python scripts/track_progress.py --note "Fixed SimpleFactoring SyntaxError"
```

**Phase 2: NameError (~2-4 hours)**
```powershell
# Continue with NameError problems
python scripts/diagnose_problem.py "tutorial/sample-problems/[Category]/[Problem].pg"

# Most will be fixed by adding missing macros to loadMacros()
# Example: Add "PGbasicmacros.pl" if Formula() is undefined

# Test and track after each batch
python scripts/quick_test.py "..."
python scripts/track_progress.py --note "Fixed [N] NameError problems"
```

---

## Key Documents

| Document | Purpose | When to Use |
|----------|---------|-----------|
| `COMPLETE_GUIDE_FIX_SAMPLE_PROBLEMS.md` | Full overview and reference | Start here for complete picture |
| `README_FIXES_WORKFLOW.md` | Practical commands and workflow | During fixing for command reference |
| `PLAN_FIX_SAMPLE_PROBLEMS.md` | Detailed 6-phase strategic plan | For strategic understanding |
| `FIX_DOCUMENTATION_TEMPLATE.md` | How to document fixes | When writing fix records |

---

## Available Tools

```powershell
# See what's failing (categorized by error type)
python scripts/batch_diagnose_all.py

# Understand a specific problem deeply
python scripts/diagnose_problem.py "tutorial/sample-problems/Algebra/Problem.pg"

# Quick test a problem
python scripts/quick_test.py "tutorial/sample-problems/Algebra/Problem.pg"

# Track progress over time
python scripts/track_progress.py --note "Fixed batch X"
python scripts/track_progress.py --report
```

---

## What to Expect

### Current State
- **Passing:** 58/157 (36.9%)
- **Failing:** 99/157

### After Phase 1 (SyntaxError - ~1-2 hours)
- **Passing:** ~73/157 (46.5%)
- **Improvement:** +15 problems

### After Phase 2 (NameError - ~2-4 hours)
- **Passing:** ~108/157 (68.8%)
- **Improvement:** +35 problems

### After Phases 3-5 (~6-10 hours)
- **Passing:** 150+/157 (95%+)
- **Improvement:** +40+ problems

**Total time:** ~10-20 hours over 3-5 days

---

## Quick Reference: Error Type → Fix

### SyntaxError (20-25 problems)
- **Cause:** Malformed code, string escaping, operator differences
- **Fix:** Edit .pg file to correct syntax (usually quick fixes)
- **Time per fix:** 2-5 minutes

### NameError (35-45 problems)
- **Cause:** Missing macro load, undefined variable
- **Fix:** Add macro to `loadMacros()` or define variable
- **Time per fix:** 3-10 minutes (often batch-fixable)

### AttributeError (10-15 problems)
- **Cause:** Missing method or wrong object type
- **Fix:** Understand object model, fix method call
- **Time per fix:** 10-20 minutes

### TypeError (10-15 problems)
- **Cause:** Type mismatch, wrong argument
- **Fix:** Convert types or refactor logic
- **Time per fix:** 15-30 minutes

### Other (10-15 problems)
- **Cause:** Various complex issues
- **Fix:** Investigate and adapt
- **Time per fix:** 30+ minutes

---

## Implementation Strategy

### Batch Processing (Recommended)

Instead of fixing problems one-by-one:

1. **Group similar problems** (same error type)
2. **Find the pattern** (why they're all failing the same way)
3. **Create batch fix** (apply to all similar problems)
4. **Test the batch** (verify all fixed)
5. **Track progress**

**Example:**
```
Found: 8 problems with NameError - Formula not defined
Pattern: All missing "PGbasicmacros.pl" macro
Batch Fix: Add macro to all 8 loadMacros() calls
Test: All 8 pass with quick_test.py
Time: 30 minutes instead of 2-3 hours!
```

### Daily Progress Goal

**Day 1:**
- Discovery (1 hour): Run diagnostics, understand errors
- Phase 1 (2-3 hours): Fix SyntaxErrors → ~15 problems fixed
- Check: Should be at 46-50% pass rate

**Day 2:**
- Phase 2 (4-5 hours): Fix NameErrors → ~35 problems fixed
- Check: Should be at 65-70% pass rate

**Day 3+:**
- Phases 3-5 (5-10 hours): Fix remaining issues → ~40 problems fixed
- Final: Should reach 95%+ pass rate

---

## Git Workflow

```powershell
# Create feature branch
git checkout -b fix/sample-problems-batch1

# Make fixes (edit .pg files)
# Test: python scripts/quick_test.py ...

# Commit after each logical batch
git commit -m "fix(sample-problems): Add PGbasicmacros.pl to 5 Algebra problems

- SimpleFactoring.pg: NameError Formula not defined
- ExpandedPolynomial.pg: NameError Formula not defined
- Problem3.pg: NameError Formula not defined
- Problem4.pg: NameError Formula not defined
- Problem5.pg: NameError Formula not defined

Fixes: 5 problems passing
Pass rate: 36.9% → 39.5%"

# After batch is done
git commit -m "fix(sample-problems): Phase 1 complete - SyntaxErrors fixed

8 SyntaxError problems resolved
Pass rate: 36.9% → 46.5%"

# Push when ready
git push origin fix/sample-problems-batch1
```

---

## Success Metrics

Check your progress with:

```powershell
# See current vs baseline
python scripts/track_progress.py --report

# Or run full test suite
python -m pytest packages/pg_translator/tests/test_tutorial_sample_problems.py::test_tutorial_problems_batch_rendering -v -s

# Look for improvement in these metrics:
# [OK] Success: X (increasing)
# [FAIL] Errors: Y (decreasing)
```

---

## Common Patterns to Watch For

As you fix problems, document patterns:

**Pattern 1: Missing PGbasicmacros.pl**
- Affects: ~12 problems
- Symptoms: `NameError: name 'Formula' is not defined`
- Fix: Add "PGbasicmacros.pl" to loadMacros()

**Pattern 2: LaTeX String Escaping**
- Affects: ~15 problems
- Symptoms: `SyntaxError: Invalid escape sequence`
- Fix: Use raw strings or macro that handles escaping

**Pattern 3: Missing Random Module**
- Affects: ~8 problems
- Symptoms: `NameError: name 'random' is not defined`
- Fix: Add "PGrandom.pl" to loadMacros()

When you find a pattern, **apply it to all affected problems**—huge time saver!

---

## Troubleshooting

### Problem: Diagnostic script is slow
```powershell
# Use --limit to test subset first
python scripts/batch_diagnose_all.py --limit 20
```

### Problem: Error message is confusing
```powershell
# Get full error message
python scripts/diagnose_problem.py "path/to/problem.pg" --show-full
```

### Problem: After fixing one error, new error appears
```powershell
# This is normal! Problems often have multiple issues
# Run diagnose_problem.py again to see the new error
# Fix it and repeat until all errors are gone
```

### Problem: Not sure what macro provides a function
```
Options:
1. Look in macros/ directory for similar names
2. Search GitHub for the function name
3. Look at a working problem that uses it
4. Check macro documentation in doc/ folder
```

---

## Next Action

**Right now:**

```powershell
cd d:\pg
python implement_fixes.py --start
```

This will show you the welcome screen with all next steps.

Then:

```powershell
python implement_fixes.py --strategy
python scripts/batch_diagnose_all.py
```

And you're off to the races! 🚀

---

## Need Help?

- **Want to understand the strategy?** Read `COMPLETE_GUIDE_FIX_SAMPLE_PROBLEMS.md`
- **Want practical commands?** Read `README_FIXES_WORKFLOW.md`
- **Want to document fixes?** See `FIX_DOCUMENTATION_TEMPLATE.md`
- **Want a detailed plan?** Read `PLAN_FIX_SAMPLE_PROBLEMS.md`
- **Want step-by-step guidance?** Run `python implement_fixes.py --checklist`

---

**Last updated:** 2025-11-09
**Status:** Ready to implement
**Estimated time to 95%+ success:** 10-20 hours over 3-5 days
