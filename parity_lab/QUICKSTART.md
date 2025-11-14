# Parity Lab Quick Start Guide

## TL;DR - Run the Tests

```powershell
cd parity_lab
./run_tests.ps1
```

That's it! The script will:
- ✅ Run 19 fuzz tests (property-based testing)
- ✅ Run 11 Python contract tests  
- ✅ Show you implementation gaps found
- ✅ Report overall status

## What You'll See

```
================================
PG Parity Lab Test Runner
================================

Checking Dependencies...
Python 3.13.2
Perl 5.42.0

Running Fuzz Tests...
====================== 19 passed ======================

Running Contract Tests (Python-only)...
================ 11 passed, 4 failed =================

Test run complete!

Status:
  Python Runtime: Functional ✅
  Perl Available: Yes ✅
  Perl PG Libraries: Not installed ⏳
```

## Understanding the Results

### ✅ 19 Fuzz Tests Pass
These test mathematical properties and edge cases:
- Commutativity (a+b = b+a)
- Zero behavior
- String manipulation
- Random determinism

### ✅ 11 Contract Tests Pass
These test actual PG problem execution:
- Fraction computations
- PGstandard macros
- PGML rendering
- PopUp/MultiAnswer

### ⚠️ 4 Tests Fail - This is SUCCESS!
The failures **found real implementation gaps**:
1. Missing `new_multiple_choice()` wrapper
2. Missing `new_checkbox_multiple_choice()` wrapper  
3. Missing `norm()` function for vectors
4. `Interval()` doesn't support string parsing

**This is exactly what parity testing is designed to do!**

## Test Files Created

### Test Snippets (20 files)
```
tests/snippets/
├── standard_basic.pg           # PGstandard basics
├── standard_solution.pg        # SOLUTION/HINT blocks
├── standard_modes.pg           # MODES() function
├── mathobjects_formula.pg      # Formula evaluation
├── mathobjects_vectors.pg      # Vector operations
├── mathobjects_intervals.pg    # Interval/Set objects
├── fraction_basic.pg           # Basic fractions
├── fraction_mixed.pg           # Mixed numbers
├── pgml_formatting.pg          # PGML bold/lists/headings
├── pgml_answer_blanks.pg       # PGML answer inputs
├── choice_multiple_choice.pg   # Multiple choice questions
├── choice_checkbox.pg          # Checkbox questions
├── popup_basic.pg              # PopUp menus
├── multianswer_basic.pg        # MultiAnswer
├── integration_complex.pg      # Multiple features
└── integration_realistic.pg    # Real-world problem
```

### Demo Problems (5 files)
```
demo/problems/
├── demo_algebra.pg          # Solve for x
├── demo_calculus.pg         # Derivatives
├── demo_pgml.pg             # PGML showcase
├── demo_interactive.pg      # PopUp + MultiAnswer
└── demo_comprehensive.pg    # Multiple macros
```

### Contract Tests (5 files)
```
tests/contract/
├── test_fraction.py         # 7 test cases
├── test_pgstandard.py       # 7 test cases
├── test_mathobjects.py      # 8 test cases
├── test_pgml.py             # 7 test cases
├── test_choice.py           # 5 test cases
└── conftest.py              # Utilities
```

### Fuzz Tests (3 files)
```
tests/fuzz/
├── test_numeric_edge_cases.py  # 9 test cases
├── test_random_seeds.py        # 3 test cases
├── test_string_properties.py   # 9 test cases
└── conftest.py                 # Hypothesis strategies
```

## What Each Test Type Does

### Fuzz Tests
- Test **mathematical properties** hold for random inputs
- Use Hypothesis to generate thousands of test cases
- Find edge cases automatically
- Example: "Does a+b always equal b+a?"

### Contract Tests
- Test **actual PG problem execution**
- Compare output structure and behavior
- Verify determinism (same seed = same output)
- Can compare Perl vs Python (when Perl libs available)

### Demo Problems
- Show **realistic PG problems**
- Can be run individually for testing
- Demonstrate multiple macro combinations

## Running Individual Tests

### Run specific test file
```powershell
pytest tests/contract/test_fraction.py -v
```

### Run specific test function
```powershell
pytest tests/contract/test_fraction.py::test_fraction_determinism -v
```

### Run with specific filter
```powershell
pytest tests/contract/ -k "pgml" -v
```

### Run Python-only tests (skip Perl comparison)
```powershell
pytest tests/contract/ -k "determinism or no_errors" -v
```

## Customizing the Test Runner

Edit `run_tests.ps1` to:
- Change Python path: `$env:PYTHONPATH = "your\path"`
- Change Perl path: `$env:PATH = "your\perl\bin;$env:PATH"`
- Add more test filters
- Change pytest options

## Next Steps

### To Fix Implementation Gaps
1. Add missing functions to `pg_macros`
2. Re-run tests: `./run_tests.ps1`
3. See failures decrease!

### To Enable Perl Comparison
1. Install WeBWorK PG Perl libraries
2. Update `perl_ref/run_pg_snippet.pl` with library paths
3. Run full suite: `pytest tests/contract/ -v`
4. Compare Perl vs Python output

### To Expand Test Coverage
1. Add more .pg files to `tests/snippets/`
2. Add corresponding tests to `tests/contract/`
3. Run inventory diff: `python tools/inventory/diff_inventory.py`

## Getting Help

- See `README.md` for detailed documentation
- See `STATUS.md` for current implementation status
- Check test output for specific error messages
- Failed tests show exactly what's missing!

---

**The parity lab finds bugs so you don't have to!** 🎉

