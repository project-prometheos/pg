# Parity Lab Quick Start Guide

## What Was Built

A comprehensive testing framework to verify 1:1 parity between Perl and Python implementations of the top 10 WeBWorK/PG macros.

## Initial Results

✅ **Successfully extracted Perl inventory**: 290 symbols from 10 macro files
⚠️ **Python inventory shows gaps**: Only 3/10 modules currently have implementations
❌ **201 parity issues identified** in initial diff report

## View the Diff Report

The initial inventory comparison is available at:
```
parity_lab/build/inv_diff.html
```

Open it in your browser to see:
- Missing Python implementations (red)
- Signature mismatches (yellow)
- Successfully matching symbols (green)

## What's Next

### Priority 1: API Coverage (Blockers)

The diff report shows **massive API gaps**. Focus areas:

1. **PGstandard.pl** - Core PG functions (random, ANS, TEXT, etc.)
2. **MathObjects.pl** - Formula, Compute, Context system
3. **PGML.pl** - PGML parser and rendering

### Priority 2: Contract Testing

Once basic API coverage exists:

```bash
# Run contract tests
cd parity_lab
pytest tests/contract -v
```

These will compare actual runtime behavior between Perl and Python.

### Priority 3: OPL Corpus Testing

Test against real-world problems:

```bash
# Requires OPL checkout
git clone https://github.com/openwebwork/webwork-open-problem-library.git ../opl

# Select test corpus
python tools/corpus/select_opl_problems.py ../opl build/corpus.json 5000
```

## Project Structure Created

```
parity_lab/
├── README.md              # Full documentation
├── QUICK_START.md         # This file
├── build/
│   ├── perl_inventory.json    # 290 Perl symbols
│   ├── py_inventory.json      # 3 Python symbols (needs work!)
│   └── inv_diff.html          # Visual diff report
├── tools/
│   ├── inventory/         # Symbol extraction & diff
│   ├── render_diff/       # Runtime output comparison
│   └── corpus/            # OPL problem selection
├── tests/
│   ├── snippets/          # 5 test PG problems
│   ├── contract/          # pytest-based contract tests
│   ├── perl/              # Perl unit tests
│   └── fuzz/              # Property-based tests
├── perl_ref/              # Perl runtime adapter
├── py_port/               # Python runtime adapter
└── demo/                  # Demo problems & scripts
```

## Key Files to Review

1. **[parity_lab/build/inv_diff.html](build/inv_diff.html)** - Start here! Visual diff report
2. **[parity_lab/README.md](README.md)** - Complete documentation
3. **[parity_lab/tests/snippets/](tests/snippets/)** - Example test problems

## Interpreting the Diff Report

### Status Colors

- 🟢 **Green (OK)**: Symbol exists in both Perl and Python with matching signatures
- 🔴 **Red (MISSING_IN_PYTHON)**: Critical - Python port missing this symbol
- 🟡 **Yellow (SIGNATURE_MISMATCH)**: Symbol exists but parameters don't match
- 🟡 **Yellow (DEFAULT_MISMATCH)**: Parameters match but defaults differ

### Example Issues

From the report, you'll see:

```
PGstandard.pl:
  ✗ random (MISSING_IN_PYTHON)
  ✗ non_zero_random (MISSING_IN_PYTHON)
  ✗ ANS (MISSING_IN_PYTHON)
  ✗ TEXT (MISSING_IN_PYTHON)
  ... (many more)

MathObjects.pl:
  ✗ Context (MISSING_IN_PYTHON)
  ✗ Compute (MISSING_IN_PYTHON)
  ✗ Formula (MISSING_IN_PYTHON)
  ... (many more)
```

## Running Individual Tools

### Extract Perl Symbols
```bash
python tools/inventory/dump_perl_inventory.py ../macros build/perl_inventory.json
```

### Extract Python Symbols
```bash
python tools/inventory/dump_py_inventory.py build/py_inventory.json
```

### Generate Diff Report
```bash
python tools/inventory/diff_inventory.py \
  build/perl_inventory.json \
  build/py_inventory.json \
  build/inv_diff.html
```

### Test a PG Snippet
```bash
# Perl runtime
perl perl_ref/run_pg_snippet.pl tests/snippets/fraction_basic.pg 12345 build/perl_out.json

# Python runtime (will show "not implemented" currently)
python py_port/run_pg_snippet.py tests/snippets/fraction_basic.pg 12345 build/py_out.json

# Compare
python tools/render_diff/diff_outputs.py build/perl_out.json build/py_out.json
```

## Success Metrics

Track progress toward these goals:

- [ ] **API Coverage**: 100% of 290 Perl symbols implemented in Python
- [ ] **Signature Parity**: All parameters and defaults match
- [ ] **Contract Tests**: 100% pass rate on snippet tests
- [ ] **OPL Corpus**: 100% pass rate on ≥100 real problems
- [ ] **Code Coverage**: ≥95% line coverage in Python implementation

## Getting Help

- **Full documentation**: [README.md](README.md)
- **Project guidelines**: [../CLAUDE.md](../CLAUDE.md)
- **Issues**: Track parity gaps in GitHub issues with labels:
  - `api-gap` - Missing function/class
  - `behavior-gap` - Wrong behavior
  - `signature-mismatch` - Parameter differences

## Recommended Workflow

1. **Open** `build/inv_diff.html` in browser
2. **Identify** top priority missing symbols (start with PGstandard.pl)
3. **Implement** Python versions in `packages/pg_macros/`
4. **Re-run** inventory diff to verify
5. **Add** contract tests to verify behavior
6. **Repeat** until all green!

## Current Status Summary

| Macro | Perl Symbols | Python Symbols | Status |
|-------|--------------|----------------|--------|
| PGstandard.pl | 64 | 0 | ❌ Not started |
| MathObjects.pl | 94 | 0 | ❌ Not started |
| PGML.pl | 52 | 0 | ❌ Not started |
| PGchoicemacros.pl | 23 | 0 | ❌ Not started |
| PGgraphmacros.pl | 18 | 0 | ❌ Not started |
| parserPopUp.pl | 12 | 3 | 🟡 Minimal |
| parserMultiAnswer.pl | 10 | 0 | ❌ Not started |
| contextFraction.pl | 8 | 0 | ❌ Not started |
| AnswerFormatHelp.pl | 7 | 0 | ❌ Not started |
| PGcourse.pl | 2 | 0 | ❌ Not started |

**Total**: 3/290 symbols implemented (1% complete)

## Notes

- The framework is **fully operational** - tools work correctly
- The **Python implementations are incomplete** - this is expected
- Use the framework to **drive development** of Python ports
- The **diff report is your roadmap** to achieving parity

---

**Generated**: 2025-11-09
**Framework Version**: 1.0
**Status**: Infrastructure complete, implementation needed
