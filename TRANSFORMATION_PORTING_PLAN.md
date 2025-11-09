# Transformation Porting Plan

## Objective

Port all missing transformations from [preprocessor.py](d:\pg\packages\pg_translator\pg_translator\preprocessor.py) (lines 840-1494, ~655 lines) to the grammar-based [pg_preprocessor_pygment.py](d:\pg\packages\pg_translator\pg_translator\pg_preprocessor_pygment.py).

**Status:** CRITICAL - Required for production readiness
**Timeline:** 3-4 weeks
**Priority:** HIGH

---

## Phase 1: Critical Transformations (Week 1)

### 1.1: AnswerHints Tuple Wrapping

**Source:** preprocessor.py lines 1074-1148 (74 lines)
**Priority:** CRITICAL
**Complexity:** MEDIUM

**What it does:**
```python
# Detect and wrap [ arr1 ], [ arr2 ] patterns in AnswerHints calls
# Input:  AnswerHints( Formula(...) => "msg", [ arr1 ], [ arr2 ] )
# Output: AnswerHints( Formula(...) => "msg", ([ arr1 ], [ arr2 ]) )
```

**Implementation location:** Pygments fallback `_rewrite_with_pygments()` method

**Test files needed:**
- Find PG files using AnswerHints with array pairs
- Create unit tests for pattern detection

### 1.2: Method Call Auto-Parenthesizing

**Source:** preprocessor.py lines 1050-1072 (22 lines)
**Priority:** CRITICAL
**Complexity:** LOW

**What it does:**
```python
# Add () to zero-arg method calls
# $obj->method    →    obj.method()
# $f->eval        →    f.eval()

# But not if already has parens:
# $obj->method()  →    obj.method()
```

**Implementation location:** Post-processing in `_rewrite_with_pygments()` or grammar method call handler

**Test cases:**
```python
test_cases = [
    ("$obj->method", "obj.method()"),
    ("$obj->method()", "obj.method()"),  # Don't double-add
    ("$obj->method($arg)", "obj.method(arg)"),  # Has args, don't change
]
```

---

## Phase 2: Important Transformations (Week 2)

### 2.1: Complex Ternary Handling

**Source:** preprocessor.py lines 1244-1333 (89 lines)
**Priority:** HIGH
**Complexity:** HIGH

**What it does:**
- Distinguish ternary colon from dict colon
- Handle nested ternaries
- Multi-line ternary expressions
- Python ternary detection to avoid double-conversion

**Current status:** Basic grammar support exists, needs enhancement

**Implementation approach:**
1. Enhance grammar ternary rule for nested cases
2. Add disambiguation logic for dict vs ternary colons
3. Port edge case handling from preprocessor.py

### 2.2: Complex Map/Grep Blocks

**Source:** preprocessor.py lines 1384-1480 (96 lines)
**Priority:** HIGH
**Complexity:** MEDIUM

**What it does:**
```perl
# Multi-line map blocks
map {
    my $x = $_;
    process($x);
    return $x * 2;
} @array

# Map with fat comma in args
map { $_ => value($#_) } @array

# Grep with complex conditions
grep { $_ > 5 && $_ < 10 } @array
```

**Current status:** Basic `map { expr } list` in grammar

**Implementation approach:**
1. Enhance grammar map/grep rules for multi-line blocks
2. Add support for block statements (not just expressions)
3. Port complex transformation logic

### 2.3: Enhanced For Loop Handling

**Source:** preprocessor.py lines 1150-1242 (92 lines)
**Priority:** MEDIUM
**Complexity:** MEDIUM

**What it does:**
```perl
# Multi-line for blocks (already mostly supported)
for my $i (1..10) {
    $sum = $sum + $i;
    print $i;
}

# C-style for loops (NOT currently supported)
for (my $i = 0; $i < 10; $i++) {
    print $i;
}

# Hash iteration
for my $key (keys %hash) {
    ...
}
```

**Implementation approach:**
1. Add C-style for loop grammar rule
2. Add hash iteration support
3. Port edge case handling

---

## Phase 3: Moderate Priority (Week 3)

### 3.1: Enhanced Statement Modifiers

**Source:** preprocessor.py lines 1335-1383 (48 lines)
**Priority:** MEDIUM
**Complexity:** LOW

**What it does:**
- Distinguish Perl statement modifiers from Python ternary
- Handle edge cases

**Current status:** Basic grammar support

**Implementation approach:**
- Port disambiguation logic from preprocessor.py
- Add tests for edge cases

### 3.2: Array/Hash Slicing

**Priority:** MEDIUM
**Complexity:** MEDIUM

**What it does:**
```perl
@arr[1..5]           →    arr[1:6]
@arr[1, 3, 5]        →    [arr[1], arr[3], arr[5]]
@hash{'a','b','c'}   →    [hash['a'], hash['b'], hash['c']]
```

**Implementation approach:**
1. Add grammar rule for slice syntax
2. Transform to Python slice notation
3. Handle list-of-indices case

---

## Phase 4: Lower Priority (Week 4)

### 4.1: Smart Match Operator (~~)

**Priority:** LOW
**Complexity:** LOW

```perl
$x ~~ @array    →    x in array
```

### 4.2: Heredoc Handling

**Priority:** LOW
**Complexity:** MEDIUM

```perl
my $text = <<'END';
Multi-line text
END
```

### 4.3: Other Missing Transformations

- Review preprocessor.py lines 840-1494 completely
- Identify any other missing transformations
- Port as needed

---

## Implementation Strategy

### For Each Transformation:

1. **Extract Logic**
   - Copy relevant code from preprocessor.py
   - Understand what it does
   - Document input/output examples

2. **Choose Implementation Location**
   - **Grammar:** If it's a syntactic construct that can be parsed
   - **Transformer:** If it needs IR manipulation
   - **Pygments Fallback:** If it's a token-level rewrite

3. **Implement**
   - Add to appropriate location
   - Maintain existing functionality
   - Add inline documentation

4. **Test**
   - Create unit tests
   - Find real PG files using the feature
   - Verify against preprocessor.py output

5. **Document**
   - Update GRAMMAR_FEATURE_REFERENCE.md
   - Add examples
   - Note any limitations

---

## Testing Strategy

### Unit Tests

For each transformation, create tests in `test_missing_transformations.py`:

```python
def test_answerhints_wrapping():
    code = "AnswerHints( Formula(...) => 'msg', [ arr1 ], [ arr2 ] )"
    expected = "AnswerHints( Formula(...) => 'msg', ([ arr1 ], [ arr2 ]) )"
    result = preprocessor.preprocess(code)
    assert expected in result.code

def test_method_auto_parens():
    code = "$obj->method"
    expected = "obj.method()"
    result = preprocessor.preprocess(code)
    assert expected in result.code
```

### Integration Tests

1. Find PG files using each transformation
2. Compare output with preprocessor.py
3. Ensure functional equivalence

### Regression Tests

- Ensure existing tests still pass
- No regressions in already-working features

---

## Success Criteria

### Phase 1 (Week 1)
- ✅ AnswerHints wrapping implemented and tested
- ✅ Method auto-parenthesizing implemented and tested
- ✅ Tests created and passing
- ✅ Documentation updated

### Phase 2 (Week 2)
- ✅ Complex ternary handling enhanced
- ✅ Complex map/grep blocks supported
- ✅ Enhanced for loops implemented
- ✅ Tests passing on real PG files

### Phase 3 (Week 3)
- ✅ Statement modifiers enhanced
- ✅ Array/hash slicing implemented
- ✅ All transformations tested

### Phase 4 (Week 4)
- ✅ Remaining transformations ported
- ✅ Full audit complete
- ✅ Documentation complete

### Final (Week 5+)
- ✅ Test on all 157 PG files
- ✅ Compare with preprocessor.py on full corpus
- ✅ Achieve 95%+ parity
- ✅ Document any intentional differences

---

## Risk Mitigation

### Risk 1: Transformations are interdependent

**Mitigation:** Port in dependency order, test incrementally

### Risk 2: Grammar can't handle some constructs

**Mitigation:** Use Pygments fallback for those cases

### Risk 3: Breaking existing functionality

**Mitigation:** Run regression tests after each change

### Risk 4: Hidden transformations

**Mitigation:** Do complete audit of preprocessor.py lines 840-1494

---

## Timeline

| Week | Tasks | Deliverable |
|------|-------|-------------|
| 1 | Phase 1: Critical transforms | AnswerHints + method parens working |
| 2 | Phase 2: Important transforms | Complex ternary/map/grep/for |
| 3 | Phase 3: Moderate priority | Statement modifiers, slicing |
| 4 | Phase 4: Audit & remaining | All transforms ported |
| 5+ | Testing & validation | 95%+ parity achieved |

---

## Conclusion

**Current State:** Grammar preprocessor has good foundation but is missing ~655 lines of critical transformations

**Required Work:** 3-4 weeks to port all missing transformations

**Outcome:** True production-ready replacement for regex preprocessor

**Priority:** HIGH - Required before any production deployment

---

**Document Version:** 1.0
**Date:** 2025-11-09
**Status:** IMPLEMENTATION PLAN
**Author:** Claude Code
