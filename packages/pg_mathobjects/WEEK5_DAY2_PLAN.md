# Week 5 Day 2: LimitedPolynomial Context - Plan

**Goal**: Create a context that restricts formulas to polynomial form

## Research Summary

From `contextLimitedPolynomial.pl`:

### What It Does
- Restricts student input to polynomial expressions only
- Rejects: functions (sin, cos, ln), complex operations, absolute values
- Allows: addition, subtraction, multiplication, division by constants, integer powers
- Has "strict" mode that disallows operations in coefficients

### Key Restrictions
1. **No functions**: sin, cos, tan, ln, log, sqrt, etc. (except on constants)
2. **No division by variables**: Can divide by numbers only
3. **Integer powers only**: x^2 is OK, x^2.5 is not
4. **Simplified form**: Optional "singlePowers" flag (one term per degree)

### Use Cases
- Polynomial expansion problems: Factor and expand
- Algebraic manipulation: Simplify to standard form
- Restrict student format: Force expanded form

## Simplified Python Approach

Instead of reimplementing the complex Perl operator checking system, we can:

1. **Parse first with regular context**
2. **Validate the parsed tree** for polynomial form
3. **Check sympy expression properties**

### Validation Strategy

```python
def is_polynomial_expression(expr, variables, strict=False):
    """Check if sympy expression is polynomial form."""
    
    # Check 1: Is it a polynomial in the given variables?
    for var in variables:
        if not expr.is_polynomial(var):
            return False, f"Not polynomial in {var}"
    
    # Check 2: No non-polynomial functions
    for func in expr.atoms(sp.Function):
        if not is_allowed_function(func, strict):
            return False, f"Function {func.func} not allowed"
    
    # Check 3: All powers are non-negative integers
    for pow_expr in expr.atoms(sp.Pow):
        base, exp = pow_expr.as_base_exp()
        if base in variables:
            if not (exp.is_Integer and exp >= 0):
                return False, f"Exponent must be non-negative integer"
    
    return True, None
```

## Implementation Plan

### Phase 1: Core Class (1 hour)

**File**: `pg_mathobjects/limited_polynomial_context.py`

```python
class LimitedPolynomialContext(Context):
    """Context for polynomial expressions only."""
    
    def __init__(self, strict=False, single_powers=False):
        super().__init__('Numeric')
        self.name = 'LimitedPolynomial' + ('-Strict' if strict else '')
        self.flags.set('strictCoefficients', strict)
        self.flags.set('singlePowers', single_powers)
        
        # Configure parser to validate polynomial form
        self._polynomial_validator = PolynomialValidator(strict, single_powers)
```

### Phase 2: Validation (1 hour)

**Class**: `PolynomialValidator`

Methods:
- `validate(formula)` - Main validation entry point
- `is_polynomial_tree(tree)` - Check sympy expression
- `check_operations(tree)` - Verify allowed operations only
- `check_powers(tree)` - Verify integer powers
- `check_single_powers(tree)` - Optional: one term per degree

### Phase 3: Formula Integration (30 min)

Override Formula parsing to validate:

```python
class LimitedPolynomialFormula(Formula):
    """Formula that validates polynomial form."""
    
    def __init__(self, expr, context):
        super().__init__(expr, context)
        
        # Validate after parsing
        validator = context._polynomial_validator
        is_valid, error = validator.validate(self)
        if not is_valid:
            raise ValueError(f"Not a polynomial: {error}")
```

### Phase 4: Testing (1.5 hours)

**File**: `tests/test_limited_polynomial.py`

Test categories:
1. **Accept Valid** (5 tests)
   - Simple: `x^2 + 2*x + 1`
   - Multiple vars: `x^2 + y^2`
   - Constants: `3*x + 5`
   - Powers: `x^3 - 2*x^2 + x - 1`
   - Division by constant: `x^2/2 + x/3`

2. **Reject Invalid** (5 tests)
   - Functions: `sin(x)`
   - Non-integer power: `x^0.5` or `sqrt(x)`
   - Division by variable: `1/x`
   - Absolute value: `abs(x)`
   - Complex operations: `e^x`

3. **Strict Mode** (3 tests)
   - Reject operations in coefficients: `(2+3)*x` 
   - Accept simple coefficients: `5*x`
   - Reject nested operations: `x^(1+1)`

4. **Single Powers** (2 tests)
   - Reject multiple terms: `x^2 + 2*x^2`
   - Accept distinct degrees: `x^2 + x`

## Simplified Scope for Day 2

To keep within 3-4 hours, we'll implement:

✅ **Must Have**:
- LimitedPolynomialContext class
- Basic polynomial validation (no functions, integer powers)
- Accept/reject test cases (10 tests)
- Integration with Formula

🔶 **Nice to Have** (if time):
- Strict mode validation
- Single powers flag
- Detailed error messages

❌ **Defer to Later**:
- Complex operator-level validation (Perl-style)
- All edge cases
- Full parity with Perl implementation

## Success Criteria

- ✅ 10+ tests passing
- ✅ Accepts valid polynomials
- ✅ Rejects functions, fractional powers, division by variables
- ✅ Can be used in problem: `Context('LimitedPolynomial')`
- ✅ Basic error messages helpful

## Time Estimate

- Research & Planning: 30 min ✅ (this document)
- Core Implementation: 1.5 hours
- Testing: 1.5 hours
- Debugging & Refinement: 30 min
- **Total**: 3.5-4 hours

## Next Steps

1. Create `limited_polynomial_context.py`
2. Implement validation logic
3. Create test file
4. Iterate until 10+ tests pass
5. Document usage
6. Create completion document

---

**Ready to begin implementation!** 🚀
