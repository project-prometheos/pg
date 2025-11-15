# Implement Perl Sub Closure Translation

## Overview

Extend the existing Lark-based preprocessor to properly translate Perl `sub { ... }` closures to Python functions/lambdas instead of stubbing them as `lambda *args, **kwargs: None`. This will enable:

1. MultiAnswer checker functions to work correctly
2. All other Perl closures in PG code to be properly translated
3. Maintain consistency with the existing Lark-based translation system

## Implementation Tasks

### 1. Extend Lark Grammar for Sub Closures

**File**: `packages/pg/translator/pg_preprocessor_pygment.py`

- Add `sub_expr` rule to the grammar to parse `sub { ... }` closures
- Handle both inline and multi-line closures
- Support closures in different contexts:
  - Parameter: `checker => sub { ... }`
  - Assignment: `$var = sub { ... }`
  - Standalone: `sub name { ... }`
- Grammar should capture:
  - Parameter list: `my ($a, $b) = @_;`
  - Variable declarations: `my $var;`
  - Statements: assignments, conditionals, returns
  - Array dereferencing: `@$array` → `list(array)`
  - Method calls: `$self->method()` → `self.method()`
  - Comparisons: `$obj == $other` → `obj.compare(other)` or `obj == other`
  - Returns: `return [1, 2]` → `return [1, 2]`

### 2. Implement Sub Closure Transformer

**File**: `packages/pg/translator/pg_preprocessor_pygment.py`

- Add transformer methods for sub closure AST nodes
- Translate Perl constructs to Python:
  - `my ($a, $b) = @_;` → `a, b = args` (or `a, b = args[0], args[1]` for specific positions)
  - `@$array` → `list(array)` or `array` (if already a list)
  - `$obj == $other` → `obj.compare(other)` (for MathObjects) or `obj == other`
  - `-$obj` → `-obj` (if obj supports negation)
  - `$self->method()` → `self.method()`
  - `return [1, 2]` → `return [1, 2]`
  - Perl conditionals → Python conditionals
  - Perl logical operators (`||`, `&&`) → Python (`or`, `and`)
- Generate Python function/lambda from translated body
- Handle variable scoping (Perl `my` → Python local variables)

### 3. Update Preprocessor Closure Detection

**File**: `packages/pg/translator/pg_preprocessor_pygment.py`

- Modify the closure detection logic (around line 429) to use Lark parsing instead of regex stubbing
- When `sub { ... }` is detected:

  1. Extract the closure body
  2. Parse with Lark grammar
  3. Transform to Python using the new transformer
  4. Generate Python function/lambda

- Remove the current stubbing code that replaces closures with `lambda *args, **kwargs: None`

### 4. Handle Special Cases

**File**: `packages/pg/translator/pg_preprocessor_pygment.py`

- **Array dereferencing**: `@$student` in checker context
  - If `student` is a list/tuple, use as-is
  - If `student` is a single value, wrap in list
  - Translate: `my ($f1stu, $f2stu) = @$student;` → `f1stu, f2stu = list(student)`

- **MathObject comparisons**: `$f1 == $f1stu`
  - Detect if operands are MathObjects (Formula, Real, etc.)
  - Use `.compare()` method for MathObjects, `==` for primitives
  - Translate: `$f1 == $f1stu` → `f1.compare(f1stu)` or `f1 == f1stu`

- **Negation**: `-$f1`
  - Check if object supports negation
  - Translate: `-$f1` → `-f1` (if Formula/Real supports `__neg__`)

- **Method calls**: `$self->setMessage(1, "msg")`
  - Translate: `$self->method(args)` → `self.method(args)`
  - Handle MultiAnswer methods: `setMessage`, etc.

- **Return values**: `return [1, 1]`
  - Preserve list returns for MultiAnswer checkers
  - Translate: `return [1, 1]` → `return [1, 1]`

### 5. Integration with MultiAnswer

**File**: `packages/pg/macros/parsers/parser_multianswer.py`

- Ensure translated checker functions work with MultiAnswer
- Verify checker signature: `(correct, student, self) → [score1, score2, ...]`
- Test that translated functions return proper score lists

### 6. Testing

- Test MultiAnswer checker translation with `Algebra/AlgebraicFractionAnswer.pg`
- Test other problems with custom checkers
- Verify no regressions in existing functionality
- Test edge cases:
  - Nested closures
  - Complex conditionals
  - Multiple return statements
  - Variable scoping

## Reference Implementation

**Perl Checker Example** (tutorial/sample-problems/Algebra/AlgebraicFractionAnswer.pg:69-98):

```perl
checker => sub {
    my ($correct, $student, $self) = @_;
    my ($f1stu, $f2stu) = @$student;
    my ($f1,    $f2)    = @$correct;
    
    if (($f1 == $f1stu && $f2 == $f2stu)
        || (-$f1 == $f1stu && -$f2 == $f2stu))
    {
        return [ 1, 1 ];
    }
    # ... more logic
}
```

**Expected Python Translation**:

```python
checker=lambda correct, student, self: (
    (lambda: (
        f1stu, f2stu = list(student),
        f1, f2 = list(correct),
        [1, 1] if ((f1.compare(f1stu) and f2.compare(f2stu)) or 
                   ((-f1).compare(f1stu) and (-f2).compare(f2stu)))
        else [1, 0] if (f1.compare(f1stu) or (-f1).compare(f1stu))
        else [0, 0]
    ))()
)
```

Or as a proper function:

```python
def checker(correct, student, self):
    f1stu, f2stu = list(student)
    f1, f2 = list(correct)
    if (f1.compare(f1stu) and f2.compare(f2stu)) or \
       ((-f1).compare(f1stu) and (-f2).compare(f2stu)):
        return [1, 1]
    elif f1.compare(f1stu) or (-f1).compare(f1stu):
        return [1, 0]
    else:
        return [0, 0]
```

## Implementation Strategy

1. **Phase 1**: Extend grammar to parse `sub { ... }` closures
2. **Phase 2**: Implement basic transformer for common patterns
3. **Phase 3**: Add MathObject-aware comparison translation
4. **Phase 4**: Handle array dereferencing and method calls
5. **Phase 5**: Test with MultiAnswer problems
6. **Phase 6**: Expand to handle all edge cases

## Files to Modify

- `packages/pg/translator/pg_preprocessor_pygment.py`:
  - Extend `_grammar()` method to include `sub_expr` rule
  - Add transformer methods in `_make_transformer()` for sub closures
  - Update closure detection logic to use Lark parsing
  - Remove stubbing code

## Dependencies

- No new dependencies required (uses existing Lark)
- May need to extend Lark grammar incrementally as edge cases are discovered