# Tutorial Sample Problems Testing Guide

This guide explains how to use the comprehensive pytest suite to test tutorial sample problems.

## Quick Start

The test file is located at:
```
packages/pg/translator/tests/test_tutorial_sample_problems_all.py
```

### Run All Tests
```bash
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py -v
```

## Usage Examples

### Run a Specific Problem by Name

```bash
# Test the UnitConversion problem
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py -v -k "UnitConversion"

# Test ExpandedPolynomial problem
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py -v -k "ExpandedPolynomial"

# Test DifferentiateFunction problem
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py -v -k "DifferentiateFunction"
```

### Run All Problems in a Category

```bash
# All Arithmetic problems
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py -v -k "Arithmetic"

# All Algebra problems
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py -v -k "Algebra"

# All DiffCalc problems
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py -v -k "DiffCalc"

# All Complex problems
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py -v -k "Complex"
```

### Run Multiple Specific Problems

```bash
# Test multiple problems by combining keywords with "or"
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py -v -k "UnitConversion or ExpandedPolynomial or VectorOperations"

# Test all failing problems
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py -v -k "AnswerWithUnits or DifferentiateFunction or GraphsInTables or ChemicalReaction"
```

### Run with Different Output Modes

```bash
# Short traceback (default, recommended for quick review)
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py -v -k "UnitConversion" --tb=short

# Long traceback (full details)
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py -v -k "GraphsInTables" --tb=long

# No traceback (just pass/fail)
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py -v -k "DiffCalc" --tb=no
```

### List All Available Problems

```bash
# See all test names without running them
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py --collect-only -q
```

### Run the Aggregate Test (Summary Report)

```bash
# Run all problems with a detailed summary at the end
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py::TestTutorialSampleProblems::test_all_sample_problems_render -v
```

### Run Only Non-Parametrized Tests

```bash
# Directory existence check
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py::TestTutorialSampleProblems::test_sample_problems_directory_exists -v

# File count check
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py::TestTutorialSampleProblems::test_sample_problems_contain_files -v

# Statistics
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py::test_sample_problems_stats -v
```

## Available Problem Categories

The tutorial sample problems are organized by category:

- **Algebra** - Polynomial, fractions, inequalities, etc.
- **Arithmetic** - Unit conversions, basic operations
- **Complex** - Complex number operations
- **DiffCalc** - Differential calculus problems
- **DiffCalcMV** - Multivariable differential calculus
- **DiffEq** - Differential equations
- **Geometry** - Geometric shapes and transformations
- **IntegralCalc** - Integration problems
- **LinearAlgebra** - Matrix operations, row operations
- **Misc** - Miscellaneous problem types
- **Parametric** - Parametric equations, polar coordinates
- **ProblemTechniques** - Various PG authoring techniques
- **Sequences** - Sequences and series
- **Snippets** - Code snippets and examples
- **Statistics** - Statistical calculations and graphs
- **Trig** - Trigonometric functions and identities
- **VectorCalc** - Vector calculus and fields

## Current Test Results

**Total: 157 problems**
- **Passing: 144 (91.7%)**
- **Failing: 13 (8.3%)**

### Failing Problems

1. **DiffCalc/AnswerWithUnits** - Cannot differentiate
2. **DiffCalc/DifferentiateFunction** - Cannot differentiate
3. **DiffEq/HeavisideStep** - Formula evaluation error
4. **Misc/ChemicalReaction** - Index out of range
5. **Misc/ManyMultipleChoice** - Sample size error
6. **Misc/MatchingAlt** - Key error
7. **ProblemTechniques/DifferentiatingFormulas** - Cannot differentiate
8. **ProblemTechniques/DigitsTolType** - String to float conversion
9. **ProblemTechniques/GraphsInTables** - Indentation error
10. **Statistics/LinearRegression** - Index out of range
11. **Sequences/AnswerOrderedList** - Index out of range
12. **Trig/PeriodicAnswers** - String to float conversion
13. **Advanced/TaylorSeries** - Cannot differentiate (if present)

## Test Features

The test suite provides:

✓ **Automatic Problem Discovery** - Finds all .pg files in tutorial/sample-problems
✓ **Individual Test Cases** - Each problem has its own parametrized test
✓ **Aggregate Testing** - Run all problems with comprehensive statistics
✓ **Detailed Error Reporting** - Shows error type and traceback for failures
✓ **Flexible Selection** - Run by problem name, category, or combination
✓ **Reproducible Results** - Uses seed=1234 for consistent results
✓ **Same Method as pg_solve.py** - Uses PGTranslator for rendering

## Advanced Options

```bash
# Run with output capture disabled (see print statements)
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py -v -s -k "UnitConversion"

# Run with specific markers
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py -v -m "not slow"

# Run with parallel execution (if pytest-xdist is installed)
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py -v -n auto

# Stop after first failure
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py -v -x

# Run previously failed tests
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py -v --lf

# Run with last failed first
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py -v --ff
```

## Integration with CI/CD

For continuous integration:

```bash
# Run with JUnit XML output
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py --junit-xml=test-results.xml

# Run with coverage (requires pytest-cov)
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py --cov=pg.translator

# Run with coverage and HTML report
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py --cov=pg.translator --cov-report=html
```

## Troubleshooting

### Problem: Tests not found
Make sure you're running from the repository root:
```bash
cd /path/to/pg
pytest packages/pg/translator/tests/test_tutorial_sample_problems_all.py -v
```

### Problem: "tutorial/sample-problems directory not found"
Ensure the tutorial/sample-problems directory exists at the expected location.

### Problem: Pytest configuration issues
Check that `pyproject.toml` is in `packages/pg/` directory with proper pytest configuration.

## Contributing New Tests

To add a new test problem:

1. Add the .pg file to `tutorial/sample-problems/<Category>/` directory
2. Re-run the test collection - the problem will be automatically discovered
3. The parametrized tests will run automatically for the new problem

## See Also

- [pg_solve.py](pg_solve.py) - Interactive problem solver using the same rendering method
- [PGTranslator Documentation](packages/pg/translator/__init__.py)
- [Tutorial Sample Problems](tutorial/sample-problems/) - The actual problem files
