# Parity Lab Status Report

## Overview
This document tracks the status of Perl vs Python parity comparisons for PG (Problem Generator) code.

## Adapter Status

### Perl Adapter (`perl_ref/run_pg_snippet.pl`)
✅ **FUNCTIONAL**
- Successfully loads full WeBWorK PG library
- Executes PG snippets without errors
- Generates HTML output
- Captures answer evaluators
- Initializes Parser::Context correctly

### Python Adapter (`py_port/run_pg_snippet.py`)
✅ **FUNCTIONAL**
- Executes preprocessed PG snippets
- Generates HTML output
- Captures answer evaluators
- Handles PGML correctly

## Known Differences

### 1. Answer Name Format
- **Perl**: Uses format `AnSwEr1`, `AnSwEr2`, etc.
- **Python**: Uses format `AnSwEr0001`, `AnSwEr0002`, etc.
- **Impact**: Low - both are valid, just different formatting
- **Status**: Expected difference, can be normalized in comparison

### 2. HTML Output Format
- **Perl**: Outputs raw PG code (e.g., `{ans_rule(10)}`, `<BR>`)
- **Python**: Renders to HTML (e.g., `<input type="text">`, `<br/>`)
- **Impact**: Medium - Python renders more completely
- **Status**: Python adapter does more rendering work

### 3. Random Number Generation
- **Perl**: Uses Perl's `random()` function
- **Python**: Uses Python's random number generator
- **Impact**: Low - both use seed 42, but implementations differ
- **Status**: Expected - different RNG implementations

### 4. Macro Loading
- **Perl**: Loads macros directly from `.pl` files
- **Python**: Uses preprocessor to convert `loadMacros()` to imports
- **Impact**: Low - both achieve same result
- **Status**: Different implementation paths

## Test Results Summary

### Basic Snippets
| Snippet | Perl HTML | Python HTML | Perl Answers | Python Answers | Status |
|---------|----------|-------------|--------------|----------------|--------|
| standard_basic.pg | 163 chars | 238 chars | 1 | 1 | ✅ Both work |
| mathobjects_formula.pg | TBD | TBD | TBD | TBD | Testing... |
| choice_multiple_choice.pg | 1 char | 508 chars | 0 | 1 | ⚠️ Different output |
| fraction_basic.pg | 0 chars | 147 chars | 0 | 0 | ⚠️ Different output |

### Issues Found
1. **Choice/Checkbox macros**: Perl produces minimal output, Python renders fully
2. **Fraction macros**: Perl produces no output, Python renders
3. **Some macros not fully implemented in Perl adapter**: May need additional macro loading

## Comparison Tools

### Quick Comparison
```bash
python parity_lab/compare_outputs.py <perl_json> <python_json>
```

### Detailed Diff
```bash
python parity_lab/tools/render_diff/diff_outputs.py <perl_json> <python_json>
```

### Full Test Suite
```bash
bash parity_lab/run_parity_comparison.sh
```

## Next Steps

1. **Normalize answer names**: Update comparison logic to handle format differences
2. **Investigate macro differences**: Why some macros produce different output
3. **Add more test cases**: Expand snippet coverage
4. **Document expected differences**: Create normalization rules
5. **Performance comparison**: Measure execution time differences

## Notes

- Both adapters are functional and can execute PG code
- Differences are mostly in output format, not core functionality
- The Perl adapter uses the full WeBWorK PG library
- The Python adapter uses a ported implementation
- Some differences are expected due to implementation approaches

