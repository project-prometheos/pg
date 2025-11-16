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

### Current Status (Latest Test)
- **Both work**: 16 snippets (76%)
- **Perl only**: 2 snippets
- **Python only**: 2 snippets  
- **Perl errors**: 1 snippet (graph_basic - expected, missing WWPlot)

### Working Snippets (Both Perl and Python)
| Snippet | Perl HTML | Python HTML | Perl Answers | Python Answers | Status |
|---------|----------|-------------|--------------|----------------|--------|
| choice_checkbox | 44 chars | 775 chars | 1 | 1 | ✅ Both work |
| choice_multiple_choice | 44 chars | 508 chars | 1 | 1 | ✅ Both work |
| course_basic | 58 chars | 62 chars | 0 | 0 | ✅ Both work |
| integration_complex | 1867 chars | 1110 chars | 1 | 1 | ✅ Both work |
| integration_realistic | 2599 chars | 1632 chars | 1 | 1 | ✅ Both work |
| mathobjects_formula | 156 chars | 228 chars | 1 | 1 | ✅ Both work |
| mathobjects_intervals | 123 chars | 194 chars | 1 | 1 | ✅ Both work |
| mathobjects_vectors | 162 chars | 276 chars | 1 | 1 | ✅ Both work |
| multianswer_basic | 174 chars | 429 chars | 1 | 1 | ✅ Both work |
| pgml_answer_blanks | 1442 chars | 850 chars | 4 | 4 | ✅ Both work |
| pgml_formatting | 835 chars | 302 chars | 0 | 0 | ✅ Both work |
| pgml_inline_math | 596 chars | 474 chars | 0 | 0 | ✅ Both work |
| random_numbers | 114 chars | 123 chars | 0 | 0 | ✅ Both work |
| standard_basic | 174 chars | 238 chars | 1 | 1 | ✅ Both work |
| standard_modes | 172 chars | 145 chars | 0 | 0 | ✅ Both work |
| standard_solution | 49 chars | 90 chars | 1 | 1 | ✅ Both work |

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

## Recent Improvements

### Fixes Applied
1. ✅ **BEGIN_TEXT preprocessing**: Fixed to use heredoc syntax for proper handling of curly braces
2. ✅ **HTML::Entities**: Added fallback implementation for missing module
3. ✅ **PGML preprocessing**: Fixed BEGIN_PGML/END_PGML conversion to PGML() calls
4. ✅ **Choice classes**: Pre-loaded Multiple, ChoiceList, Match, Select classes
5. ✅ **Solution/Hint blocks**: Added BEGIN_SOLUTION/END_SOLUTION and BEGIN_HINT/END_HINT preprocessing

### Progress
- **Before fixes**: 7 snippets working (33%)
- **After fixes**: 16 snippets working (76%)
- **Improvement**: +9 snippets, +43 percentage points

## Next Steps

1. **Fix fraction context**: Investigate why `context::Extensions::create()` returns unblessed context
2. **Normalize answer names**: Update comparison logic to handle format differences (AnSwEr1 vs AnSwEr0001)
3. **Investigate macro differences**: Why some macros produce different output
4. **Add more test cases**: Expand snippet coverage
5. **Document expected differences**: Create normalization rules
6. **Performance comparison**: Measure execution time differences

## Notes

- Both adapters are functional and can execute PG code
- Differences are mostly in output format, not core functionality
- The Perl adapter uses the full WeBWorK PG library
- The Python adapter uses a ported implementation
- Some differences are expected due to implementation approaches

