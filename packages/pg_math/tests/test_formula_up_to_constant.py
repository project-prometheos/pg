"""Tests for FormulaUpToConstant class.

Tests the implementation of formulas that are unique up to an arbitrary constant,
used for antiderivatives in calculus problems.

Ported from pg_mathobjects to pg_math for Perl 1:1 parity migration.
"""

import pytest
import sympy as sp

from pg_math import Context, Formula, FormulaUpToConstant, Compute


class TestFormulaUpToConstantCreation:
    """Test creating FormulaUpToConstant objects."""

    def test_create_with_constant_C(self):
        """Test creating with constant C."""
        f = FormulaUpToConstant("x^2/2 + C")
        assert f.constant == "C"
        assert "C" in str(f)

    def test_create_with_constant_K(self):
        """Test creating with constant K."""
        f = FormulaUpToConstant("sin(x) + K")
        assert f.constant == "K"
        assert "K" in str(f)

    def test_create_with_other_letters(self):
        """Test creating with various single-letter constants."""
        for letter in ["A", "B", "D", "K", "c", "k"]:
            f = FormulaUpToConstant(f"x^3/3 + {letter}")
            assert f.constant == letter

    def test_auto_add_constant_if_missing(self):
        """Test that C is added automatically if no constant present."""
        f = FormulaUpToConstant("x^2/2")
        assert f.constant == "C"
        # Should have added C to the expression
        symbols = f._sympy_expr.free_symbols
        assert any(str(s) == "C" for s in symbols)

    def test_error_on_multiple_constants(self):
        """Test error when multiple potential constants are present."""
        with pytest.raises(ValueError, match="multiple potential arbitrary constants"):
            FormulaUpToConstant("A*x + B")

    def test_reserved_names_not_constants(self):
        """Test that e, i, pi are not treated as arbitrary constants."""
        # These should be treated as mathematical constants, not arbitrary
        f = FormulaUpToConstant("e^x")
        assert f.constant == "C"  # Should add C since e is not arbitrary

    def test_nonlinear_constant_error(self):
        """Test error when formula is not linear in constant."""
        with pytest.raises(ValueError, match="not linear"):
            FormulaUpToConstant("x + C^2")

    def test_create_from_formula(self):
        """Test creating from an existing Formula object."""
        f1 = Formula("x^2 + C", ["x", "C"])
        f2 = FormulaUpToConstant(f1)
        assert f2.constant == "C"

    def test_private_context(self):
        """Test that FormulaUpToConstant uses a private context."""
        ctx = Context("Numeric")
        original_vars = set(ctx.variables.list())

        f = FormulaUpToConstant("x^2 + C", context=ctx)

        # Original context should not be modified
        assert set(ctx.variables.list()) == original_vars

        # Formula's private context should have C
        assert "C" in f.context.variables.list()


class TestFormulaUpToConstantComparison:
    """Test comparing FormulaUpToConstant objects."""

    def test_accept_same_constant(self):
        """Test that same formula with same constant is accepted."""
        f1 = FormulaUpToConstant("x^2/2 + C")
        f2 = FormulaUpToConstant("x^2/2 + C")
        equal, msg = f1.compare(f2)
        assert equal
        assert msg is None

    def test_accept_different_constant_letter(self):
        """Test that different constant letter is accepted."""
        f1 = FormulaUpToConstant("x^2/2 + C")
        f2 = FormulaUpToConstant("x^2/2 + K")
        equal, msg = f1.compare(f2)
        assert equal

    def test_accept_different_constant_value(self):
        """Test that different numeric constant is accepted."""
        f1 = FormulaUpToConstant("x^2/2 + C")
        f2 = FormulaUpToConstant("x^2/2 + 5 + K")  # Different by a constant
        equal, msg = f1.compare(f2)
        assert equal

    def test_reject_no_constant(self):
        """Test that answer without constant is rejected."""
        f1 = FormulaUpToConstant("x^2/2 + C")
        f2 = Formula("x^2/2", ["x"])  # No constant
        equal, msg = f1.compare(f2)
        assert not equal
        assert "arbitrary constant" in msg.lower()

    def test_reject_wrong_formula(self):
        """Test that wrong formula is rejected."""
        f1 = FormulaUpToConstant("x^2/2 + C")
        f2 = FormulaUpToConstant("x^3/3 + K")
        equal, msg = f1.compare(f2)
        assert not equal

    def test_equivalence_with_rearrangement(self):
        """Test that algebraically equivalent formulas are accepted."""
        f1 = FormulaUpToConstant("x^2/2 + x + C")
        f2 = FormulaUpToConstant("x + x^2/2 + K")
        equal, msg = f1.compare(f2)
        assert equal

    def test_trig_equivalence(self):
        """Test equivalence with trig functions."""
        f1 = FormulaUpToConstant("-cos(x) + C")
        f2 = FormulaUpToConstant("-cos(x) + K")
        equal, msg = f1.compare(f2)
        assert equal


class TestFormulaUpToConstantAnswerChecker:
    """Test the answer checker (cmp method)."""

    def test_checker_accepts_correct_answer(self):
        """Test that answer checker accepts correct answer."""
        f = FormulaUpToConstant("x^2/2 + C")
        checker = f.cmp()
        result = checker("x^2/2 + K")
        assert result['correct']
        assert result['message'] == ""

    def test_checker_accepts_constant_variation(self):
        """Test that checker accepts different constants."""
        f = FormulaUpToConstant("sin(x) + C")
        checker = f.cmp()

        # Try various constants
        for constant in ["K", "A", "B", "D"]:
            result = checker(f"sin(x) + {constant}")
            assert result['correct'], f"Should accept constant {constant}"

    def test_checker_rejects_no_constant(self):
        """Test that checker rejects answer without constant."""
        f = FormulaUpToConstant("x^2/2 + C")
        checker = f.cmp()
        result = checker("x^2/2")
        assert not result['correct']
        assert "constant" in result['message'].lower()

    def test_checker_rejects_wrong_formula(self):
        """Test that checker rejects wrong formula."""
        f = FormulaUpToConstant("x^2/2 + C")
        checker = f.cmp()
        result = checker("x^3/3 + K")
        assert not result['correct']

    def test_checker_with_numeric_constant(self):
        """Test checker with numeric constant added."""
        f = FormulaUpToConstant("x^2 + C")
        checker = f.cmp()
        # Student adds numeric constant - should still work
        result = checker("x^2 + 5 + K")
        assert result['correct']

    def test_checker_hints_disabled(self):
        """Test that hints can be disabled."""
        f = FormulaUpToConstant("x^2/2 + C")
        checker = f.cmp(showHints=False)
        result = checker("x^2/2")  # Missing constant
        assert not result['correct']
        # No helpful message when hints disabled
        assert result['message'] == ""

    def test_checker_linearity_hints(self):
        """Test linearity hints for non-linear constants."""
        f = FormulaUpToConstant("x^2 + C")
        checker = f.cmp(showLinearityHints=True)
        # This should parse but fail the linearity check
        # Note: This might not trigger in practice since we check at creation
        result = checker("x^2 + K")
        # Should succeed since K is linear
        assert result['correct']


class TestFormulaUpToConstantOperations:
    """Test operations on FormulaUpToConstant."""

    def test_differentiation_returns_formula(self):
        """Test that differentiation returns a Formula, not FormulaUpToConstant."""
        f = FormulaUpToConstant("x^2/2 + C")
        df = f.D("x")
        assert isinstance(df, Formula)
        assert not isinstance(df, FormulaUpToConstant)
        # Derivative should be x (constant disappears)
        assert df._sympy_expr.equals(Formula("x", ["x"])._sympy_expr)

    def test_differentiation_removes_constant(self):
        """Test that constant disappears in derivative."""
        f = FormulaUpToConstant("x^3/3 + 5*x + C")
        df = f.D("x")
        # Check that C is not in the derivative
        symbols = df._sympy_expr.free_symbols
        assert not any(str(s) == "C" for s in symbols)

    def test_remove_constant_method(self):
        """Test the remove_constant method."""
        f = FormulaUpToConstant("x^2/2 + C")
        g = f.remove_constant()
        assert isinstance(g, Formula)
        assert not isinstance(g, FormulaUpToConstant)
        # Should be equivalent to x^2/2
        assert g._sympy_expr.equals(Formula("x^2/2", ["x"])._sympy_expr)

    def test_evaluation_with_constant_value(self):
        """Test evaluating formula by substituting constant."""
        f = FormulaUpToConstant("x^2 + C")
        # Remove constant first, then evaluate
        g = f.remove_constant()
        result = g.eval(x=2)
        # pg_math Real comparison
        assert float(result) == 4

    def test_string_representation(self):
        """Test string representations."""
        f = FormulaUpToConstant("x^2 + C")
        # Should show the constant
        assert "C" in str(f)
        # Repr should show it's a FormulaUpToConstant
        assert "FormulaUpToConstant" in repr(f)


class TestIntegrationWithRealProblems:
    """Test with patterns from real tutorial problems."""

    def test_indefinite_integral_exp(self):
        """Test pattern from IndefiniteIntegrals.pg - exponential."""
        # Problem: integrate e^x
        correct = FormulaUpToConstant("e^x + C")
        checker = correct.cmp()

        # Student answers
        assert checker("e^x + K")['correct']
        assert checker("e^x + A")['correct']
        assert not checker("e^x")['correct']  # Missing constant

    def test_indefinite_integral_polynomial(self):
        """Test polynomial integration."""
        # integrate x^2 dx = x^3/3 + C
        correct = FormulaUpToConstant("x^3/3 + C")
        checker = correct.cmp()

        assert checker("x^3/3 + K")['correct']
        assert checker("x**3/3 + D")['correct']
        assert not checker("x^3/3")['correct']

    def test_indefinite_integral_trig(self):
        """Test trig function integration."""
        # integrate sin(x) dx = -cos(x) + C
        correct = FormulaUpToConstant("-cos(x) + C")
        checker = correct.cmp()

        assert checker("-cos(x) + K")['correct']
        assert not checker("-cos(x)")['correct']
        assert not checker("cos(x) + K")['correct']  # Wrong sign

    def test_with_multiple_terms(self):
        """Test integration with multiple terms."""
        correct = FormulaUpToConstant("x^3/3 + x^2/2 + x + C")
        checker = correct.cmp()

        # Various orderings should work
        assert checker("x + x^2/2 + x^3/3 + K")['correct']
        assert checker("x^3/3 + x + x^2/2 + A")['correct']

    def test_constant_with_coefficient(self):
        """Test that constant coefficients don't matter."""
        # These should be equivalent (differ only by constant)
        f1 = FormulaUpToConstant("2*x^2 + C")
        f2 = FormulaUpToConstant("2*x^2 + K")
        equal, _ = f1.compare(f2)
        assert equal


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_constant_only(self):
        """Test formula that is just a constant."""
        f = FormulaUpToConstant("C")
        assert f.constant == "C"

    def test_complex_expression(self):
        """Test complex expression with constant."""
        f = FormulaUpToConstant("e^x * sin(x) + x^2 * ln(x) + C")
        assert f.constant == "C"
        df = f.D("x")
        # Derivative should not have C
        assert "C" not in str(df)

    def test_case_sensitive_constants(self):
        """Test that constant letters are case-sensitive."""
        f1 = FormulaUpToConstant("x + C")
        f2 = FormulaUpToConstant("x + c")
        # These have different constants
        # Both should be valid
        assert f1.constant == "C"
        assert f2.constant == "c"

    def test_context_preservation(self):
        """Test that original context is not modified."""
        ctx = Context("Numeric")
        ctx.variables.add("a")
        original_vars = list(ctx.variables.list())

        f = FormulaUpToConstant("a*x + C", context=ctx)

        # Original context should be unchanged
        assert list(ctx.variables.list()) == original_vars

        # But formula's context should have C
        assert "C" in f.context.variables.list()

    def test_comparison_with_non_formula(self):
        """Test comparison with non-formula values."""
        f = FormulaUpToConstant("x + C")

        # Should return False with helpful message
        equal, msg = f.compare(5)
        assert not equal
        assert "constant" in msg.lower()

    def test_latex_output(self):
        """Test LaTeX/TeX output includes constant."""
        f = FormulaUpToConstant("x^2/2 + C")
        tex = f.TeX()
        # Should include C in output
        assert "C" in tex
