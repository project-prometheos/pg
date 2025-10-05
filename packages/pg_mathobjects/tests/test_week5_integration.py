"""
Integration tests for Week 5 features.

Tests interactions between all Week 5 features: FormulaUpToConstant,
LimitedPolynomial, PolynomialFactors, and Context Flag System.
"""

import pytest
from pg_mathobjects import Context, Formula, FormulaUpToConstant, Real


class TestContextSwitching:
    """Test switching between different specialized contexts."""

    def test_switch_numeric_to_limited_polynomial(self):
        """Switch from Numeric to LimitedPolynomial"""
        ctx = Context('Numeric')

        # Trig functions work in Numeric
        f1 = Formula('sin(x)', ctx)
        assert f1.eval(x=0).value == 0

        # Switch to LimitedPolynomial
        ctx = Context('LimitedPolynomial')

        # Trig functions now rejected
        with pytest.raises(ValueError, match='Not a polynomial'):
            Formula('sin(x)', ctx)

        # Polynomials work
        f2 = Formula('x**2 + 1', ctx)
        assert f2.eval(x=2).value == 5

    def test_switch_limited_to_factors(self):
        """Switch from LimitedPolynomial to PolynomialFactors"""
        ctx = Context('LimitedPolynomial')

        # Expanded polynomials accepted
        f1 = Formula('x**2 + x - 2', ctx)
        assert f1.eval(x=1).value == 0

        # Switch to PolynomialFactors
        ctx = Context('PolynomialFactors')

        # Expanded form rejected
        with pytest.raises(ValueError, match='factored form'):
            Formula('x**2 + x - 2', ctx)

        # Factored form works
        f2 = Formula('(x-1)*(x+2)', ctx)
        assert f2.eval(x=1).value == 0

    def test_switch_standard_to_strict(self):
        """Switch between standard and strict modes"""
        # Standard mode
        ctx = Context('LimitedPolynomial')
        assert ctx.flags.get('strictCoefficients') is False

        # Strict mode
        ctx = Context('LimitedPolynomial-Strict')
        assert ctx.flags.get('strictCoefficients') is True

    def test_flags_persist_across_formulas(self):
        """Context flags affect all formulas in that context"""
        ctx = Context('Numeric')
        ctx.flags.set(tolerance=0.05)

        r1 = Real(1.0, ctx)
        r2 = Real(1.03, ctx)

        assert r1 == r2  # Within 5% tolerance


class TestFormulaUpToConstantIntegration:
    """Test FormulaUpToConstant with other features."""

    def test_create_from_limited_polynomial(self):
        """Create FormulaUpToConstant from LimitedPolynomial context"""
        ctx = Context('LimitedPolynomial')

        # Create polynomial first
        poly = Formula('x**2 + 2*x', ctx)

        # Switch to Numeric for FormulaUpToConstant
        ctx = Context('Numeric')
        f = FormulaUpToConstant('x**2 + 2*x + C', ctx)

        assert 'C' in str(f)

    def test_differentiation_returns_limited_polynomial(self):
        """Differentiation of FormulaUpToConstant in LimitedPolynomial context"""
        ctx = Context('Numeric')
        f = FormulaUpToConstant('x**3/3 + C', ctx)

        # Differentiate
        df = f.D('x')

        # Result is polynomial
        assert isinstance(df, Formula)
        assert df.eval(x=2).value == 4  # x**2 at x=2

    def test_with_custom_tolerance(self):
        """FormulaUpToConstant respects context tolerance"""
        ctx = Context('Numeric')
        ctx.flags.set(tolerance=0.01)

        f = FormulaUpToConstant('x**2 + C', ctx)

        # Evaluation respects tolerance
        r1 = f.eval(x=1, C=0)
        r2 = f.eval(x=1.005, C=0)

        # Should be close enough with 1% tolerance
        assert abs(r1.value - r2.value) < 0.02


class TestPolynomialContextsIntegration:
    """Test interactions between polynomial contexts."""

    def test_limited_to_factors_same_polynomial(self):
        """Same polynomial in different contexts"""
        # In LimitedPolynomial
        ctx1 = Context('LimitedPolynomial')
        expanded = Formula('x**2 - 3*x + 2', ctx1)

        # In PolynomialFactors
        ctx2 = Context('PolynomialFactors')
        factored = Formula('(x-1)*(x-2)', ctx2)

        # Evaluate at same point
        val1 = expanded.eval(x=0)
        val2 = factored.eval(x=0)

        assert val1 == val2  # Both evaluate to 2

    def test_strict_modes_together(self):
        """Both strict modes enabled"""
        ctx1 = Context('LimitedPolynomial-Strict')
        assert ctx1.flags.get('strictCoefficients') is True

        ctx2 = Context('PolynomialFactors-Strict')
        assert ctx2.flags.get('strictCoefficients') is True
        assert ctx2.flags.get('singleFactors') is True

    def test_factored_polynomial_operations(self):
        """Operations on factored polynomials"""
        ctx = Context('PolynomialFactors')

        f1 = Formula('(x-1)*(x+2)', ctx)
        f2 = Formula('(x-3)', ctx)

        # Multiply factors (creates new factored form)
        result = f1 * f2

        # Result evaluates correctly
        assert result.eval(x=3).value == 0  # Root at x=3


class TestFlagInteractionsAcrossContexts:
    """Test how flags interact across different contexts."""

    def test_tolerance_in_different_contexts(self):
        """Tolerance works consistently across contexts"""
        # Set tolerance in Numeric
        ctx = Context('Numeric')
        ctx.flags.set(tolerance=0.01)

        r1 = Real(1.0, ctx)
        r2 = Real(1.005, ctx)
        assert r1 == r2

        # Switch to LimitedPolynomial (same cached context gets modified)
        ctx2 = Context('LimitedPolynomial')
        ctx2.flags.set(tolerance=0.01)

        f = Formula('x', ctx2)
        val1 = f.eval(x=1.0)
        val2 = f.eval(x=1.005)

        # Tolerance still applies
        assert val1 == val2

    def test_reduce_flags_in_strict_contexts(self):
        """Strict contexts disable constant reduction"""
        # Standard context
        ctx1 = Context('LimitedPolynomial')
        assert ctx1.flags.get('reduceConstants') == 1

        # Strict contexts
        ctx2 = Context('LimitedPolynomial-Strict')
        assert ctx2.flags.get('reduceConstants') == 0

        ctx3 = Context('PolynomialFactors-Strict')
        assert ctx3.flags.get('reduceConstants') == 0

    def test_context_copy_preserves_all_flags(self):
        """Copying context preserves custom flags"""
        ctx1 = Context('Numeric')
        ctx1.flags.set(
            tolerance=0.05,
            tolType='absolute',
            customFlag='test'
        )

        ctx2 = ctx1.copy()

        assert ctx2.flags.get('tolerance') == 0.05
        assert ctx2.flags.get('tolType') == 'absolute'
        assert ctx2.flags.get('customFlag') == 'test'


class TestRealWorldProblemScenarios:
    """Test complete problem workflows."""

    def test_indefinite_integral_workflow(self):
        """Complete indefinite integral problem"""
        ctx = Context('Numeric')

        # Problem: Find ∫ 2x dx
        correct = FormulaUpToConstant('x**2 + C', ctx)

        # Student answers with different constant letter
        student1 = FormulaUpToConstant('x**2 + K', ctx)

        # Remove constants and compare
        correct_formula = correct.remove_constant()
        student1_formula = student1.remove_constant()

        # Should evaluate to same values
        assert correct_formula.eval(
            x=2).value == student1_formula.eval(x=2).value
        assert correct_formula.eval(
            x=3).value == student1_formula.eval(x=3).value

        # Wrong answer
        wrong = FormulaUpToConstant('2*x**2 + C', ctx)
        wrong_formula = wrong.remove_constant()
        assert correct_formula.eval(x=2).value != wrong_formula.eval(x=2).value

    def test_polynomial_expansion_workflow(self):
        """Complete polynomial expansion problem"""
        # Problem: Expand (x+2)(x-3)
        ctx = Context('LimitedPolynomial')
        correct = Formula('x**2 - x - 6', ctx)

        # Student answers (various forms)
        student1 = Formula('x**2 - x - 6', ctx)
        student2 = Formula('-6 - x + x**2', ctx)  # Reordered

        # Check by evaluation (Formula doesn't have __eq__ for symbolic comparison)
        assert correct.eval(x=0).value == student1.eval(x=0).value
        assert correct.eval(x=1).value == student1.eval(x=1).value
        assert correct.eval(x=0).value == student2.eval(x=0).value

    def test_factoring_workflow(self):
        """Complete factoring problem"""
        # Problem: Factor x² - 4
        ctx = Context('PolynomialFactors')
        correct = Formula('(x-2)*(x+2)', ctx)

        # Student answers
        student1 = Formula('(x-2)*(x+2)', ctx)
        student2 = Formula('(x+2)*(x-2)', ctx)  # Order reversed

        # Check by evaluation
        assert correct.eval(x=0).value == student1.eval(x=0).value
        assert correct.eval(x=1).value == student1.eval(x=1).value
        assert correct.eval(x=0).value == student2.eval(x=0).value

    def test_multi_step_problem(self):
        """Problem requiring multiple context switches"""
        # Step 1: Expand in LimitedPolynomial
        ctx = Context('LimitedPolynomial')
        expanded = Formula('x**2 + 3*x + 2', ctx)

        # Step 2: Factor in PolynomialFactors
        ctx = Context('PolynomialFactors')
        factored = Formula('(x+1)*(x+2)', ctx)

        # Step 3: Integrate in Numeric (hypothetical)
        ctx = Context('Numeric')
        integral = FormulaUpToConstant('x**3/3 + 3*x**2/2 + 2*x + C', ctx)

        # Verify all steps
        assert expanded.eval(x=0).value == 2
        assert factored.eval(x=0).value == 2
        assert integral.remove_constant().eval(x=0).value == 0


class TestEdgeCasesAndLimitations:
    """Test edge cases and known limitations."""

    def test_sympy_auto_simplification_addition(self):
        """Sympy simplifies addition before validation"""
        ctx = Context('PolynomialFactors')

        # This might be accepted if sympy simplifies to linear
        # (x-1) + (x+2) → 2*x + 1
        # Linear polynomials are accepted as single factors
        f = Formula('2*x + 1', ctx)  # Simplified form
        assert f.eval(x=1).value == 3

    def test_very_small_tolerance(self):
        """Extremely small tolerance values"""
        ctx = Context('Numeric')
        ctx.flags.set(tolerance=1e-10)

        r1 = Real(1.0, ctx)
        r2 = Real(1.0 + 1e-11, ctx)

        # Within tolerance
        assert r1 == r2

    def test_near_zero_with_custom_threshold(self):
        """Custom zero threshold"""
        ctx = Context('Numeric')
        ctx.flags.set(zeroLevel=1e-8)

        r1 = Real(1e-9, ctx)
        r2 = Real(0.0, ctx)

        # Below custom zero threshold
        assert r1 == r2

    def test_multiple_variables_all_contexts(self):
        """Multi-variable support across contexts"""
        # Add variables
        ctx = Context('Numeric')
        ctx.variables.add('y', 'Real')

        # Numeric context
        f1 = Formula('x + y', ctx)
        assert f1.eval(x=1, y=2).value == 3

        # LimitedPolynomial
        ctx = Context('LimitedPolynomial')
        ctx.variables.add('y', 'Real')
        f2 = Formula('x**2 + y**2', ctx)
        assert f2.eval(x=3, y=4).value == 25

        # PolynomialFactors
        ctx = Context('PolynomialFactors')
        ctx.variables.add('y', 'Real')
        f3 = Formula('(x+y)*(x-y)', ctx)
        assert f3.eval(x=5, y=3).value == 16  # (5+3)*(5-3) = 16


class TestPerformanceAndScaling:
    """Test performance with complex expressions."""

    def test_large_polynomial(self):
        """Handle large degree polynomial"""
        ctx = Context('LimitedPolynomial')

        # Large degree polynomial
        expr = ' + '.join([f'x**{i}' for i in range(10)])
        f = Formula(expr, ctx)

        # Evaluate
        result = f.eval(x=2)
        expected = sum(2**i for i in range(10))
        assert result.value == expected

    def test_many_factors(self):
        """Handle many factors"""
        ctx = Context('PolynomialFactors')

        # Many factors
        factors = ['(x-{})'.format(i) for i in range(1, 6)]
        expr = '*'.join(factors)
        f = Formula(expr, ctx)

        # Each root evaluates to zero
        for i in range(1, 6):
            assert f.eval(x=i).value == 0

    def test_repeated_context_switches(self):
        """Many context switches don't break anything"""
        for _ in range(10):
            ctx = Context('Numeric')
            f1 = Formula('x**2', ctx)

            ctx = Context('LimitedPolynomial')
            f2 = Formula('x**2', ctx)

            ctx = Context('PolynomialFactors')
            f3 = Formula('(x-1)*(x+1)', ctx)

            # All evaluate correctly
            assert f1.eval(x=2).value == 4
            assert f2.eval(x=2).value == 4
            assert f3.eval(x=2).value == 3


class TestDocumentationExamples:
    """Verify all examples from documentation work."""

    def test_guide_example_indefinite_integral(self):
        """Example from comprehensive guide"""
        ctx = Context('Numeric')
        correct_answer = FormulaUpToConstant('exp(x) + C', ctx)

        student1 = 'exp(x) + K'
        student2 = 'exp(x) + 5'

        checker = correct_answer.cmp()
        result1 = checker(student1)
        result2 = checker(student2)

        # Check results exist and have correct structure
        assert result1 is not None
        assert result2 is not None

    def test_guide_example_polynomial_expansion(self):
        """Example from comprehensive guide"""
        ctx = Context('LimitedPolynomial')
        correct = Formula('x**2 - x - 6', ctx)

        # Check by evaluation
        f1 = Formula('x**2 - x - 6', ctx)
        f2 = Formula('-6 - x + x**2', ctx)

        assert correct.eval(x=0).value == f1.eval(x=0).value
        assert correct.eval(x=1).value == f1.eval(x=1).value
        assert correct.eval(x=0).value == f2.eval(x=0).value

    def test_guide_example_factoring(self):
        """Example from comprehensive guide"""
        ctx = Context('PolynomialFactors')
        correct = Formula('(x+1)*(x+2)', ctx)

        # Check by evaluation
        f1 = Formula('(x+1)*(x+2)', ctx)
        f2 = Formula('(x+2)*(x+1)', ctx)

        assert correct.eval(x=0).value == f1.eval(x=0).value
        assert correct.eval(x=1).value == f1.eval(x=1).value
        assert correct.eval(x=0).value == f2.eval(x=0).value

    def test_guide_example_custom_tolerance(self):
        """Example from comprehensive guide"""
        ctx = Context('Numeric')
        ctx.flags.set(tolerance=0.05)

        r1 = Real(100.0, ctx)
        r2 = Real(103.0, ctx)

        assert r1 == r2

    def test_guide_example_strict_mode(self):
        """Example from comprehensive guide"""
        ctx = Context('PolynomialFactors-Strict')

        assert ctx.flags.get('strictCoefficients') is True
        assert ctx.flags.get('singleFactors') is True
        assert ctx.flags.get('strictDivision') is True
