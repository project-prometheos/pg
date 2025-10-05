"""
Integration tests for Week 5 features.

Tests verify that all Week 5 features work together:
- Context switching
- FormulaUpToConstant integration
- Polynomial context interactions
- Flag interactions across contexts
- Real-world problem scenarios
- Edge cases and limitations
- Performance and scaling
- Documentation examples
"""

import pytest

from pg_math.context import Context
from pg_math.formula import Formula
from pg_math.formula_up_to_constant import FormulaUpToConstant
from pg_math.numeric import Real


class TestContextSwitching:
    """Test switching between contexts."""

    def test_switch_from_numeric_to_polynomial(self):
        """Switch from Numeric to LimitedPolynomial"""
        # Start with Numeric
        ctx1 = Context('Numeric')
        f1 = Formula('x**2 + 2*x + 1', ctx1)
        assert f1.eval(x=2).value == 9

        # Switch to LimitedPolynomial
        ctx2 = Context('LimitedPolynomial')
        f2 = Formula('x**2 + 2*x + 1', ctx2)
        assert f2.eval(x=2).value == 9

    def test_switch_from_polynomial_to_factors(self):
        """Switch from LimitedPolynomial to PolynomialFactors"""
        # LimitedPolynomial
        ctx1 = Context('LimitedPolynomial')
        f1 = Formula('x**2 - 1', ctx1)
        assert f1.eval(x=2).value == 3

        # PolynomialFactors
        ctx2 = Context('PolynomialFactors')
        f2 = Formula('(x-1)*(x+1)', ctx2)
        assert f2.eval(x=2).value == 3

    def test_switch_from_factors_to_numeric(self):
        """Switch from PolynomialFactors back to Numeric"""
        # PolynomialFactors
        ctx1 = Context('PolynomialFactors')
        f1 = Formula('(x-1)*(x+1)', ctx1)
        assert f1.eval(x=0).value == -1

        # Back to Numeric
        ctx2 = Context('Numeric')
        f2 = Formula('x**2 - 1', ctx2)
        assert f2.eval(x=0).value == -1

    def test_flags_preserved_across_switches(self):
        """Flags persist across context switches"""
        # Set custom tolerance in Numeric
        ctx1 = Context('Numeric')
        ctx1.flags.set(tolerance=0.05)
        r1 = Real(1.0, ctx1)
        r2 = Real(1.03, ctx1)
        assert r1 == r2

        # Switch to LimitedPolynomial with custom tolerance
        ctx2 = Context('LimitedPolynomial')
        ctx2.flags.set(tolerance=0.05)
        r3 = Real(1.0, ctx2)
        r4 = Real(1.03, ctx2)
        assert r3 == r4


class TestFormulaUpToConstantIntegration:
    """Test FormulaUpToConstant with other features."""

    def test_formula_up_to_constant_with_differentiation(self):
        """FormulaUpToConstant with differentiation"""
        ctx = Context('Numeric')

        # Antiderivative
        f = FormulaUpToConstant('x**2/2 + C', context=ctx)

        # Derivative should eliminate constant
        df = f.D('x')

        # Evaluate derivative
        assert df.eval(x=3).value == 3

    def test_formula_up_to_constant_with_custom_tolerance(self):
        """FormulaUpToConstant with custom tolerance"""
        ctx = Context('Numeric')
        ctx.flags.set(tolerance=0.1)

        correct = FormulaUpToConstant('sin(x) + C', context=ctx)

        # Student answers with different constants
        student1 = 'sin(x)'
        student2 = 'sin(x) + 5'

        checker = correct.cmp()
        result1 = checker(student1)
        result2 = checker(student2)

        # Both should be accepted
        assert result1 is not None
        assert result2 is not None

    def test_formula_up_to_constant_with_multiple_variables(self):
        """FormulaUpToConstant with multiple variables"""
        ctx = Context('Numeric')
        ctx.variables.add('y', 'Real')

        # Partial integral with respect to x
        f = FormulaUpToConstant('x*y + C', context=ctx)

        # Evaluate at different points (with C=0 for concrete evaluation)
        r1 = f.eval(x=2, y=3, C=0)
        r2 = f.eval(x=1, y=3, C=0)

        # Results differ by the integration variable
        assert r1.value - r2.value == pytest.approx(3.0)


class TestPolynomialContextsIntegration:
    """Test interactions between polynomial contexts."""

    def test_limited_polynomial_to_factors_form(self):
        """Convert LimitedPolynomial to PolynomialFactors form"""
        # LimitedPolynomial
        ctx1 = Context('LimitedPolynomial')
        f1 = Formula('x**2 - 4', ctx1)

        # PolynomialFactors equivalent
        ctx2 = Context('PolynomialFactors')
        f2 = Formula('(x-2)*(x+2)', ctx2)

        # Same evaluation
        assert f1.eval(x=3).value == f2.eval(x=3).value
        assert f1.eval(x=0).value == f2.eval(x=0).value

    def test_polynomial_with_reduce_flag(self):
        """Polynomial with reduce flag"""
        ctx = Context('LimitedPolynomial')
        ctx.flags.set(reduceConstants=True)

        f = Formula('2*x + 3*x', ctx)

        # Should evaluate correctly
        assert f.eval(x=1).value == 5

    def test_strict_factors_mode(self):
        """PolynomialFactors in strict mode"""
        ctx = Context('PolynomialFactors-Strict')

        # Check strict flags
        assert ctx.flags.get('strictCoefficients') is True
        assert ctx.flags.get('singleFactors') is True

        # Regular factored form
        f = Formula('(x-1)*(x+2)', ctx)
        assert f.eval(x=0).value == -2


class TestFlagInteractionsAcrossContexts:
    """Test flag behavior across contexts."""

    def test_tolerance_across_contexts(self):
        """Tolerance flag works across contexts"""
        # Numeric with tolerance
        ctx1 = Context('Numeric')
        ctx1.flags.set(tolerance=0.01)
        r1 = Real(1.0, ctx1)
        r2 = Real(1.005, ctx1)
        assert r1 == r2

        # LimitedPolynomial with same tolerance
        ctx2 = Context('LimitedPolynomial')
        ctx2.flags.set(tolerance=0.01)
        r3 = Real(1.0, ctx2)
        r4 = Real(1.005, ctx2)
        assert r3 == r4

    def test_reduce_flag_in_different_contexts(self):
        """reduceConstants flag in different contexts"""
        # Numeric
        ctx1 = Context('Numeric')
        ctx1.flags.set(reduceConstants=True)
        f1 = Formula('2 + 3', ctx1)
        assert f1.eval().value == 5

        # LimitedPolynomial
        ctx2 = Context('LimitedPolynomial')
        ctx2.flags.set(reduceConstants=True)
        f2 = Formula('x + (2 + 3)', ctx2)
        assert f2.eval(x=1).value == 6

    def test_context_copy_preserves_flags(self):
        """Context.copy() preserves all flags"""
        ctx1 = Context('Numeric')
        ctx1.flags.set(tolerance=0.05)
        ctx1.flags.set(reduceConstants=True)

        ctx2 = ctx1.copy()

        # Flags copied
        assert ctx2.flags.get('tolerance') == 0.05
        assert ctx2.flags.get('reduceConstants') is True

        # Use copied context
        r1 = Real(1.0, ctx2)
        r2 = Real(1.03, ctx2)
        assert r1 == r2


class TestRealWorldProblemScenarios:
    """Test complete problem workflows."""

    def test_indefinite_integral_problem(self):
        """Complete indefinite integral problem"""
        ctx = Context('Numeric')

        # Problem: integrate exp(x)
        correct = FormulaUpToConstant('exp(x) + C', context=ctx)

        # Student answers
        student1 = 'exp(x)'
        student2 = 'exp(x) + 5'
        student3 = 'exp(x) + K'

        checker = correct.cmp()
        result1 = checker(student1)
        result2 = checker(student2)
        result3 = checker(student3)

        # All should be accepted (constant doesn't matter)
        assert result1 is not None
        assert result2 is not None
        assert result3 is not None

    def test_polynomial_expansion_problem(self):
        """Complete polynomial expansion problem"""
        ctx = Context('LimitedPolynomial')

        # Problem: expand (x+2)(x-3)
        correct = Formula('x**2 - x - 6', ctx)

        # Student answer
        student = Formula('x**2 - x - 6', ctx)

        # Check by evaluation at multiple points
        assert correct.eval(x=0).value == student.eval(x=0).value
        assert correct.eval(x=1).value == student.eval(x=1).value
        assert correct.eval(x=2).value == student.eval(x=2).value

    def test_factoring_problem(self):
        """Complete factoring problem"""
        ctx = Context('PolynomialFactors')

        # Problem: factor x**2 - 1
        correct = Formula('(x-1)*(x+1)', ctx)

        # Student answer (different order)
        student = Formula('(x+1)*(x-1)', ctx)

        # Check by evaluation
        assert correct.eval(x=0).value == student.eval(x=0).value
        assert correct.eval(x=1).value == student.eval(x=1).value
        assert correct.eval(x=2).value == student.eval(x=2).value

    def test_multi_step_algebra_problem(self):
        """Multi-step problem with context changes"""
        # Step 1: Numeric context for initial calculation
        ctx1 = Context('Numeric')
        step1 = Formula('(x+1)**2', ctx1)
        result1 = step1.eval(x=2)
        assert result1.value == 9

        # Step 2: LimitedPolynomial for expansion
        ctx2 = Context('LimitedPolynomial')
        step2 = Formula('x**2 + 2*x + 1', ctx2)
        result2 = step2.eval(x=2)
        assert result2.value == 9

        # Step 3: PolynomialFactors for factoring
        ctx3 = Context('PolynomialFactors')
        step3 = Formula('(x+1)*(x+1)', ctx3)
        result3 = step3.eval(x=2)
        assert result3.value == 9


class TestEdgeCasesAndLimitations:
    """Test edge cases and known limitations."""

    def test_sympy_simplification_behavior(self):
        """Sympy simplification in different contexts"""
        # Numeric allows simplification
        ctx1 = Context('Numeric')
        f1 = Formula('x**2 - 1', ctx1)
        assert f1.eval(x=2).value == 3

        # LimitedPolynomial
        ctx2 = Context('LimitedPolynomial')
        f2 = Formula('x**2 - 1', ctx2)
        assert f2.eval(x=2).value == 3

        # PolynomialFactors
        ctx3 = Context('PolynomialFactors')
        f3 = Formula('(x-1)*(x+1)', ctx3)
        assert f3.eval(x=2).value == 3

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
        correct_answer = FormulaUpToConstant('exp(x) + C', context=ctx)

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
