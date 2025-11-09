# Sample Problems Fix Status

## Current Status
- **Total Problems**: 160
- **Passing**: 116
- **Failing**: 44
- **Pass Rate**: 72.5%

## Systematic Fix Plan Created

### Documents Created:
1. **FIX_SAMPLE_PROBLEMS_PLAN.md** - Detailed analysis with root causes for each category
2. **QUICK_START_SAMPLE_FIXES.md** - Quick reference guide for implementing fixes
3. **SAMPLE_PROBLEMS_FIX_STATUS.md** - This document

## Categories of Failures

### Category 1: SyntaxError - Lambda/Closure Issues
**Count**: ~10 problems
**Root Cause**: Perl closures (`sub { ... }`) in dict values not translating correctly to Python
**Example**: GraphToolCustomChecker.pg line 81
```perl
cmpOptions => { list_checker => sub { ... } }
```
**Generated Issue**: Lambda stub in dict context causes brace mismatch
**Fix Strategy**:
- Option A: Fix translator to generate proper functions
- Option B: Rewrite Perl to avoid closures in dicts
- Option C: Use proper function stubs instead of lambda

### Category 2: AttributeError - Missing Methods
**Count**: ~8 problems
**Root Cause**: `.cmp()` method called on String/Vector/Matrix objects
**Example**: StringOrOtherType.pg - `'String' object has no attribute 'cmp'`
```perl
$ans->cmp()  # Works in Perl, doesn't in Python
```
**Fix Strategy**:
- Check Python MathObject implementation for equivalent
- Add `.cmp()` method or find replacement
- May need to update String, Vector, Matrix classes

### Category 3: Complex Syntax Issues
**Count**: ~8 problems
**Examples**:
- TableOfValues.pg - invalid syntax
- RiemannSums.pg, RiemannSumPlot.pg
- Matching.pg variants
- MultipleChoice.pg variants
**Root Cause**: Complex nested list/hash structures with method chaining
**Fix Strategy**: Problem-by-problem analysis and fixes

### Category 4: Statistics/Special Macros
**Count**: ~8 problems
**Examples**:
- BarGraph.pg
- LinearRegression.pg
- MeanStdDev.pg
- ScatterPlot.pg
- ChemicalReaction.pg
- DraggableSubsets.pg
- DynamicGraphPolygon.pg
**Root Cause**: Macros not fully implemented in Python or translator issues
**Fix Strategy**: Check macro implementations, add stubs if needed

### Category 5: UI/Layout Issues
**Count**: ~8 problems
**Examples**:
- Images.pg
- LayoutTable.pg
- GraphsInTables.pg
- Scaffolding.pg
- SimplePopUp.pg
**Root Cause**: HTML generation or special layout code not translating
**Fix Strategy**: Analyze each macro used, implement or stub as needed

### Category 6: Data/Answer Checking Issues
**Count**: ~10 problems
**Examples**:
- CustomAnswerCheckers.pg
- CustomAnswerListChecker.pg
- CalculatingWithPoints.pg
- ExtractingCoordinatesFromPoint.pg
- DataTables.pg
- AnswerOrderedList.pg
- SeriesTest.pg
**Root Cause**: Custom answer checking code or data structures
**Fix Strategy**: Implement custom checking functions or update syntax

### Category 7: Edge Cases
**Count**: ~3 problems
**Examples**:
- ProvingTrigIdentities.pg
- SpecialTrigValues.pg
- PrimesInFormulas.pg
- RandomFunction.pg
**Root Cause**: Specific to problem, need individual analysis
**Fix Strategy**: Analyze and fix each

## Implementation Priority

### Phase 1 (Current): Analysis & Documentation ✓
- [x] Identify all 44 failing problems
- [x] Categorize by error type
- [x] Document root causes
- [x] Create fix strategy

### Phase 2 (Next): High-Impact Fixes
Focus on issues affecting multiple problems:
1. **Lambda/Closure translator fix** - Fixes ~10 problems
2. **MathObject .cmp() method** - Fixes ~8 problems
3. **Complex syntax patterns** - Fixes ~8 problems

### Phase 3: Problem-by-Problem Fixes
Systematically fix remaining issues in Groups D-G

### Phase 4: Verification
Run full test suite and verify 100% pass rate

## How to Get Started

### Option 1: Follow the Plan
```
1. Read: FIX_SAMPLE_PROBLEMS_PLAN.md
2. Follow: QUICK_START_SAMPLE_FIXES.md
3. Pick a problem and start fixing
```

### Option 2: Quick Verification of Issues
```bash
# Run all tests to see current state
"C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest \
  "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py" \
  -v --tb=short 2>&1 | grep -E "FAILED|PASSED" | tail -50
```

### Option 3: Deep Dive Into One Problem
```bash
# Test one problem
"C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest \
  "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py::test_tutorial_problem_renders[GraphToolCustomChecker]" \
  -v --tb=long
```

## Key Insights

### Translator-Level vs. Problem-Level Fixes
- **Translator fixes** (high impact): Fix translator to handle closures, .cmp(), etc.
- **Problem fixes** (individual): Rewrite specific .pg files to work with current translator

### Best Approach
1. Identify patterns that affect multiple problems (translator-level)
2. Fix translator once
3. Quickly fix remaining individual problems
4. Total effort: Estimated 2-3 hours with systematic approach

## Resources

### Files to Modify
- Sample problems: `tutorial/sample-problems/**/*.pg`
- Translator: `packages/pg_translator/pg_translator/*.py`
- Macros: `packages/pg_macros/pg_macros/*.py`
- Math objects: `packages/pg_math/pg_math/*.py`

### Testing
```bash
# Run all sample problem tests
pytest d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py -v

# Run one test repeatedly while fixing
pytest d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py::test_tutorial_problem_renders[GraphToolCustomChecker] -v --tb=short
```

### Tools
- Python 3.12 with pytorch-5090 conda env
- pytest for testing
- PGTranslator class for converting .pg to Python

## Next Action Items

1. **Read the detailed plan**: `FIX_SAMPLE_PROBLEMS_PLAN.md`
2. **Follow the quick start**: `QUICK_START_SAMPLE_FIXES.md`
3. **Pick first problem**: GraphToolCustomChecker.pg (easiest, most impactful)
4. **Run test** and examine error
5. **Determine fix**: Translator or problem
6. **Implement** and verify
7. **Repeat** for next problem

## Success Criteria

- [x] Plan created and documented
- [ ] Group A (Grammar/Syntax) - 0/10 fixed
- [ ] Group B (AttributeError) - 0/8 fixed
- [ ] Group C (Complex Syntax) - 0/8 fixed
- [ ] Group D (Macros) - 0/8 fixed
- [ ] Group E (UI/Layout) - 0/8 fixed
- [ ] Group F (Data/Answer) - 0/10 fixed
- [ ] Group G (Edge Cases) - 0/3 fixed
- [ ] **FINAL**: 160/160 tests passing

---

**Created**: 2025-11-10
**Status**: Ready for implementation
**Next Step**: Pick a problem and start fixing!

