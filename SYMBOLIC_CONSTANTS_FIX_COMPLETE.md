# Symbolic Constants Fix Complete

## Problem
PS1 Problem 25 asks for `arccos(-1)` which equals `π`, but only numeric values like `3.1415` were accepted. Symbolic answers like `pi`, `Pi`, or `π` were rejected with "Invalid number format".

## Root Cause
The `RealAnswerChecker` in `pg_mathobjects` was only trying to parse student answers as floats using `float(student_answer)`. This failed for symbolic constants like `pi` which need to be evaluated through a formula parser first.

## Solution

**File**: `packages/pg_mathobjects/pg_mathobjects/answer_checker.py`

Modified the `RealAnswerChecker.check()` method to:

1. **Normalize common variations**: Replace unicode `π` → `pi`, uppercase `Pi` → `pi`
2. **Try simple float parsing first**: For purely numeric answers
3. **Fall back to formula parsing**: Parse as Formula (which handles constants like `pi`, `e`) and evaluate to numeric value

### Code Changes

```python
def check(self, student_answer: str) -> Dict[str, Any]:
    """Check if student answer matches correct Real number."""
    from .real import Real
    from .formula import Formula

    try:
        # Normalize common constant representations
        normalized = student_answer.replace('π', 'pi').replace('Pi', 'pi')
        
        # First try to parse as a simple float
        try:
            student_value = float(normalized)
            student_real = Real(student_value, self.correct_value.context)
        except ValueError:
            # If that fails, try parsing as a formula (handles pi, e, etc.)
            formula = Formula(normalized, self.correct_value.context)
            import sympy as sp
            student_value = float(formula._tree.evalf())
            student_real = Real(student_value, self.correct_value.context)

        # Compare with tolerance
        if student_real == self.correct_value:
            return {'score': 1.0, 'correct': True}
        else:
            return {'score': 0.0, 'correct': False}

    except (ValueError, TypeError) as e:
        return {
            'score': 0.0,
            'correct': False,
            'message': 'Invalid number format'
        }
```

## Test Results

### Problem 25: arccos(-1) = π

All forms now accepted:
```
✅ pi              (lowercase, sympy native)
✅ Pi              (uppercase, normalized to pi)
✅ π               (unicode symbol, normalized to pi)
✅ 3.14159         (numeric approximation)
✅ 3.141592653589793 (high precision)
```

### Expression Support

Simple expressions also work:
```
✅ 2*pi/2          (arithmetic with pi)
✅ pi*1            (multiplication)
✅ pi/2            (division)
```

### Not Supported (as expected)

Trigonometric functions in answers are not supported:
```
❌ arccos(-1)      (trig functions not in formula parser)
❌ 2*arcsin(1)     (same)
```

This is acceptable since the problem explicitly states "Svaret får inte innehålla trigonometriska funktioner" (The answer may not contain trigonometric functions).

## Impact

This fix enables students to enter symbolic mathematical constants in numeric answer contexts:
- **π (pi)**: All variants (pi, Pi, π)
- **e**: Euler's constant
- **Expressions**: `2*pi`, `pi/2`, `e^2`, etc.

The fix maintains backward compatibility - purely numeric answers still work exactly as before.

## Files Modified

1. `packages/pg_mathobjects/pg_mathobjects/answer_checker.py` - RealAnswerChecker.check()

## Status: ✅ COMPLETE

Students can now answer symbolic questions using `pi`, `Pi`, or `π` symbols, and they will be correctly evaluated and compared against the expected numeric value.
