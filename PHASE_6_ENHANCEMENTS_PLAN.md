# Phase 6: Grammar Enhancements Implementation Plan

## Overview

This document outlines the plan to address the three remaining gaps in the grammar-based preprocessor and implement future enhancements.

## Current State (from test results)

- **Zero failures** on 20 real PG files ✅
- **100% success rate** on functionality tests ✅
- **97% parity** with regex preprocessor ✅
- **Remaining gaps:** 3 known limitations

## Identified Gaps

### 1. Complex Multi-line Blocks
**Status:** Fall back to existing regex logic
**Priority:** HIGH
**Example:**
```perl
if ($x > 0) {
    $y = 1;
    $z = 2;
} elsif ($x < 0) {
    $y = -1;
} else {
    $y = 0;
}
```

### 2. Closure Handling
**Status:** Perl `sub { }` use regex detection
**Priority:** MEDIUM
**Example:**
```perl
checker => sub {
    my ($correct, $student) = @_;
    return $correct == $student;
}
```

### 3. Context-Sensitive Fat Comma
**Status:** Could be more sophisticated
**Priority:** MEDIUM
**Example:**
```perl
%hash = (key => 'value')  # Dict context: key: 'value'
func(key => 'value')      # Args context: key='value'
```

## Implementation Plan

---

## Phase 6.1: Perl Closures (Weeks 1-2)

### Grammar Extensions

Add support for anonymous subroutines and named subroutines:

```lark
// Add to statements
stmt: ...
    | sub_decl

// Subroutine declarations
sub_decl: "sub" NAME? block                -> sub_decl

// Add to expressions (for closures in args)
?primary: ...
        | "sub" block                      -> closure_expr
```

### IR Nodes

```python
# New IR node types:
("sub_decl", name_or_none, block)     # Named/anonymous sub
("closure", block)                     # Closure expression
```

### Code Generation

```python
if typ == "sub_decl":
    _, name, block = ir
    if name:
        return f"def {name}():{self._emit_block(block)}"
    else:
        return f"lambda: {self._emit_closure_body(block)}"
```

### Test Coverage

- Named subroutines: `sub checker { ... }`
- Anonymous closures: `sub { ... }`
- Closures in arguments: `checker => sub { ... }`
- Closures with parameters: `sub { my ($x, $y) = @_; ... }`

---

## Phase 6.2: Hash & Array Literals (Week 3)

### Grammar Extensions

```lark
// Hash literals
hash_literal: "{" hash_pairs? "}"           -> hash_literal
hash_pairs: hash_pair ("," hash_pair)*
hash_pair: expr "=>" expr                   -> hash_pair

// Array literals
array_literal: "[" array_items? "]"         -> array_literal
array_items: expr ("," expr)*
```

### Context-Aware Fat Comma

Detect context based on surrounding construct:
- Inside `{ }` after assignment → Hash literal
- Inside `( )` for function args → Named argument
- Default → Assignment operator

### Code Generation

```python
if typ == "hash_literal":
    pairs = [f"{k}: {v}" for k, v in items]
    return "{" + ", ".join(pairs) + "}"

if typ == "hash_pair":
    # In hash context: "key": value
    # In args context: key=value
    ...
```

---

## Phase 6.3: Better Error Messages (Week 4)

### Error Formatting

```python
def _format_parse_error(self, code, error):
    """Format helpful error message with context."""
    line_no = error.line
    col_no = error.column

    # Show error location
    lines = code.split('\n')
    error_line = lines[line_no-1]
    pointer = ' ' * (col_no-1) + '^'

    return f"""
Parse error at line {line_no}, column {col_no}:
  {error_line}
  {pointer}
{error.message}

Suggestion: {self._suggest_fix(error)}
Falling back to Pygments rewriting.
"""
```

### Error Recovery

- Attempt to parse remaining code
- Provide suggestions based on error type
- Log detailed error for debugging
- Gracefully fall back to Pygments

---

## Phase 6.4: Type Inference (Weeks 5-6)

### Type Tracking

```python
class TypeTracker:
    def __init__(self):
        self.types = {}  # var_name -> inferred_type

    def track_assignment(self, var_name, expr_ir):
        """Track variable type from assignment."""
        expr_type = self._infer_type(expr_ir)
        self.types[var_name] = expr_type

    def _infer_type(self, expr_ir):
        """Infer type from expression IR."""
        if expr_ir[0] == "hash_literal":
            return "dict"
        elif expr_ir[0] == "array_literal":
            return "list"
        elif expr_ir[0] == "call":
            return self._infer_function_return(expr_ir[1])
        return "unknown"
```

### Type-Aware Transformations

Use type information to:
- Optimize operator selection
- Insert appropriate conversions
- Detect type errors early
- Generate better Python code

Example:
```python
# If we know $x is a MathObject:
$x->eval(...)  →  x.eval(...)  # Direct method call

# If we know $arr is an array:
$arr[0]  →  arr[0]  # Direct indexing

# If we know %hash is a hash:
$hash{key}  →  hash['key']  # Direct access
```

---

## Implementation Timeline

| Week | Task | Deliverable |
|------|------|-------------|
| 1-2  | Closure support | Grammar + IR + codegen |
| 3    | Hash/array literals | Context-aware fat comma |
| 4    | Error messages | Helpful errors + recovery |
| 5-6  | Type inference | Type tracking + optimization |
| 7    | Integration testing | Run on 157 PG files |
| 8    | Documentation | Update docs + migration guide |

---

## Success Metrics

### Coverage
- ✅ 100% parity with regex preprocessor
- ✅ All 157 tutorial files process successfully
- ✅ Zero functional regressions

### Quality
- ✅ Helpful error messages with context
- ✅ 90%+ type inference accuracy
- ✅ Cleaner output than regex approach

### Performance
- ✅ ≤2x regex preprocessor time
- ✅ No memory regressions
- ✅ Acceptable parsing overhead

---

## Risk Management

### High-Risk Items

1. **Closure complexity**
   - Risk: May require significant grammar changes
   - Mitigation: Start simple, iterate incrementally

2. **Type inference accuracy**
   - Risk: False positives cause errors
   - Mitigation: Conservative inference, make optional

3. **Performance regression**
   - Risk: Grammar parsing too slow
   - Mitigation: Profile and optimize, add caching

### Contingency Plans

- If closures too complex → Keep regex fallback for edge cases
- If type inference unstable → Make it opt-in feature
- If performance issues → Implement selective parsing

---

## Testing Strategy

### Unit Tests
- Each grammar rule tested in isolation
- Each transformer method tested
- Each code generation path tested

### Integration Tests
- All 157 tutorial PG files
- Compare outputs with regex preprocessor
- Measure performance differences

### Regression Tests
- Ensure no existing features break
- Track new failures
- Monitor output quality

---

## Deliverables

1. **Code**
   - Enhanced grammar in pg_preprocessor_pygment.py
   - New transformer methods
   - Updated code generation
   - Type inference system

2. **Tests**
   - Unit tests for new features
   - Integration tests on PG files
   - Performance benchmarks

3. **Documentation**
   - Updated GRAMMAR_MIGRATION_PLAN.md
   - Phase 6 completion summary
   - User migration guide
   - Grammar reference

---

## Conclusion

This plan systematically addresses all remaining gaps:

1. ✅ **Closures** → Full Perl sub support
2. ✅ **Hash/Array literals** → Context-aware fat comma
3. ✅ **Error messages** → Helpful feedback + recovery
4. ✅ **Type inference** → Smarter transformations

**Timeline:** 8 weeks
**Outcome:** 100% parity + better quality than regex approach
**Status:** Ready to implement
