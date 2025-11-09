# Plan to Systematically Fix Sample Problems

## Overview
44 out of 160 sample problems are failing. The failures fall into several categories that need systematic fixes.

## Failing Problems Summary

**Total Failures: 44**

### By Category:

#### 1. **SyntaxError - Lambda/Closure Issues (10+ problems)**
Problems where Perl closures (`sub { ... }`) are being converted incorrectly to Python lambdas:
- GraphToolCustomChecker.pg - Line 81: lambda with dict has mismatched braces
- ParametricPlot.pg
- ParametricPlotAlt.pg
- GraphShading.pg
- GraphShadingPlot.pg
- And similar GraphTool related problems

**Root Cause**: The translator converts Perl `sub { ... }` to `lambda *args, **kwargs: None`, but the dict still has `{` which confuses the parser when there's a nested structure like:
```python
lambda *args, **kwargs: None )  # in a dict context
```

**Solution**: These need to be converted to proper Python functions, not lambdas. Or the dict syntax needs fixing.

#### 2. **AttributeError - Missing Methods (8+ problems)**
- StringOrOtherType.pg: `'String' object has no attribute 'cmp'`
- VectorOperations.pg
- Vectors.pg
- MatrixAnswer1.pg
- RowOperations.pg

**Root Cause**: Perl MathObjects have `.cmp()` method for comparisons, which doesn't exist in Python equivalents.

**Solution**: Check if the method is being called on a MathObject and provide proper Python equivalent.

#### 3. **Complex Syntax Issues (8+ problems)**
- TableOfValues.pg
- RiemannSums.pg
- RiemannSumPlot.pg
- Matching.pg, MatchingAlt.pg, MatchingGraphs.pg
- ManyMultipleChoice.pg
- MultipleChoiceCheckbox.pg, MultipleChoiceRadio.pg

**Root Cause**: Complex list/hash structures with method chaining or special syntax

**Solution**: Manual inspection and fix for each

#### 4. **Special Macro Issues (8+ problems)**
- ChemicalReaction.pg
- BarGraph.pg, LinearRegression.pg, MeanStdDev.pg, ScatterPlot.pg (stats-related)
- DraggableSubsets.pg
- DynamicGraphPolygon.pg
- DraggableSubsets.pg

**Root Cause**: Specialized macros not fully supported in Python translator

**Solution**: Check macro implementations in pg_macros package

#### 5. **Other Issues (10+ problems)**
- Images.pg, LayoutTable.pg, GraphsInTables.pg
- CustomAnswerCheckers.pg, CustomAnswerListChecker.pg
- ExtractingCoordinatesFromPoint.pg
- CalculatingWithPoints.pg
- DataTables.pg
- Scaffolding.pg
- SimplePopUp.pg
- QuadrilateralGraphTool.pg, TriangleGraphTool.pg
- AnswerOrderedList.pg, SeriesTest.pg
- ProvingTrigIdentities.pg, SpecialTrigValues.pg
- PrimesInFormulas.pg
- RandomFunction.pg

## Fix Strategy

### Phase 1: Analyze & Document (CURRENT)
- [x] Run test suite and identify all 44 failing problems
- [x] Categorize by error type
- [x] Document root causes

### Phase 2: Fix Translator Issues (HIGH PRIORITY)
Target: In-process sandbox and PGPreprocessor to better handle:
1. Lambda conversions in dict values
2. Method calls on MathObject strings
3. Complex nested structures

### Phase 3: Problem-by-Problem Fixes
Tackle in order of impact:

**Group A: Grammar/Syntax Fixes** (fix in .pg files)
1. GraphToolCustomChecker.pg - fix lambda in dict
2. ParametricPlot.pg, ParametricPlotAlt.pg
3. GraphShading.pg, GraphShadingPlot.pg
4. QuadrilateralGraphTool.pg, TriangleGraphTool.pg

**Group B: Method Call Fixes** (fix .cmp() calls)
1. StringOrOtherType.pg
2. VectorOperations.pg, Vectors.pg
3. MatrixAnswer1.pg, RowOperations.pg

**Group C: Complex Structure Fixes**
1. TableOfValues.pg
2. RiemannSums.pg, RiemannSumPlot.pg
3. Matching.pg and variants
4. MultipleChoice variants

**Group D: Statistics/Specialized Macro Fixes**
1. BarGraph.pg, LinearRegression.pg
2. MeanStdDev.pg, ScatterPlot.pg
3. ChemicalReaction.pg

**Group E: UI/Layout Fixes**
1. Images.pg, LayoutTable.pg
2. GraphsInTables.pg
3. Scaffolding.pg, SimplePopUp.pg
4. DraggableSubsets.pg, DynamicGraphPolygon.pg

**Group F: Data/Answer Checking Fixes**
1. CustomAnswerCheckers.pg, CustomAnswerListChecker.pg
2. CalculatingWithPoints.pg, ExtractingCoordinatesFromPoint.pg
3. DataTables.pg
4. AnswerOrderedList.pg, SeriesTest.pg

**Group G: Edge Cases**
1. ProvingTrigIdentities.pg, SpecialTrigValues.pg
2. PrimesInFormulas.pg
3. RandomFunction.pg

### Phase 4: Verification
- Run full test suite
- Target: 100% pass rate (160/160)

## Implementation Steps

### Step 1: Convert .pg to .pypg for easier analysis
```bash
python -m pg_translator.convert_pg_to_pypg tutorial/sample-problems/Algebra/GraphToolCustomChecker.pg
```

This shows what the converted Python looks like, making it easier to identify what needs fixing.

### Step 2: Fix the actual .pg file
Modify the Perl code to work better with Python conversion OR update the preprocessor to handle it better.

### Step 3: Test the fix
```bash
"C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py::test_tutorial_problem_renders[ProblemName]" -v --tb=short
```

### Step 4: Document the fix
Record what was changed and why.

## Commands Reference

Run all tests:
```bash
"C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py" -v --tb=short
```

Run specific test:
```bash
"C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py::test_tutorial_problem_renders[GraphToolCustomChecker]" -v --tb=short
```

Get only failures:
```bash
"C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py" -v --tb=line 2>&1 | grep FAILED
```

## Next Steps

1. Start with GraphToolCustomChecker.pg (SyntaxError - easiest to understand)
2. Move through Groups A-G systematically
3. After each fix, run the test to verify
4. Update this plan as you discover additional issues

---

## Detailed Error Analysis

### Error 1: GraphToolCustomChecker.pg
**Error**: SyntaxError: closing parenthesis ')' does not match opening parenthesis '{'
**Line**: 69 (in generated Python)
**Cause**: Lambda closure in method_dict context
**Perl Code**:
```perl
$gt = GraphTool("...")->with(
    cmpOptions => {
        list_checker => sub { ... }  # <- This is the issue
    }
);
```
**Generated Python Error**:
```python
lambda *args, **kwargs: None )  # <- Brace mismatch
```
**Fix Options**:
- Option A: Fix the translator to generate proper functions
- Option B: Rewrite the .pg file to avoid the closure in dict
- Option C: Add a stub function instead of lambda

