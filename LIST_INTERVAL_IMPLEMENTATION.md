# List and Interval MathObject Implementation

## Summary

Successfully implemented `List` and `Interval` MathObject classes to fix two previously broken tutorial problems: **SimpleFactoring.pg** and **DomainRange.pg**.

## What Was Implemented

### 1. List MathObject (`packages/pg_mathobjects/pg_mathobjects/list.py`)

A MathObject for handling comma-separated lists of values.

**Features:**
- Supports any MathObject types (Real, Formula, etc.)
- Automatic promotion of primitives to MathObjects
- Special `List("NONE")` for problems with no solutions
- Ordered and unordered comparison modes
- Answer checking with `ListAnswerChecker`

**Usage Examples:**
```python
# List of numbers (promoted to Real)
roots = List(1, 2, 3)

# List of Formulas
factors = List(Formula("x+1"), Formula("x-1"))

# Empty solution set
no_solutions = List("NONE")

# Answer checking
checker = roots.cmp(ordered=True, partialCredit=True)
```

### 2. Interval MathObject (`packages/pg_mathobjects/pg_mathobjects/interval.py`)

A MathObject for handling interval notation.

**Features:**
- Closed intervals: `[a, b]`
- Open intervals: `(a, b)`
- Half-open: `[a, b)`, `(a, b]`
- Infinite intervals: `(-inf, a]`, `[b, inf)`
- Set notation: `{a, b, c}`
- Unions: `(a, b) U [c, d]`
- LaTeX rendering with proper symbols
- Answer checking with `IntervalAnswerChecker`

**Usage Examples:**
```python
Context('Interval')

# Closed interval
i1 = Interval("[1, 5]")
i1.contains(3)  # True

# Infinite interval
i2 = Interval("[5, inf)")

# Union of intervals
i3 = Interval("(0, 1) U [2, 3]")

# Answer checking
checker = i1.cmp()
```

### 3. Answer Checkers (`packages/pg_mathobjects/pg_mathobjects/answer_checker.py`)

**ListAnswerChecker:**
- Supports ordered and unordered list comparison
- Partial credit option
- Length hint messages

**IntervalAnswerChecker:**
- Validates interval notation
- Checks semantic equivalence

### 4. Context Integration (`packages/pg_mathobjects/pg_mathobjects/compute.py`)

Modified `Compute()` function to detect context and return appropriate MathObject:

```python
# In Interval context, returns Interval
Context('Interval')
domain = Compute("[1, 5)")  # Returns Interval object

# In Inequalities context, returns Formula
Context('Inequalities-Only')
domain = Compute("x >= 5")  # Returns Formula object
```

### 5. Context Flags Fix (`packages/pg_mathobjects/pg_mathobjects/context.py`)

Fixed `ContextFlags.get()` to accept optional default parameter:
```python
def get(self, name: str, default: Any = None) -> Any:
    """Get flag value with optional default."""
    return self._flags.get(name, default)
```

### 6. Sandbox Integration (`packages/pg_translator/pg_translator/in_process_sandbox.py`)

Added `List` and `Interval` to the sandbox namespace so they're available during problem execution.

## Fixed Problems

### ✅ SimpleFactoring.pg
**Before:** `NameError: name 'List' is not defined`
**After:** Works correctly! Uses `List` for factors and roots.

**Problem structure:**
```perl
$factors = List($factor1, $factor2);
$roots   = List($x0, $x1);
```

### ✅ DomainRange.pg
**Before:** `ValueError: Error parsing formula '[5.22..., inf)'`
**After:** Works correctly! Uses `Interval` for interval notation.

**Problem structure:**
```perl
Context('Interval')
$domain_interval = Compute("[$a, inf)");
$range_interval  = Compute('[0, inf)');
```

## Test Results

### Comprehensive Tests (test_list_interval.py)
```
✅ TEST 1: SimpleFactoring (List MathObject) - PASSED
✅ TEST 2: DomainRange (Interval MathObject) - PASSED
✅ TEST 3: List Class Functionality - PASSED
✅ TEST 4: Interval Class Functionality - PASSED
✅ TEST 5: Compute() with Interval Context - PASSED
```

### Preprocessor Tests (test_preprocessor_pygment.py)
```
✅ test_pygment_preprocess_text_block - PASSED
✅ test_pygment_preprocess_pgml_blocks - PASSED
✅ test_pygment_preprocess_without_lark - PASSED
```

## Files Modified

1. **Created:**
   - `packages/pg_mathobjects/pg_mathobjects/list.py` (159 lines)
   - `packages/pg_mathobjects/pg_mathobjects/interval.py` (289 lines)

2. **Modified:**
   - `packages/pg_mathobjects/pg_mathobjects/__init__.py` - Added exports
   - `packages/pg_mathobjects/pg_mathobjects/answer_checker.py` - Added checkers
   - `packages/pg_mathobjects/pg_mathobjects/compute.py` - Added context detection
   - `packages/pg_mathobjects/pg_mathobjects/context.py` - Fixed `get()` method
   - `packages/pg_translator/pg_translator/in_process_sandbox.py` - Added to namespace
   - `packages/pg_translator/tests/test_preprocessor_pygment.py` - Updated tests

## API Reference

### List

```python
List(*items, context=None)

# Methods
len(list)              # Number of items
list[i]                # Get item by index
for item in list       # Iterate
list.cmp(**options)    # Get answer checker

# Options for cmp()
ordered=True           # Whether order matters
partialCredit=False    # Give partial credit
showLengthHints=True   # Show length hints
```

### Interval

```python
Interval(interval_str, context=None)

# Methods
interval.contains(x)      # Check if x is in interval
interval.cmp(**options)   # Get answer checker
str(interval)             # String representation
interval.TeX()            # LaTeX representation

# Supported notation
"[a, b]"      # Closed
"(a, b)"      # Open
"[a, b)"      # Half-open
"(-inf, b]"   # Left-infinite
"[a, inf)"    # Right-infinite
"{a, b, c}"   # Set (discrete points)
"(a,b) U [c,d]"  # Union
```

### Context Usage

```python
# For Lists (in any context)
from pg_mathobjects import List
lst = List(1, 2, 3)

# For Intervals (use Interval context)
from pg_mathobjects import Context, Compute
Context('Interval')
interval = Compute("[1, 5)")  # Returns Interval

# For Inequalities (use Inequalities context)
Context('Inequalities-Only')
ineq = Compute("x >= 5")  # Returns Formula
```

## Integration with Existing Code

The implementation follows WeBWorK MathObject patterns:
- Inherits from `Value` base class
- Implements `cmp()` method returning answer checker
- Context-aware through `Context()` system
- Works with PGML answer blanks `[_]{$answer}`

## Next Steps (Future Enhancements)

1. **Inequality MathObject** - Dedicated class for inequality notation
2. **Set Operations** - Union, intersection, complement
3. **Interval Arithmetic** - Add/subtract intervals
4. **Enhanced Validation** - Better error messages for malformed input
5. **Performance** - Optimize interval parsing for complex unions

## Compatibility

- ✅ Works with existing Formula and Real MathObjects
- ✅ Compatible with PGML rendering
- ✅ Integrates with answer checking system
- ✅ Supports context switching
- ✅ Follows WeBWorK conventions

## Status: Complete and Tested ✅

Both `List` and `Interval` MathObjects are fully implemented, tested, and integrated into the pg_translator system. All previously broken problems using these types now render correctly.
