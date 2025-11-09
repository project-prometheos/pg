# Fix Documentation Template

Use this template to document each problem fix. Helps track patterns and makes it easier to apply similar fixes to other problems.

---

## Fix Record Template

```
# FIX: [Problem Name]
Date: [YYYY-MM-DD]
Status: ✓ FIXED / ⚠ PARTIAL / ✗ UNABLE

## Problem Information
- File: tutorial/sample-problems/[Category]/[ProblemName].pg
- Error Type: [SyntaxError|NameError|AttributeError|TypeError|ImportError]
- Error Message: [First line of actual error]

## Root Cause Analysis
[Explain what was wrong and why]

## Generated Python (Relevant Section)
[Show the generated Python code that was causing the problem]

## Fix Applied
[Describe the exact changes made to the .pg file]

### Before:
[Relevant code snippet]

### After:
[Corrected code snippet]

## Testing
- Test command: `python scripts/quick_test.py "tutorial/sample-problems/.../[name].pg"`
- Result: ✓ PASSED / ⚠ WARNING / ✗ FAILED
- Output: [Brief description of test result]

## Notes & Gotchas
[Any special considerations, alternative approaches tried, etc.]

## Similar Problems
[Other problems that might need the same fix]

## Tags
[#NameError, #MacroLoad, #SyntaxFix, #Algebra, etc.]
```

---

## Example Fix Documentation

### Fix Record 1: SimpleFactoring

```
# FIX: SimpleFactoring
Date: 2025-11-09
Status: ✓ FIXED

## Problem Information
- File: tutorial/sample-problems/Algebra/SimpleFactoring.pg
- Error Type: NameError
- Error Message: NameError: name 'Formula' is not defined

## Root Cause Analysis
The problem uses Formula() to create algebraic expressions but the loadMacros()
call didn't include "PGbasicmacros.pl" which provides the Formula function.

## Generated Python (Relevant Section)
```
File: .../SimpleFactoring.pg:
    # ERROR: name 'Formula' is not defined
    ans1 = Formula("x-2")
    ans2 = Formula("x-3")
```

## Fix Applied
Added "PGbasicmacros.pl" to the loadMacros() call.

### Before:
```perl
loadMacros("PG.pl", "PGcourse.pl");
```

### After:
```perl
loadMacros("PG.pl", "PGbasicmacros.pl", "PGcourse.pl");
```

## Testing
- Test command: `python scripts/quick_test.py "tutorial/sample-problems/Algebra/SimpleFactoring.pg"`
- Result: ✓ PASSED
- Output: ✅ PASSED - Statement HTML: 2847 characters

## Notes & Gotchas
- Formula() is from PGbasicmacros.pl
- Many problems have missing macro loads
- Should check macro documentation to see what each provides

## Similar Problems
- LinearInterpolation.pg (same NameError issue)
- ExpandedPolynomial.pg (likely same issue)
- Other Algebra problems

## Tags
#NameError #MacroLoad #Algebra #PGbasicmacros
```

---

### Fix Record 2: ComplexNumberArithmetic

```
# FIX: ComplexNumberArithmetic
Date: 2025-11-09
Status: ✓ FIXED

## Problem Information
- File: tutorial/sample-problems/Complex/ComplexNumberArithmetic.pg
- Error Type: SyntaxError
- Error Message: SyntaxError: Invalid escape sequence in string

## Root Cause Analysis
The .pg file had a backslash in a string that's interpreted as an escape
sequence by Python. Perl string escaping is different from Python.

## Generated Python (Relevant Section)
```python
# Original PG:
$latex = "\\sqrt{x}";

# Generated Python (WRONG):
latex = "\sqrt{x}"  # \s is invalid escape sequence

# Should be:
latex = r"\sqrt{x}"  # raw string, or
latex = "\\sqrt{x}"  # escaped backslash
```

## Fix Applied
Changed the string handling in the generated Python (or fixed the .pg if possible).

### Before:
```perl
$latex = "\\sqrt{x}";
```

### After:
```perl
$latex = r"\\sqrt{x}";  # or similar handling
```

## Testing
- Test command: `python scripts/quick_test.py "tutorial/sample-problems/Complex/ComplexNumberArithmetic.pg"`
- Result: ✓ PASSED
- Output: ✅ PASSED - Statement HTML: 1523 characters

## Notes & Gotchas
- This is a translator issue - the generated code needs to use raw strings
- May need to be fixed in PGTranslator itself, not the .pg file
- Multiple problems likely have this issue

## Similar Problems
- Any problem with LaTeX in strings (likely most of them)

## Tags
#SyntaxError #LaTeX #PythonEscaping #Translator
```

---

## Batch Fix Summary Template

Use this after fixing a batch of problems:

```
# BATCH FIX SUMMARY
Date: [YYYY-MM-DD]

## Batch Information
- Category: [Priority 1|Priority 2|Priority 3]
- Error Type: [NameError|SyntaxError|etc.]
- Number of Problems: [count]

## Problems Fixed
1. [Problem1] - ✓ FIXED
2. [Problem2] - ✓ FIXED
3. [Problem3] - ✓ FIXED
...

## Common Pattern
[Description of the common issue found]

## Applied Fix Pattern
[General fix that works for this batch]

## Test Results
- Before: [X problems passing]
- After: [Y problems passing]
- Improvement: +[Y-X] problems

## Related Problems Not Yet Fixed
[Other problems with similar issues]

## Notes
[Lessons learned, patterns to watch for, etc.]
```

---

## Using These Templates

### For Individual Fixes
1. Copy the **Fix Record Template**
2. Fill in each section as you work on a problem
3. Save to `FIXES_LOG.md` or similar
4. Git commit with reference to fix record

### For Batch Fixes
1. Use **Batch Fix Summary Template**
2. Group similar problems and fixes
3. Document the common pattern
4. Makes it easier to apply fix to similar problems

### Benefits
- **Traceability:** Know why each problem was fixed
- **Learning:** Identify patterns across problems
- **Reference:** Find similar problems that need same fix
- **Efficiency:** Apply batch fixes to multiple problems
- **Communication:** Share findings with team

---

## Quick Reference: Error Types & Common Fixes

### SyntaxError
**Cause:** Malformed PG code
**Common Fixes:**
- Fix string escaping (use raw strings for LaTeX)
- Fix parentheses/brackets
- Fix operator syntax differences between Perl/Python

### NameError
**Cause:** Function or variable not defined
**Common Fixes:**
- Add missing macro to loadMacros()
- Define variable before use
- Check variable naming (case-sensitive)

### AttributeError
**Cause:** Object missing method or property
**Common Fixes:**
- Check object type is correct
- Look for renamed methods
- Verify initialization

### TypeError
**Cause:** Wrong type for operation
**Common Fixes:**
- Fix function argument types
- Convert between types as needed
- Fix list/array operations

### ImportError
**Cause:** Macro or module not found
**Common Fixes:**
- Check macro path in loadMacros()
- Verify macro file exists
- Check for circular dependencies

---

## Statistics to Track

As you fix problems, track these:

```
Date          Syntax  Name    Attr   Type   Import  Total  %Pass  Notes
2025-11-09    20      40      15     15     9       99     36.9%  Initial
2025-11-09    5       35      15     15     9       79     50.3%  After syntax fixes
2025-11-09    5       10      15     15     9       54     65.6%  After NameErrors
```

This shows progress and helps identify where most issues are.

---

## Next Steps

1. **Create FIXES_LOG.md** in project root
2. **Start with highest-impact error type** (SyntaxError has most problems)
3. **Document each fix** using this template
4. **Identify and document patterns** (most problems have similar issues)
5. **Apply batch fixes** to similar problems
6. **Track progress** with statistics

---

*Remember: Good documentation saves time when fixing similar problems later!*
