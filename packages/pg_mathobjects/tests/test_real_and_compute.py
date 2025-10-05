"""
Tests for Real class and Compute function.
"""

import pytest
from pg_mathobjects import Context, Real, Compute


class TestRealCreation:
    """Test creating Real numbers."""

    def test_real_from_int(self):
        """Test creating Real from int."""
        r = Real(5)
        assert r.value == 5.0

    def test_real_from_float(self):
        """Test creating Real from float."""
        r = Real(3.14)
        assert r.value == 3.14

    def test_real_from_string(self):
        """Test creating Real from string."""
        r = Real("2.5")
        assert r.value == 2.5

    def test_real_string_repr(self):
        """Test string representation."""
        r = Real(5)
        assert str(r) == "5"

        r2 = Real(3.14)
        assert "3.14" in str(r2)


class TestRealArithmetic:
    """Test Real arithmetic operations."""

    def test_real_addition(self):
        """Test adding Real numbers."""
        r1 = Real(5)
        r2 = Real(3)
        r3 = r1 + r2
        assert r3.value == 8.0

    def test_real_addition_with_int(self):
        """Test adding Real and int."""
        r1 = Real(5)
        r2 = r1 + 3
        assert r2.value == 8.0

    def test_real_subtraction(self):
        """Test subtracting Real numbers."""
        r1 = Real(5)
        r2 = Real(3)
        r3 = r1 - r2
        assert r3.value == 2.0

    def test_real_multiplication(self):
        """Test multiplying Real numbers."""
        r1 = Real(5)
        r2 = Real(3)
        r3 = r1 * r2
        assert r3.value == 15.0

    def test_real_division(self):
        """Test dividing Real numbers."""
        r1 = Real(6)
        r2 = Real(3)
        r3 = r1 / r2
        assert r3.value == 2.0

    def test_real_power(self):
        """Test Real exponentiation."""
        r1 = Real(2)
        r2 = r1 ** 3
        assert r2.value == 8.0

    def test_real_negation(self):
        """Test negating Real."""
        r1 = Real(5)
        r2 = -r1
        assert r2.value == -5.0

    def test_real_absolute_value(self):
        """Test absolute value of Real."""
        r1 = Real(-5)
        r2 = abs(r1)
        assert r2.value == 5.0


class TestRealComparison:
    """Test Real comparison operations."""

    def test_real_equality(self):
        """Test Real equality."""
        r1 = Real(5)
        r2 = Real(5)
        assert r1 == r2

    def test_real_equality_with_tolerance(self):
        """Test Real equality with tolerance."""
        Context('Numeric')
        Context().flags.set(tolerance=0.01, tolType='absolute')

        r1 = Real(5)
        r2 = Real(5.005)
        assert r1 == r2

    def test_real_inequality(self):
        """Test Real inequality."""
        r1 = Real(5)
        r2 = Real(6)
        assert r1 != r2

    def test_real_less_than(self):
        """Test Real less than."""
        r1 = Real(5)
        r2 = Real(6)
        assert r1 < r2
        assert not r2 < r1

    def test_real_greater_than(self):
        """Test Real greater than."""
        r1 = Real(6)
        r2 = Real(5)
        assert r1 > r2
        assert not r2 > r1


class TestCompute:
    """Test Compute function."""

    def test_compute_integer(self):
        """Test Compute with integer."""
        result = Compute(5)
        assert isinstance(result, Real)
        assert result.value == 5.0

    def test_compute_float(self):
        """Test Compute with float."""
        result = Compute(3.14)
        assert isinstance(result, Real)
        assert result.value == 3.14

    def test_compute_string_number(self):
        """Test Compute with string number."""
        result = Compute("42")
        assert isinstance(result, Real)
        assert result.value == 42.0

    def test_compute_simple_addition(self):
        """Test Compute with simple addition."""
        result = Compute("2+3")
        assert isinstance(result, Real)
        assert result.value == 5.0

    def test_compute_multiplication(self):
        """Test Compute with multiplication."""
        result = Compute("3*4")
        assert isinstance(result, Real)
        assert result.value == 12.0

    def test_compute_with_parentheses(self):
        """Test Compute with parentheses."""
        result = Compute("(2+3)*4")
        assert isinstance(result, Real)
        assert result.value == 20.0

    def test_compute_with_power(self):
        """Test Compute with exponentiation."""
        result = Compute("2^3")
        assert isinstance(result, Real)
        assert result.value == 8.0

    def test_compute_with_function(self):
        """Test Compute with math function."""
        result = Compute("sqrt(4)")
        assert isinstance(result, Real)
        assert result.value == 2.0

    def test_compute_with_constant(self):
        """Test Compute with constant."""
        result = Compute("2*pi")
        assert isinstance(result, Real)
        assert abs(result.value - 6.28318) < 0.01  # Looser tolerance

    def test_compute_with_variable_returns_formula(self):
        """Test Compute with variable returns Formula."""
        from pg_mathobjects.formula import Formula
        result = Compute("x+1")
        assert isinstance(result, Formula)
        assert "x" in str(result) and "1" in str(result)


class TestRealAnswerChecker:
    """Test Real answer checking."""

    def test_real_cmp_correct_answer(self):
        """Test correct answer."""
        correct = Real(42)
        checker = correct.cmp()
        result = checker.check("42")
        assert result['correct'] is True
        assert result['score'] == 1.0

    def test_real_cmp_incorrect_answer(self):
        """Test incorrect answer."""
        correct = Real(42)
        checker = correct.cmp()
        result = checker.check("43")
        assert result['correct'] is False
        assert result['score'] == 0.0

    def test_real_cmp_with_tolerance(self):
        """Test answer within tolerance."""
        Context('Numeric')
        Context().flags.set(tolerance=0.01, tolType='absolute')

        correct = Real(42)
        checker = correct.cmp()
        result = checker.check("42.005")
        assert result['correct'] is True

    def test_real_cmp_invalid_input(self):
        """Test invalid input."""
        correct = Real(42)
        checker = correct.cmp()
        result = checker.check("not a number")
        assert result['correct'] is False
        assert 'message' in result
