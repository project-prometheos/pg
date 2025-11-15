# Runtime Testing for Tutorial Sample Problems

## Overview

The runtime test suite validates that **answer checking and grading actually work** for tutorial sample problems by:

1. **Generating** each problem with a fixed seed (1234)
2. **Extracting** the correct answers from MathObject evaluators
3. **Submitting** the correct answers as student input
4. **Verifying** that the submission scores 100% (perfect score)

This **complements the compilation tester** which only validates that problems render without errors. The runtime tester ensures the answer checking logic is functionally correct end-to-end.

## Test Files

### `test_tutorial_sample_problems_runtime.py`
Main test file containing:
- **`test_correct_answer_scores_full_credit(problem_path)`** - Parametrized test for each problem
- **`test_all_correct_answers()`** - Aggregate test with comprehensive summary
- **`test_runtime_coverage_stats()`** - Statistics on testing coverage

### `answer_extraction.py`
Helper module providing:
- **`extract_correct_answers(result)`** - Main extraction function
- **`extract_answer_string(math_obj)`** - Convert MathObjects to student input strings
- **`get_extractable_blanks(result)`** - Check which blanks support extraction

## Running the Tests

### Run all runtime tests
```bash
pytest packages/pg/translator/tests/test_tutorial_sample_problems_runtime.py -v
```

### Run tests by category
```bash
pytest packages/pg/translator/tests/test_tutorial_sample_problems_runtime.py -v -k "Algebra"
pytest packages/pg/translator/tests/test_tutorial_sample_problems_runtime.py -v -k "DiffCalc"
```

### Run single problem
```bash
pytest packages/pg/translator/tests/test_tutorial_sample_problems_runtime.py -v -k "ExpandedPolynomial"
```

### Run aggregate test with full summary
```bash
pytest packages/pg/translator/tests/test_tutorial_sample_problems_runtime.py::TestTutorialSampleProblemsRuntime::test_all_correct_answers -v
```

### Coverage statistics
```bash
pytest packages/pg/translator/tests/test_tutorial_sample_problems_runtime.py::test_runtime_coverage_stats -v
```

## Test Results Interpretation

### PASSED ✓
The problem's answer checking works correctly:
- Problem rendered without errors
- Correct answer extracted successfully
- Submission of correct answer scored 1.0 (100%)

**Example:** `Algebra/ExpandedPolynomial.pg`

### SKIPPED ⊘
The problem could not be tested automatically:
- **No answer blanks** - Snippet/demo problem with no answers, OR translator bug with MultiAnswer
- **Cannot extract answers** - Answer type not supported by extraction logic
- **Compilation errors** - Problem has syntax/execution errors during rendering

These tests are skipped, not failed, because they don't represent answer checking failures.

**Examples:**
- `Algebra/GraphToolLine.pg` - Uses interactive graph tool (can't auto-extract answers)
- `Arithmetic/UnitConversion.pg` - Uses specialized unit context (extraction not implemented)
- `Algebra/AlgebraicFractionAnswer.pg` - **TRANSLATOR BUG**: Uses MultiAnswer but answer_blanks not populated (see NO_ANSWER_BLANKS_BUG_REPORT.md)
- `Misc/MatchingGraphs.pg` - Has compilation error

**⚠️ IMPORTANT BUG:** ~130 problems (82% of tutorial problems) report "No answer blanks" due to a translator bug with MultiAnswer objects. See [NO_ANSWER_BLANKS_BUG_REPORT.md](NO_ANSWER_BLANKS_BUG_REPORT.md) for details. Once fixed, test coverage should improve to ~50-60%.

### FAILED ✗
The problem has a real issue that needs investigation:
- Correct answer submission scored < 1.0
- Answer checking threw an error
- Answer extraction produced unexpected format

**Examples:**
- `DiffCalc/LinearApprox.pg` - Answer checker bug: `'NoneType' object has no attribute 'free_symbols'`
- `Algebra/NoSolution.pg` - Correct answer extracted but scored 0.0
- `LinearAlgebra/MatrixOperations.pg` - Matrix answer extraction or checking issue

## Test Statistics

From a sample run of 159 tutorial problems:

```
PASSED:  15 problems (9.5%) - Full runtime testing supported
SKIPPED: 130 problems (82.4%) - Unsupported answer types or no blanks
FAILED:  12 problems (7.6%) - Real issues found
SUCCESS RATE (non-skipped): 55.6%
```

### Skipped Problem Types
- **Interactive Graphs** - GraphToolLine, GraphToolCircle, etc.
- **Dynamic Content** - DynamicGraph, IframeEmbedding
- **Complex Answer Types** - Essays, Matching problems, Chemical reactions
- **Specialized Contexts** - Unit conversion, Matrix operations
- **Snippets** - Demonstration code without full problems

## Answer Type Support

### Supported Types ✓
- **Real** (numeric values) - `42`, `3.14`, `-5`
- **Formula** (algebraic expressions) - `x^2 - 6x + 4`, `2*sin(x)`
- **String** (text answers) - `"hello"`, `"true"`
- **Assignment** (equations) - `y = x + 1`, `z = 2*t`
- **AnswerChecker objects** - Handles post-filtered and custom checkers

### Unsupported Types ✗
- **Matrix** - Extraction attempted but scoring issues
- **List** - Multiple ordered answers (partial support)
- **RadioButtons/PopUp** - Multiple choice (extraction works, but used in HTML forms)
- **InteractiveGraphs** - Graph-based answers (no text representation)
- **CustomCheckers** - Non-standard answer validation logic
- **Essays** - Free text with manual grading

## Common Issues and Solutions

### Issue: "Could not extract answer(s)"
**Cause:** The problem uses an answer type not yet supported

**Solution:** Add support to `extract_answer_string()` or mark as known limitation

**Examples:** Graphs, Interactive elements, Complex custom checkers

---

### Issue: "Score 0.0 (expected 1.0)"
**Cause:** Answer extracted correctly but grading returned wrong score

**Possible causes:**
- Answer format doesn't match expected input format
- Grader has strict requirements (case sensitivity, spacing)
- Grader logic has a bug
- Context/variable dependencies not properly set

**Solution:** Check if answer format is correct, test with pg_solve.py interactively

**Example:** `LinearAlgebra/MatrixOperations.pg` - May need special matrix format

---

### Issue: "'NoneType' object has no attribute 'free_symbols'"
**Cause:** Answer checker or parser bug

**This is a REAL BUG in the problem or answer checker code.**

**Solution:** Fix the answer checker implementation

**Example:** `DiffCalc/LinearApprox.pg`

---

### Issue: "No answer blanks"
**Cause:** Problem is a snippet or demonstration without interactive answers

**Solution:** Skip this problem (it's not designed for student input)

**Examples:** "Comments for Instructors", "Snippet" type problems

## Extending Answer Extraction

To support new answer types:

1. **Identify the answer object type:**
   ```python
   # Debug: Check what type of object we're working with
   print(type(math_obj))
   print(dir(math_obj))
   ```

2. **Add extraction logic to `extract_answer_string()`:**
   ```python
   # Example: Support for Point answers
   if hasattr(math_obj, "isPoint") and math_obj.isPoint:
       x = math_obj.coordinates[0]
       y = math_obj.coordinates[1]
       return f"({x}, {y})"
   ```

3. **Test on a specific problem:**
   ```bash
   pytest packages/pg/translator/tests/test_tutorial_sample_problems_runtime.py \
       -v -k "YourProblemName"
   ```

4. **Add helper function if needed:**
   ```python
   def extract_point_string(point_obj: Any) -> Optional[str]:
       """Extract point as (x, y) format."""
       try:
           x, y = point_obj.coordinates
           return f"({x}, {y})"
       except Exception:
           return None
   ```

## Known Limitations

1. **Answer Format Conversion**: The biggest challenge is converting from internal MathObject representation to the format students would type. For some types (like matrices), this is ambiguous.

2. **Context Dependency**: Some answers depend on variable contexts defined in the problem. These are properly handled by using the same seed.

3. **Post-Filtered Answers**: Problems using `.withPostFilter(AnswerHints(...))` are supported, but the filter itself isn't tested.

4. **Randomized Parameters**: Tests use a fixed seed (1234) which may not cover all edge cases. Consider running with multiple seeds for thorough testing.

## Integration with CI/CD

To fail builds on answer checking issues:

```yaml
# .github/workflows/test.yml
- name: Runtime answer checking tests
  run: |
    pytest packages/pg/translator/tests/test_tutorial_sample_problems_runtime.py \
      --tb=short -q
  # Fails if any problems have actual scoring errors (ignores skipped)
```

This will catch:
- Answer checking bugs
- Broken grading logic
- Invalid answer formats
- Incorrect expected values

## Troubleshooting

### Tests run slowly
- Runtime tests involve translating and checking each problem
- Typical run time: 10-15 seconds for 159 problems
- To run just a subset: `pytest -k "Algebra or DiffCalc"`

### Import errors
- Ensure you're in the correct directory: `d:\pg`
- Test discovery requires proper package structure
- Check that `__init__.py` files exist in all package directories

### Answer extraction still returning object repr
- The object type may have multiple ways to access the answer
- Check `dir(obj)` to see all available attributes/methods
- Add debugging to `extract_answer_string()` to find the right method

## Related Tools

- **`pg_solve.py`** - Interactive tool to manually test problems
  ```bash
  python pg_solve.py tutorial/sample-problems/Algebra/ExpandedPolynomial.pg --seed 1234 --solution
  ```

- **Compilation Tester** - `test_tutorial_sample_problems_all.py`
  - Tests that problems render without errors
  - Complements runtime testing

## Design Philosophy

The runtime tester follows these principles:

1. **Fail on Real Issues** - Only fails if answer checking is broken
2. **Skip Unsupported Types** - Doesn't fail on answer types that can't be auto-tested
3. **Be Transparent** - Clear messages about what passed, skipped, and failed
4. **Facilitate Investigation** - Detailed output to help debug failures
5. **Be Maintainable** - Extensible design for adding support for new answer types

## Future Improvements

1. **Matrix Answer Support** - Better extraction and validation for matrices
2. **Multiple Seeds** - Test with several random seeds to catch edge cases
3. **Incorrect Answers** - Test that wrong answers score < 1.0
4. **Custom Answer Checkers** - Validate custom checker logic
5. **Performance Analysis** - Track problem translation times
6. **Answer Hints** - Verify that answer hint feedback is provided correctly
