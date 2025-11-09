# Tutorial Sample Problems Test Results

## Test Suite: `test_tutorial_sample_problems.py`

Comprehensive pytest suite that validates all 157 tutorial sample problems can render without errors.

### Quick Start

```bash
# Run all parametrized tests (individual problem tests)
pytest packages/pg_translator/tests/test_tutorial_sample_problems.py -v

# Run just the batch summary test
pytest packages/pg_translator/tests/test_tutorial_sample_problems.py::test_tutorial_problems_batch_rendering -v -s

# Run specific problem tests
pytest packages/pg_translator/tests/test_tutorial_sample_problems.py -k "ExpandedPolynomial or FactoredPolynomial" -v
```

### Current Status (2025-01-09)

**Overall: 58/157 (36.9%) passing**

- ✓ Success: 58 problems
- ⚠ Warnings: 3 problems (non-fatal errors)
- ✗ Errors: 96 problems

### Error Breakdown

| Error Type | Count | Examples |
|------------|-------|----------|
| SyntaxError | 43 | Preprocessor generates invalid Python syntax |
| AttributeError | 34 | Missing stub methods (.cmp(), .reduce(), etc.) |
| NameError | 11 | Missing stub classes (List, String, etc.) |
| TypeError | 8 | Stub implementation issues |

### Common Issues

1. **SyntaxError (43 problems)**
   - Preprocessor converting PG syntax incorrectly
   - Need to improve pg_preprocessor_pygment.py

2. **AttributeError (34 problems)**
   - Stub Formula missing .cmp() method ✓ FIXED
   - Stub Formula missing .reduce() method ✓ FIXED
   - Other MathObjects missing methods

3. **NameError (11 problems)**
   - Missing List class stub
   - Missing String class stub
   - Other missing MathObject types

4. **TypeError (8 problems)**
   - Context not subscriptable
   - Complex() constructor issues

### Recent Fixes

- ✓ Enhanced `_FormulaStub` to support `.reduce()` method
- ✓ Enhanced `_StubContext` to support `.flags`, `.functions`, `.constants`
- ✓ ExpandedPolynomial.pg now renders correctly
- ✓ FactoredPolynomial.pg now renders correctly

### Next Steps

To improve pass rate to 90%+:

1. Fix SyntaxError issues in preprocessor (highest impact - 43 problems)
2. Add missing MathObject stubs (List, String) (11 problems)
3. Add .cmp() method to Formula and other stubs (34 problems)
4. Fix Context subscriptability and Complex constructor (8 problems)

### Test Configuration

- **Baseline threshold**: 30% (prevents regressions)
- **Target**: 90%+
- **Seed**: 12345 (fixed for reproducibility)
- **Mode**: Render-only (--no-check equivalent)
