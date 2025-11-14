# Week 5 Action Plan: Advanced MathObjects

**Start Date**: Next Session
**Goal**: Implement FormulaUpToConstant and additional contexts
**Priority**: High - Completes Calculus 2 support

## Week 5 Overview

### Primary Objectives

1. **FormulaUpToConstant** - Antiderivatives with required constant
2. **LimitedPolynomial Context** - Restrict student input format
3. **PolynomialFactors Context** - Require factored form
4. **Context Flag System** - Full flag implementation

### Success Criteria

- ✅ 40+ new tests passing
- ✅ Calculus 2 problems fully supported
- ✅ OPL tutorial compatibility expanded
- ✅ Documentation complete

## Day 1: FormulaUpToConstant

### Research Phase (1-2 hours)

**Study Perl Implementation**:
```bash
# Key files to review
lib/Value/Formula.pm
macros/parsers/parserFormulaUpToConstant.pl
```

**Understand Requirements**:
- Must include constant term (C, K, etc.)
- Any single-letter constant allowed (not e or i)
- Answer checking up to constant
- TeX display with constant

### Design Phase (1 hour)

**API Design**:
```python
# Usage pattern
from pg_mathobjects import FormulaUpToConstant

# Create with constant
f = FormulaUpToConstant("x^2/2 + C")

# Answer checking accepts any constant
checker = f.cmp()
result = checker.check("x^2/2 + K")  # Should pass
result = checker.check("x^2/2 + 5")  # Should pass
result = checker.check("x^2/2")      # Should fail (no constant)
```

**Implementation Strategy**:
1. Extend Formula class or create subclass
2. Parse and identify constant variable
3. Modify equivalence checking
4. Update answer checker

### Implementation Phase (2-3 hours)

**Create File**: `packages/pg_mathobjects/pg_mathobjects/formula_up_to_constant.py`

**Key Components**:
```python
class FormulaUpToConstant(Formula):
    """Formula that is only unique up to a constant."""

    def __init__(self, expr: str, context: Context | None = None):
        # Parse expression
        # Identify constant variable
        # Set up for equivalence checking

    def cmp(self, **options):
        # Custom answer checker
        # Accept any single-letter constant
        # Check equivalence up to constant
```

### Testing Phase (1-2 hours)

**Create Test File**: `packages/pg_mathobjects/tests/test_formula_up_to_constant.py`

**Test Cases** (20+ tests):
1. Creation with C
2. Creation with K
3. Creation with other letters
4. Error if no constant
5. Answer checking - accept C
6. Answer checking - accept K
7. Answer checking - accept numeric constant
8. Answer checking - reject no constant
9. Equivalence up to constant
10. Differentiation (should work)
11. Evaluation (with constant value)
12. TeX output
13. Integration with DOCUMENT/ENDDOCUMENT
14. PGML integration
15. Multiple constants (edge case)
16. Constant in wrong context (error)
17. Reserved names (e, i, pi) rejected
18. Case sensitivity
19. Complex expressions with constant
20. Nested constants

### Validation Phase (1 hour)

**Test with Real Problem**: `IntegralCalc/IndefiniteIntegrals.pg`
```python
# Original problem uses:
$general = FormulaUpToConstant('e^x');

# Should now work:
ANS($general->cmp())
```

### Expected Outcome

- ✅ FormulaUpToConstant class working
- ✅ 20+ tests passing
- ✅ Tutorial problem compatible
- ✅ Documentation complete

## Day 2: LimitedPolynomial Context

### Research Phase (1 hour)

**Study**: `macros/contexts/contextLimitedPolynomial.pl`

**Key Features**:
- Restricts student input to polynomial form
- No functions allowed
- No complex operations
- Optional strict mode

### Implementation Phase (2 hours)

**Create File**: `packages/pg_mathobjects/pg_mathobjects/contexts/limited_polynomial.py`

**Key Components**:
```python
class LimitedPolynomialContext(Context):
    """Context that only allows polynomial expressions."""

    def __init__(self, strict: bool = False):
        super().__init__('Numeric')
        self.name = 'LimitedPolynomial'
        self.strict = strict
        # Configure restrictions
```

### Testing Phase (1-2 hours)

**Test Cases** (15+ tests):
1. Polynomial accepted
2. Function rejected (sin, cos, etc.)
3. Division rejected
4. Powers limited
5. Strict mode - no operations in coefficients
6. Single powers flag
7. Multiple variables
8. Answer checking
9. Error messages
10. Context switching

### Expected Outcome

- ✅ LimitedPolynomial context working
- ✅ 15+ tests passing
- ✅ ExpandedPolynomial.pg uses it

## Day 3: PolynomialFactors Context

### Implementation (2 hours)

**File**: `packages/pg_mathobjects/pg_mathobjects/contexts/polynomial_factors.py`

**Key Features**:
- Allows products of polynomials
- Optionally allows powers
- Restricts to factored form

### Testing (1-2 hours)

**Test Cases** (15+ tests):
1. Factored form accepted
2. Expanded form rejected
3. Power restrictions
4. Multiple factors
5. Single factors flag
6. Answer checking
7. FactoredPolynomial.pg compatibility

### Expected Outcome

- ✅ PolynomialFactors context working
- ✅ 15+ tests passing

## Day 4: Context Flag System

### Design Phase (1 hour)

**Flag Architecture**:
```python
class Context:
    def __init__(self):
        self.flags = ContextFlags()

class ContextFlags:
    def __init__(self):
        self.reduceConstants = True
        self.reduceConstantFunctions = True
        self.formatStudentAnswer = 'evaluated'
        # ... more flags

    def set(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
```

### Implementation (2 hours)

**Implement Common Flags**:
- reduceConstants
- reduceConstantFunctions
- formatStudentAnswer
- tolerance
- tolType
- singlePowers
- singleFactors

### Testing (1 hour)

**Test Cases** (10+ tests):
1. Flag setting
2. Flag reading
3. Flag effects on formulas
4. Flag inheritance
5. Flag copying

### Expected Outcome

- ✅ Flag system working
- ✅ 10+ tests passing

## Day 5: Integration & Documentation

### Integration Testing (2 hours)

**Test Suites**:
1. All Week 5 features together
2. Week 4 + Week 5 combined
3. Full tutorial problem suite

### Documentation (2 hours)

**Documents to Create**:
1. `WEEK5_COMPLETE.md` - Summary
2. `FORMULA_UP_TO_CONSTANT_GUIDE.md` - Usage guide
3. `CONTEXT_GUIDE.md` - All contexts documented
4. Update `MATHOBJECTS_STATUS_REPORT.md`

### Final Validation (1 hour)

**Test with OPL Problems**:
- IntegralCalc tutorials
- Algebra factoring problems
- Full problem rendering

### Expected Outcome

- ✅ All 205+ tests passing (165 Week 4 + 40+ Week 5)
- ✅ Full documentation
- ✅ Production ready for Calculus 2

## Week 5 Test Targets

| Feature | Target Tests | Priority |
|---------|-------------|----------|
| FormulaUpToConstant | 20 | High |
| LimitedPolynomial | 15 | High |
| PolynomialFactors | 15 | Medium |
| Context Flags | 10 | Medium |
| Integration | 5 | High |
| **Total** | **65** | |

Combined with Week 4: **230 total tests**

## Success Metrics

### Must Have ✅
- FormulaUpToConstant working
- Calculus 2 integral problems supported
- 200+ tests passing total

### Should Have ✅
- LimitedPolynomial context
- PolynomialFactors context
- Basic flag system

### Nice to Have
- Complex context
- Vector context
- Advanced flags

## Risk Mitigation

### Potential Issues

1. **FormulaUpToConstant Complexity**
   - Mitigation: Study Perl code thoroughly
   - Fallback: Simplified version first

2. **Context System Changes**
   - Mitigation: Incremental addition
   - Fallback: Keep existing contexts working

3. **Time Overrun**
   - Mitigation: Prioritize FormulaUpToConstant
   - Fallback: Move lower priority items to Week 6

## Resources Needed

### Code References
- `lib/Value/Formula.pm` (Perl)
- `macros/parsers/parserFormulaUpToConstant.pl`
- `macros/contexts/contextLimitedPolynomial.pl`
- `macros/contexts/contextPolynomialFactors.pl`

### Documentation
- MathObjects documentation
- WeBWorK wiki
- OPL tutorial problems

### Testing
- pytest framework
- Tutorial problem files
- OPL problem library

## Deliverables

### Code
1. `formula_up_to_constant.py` (new)
2. `contexts/limited_polynomial.py` (new)
3. `contexts/polynomial_factors.py` (new)
4. `context.py` (enhanced with flags)
5. Test files (4 new files, 65+ tests)

### Documentation
1. Week 5 completion summary
2. FormulaUpToConstant guide
3. Context reference guide
4. Updated status report

### Validation
1. Tutorial problem tests
2. Integration test suite
3. Performance benchmarks

## Timeline

| Day | Focus | Hours | Deliverable |
|-----|-------|-------|-------------|
| 1 | FormulaUpToConstant | 5-6 | Class + 20 tests |
| 2 | LimitedPolynomial | 3-4 | Context + 15 tests |
| 3 | PolynomialFactors | 3-4 | Context + 15 tests |
| 4 | Context Flags | 3-4 | System + 10 tests |
| 5 | Integration & Docs | 4-5 | Complete + docs |
| **Total** | | **18-23** | **65+ tests** |

## Post-Week 5 Roadmap

### Week 6: Additional Contexts
- Complex context
- Vector context
- Fraction context
- Matrix basics

### Week 7: Advanced Features
- Custom answer checkers
- Advanced simplification
- Performance optimization
- Extended testing

### Week 8: OPL Integration
- Test entire tutorial library
- Document compatibility
- Create migration guide
- Instructor documentation

## Conclusion

Week 5 will complete the core MathObjects implementation by adding the most requested feature (FormulaUpToConstant) and essential contexts. After Week 5, the system will support:

- ✅ Algebra 1 & 2 (100%)
- ✅ Trigonometry (100%)
- ✅ Pre-Calculus (100%)
- ✅ Calculus 1 (100%)
- ✅ Calculus 2 (100%)
- ✅ Linear Algebra basics (80%)

This represents **comprehensive coverage** of undergraduate mathematics courses up through Calculus 2.

---

**Ready to begin Week 5!** 🚀

Let's implement FormulaUpToConstant and complete the MathObjects system!
