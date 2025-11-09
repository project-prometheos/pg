# pypg.py vs pg_solve.py - Quick Reference

## TL;DR

**pypg.py**: Simple, fast, but **ignores Perl syntax** → may render **incorrectly**  
**pg_solve.py**: Complex, slower, but **translates Perl** → more **accurate**

---

## The One Key Difference

```
pypg.py:    Perl code → ❌ ignored → wrong output, no error
pg_solve.py: Perl code → 🔄 translated → correct output or syntax error
```

---

## Example: Why They Differ

**Problem with Perl code:**
```perl
do { $b = random(2, 9) } until $b != $a;
```

**pypg.py behavior:**
- Doesn't understand `do-until`
- Ignores it or fails silently
- Result: `$b` stays as `$b` (not expanded)
- **Output**: `(-1 x^($b) + $b)/x` ❌ WRONG

**pg_solve.py behavior:**
- Translates to Python: `while True: b = random(2, 9); if b != a: break`
- Executes correctly
- Result: `$b = 9` (actual value)
- **Output**: `(9 - x**9)/x` ✅ CORRECT

---

## Package Architecture

### pypg.py → pg_renderer
```
Simple regex parser
   ↓
Direct Python eval()
   ↓
PGML to HTML
   ↓
Output
```
**Dependencies**: sympy only

### pg_solve.py → pg_translator
```
Pygments+Lark parser (Perl→Python)
   ↓
RestrictedPython sandbox
   ↓
Macro loader + pg_math
   ↓
PGML renderer
   ↓
Output
```
**Dependencies**: pg_parser, pg_math, pg_answer, pg_pgml, RestrictedPython, Pygments, Lark

---

## When Each Gets Errors

### pypg.py
**Syntax errors**: Rare (ignores unsupported code)  
**Runtime errors**: When Perl-isms leak through  
**Incorrect output**: Common (variables not expanded)

### pg_solve.py
**Syntax errors**: When Perl translation fails:
- Complex string concatenation (`. operator`)
- Array slicing
- Hash operations with `{}`
- Nested do-until loops

**Runtime errors**: When translated code is invalid  
**Incorrect output**: Rare (either works or errors)

---

## Comparison Matrix

| What | pypg.py | pg_solve.py |
|------|---------|------------|
| **Speed** | Fast | Slower |
| **Correctness** | ⚠️ May be wrong | ✅ Accurate |
| **Perl do-until** | ❌ No | ✅ Yes |
| **Variable expansion** | ⚠️ Basic | ✅ Full |
| **Syntax errors** | Rare | Possible |
| **Dependencies** | 1 package | 5+ packages |
| **LOC** | ~1K | ~10K |

---

## Which Should You Use?

### Use pypg.py if:
- Testing simple Python-style problems
- Need fast iteration
- Don't care about Perl features

### Use pg_solve.py if:
- Working with real WeBWorK problems (Perl-based)
- Need accurate rendering
- Production use
- **This is the recommended default**

---

## Real Test Results

### Test: `FormulaAnswer.pg`
Problem contains: `do { $b = random(2, 9) } until $b != $a;`

**pypg.py output:**
```
Enter $$(-1 x^($b) + $b)/x$$: [____]
```
Status: ⚠️ Renders but **WRONG** ($b not expanded)

**pg_solve.py output:**
```
Enter (9 - x**9)/x : ___
```
Status: ✅ **CORRECT** (loop executed, variable expanded)

---

## Summary

**pypg.py** is like Google Translate: fast but may miss nuances  
**pg_solve.py** is like a professional translator: slower but accurate

For production: **Use pg_solve.py**

