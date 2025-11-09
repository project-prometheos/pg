# Sample Problems Systematic Fix Plan

## Executive Summary

Based on test run, **57 out of 157 tutorial sample problems** are failing (36% failure rate).
This plan provides a systematic approach to fix all failing problems.

## Current Status

### Test Command
```powershell
& "C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe" -m pytest `
  "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py" `
  -v --tb=short
```

### Failure Categories (57 failing problems)

1. **SyntaxError** (21 problems)
   - Invalid syntax from preprocessing
   - Mismatched parentheses/braces
   - Assignment in expression context
   - Unterminated strings
   
2. **NameError** (8 problems)
   - Undefined variables (e.g., `String`, `x3`)
   - Missing imports/context objects
   
3. **TypeError** (5 problems)
   - Type mismatches (str + int)
   - Object not callable
   
4. **Other errors** (23 problems)
   - Runtime errors
   - Logic errors
   - Missing features

## Systematic Approach

### Phase 1: Setup & Tooling (1-2 hours)

#### 1.1 Create Helper Script
Create `tools/fix_sample_problem.py` to automate the debugging workflow:

```python
#!/usr/bin/env python3
"""
Helper script to debug and fix sample problems.

Usage:
  python tools/fix_sample_problem.py NoSolution
  python tools/fix_sample_problem.py --list-failing
  python tools/fix_sample_problem.py --convert NoSolution
"""

Features:
- List all failing problems
- Convert .pg to .pypg (preprocessed Python)
- Show detailed error for a specific problem
- Re-run single problem test
- Diff original vs fixed
```

#### 1.2 Create Conversion Utility
Add method to convert PG → Python for inspection:

```python
def convert_pg_to_python(pg_file_path: str, output_path: str = None):
    """
    Convert a .pg file to preprocessed Python (.pypg).
    
    Args:
        pg_file_path: Path to .pg file
        output_path: Optional output path (default: same name with .pypg)
    
    Returns:
        tuple: (python_code, errors)
    """
    from pg_translator.preprocessor import PGPreprocessor
    
    preprocessor = PGPreprocessor()
    with open(pg_file_path) as f:
        pg_code = f.read()
    
    result = preprocessor.preprocess(pg_code)
    
    if output_path is None:
        output_path = pg_file_path.replace('.pg', '.pypg')
    
    with open(output_path, 'w') as f:
        f.write(result.code)
    
    return result.code, result.errors
```

### Phase 2: Categorize & Prioritize (2-3 hours)

#### 2.1 Generate Error Report
Run comprehensive error analysis:

```powershell
& python -m pytest `
  "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py" `
  -v --tb=short > test_output.txt 2>&1

# Extract and categorize errors
& python tools/analyze_sample_errors.py test_output.txt > ERROR_ANALYSIS.md
```

#### 2.2 Categorization Script
Create `tools/analyze_sample_errors.py`:

```python
"""
Analyze test output and categorize errors.

Output:
- ERROR_ANALYSIS.md with:
  - Error type breakdown
  - Problem list by error type
  - Common patterns
  - Fix priority ranking
"""

categories = {
    'SyntaxError': [],
    'NameError': [],
    'TypeError': [],
    'AttributeError': [],
    'Other': []
}

# Parse pytest output
# Group by error type
# Identify patterns
# Suggest fixes
```

#### 2.3 Priority Ranking

**Priority 1 - Quick Wins (Preprocessor bugs):**
- Problems with consistent syntax errors
- Missing imports that can be auto-added
- Variable name conversion issues
- String interpolation bugs

**Priority 2 - Medium Complexity (Context objects):**
- Missing Context objects (String, etc.)
- Variable scope issues
- Function call syntax

**Priority 3 - Complex (Feature gaps):**
- Missing MathObject features
- Complex control flow
- Advanced Perl features

### Phase 3: Fix Preprocessor Issues (3-5 hours)

#### 3.1 Identify Preprocessor Patterns

For each failing problem:
1. Convert to .pypg to see generated Python
2. Identify preprocessing bug
3. Check if pattern affects multiple problems
4. Fix preprocessor, not individual files

**Common patterns to check:**
- Assignment in conditional: `if ($x = 5)` → needs `if (x := 5)` or `x = 5; if x`
- String interpolation: `"$var"` → `f"{var}"`
- Mismatched braces in hash literals
- Perl-specific syntax not converted

#### 3.2 Preprocessor Fix Template

For each pattern found:

```python
# File: packages/pg_translator/pg_translator/pg_preprocessor_pygment.py

def _fix_assignment_in_condition(self, code: str) -> str:
    """
    Convert Perl assignment in condition to Python walrus operator.
    
    Perl: if ($x = compute())
    Python: if (x := compute())
    """
    pattern = r'if\s*\(\s*\$(\w+)\s*=\s*([^)]+)\)'
    replacement = r'if (\1 := \2)'
    return re.sub(pattern, replacement, code)
```

#### 3.3 Test Each Fix

After each preprocessor fix:

```powershell
# Test specific problem
& python -m pytest `
  "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py::test_tutorial_problem_renders[ProblemName]" `
  -v

# Test all to check for regressions
& python -m pytest `
  "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py" `
  -v --tb=line
```

### Phase 4: Fix Context Objects (2-4 hours)

#### 4.1 Missing Context Types

Problems with `NameError` for undefined types:
- `String` - needs Context("String") import
- Other context types from PG ecosystem

#### 4.2 Fix Strategy

1. **Auto-detect required contexts:**
   ```python
   # Add to preprocessor
   def detect_required_contexts(code: str) -> list[str]:
       """Scan code for Context() calls and undefined types."""
       contexts = set()
       # Look for Context("Type") patterns
       # Look for common PG types
       return list(contexts)
   ```

2. **Auto-inject imports:**
   ```python
   # Add to code generation
   if 'String' in code and 'Context("String")' not in code:
       inject_at_start('Context("String")')
   ```

### Phase 5: Fix Individual Problems (5-10 hours)

For problems that need individual attention:

#### 5.1 Problem Fix Workflow

```bash
# 1. Extract problem
cd tutorial/sample-problems/[Category]/

# 2. Convert to Python
python tools/fix_sample_problem.py --convert ProblemName

# 3. Review generated Python
code ProblemName.pypg

# 4. Identify issue
#    - Syntax error → fix preprocessor
#    - Missing feature → add to MathObjects/Context
#    - Logic error → might need .pg file edit

# 5. Test fix
python -m pytest \
  "tests/test_tutorial_sample_problems.py::test_tutorial_problem_renders[ProblemName]" \
  -v -s

# 6. Document if .pg edited
git commit -m "fix(tutorial): Fix ProblemName - [description]"
```

#### 5.2 Problem Fix Template

For each problem, create entry in `SAMPLE_PROBLEMS_FIXES.md`:

```markdown
## ProblemName.pg

**Category:** [Algebra/Calculus/etc]
**Error Type:** SyntaxError / NameError / TypeError
**Root Cause:** [Brief description]

### Original Error
```
[Paste error message]
```

### Generated Python Issue
```python
# Line XX in .pypg
[Problematic code]
```

### Fix Applied
- [ ] Preprocessor fix in: [file]
- [ ] MathObject enhancement: [feature]
- [ ] .pg file edit: [what changed]

### Fix Code
```python
# Before
[old code]

# After
[new code]
```

### Test Result
```
PASSED - [timestamp]
```
```

### Phase 6: Validation & Documentation (2-3 hours)

#### 6.1 Full Test Suite

```powershell
# Run full test suite
& python -m pytest `
  "d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py" `
  -v --tb=short > FINAL_TEST_RESULTS.txt 2>&1

# Generate final report
& python tools/generate_fix_report.py
```

#### 6.2 Documentation

Create `SAMPLE_PROBLEMS_FIX_SUMMARY.md`:

```markdown
# Sample Problems Fix Summary

## Results
- Total problems: 157
- Initially failing: 57 (36%)
- Fixed: XX (XX%)
- Remaining: XX (XX%)

## Fixes Applied

### Preprocessor Fixes (XX problems)
1. [Pattern] - Fixed in [commit] - Affected: [list]
2. ...

### Context Fixes (XX problems)
1. [Type] - Added support in [commit] - Affected: [list]
2. ...

### Individual Fixes (XX problems)
1. [Problem] - [Description] - [commit]
2. ...

## Known Issues
[Problems still failing with explanation]

## Testing
All fixes validated with:
- Individual problem tests
- Full test suite
- No regressions introduced
```

## Implementation Checklist

### Week 1: Setup & Analysis
- [ ] Create `tools/fix_sample_problem.py` helper script
- [ ] Create `tools/analyze_sample_errors.py` analysis script
- [ ] Generate comprehensive error report
- [ ] Categorize all 57 failing problems
- [ ] Prioritize fixes (Quick wins → Complex)

### Week 2: Preprocessor Fixes
- [ ] Fix assignment-in-condition syntax errors
- [ ] Fix string interpolation issues
- [ ] Fix hash literal brace matching
- [ ] Fix unterminated string literals
- [ ] Test preprocessor fixes on affected problems

### Week 3: Context & Type Fixes
- [ ] Add missing Context types (String, etc.)
- [ ] Fix variable scoping issues
- [ ] Add auto-detection for required contexts
- [ ] Test context fixes

### Week 4: Individual Problem Fixes
- [ ] Fix remaining SyntaxErrors
- [ ] Fix remaining NameErrors
- [ ] Fix remaining TypeErrors
- [ ] Document each fix

### Week 5: Validation & Polish
- [ ] Run full test suite
- [ ] Fix any regressions
- [ ] Generate final documentation
- [ ] Create regression test suite

## Success Metrics

- **Target:** ≥95% of sample problems passing (149/157)
- **Minimum:** ≥90% passing (142/157)
- **Current:** 64% passing (100/157)

## Time Estimate

- **Optimistic:** 2-3 weeks (15-20 hours)
- **Realistic:** 3-4 weeks (25-35 hours)
- **Pessimistic:** 4-6 weeks (40-50 hours)

## Risk Mitigation

1. **Regression Risk:**
   - Test full suite after each preprocessor change
   - Commit frequently with clear messages
   - Maintain rollback capability

2. **Complexity Creep:**
   - Focus on high-impact fixes first
   - Document "won't fix" items
   - Set time boxes for complex problems

3. **Breaking Changes:**
   - Don't modify .pg files unless absolutely necessary
   - Prefer preprocessor/library fixes
   - Coordinate with team on .pg changes

## Next Steps

1. **Immediate (Today):**
   - Create helper scripts
   - Run comprehensive error analysis
   - Create ERROR_ANALYSIS.md

2. **This Week:**
   - Fix top 5 preprocessor patterns
   - Add missing Context types
   - Achieve 75% pass rate

3. **Next Week:**
   - Fix individual problems
   - Achieve 90% pass rate
   - Document all fixes

---

**Created:** 2025-11-09
**Status:** Planning
**Owner:** [Your name]
