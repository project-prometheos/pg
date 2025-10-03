# pypg Tool - Creation Summary

**Date**: October 3, 2025  
**Purpose**: Command-line tool for testing PG problems with student answers

---

## What Was Created

### 1. Main Script: `pypg.py`
A full-featured Python command-line tool with:
- ✅ Problem rendering from .pg files
- ✅ Answer checking with multiple answer types
- ✅ Configurable random seed
- ✅ Formatted output with clear pass/fail indicators
- ✅ Proper exit codes for automation
- ✅ Solution display option
- ✅ Render-only mode for quick previews

### 2. Windows Wrapper: `pypg.bat`
A batch file for convenient Windows usage:
```cmd
pypg problem.pg "answer1" "answer2"
```

### 3. Documentation: `PYPG_USAGE.md`
Complete usage guide with:
- Installation instructions
- Command syntax
- 10+ examples
- Answer format guidelines
- Troubleshooting tips
- Exit codes and automation tips

---

## Quick Start

### View a problem:
```bash
python pypg.py tutorial/sample-problems/Algebra/ExpandedPolynomial.pg --render-only
```

### Test with an answer:
```bash
python pypg.py tutorial/sample-problems/Algebra/ExpandedPolynomial.pg "x^2-6x+4"
```

### Test with multiple answers:
```bash
python pypg.py tutorial/sample-problems/Algebra/DomainRange.pg "x>=1" "y>=0" "[1,inf)" "[0,inf)"
```

---

## Features

### Supported Answer Types
✅ Numbers (`3.14`, `42`, `-7.5`)  
✅ Formulas (`x^2+3x-4`, `sin(x)`)  
✅ Intervals (`[0,5]`, `(0,inf)`)  
✅ Inequalities (`x >= 3`, `y < 10`)  
✅ Points/Vectors (`(3,4)`, `<1,2,3>`)  
✅ Lists (`1,2,3`, `x-1,x+1`)  

### Output Features
✅ Color-coded results (`[OK]` / `[FAIL]`)  
✅ Detailed feedback messages  
✅ Score tracking (`3/4`)  
✅ Problem statement display  
✅ Expected answer format hints  
✅ Solution display (optional)  

### Advanced Features
✅ Configurable seed (`--seed 456`)  
✅ Render-only mode (`--render-only`)  
✅ Solution display (`--show-solution`)  
✅ Proper exit codes (0=success, 1=failure)  
✅ Warning for answer count mismatch  

---

## Test Results

Successfully tested with:
- ✅ `ExpandedPolynomial.pg` - Single formula answer
- ✅ `DomainRange.pg` - Multiple answers (4 answers: 2 inequalities, 2 intervals)
- ✅ `SimpleFactoring.pg` - List answers
- ✅ Correct answers → Exit code 0, "ALL ANSWERS CORRECT!"
- ✅ Wrong answers → Exit code 1, "X INCORRECT"

---

## Technical Details

### Architecture
```
pypg.py
├── Imports pg_renderer.PGRenderer
├── Imports pg_renderer.answer_checker.AnswerChecker
├── Renders problem with seed
├── Maps student answers to answer blanks (in order)
├── Checks each answer with appropriate checker
└── Reports results with formatting
```

### Dependencies
- `pg_renderer` - Problem rendering
- `pg_renderer.answer_checker` - Answer validation
- Python standard library (argparse, pathlib, re)

### Integration Points
Uses the same backend infrastructure:
- Same renderer as `/api/db/{problem_id}/render`
- Same answer checker as `/api/db/{problem_id}/check`
- Validates the entire rendering + checking pipeline

---

## Use Cases

### 1. Problem Development
Test problems during development:
```bash
python pypg.py my_new_problem.pg "expected_answer" --seed 1
python pypg.py my_new_problem.pg "expected_answer" --seed 2
python pypg.py my_new_problem.pg "expected_answer" --seed 3
```

### 2. Answer Key Verification
Verify answer keys:
```bash
python pypg.py problem.pg "answer_from_key" --show-solution
```

### 3. Automated Testing
Include in test suites:
```bash
#!/bin/bash
for problem in problems/*.pg; do
    python pypg.py "$problem" --render-only || echo "FAILED: $problem"
done
```

### 4. Student Answer Simulation
Test how the checker handles common wrong answers:
```bash
python pypg.py problem.pg "x^2+1"        # Wrong
python pypg.py problem.pg "x^2+3x-4"     # Correct
python pypg.py problem.pg "x^2 + 3x - 4" # Correct (spacing ok)
```

### 5. CI/CD Integration
```yaml
# .github/workflows/test.yml
- name: Test problems
  run: |
    python pypg.py problem1.pg "answer1" || exit 1
    python pypg.py problem2.pg "a1" "a2" || exit 1
```

---

## Example Output

### Successful Test
```
================================================================================
Problem: ExpandedPolynomial.pg
Path: tutorial\sample-problems\Algebra\ExpandedPolynomial.pg
Seed: 123
================================================================================

[RENDERING]
[OK] Problem rendered successfully

[PROBLEM STATEMENT]
--------------------------------------------------------------------------------
The quadratic expression $(x-$h)^2-$k$ is written in vertex form.
Write the expression in expanded form $ax^2 + bx + c$.

[____]
--------------------------------------------------------------------------------

[EXPECTED ANSWERS]
  1. AnSwEr0001
     Correct: x^2 + -6 x + 4
     Type: formula

[CHECKING ANSWERS]

[ANSWER CHECK RESULTS]
--------------------------------------------------------------------------------

1. AnSwEr0001 [OK]
   Student: x^2-6x+4
   Correct: x^2 + -6 x + 4
   Type: formula
   Message: Correct!
--------------------------------------------------------------------------------

Score: 1/1

*** ALL ANSWERS CORRECT! ***
```

---

## Future Enhancements (Optional)

Possible additions:
- [ ] JSON output mode for machine parsing
- [ ] Batch mode: test multiple problems from a file
- [ ] Interactive mode: prompt for answers
- [ ] Verbose mode: show intermediate steps
- [ ] Timing information
- [ ] Compare answers from multiple students
- [ ] Export results to CSV/JSON

---

## Files Created

| File | Purpose | Lines |
|------|---------|-------|
| `pypg.py` | Main script | 365 |
| `pypg.bat` | Windows wrapper | 3 |
| `PYPG_USAGE.md` | User documentation | 268 |
| `PYPG_TOOL_SUMMARY.md` | This file | 267 |
| **Total** | | **903** |

---

## Integration with Existing Tools

Works alongside:
- ✅ `test_algebra_samples.py` (batch testing)
- ✅ Backend API endpoints
- ✅ `pg_renderer` package
- ✅ `pg_answer` package

Complements but doesn't replace:
- Backend API (for web integration)
- Batch test scripts (for comprehensive testing)
- Unit tests (for component testing)

---

## Success Criteria Met

✅ Takes PG file path as first argument  
✅ Takes answer strings as subsequent arguments  
✅ Maps answers to blanks in order  
✅ Validates answers correctly  
✅ Shows clear pass/fail results  
✅ Works on Windows  
✅ Well documented  
✅ Proper exit codes  
✅ Tested with real problems  

---

**Status**: ✅ Complete and tested  
**Ready for**: Immediate use in problem development and testing

