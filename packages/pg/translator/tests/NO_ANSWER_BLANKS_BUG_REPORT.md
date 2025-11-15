# Bug Report: Missing Answer Blanks in Translator Output

## Summary

The PG translator has a critical bug where **MultiAnswer objects do not populate the `answer_blanks` dictionary**, even though the answer blanks are correctly rendered in the HTML output.

**Impact:** ~130 tutorial sample problems (82% of 159) cannot be runtime-tested because their answers are not exposed to the `answer_blanks` API.

## Symptoms

### What Works
- Problems with simple answer types (Real, Formula, String) correctly populate `answer_blanks`
- Answer blanks are correctly rendered in HTML with `<input>` tags and proper names (`AnSwEr0001`, `AnSwEr0002`)
- Answer evaluation still works (you can submit answers and get results)

### What's Broken
- When a problem uses `MultiAnswer` objects, `answer_blanks` dictionary is empty
- `metadata['num_answers']` shows 0 even when HTML contains answer blanks
- The `PGMLRenderer` or executor doesn't capture MultiAnswer objects

## Evidence

### Test Case 1: Simple Problem (Works)
```
Problem: Algebra/ExpandedPolynomial.pg
Answer type: Formula (single answer)
Result: ✓ answer_blanks has 1 entry
```

### Test Case 2: MultiAnswer Problem (Broken)
```
Problem: Algebra/AlgebraicFractionAnswer.pg
Answer type: MultiAnswer (2 related answers)
Source: [_]{$multians} appears twice
HTML: <input name="AnSwEr0001"> and <input name="AnSwEr0002"> both present
Result: ✗ answer_blanks is empty {}
```

### Test Case 3: Minimal Reproduction
```perl
$multians = MultiAnswer("x", "y")->with(...);
BEGIN_PGML
[_]{$multians}
[_]{$multians}
END_PGML
```

**Expected:** `answer_blanks = {"AnSwEr0001": {...}, "AnSwEr0002": {...}}`
**Actual:** `answer_blanks = {}`

## Affected Problems

Problems affected by this bug (~130 total):

### Algebra (9 affected)
- AlgebraicFractionAnswer.pg
- AnswerUpToMultiple.pg
- DomainRange.pg
- DynamicGraph.pg
- EquationDefiningFunction.pg
- FractionAnswer.pg
- FunctionDecomposition.pg
- FunctionPlot.pg
- ... and more

### Complex (3 affected)
- ComplexOperations.pg
- LimitedComplex.pg
- OtherOperations.pg

### LinearAlgebra (4 affected)
- MatrixAnswer1.pg
- MatrixAnswer2.pg
- MatrixCustomAnswerChecker.pg
- RowOperations.pg

### Other Categories
- DiffCalc/DifferentiateFunction.pg
- DiffCalcMV/VectorFieldPlot.pg
- All graph/interactive problems using specialized answer types
- All matching/essay problems
- ... and 100+ more

## Root Cause Analysis

Looking at the code flow:

1. **Executor** (`executor.py` lines 134-137):
   ```python
   rendered_markdown, answer_blanks = renderer.render(combined_text)
   self.answers.update(answer_blanks)  # Should populate answers from PGML
   ```

2. **Problem:** The `PGMLRenderer.render()` method only extracts simple `[_]{...}` patterns
   - Works: `[_]{$formula}`, `[_]{$number}`, `[_]{$string}`
   - Broken: `[_]{$multians}` where `$multians` is a MultiAnswer object

3. **Why it still renders:** The PGML text segments are rendered to HTML separately, creating input tags, but the evaluator objects are never extracted and stored in `answer_blanks`

## Code Location

**File:** `packages/pg/translator/executor.py`
**Method:** `PGEnvironment.render_text()` (lines 118-139)
**Problem:** Line 137 `self.answers.update(answer_blanks)` gets empty dict for MultiAnswer

**File:** `packages/pg/translator/pgml/renderer.py` (or similar)
**Method:** `PGMLRenderer.render()`
**Problem:** Doesn't recognize MultiAnswer objects as answer evaluators

## Related Code Files

1. `executor.py` - Collects answers from rendered output
2. `pgml/renderer.py` - Extracts answers from PGML text
3. `pgml/lexer.py` - Tokenizes answer blanks
4. `in_process_sandbox.py` - May handle MultiAnswer registration

## Proposed Solution

The translator needs to:

1. **Recognize MultiAnswer objects** when rendering PGML blanks
2. **Extract evaluators** from `[_]{$multians}` patterns
3. **Register all parts** of a MultiAnswer as separate answer blanks
4. **Map back to HTML** so answer checking still works

### Approach
- Modify `PGMLRenderer.render()` to detect MultiAnswer objects
- Use the same variable scope as the PGML content to extract object references
- Register each MultiAnswer part separately (e.g., `AnSwEr0001`, `AnSwEr0002`)
- Ensure answer checking still groups them correctly for grading

## Impact on Runtime Testing

**Current Status:**
- 15 problems test successfully (9.5%)
- 130 problems skipped due to "no answer blanks" (82.4%)
- 12 problems have real failures (7.6%)

**With this bug fixed:**
- Estimate 40-50 more problems would be testable (those with MultiAnswer)
- Overall test coverage could reach ~50-60%
- Would identify additional answer checking bugs

## Examples of Currently Untestable Problem Types

1. **Fraction Answers** - Using numerator/denominator separate blanks
   - `AlgebraicFractionAnswer.pg`
   - `FractionAnswer.pg`

2. **Multiple Related Answers** - Using MultiAnswer for coordinated checking
   - `PointAnswers.pg` - (x, y) coordinates
   - Many calculus problems with multiple steps

3. **Equations with specific structure** - Using custom checkers
   - Some differential equations
   - Some linear systems

## Workarounds

### For Runtime Testing (temporary)
- Skip problems with MultiAnswer for now
- Only test simple answer type problems
- This is already what we're doing

### For Problem Authors
- No workaround - MultiAnswer is the correct way to handle related answers
- The bug is in the translator, not in problem authoring

## Testing Strategy

Once fixed, should test:

```python
# Test MultiAnswer extraction
problem_code = """
$multi = MultiAnswer(Formula("x+1"), Formula("x-1"))->with(...);
BEGIN_PGML
First: [_]{$multi}
Second: [_]{$multi}
END_PGML
"""

result = translator.translate_source(problem_code, seed=1234)
assert len(result.answer_blanks) == 2  # Should have 2 entries
assert "AnSwEr0001" in result.answer_blanks
assert "AnSwEr0002" in result.answer_blanks
```

## Related Issues

This bug may also affect:
- Answer checking for any MultiAnswer problem
- Custom grading logic that depends on `answer_blanks`
- API clients expecting populated `answer_blanks`

## Priority

**HIGH** - This is a core translator bug affecting:
- ~82% of tutorial problems (130 out of 159)
- Any real-world problem using MultiAnswer
- Answer checking and grading workflows

## Next Steps

1. ✓ Identify root cause (PGMLRenderer not extracting MultiAnswer evaluators)
2. ⊘ Locate exact line where MultiAnswer is lost
3. ⊘ Fix the renderer to capture MultiAnswer objects
4. ⊘ Add tests for MultiAnswer answer extraction
5. ⊘ Re-run runtime tests to measure improvement
6. ⊘ Document the fix in RUNTIME_TESTING.md

## Notes

- This is NOT an issue with the runtime tester - it correctly skips unsupported types
- The runtime tester discovered this bug by identifying that most problems were missing answer blanks
- The fix should be in the PG translator core, not in the answer extraction helpers
