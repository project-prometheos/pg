# Quick Start Guide: Fixing Sample Problems

## TL;DR - What to Do Now

You have 44 failing problems across 7 groups. Here's the systematic approach:

### Step 1: Understand the Issues
Read: `FIX_SAMPLE_PROBLEMS_PLAN.md`

Key categories:
1. **SyntaxError** (10 problems) - Lambda/closure syntax issues
2. **AttributeError** (8 problems) - Missing .cmp() method
3. **Complex Syntax** (8 problems) - List/hash structures
4. **Macros** (8 problems) - Stats and special macros
5. **UI/Layout** (8 problems) - Images, tables, etc.
6. **Data/Answer** (10 problems) - Custom checking, etc.
7. **Edge Cases** (3 problems) - Misc issues

### Step 2: Pick One Problem to Fix

Start with the easiest to understand:

```bash
# Test just one problem
"C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest \
  "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py::test_tutorial_problem_renders[GraphToolCustomChecker]" \
  -v --tb=short
```

### Step 3: Analyze the Failing Problem

1. Read the .pg file:
   ```
   D:\pg\tutorial\sample-problems\Algebra\GraphToolCustomChecker.pg
   ```

2. Look for the error message - find what line is causing the issue

3. Understand: Is it a translator issue or a problem-code issue?

### Step 4: Fix It

**Option A: Fix the .pg file** (Recommended for most cases)
- Modify the Perl code to work better with Python conversion
- Test it

**Option B: Fix the translator** (For systemic issues)
- Fix the preprocessor or in_process_sandbox
- Test it across multiple problems

### Step 5: Verify

```bash
# Run the test again
"C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest \
  "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py::test_tutorial_problem_renders[ProblemName]" \
  -v --tb=short
```

If it passes, move to the next problem.

## The 44 Failing Problems

### Group A: Grammar/Syntax (10 problems)
```
GraphToolCustomChecker.pg
ParametricPlot.pg
ParametricPlotAlt.pg
GraphShading.pg
GraphShadingPlot.pg
QuadrilateralGraphTool.pg
TriangleGraphTool.pg
```

### Group B: AttributeError - .cmp() method (8 problems)
```
StringOrOtherType.pg
VectorOperations.pg
Vectors.pg
MatrixAnswer1.pg
RowOperations.pg
```

### Group C: Complex Syntax (8 problems)
```
TableOfValues.pg
RiemannSums.pg
RiemannSumPlot.pg
Matching.pg
MatchingAlt.pg
MatchingGraphs.pg
ManyMultipleChoice.pg
MultipleChoiceCheckbox.pg
MultipleChoiceRadio.pg
```

### Group D: Macros (8 problems)
```
ChemicalReaction.pg
BarGraph.pg
LinearRegression.pg
MeanStdDev.pg
ScatterPlot.pg
DraggableSubsets.pg
DynamicGraphPolygon.pg
```

### Group E: UI/Layout (8 problems)
```
Images.pg
LayoutTable.pg
GraphsInTables.pg
Scaffolding.pg
SimplePopUp.pg
```

### Group F: Data/Answer (10 problems)
```
CustomAnswerCheckers.pg
CustomAnswerListChecker.pg
CalculatingWithPoints.pg
ExtractingCoordinatesFromPoint.pg
DataTables.pg
AnswerOrderedList.pg
SeriesTest.pg
```

### Group G: Edge Cases (3 problems)
```
ProvingTrigIdentities.pg
SpecialTrigValues.pg
PrimesInFormulas.pg
RandomFunction.pg
```

## Workflow

1. **Pick a problem** from the list above
2. **Run the test** to see the error
3. **Read the .pg file** in tutorial/sample-problems/
4. **Understand the error** and root cause
5. **Fix it** (either .pg file or translator)
6. **Test it** again
7. **Move to next problem**
8. **Track progress** with the todo list

## Commands Cheat Sheet

```bash
# Run all tests
"C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest \
  "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py" \
  -v --tb=short

# Get failure count
"C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest \
  "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py" \
  -v --tb=line 2>&1 | grep FAILED | wc -l

# Run one test
"C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest \
  "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py::test_tutorial_problem_renders[PROBLEMNAME]" \
  -v --tb=short

# See detailed error for one test
"C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest \
  "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py::test_tutorial_problem_renders[PROBLEMNAME]" \
  -v --tb=long
```

## Key Files

- **Plan**: `d:\pg\FIX_SAMPLE_PROBLEMS_PLAN.md`
- **This guide**: `d:\pg\QUICK_START_SAMPLE_FIXES.md`
- **Test file**: `d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py`
- **Sample problems**: `d:\pg\tutorial\sample-problems\`

## When Stuck

1. Check if the error is in the generated Python code or the Perl translation
2. Look at similar problems that pass to see what works
3. Check the translator code:
   - `packages/pg_translator/pg_translator/pg_preprocessor.py`
   - `packages/pg_translator/pg_translator/in_process_sandbox.py`
4. Consider if you need to fix the .pg file or the translator

---

**Status**: Ready to start fixing! Pick any problem and begin.

