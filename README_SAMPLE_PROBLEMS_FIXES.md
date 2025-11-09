# Sample Problems Systematic Fix Initiative

## Executive Summary

A comprehensive plan has been created to systematically fix **44 failing sample problems** (out of 160 total). The problems have been analyzed, categorized, and prioritized for fixing.

**Current Status**: 116/160 passing (72.5%)
**Target**: 160/160 passing (100%)
**Estimated Effort**: 2-3 hours

## What Was Done

### 1. ✅ Analysis Complete
- Ran comprehensive test suite
- Identified all 44 failing problems
- Categorized by error type
- Identified root causes
- Created detailed documentation

### 2. ✅ Plan Created
- 7 categories of failures identified
- Root causes documented
- Fix strategies outlined
- Implementation order recommended

### 3. ✅ Documentation Generated
Four comprehensive documents created:

| Document | Purpose | Content |
|----------|---------|---------|
| **QUICK_START_SAMPLE_FIXES.md** | Quick reference | How to get started, commands, quick guide |
| **FIX_SAMPLE_PROBLEMS_PLAN.md** | Detailed plan | Root causes, fix strategies, detailed analysis |
| **SAMPLE_PROBLEMS_FIX_STATUS.md** | Status tracking | Current metrics, categories, implementation phases |
| **ISSUES_BREAKDOWN.txt** | Visual summary | ASCII breakdown of all issues and effort estimates |

## The 7 Categories of Failures

### Category 1: SyntaxError - Lambda/Closure Issues (10 problems)
**Difficulty**: Medium | **Impact**: High | **Estimated Time**: 30 min

Perl closures in dict values not translating to Python correctly.

```
GraphToolCustomChecker.pg, ParametricPlot.pg, ParametricPlotAlt.pg,
GraphShading.pg, GraphShadingPlot.pg, QuadrilateralGraphTool.pg,
TriangleGraphTool.pg, + 3 more
```

### Category 2: AttributeError - Missing Methods (8 problems)
**Difficulty**: Medium | **Impact**: Medium | **Estimated Time**: 30 min

`.cmp()` method called on String/Vector/Matrix objects.

```
StringOrOtherType.pg, VectorOperations.pg, Vectors.pg,
MatrixAnswer1.pg, RowOperations.pg, + 3 more
```

### Category 3: Complex Syntax Issues (8 problems)
**Difficulty**: Medium-High | **Impact**: Medium | **Estimated Time**: 45 min

Complex nested list/hash structures with method chaining.

```
TableOfValues.pg, RiemannSums.pg, RiemannSumPlot.pg,
Matching.pg, MatchingAlt.pg, MatchingGraphs.pg,
ManyMultipleChoice.pg, MultipleChoice*.pg variants
```

### Category 4: Macros/Statistics Issues (8 problems)
**Difficulty**: Medium-High | **Impact**: Medium | **Estimated Time**: 45 min

Specialized macros not fully implemented in Python translator.

```
BarGraph.pg, LinearRegression.pg, MeanStdDev.pg, ScatterPlot.pg,
ChemicalReaction.pg, DraggableSubsets.pg, DynamicGraphPolygon.pg, + 1 more
```

### Category 5: UI/Layout Issues (8 problems)
**Difficulty**: Medium | **Impact**: Medium | **Estimated Time**: 45 min

HTML/Layout generation, image handling not translating.

```
Images.pg, LayoutTable.pg, GraphsInTables.pg,
Scaffolding.pg, SimplePopUp.pg, + 3 more
```

### Category 6: Data/Answer Checking (10 problems)
**Difficulty**: High | **Impact**: Medium | **Estimated Time**: 60 min

Custom answer checking, data structures, evaluation functions.

```
CustomAnswerCheckers.pg, CustomAnswerListChecker.pg,
CalculatingWithPoints.pg, ExtractingCoordinatesFromPoint.pg,
DataTables.pg, AnswerOrderedList.pg, SeriesTest.pg, + 3 more
```

### Category 7: Edge Cases (3 problems)
**Difficulty**: Varies | **Impact**: Low | **Estimated Time**: 30 min

Problem-specific issues.

```
ProvingTrigIdentities.pg, SpecialTrigValues.pg,
PrimesInFormulas.pg, RandomFunction.pg
```

## Recommended Approach

### Strategy: Translator-First (Recommended)
1. **Fix translator for Categories 1-3** (26 problems in ~1 hour)
   - Single lambda/closure fix → 10 problems
   - Single .cmp() method fix → 8 problems
   - Single complex syntax pattern fix → 8 problems

2. **Fix remaining problems individually** (18 problems in ~1.5 hours)
   - Categories 4-7 require individual attention

3. **Total time**: 2-2.5 hours for 100% pass rate

### Strategy: Problem-by-Problem (Alternative)
1. Fix each problem individually
2. Takes longer but simpler to understand
3. May discover translator patterns along the way
4. Total time: 3-4 hours

## Getting Started

### Step 1: Read the Documentation
```bash
# Quick overview (5 minutes)
cat QUICK_START_SAMPLE_FIXES.md

# Detailed analysis (15 minutes)
cat FIX_SAMPLE_PROBLEMS_PLAN.md

# Current status (5 minutes)
cat ISSUES_BREAKDOWN.txt
```

### Step 2: Pick Your Approach
- **I want quick reference**: Use `QUICK_START_SAMPLE_FIXES.md`
- **I want detailed analysis**: Use `FIX_SAMPLE_PROBLEMS_PLAN.md`
- **I want visual overview**: Use `ISSUES_BREAKDOWN.txt`

### Step 3: Start Fixing
```bash
# Test a single problem to understand the error
"C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest \
  "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py::test_tutorial_problem_renders[GraphToolCustomChecker]" \
  -v --tb=short

# After fixing, run again to verify
# Then pick next problem...
```

### Step 4: Track Progress
- Update `SAMPLE_PROBLEMS_FIX_STATUS.md` success criteria as you fix problems
- Update todo list in this session
- Watch pass rate increase from 116/160 to 160/160

## Key Files

### Documentation Files (Read These)
- `QUICK_START_SAMPLE_FIXES.md` - Quick reference guide
- `FIX_SAMPLE_PROBLEMS_PLAN.md` - Detailed analysis and root causes
- `SAMPLE_PROBLEMS_FIX_STATUS.md` - Status tracking and phases
- `ISSUES_BREAKDOWN.txt` - Visual ASCII breakdown
- `README_SAMPLE_PROBLEMS_FIXES.md` - This file

### Problem Files (Fix These)
- `tutorial/sample-problems/**/*.pg` - The actual problem files to fix

### Test File
- `packages/pg_translator/tests/test_tutorial_sample_problems.py` - The test suite

### Code Files (May Need to Modify)
- `packages/pg_translator/pg_translator/pg_preprocessor.py` - Main translator
- `packages/pg_translator/pg_translator/in_process_sandbox.py` - Execution environment
- `packages/pg_macros/**/*.py` - Macro implementations
- `packages/pg_math/**/*.py` - Math object implementations

## Quick Commands Reference

### Test All Problems
```bash
"C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest \
  "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py" \
  -v --tb=short
```

### Test One Problem
```bash
"C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest \
  "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py::test_tutorial_problem_renders[GraphToolCustomChecker]" \
  -v --tb=short
```

### Count Failures
```bash
"C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest \
  "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py" \
  -v --tb=line 2>&1 | grep FAILED | wc -l
```

### Get Failure List
```bash
"C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest \
  "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py" \
  -v --tb=line 2>&1 | grep FAILED
```

### Detailed Error for One Test
```bash
"C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest \
  "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py::test_tutorial_problem_renders[GraphToolCustomChecker]" \
  -v --tb=long
```

## Understanding the Errors

### Example 1: GraphToolCustomChecker.pg
**Error**: `SyntaxError: closing parenthesis ')' does not match opening parenthesis '{'`

**What it means**: The translator converted a Perl closure (anonymous subroutine) to a Python lambda, but the syntax is incorrect.

**Perl code**:
```perl
cmpOptions => {
    list_checker => sub { my ($correct, $student) = @_; ... }
}
```

**Generated Python (wrong)**:
```python
cmpOptions = {
    'list_checker': lambda *args, **kwargs: None )  # <- Brace mismatch!
}
```

**Fix options**:
1. Fix the translator to generate a proper function
2. Rewrite the .pg file to avoid closures in dicts
3. Create a proper function stub

### Example 2: StringOrOtherType.pg
**Error**: `AttributeError: 'String' object has no attribute 'cmp'`

**What it means**: The code calls `.cmp()` on a String object, but Python String class doesn't have this method.

**Perl code**:
```perl
$ans = String("hello");
$ans->cmp();  # Perl MathObject method
```

**Generated Python (wrong)**:
```python
ans = String("hello")
ans.cmp()  # <- Method doesn't exist!
```

**Fix options**:
1. Add `.cmp()` method to String class
2. Use a different comparison method
3. Implement comparison logic differently

## Success Metrics

Track progress using these metrics:

| Phase | Target | Status |
|-------|--------|--------|
| **Phase 1: Analysis** | 7 categories identified | ✅ Done |
| **Phase 2: Plan Creation** | Strategies documented | ✅ Done |
| **Phase 3A: Translator Fixes** | 26 problems fixed | ⬜ Ready |
| **Phase 3B: Individual Fixes** | 18 problems fixed | ⬜ Ready |
| **Phase 4: Verification** | 160/160 passing | ⬜ Not started |

## Timeline

### Ideal Schedule
- **Now**: Read documentation (30 min)
- **Hour 1**: Fix translator issues (Categories 1-3, 26 problems)
- **Hour 2**: Fix remaining problems (Categories 4-7, 18 problems)
- **Hour 2.5**: Verification and testing
- **Total**: 2.5 hours to 100% pass rate

## When You Get Stuck

1. **Error is confusing?** → Read the problem file and understand what it's trying to do
2. **Not sure if it's translator or problem?** → Look for similar passing problems
3. **Can't figure out the fix?** → Check the detailed plan in `FIX_SAMPLE_PROBLEMS_PLAN.md`
4. **Need to modify translator?** → Check these files:
   - `packages/pg_translator/pg_translator/pg_preprocessor.py`
   - `packages/pg_translator/pg_translator/in_process_sandbox.py`
5. **Need macro implementation?** → Check:
   - `packages/pg_macros/pg_macros/`
   - `packages/pg_math/pg_math/`

## Next Steps

1. ✅ **Documentation created** - You're reading it now!
2. ⏭️ **Read detailed plan** - Open `FIX_SAMPLE_PROBLEMS_PLAN.md`
3. ⏭️ **Follow quick start** - Open `QUICK_START_SAMPLE_FIXES.md`
4. ⏭️ **Pick first problem** - Start with GraphToolCustomChecker.pg
5. ⏭️ **Implement fix** - Either translator or problem file
6. ⏭️ **Test and verify** - Confirm the test passes
7. ⏭️ **Repeat** - Move to next problem

---

## Document Index

```
d:\pg\
  ├── README_SAMPLE_PROBLEMS_FIXES.md     (This file - START HERE)
  ├── QUICK_START_SAMPLE_FIXES.md         (Quick reference)
  ├── FIX_SAMPLE_PROBLEMS_PLAN.md         (Detailed plan)
  ├── SAMPLE_PROBLEMS_FIX_STATUS.md       (Status tracking)
  ├── ISSUES_BREAKDOWN.txt                (Visual breakdown)
  │
  ├── tutorial/sample-problems/           (Problem files to fix)
  │   └── **/*.pg
  │
  └── packages/pg_translator/
      └── tests/
          └── test_tutorial_sample_problems.py  (Test file)
```

---

**Created**: 2025-11-10
**Status**: Ready for Implementation
**Next Action**: Read `QUICK_START_SAMPLE_FIXES.md` or `FIX_SAMPLE_PROBLEMS_PLAN.md`

