"""Unit tests for numeric MathValue types."""

import math

import pytest

from pg_math import Complex, Infinity, Real, ToleranceMode


class TestReal:
    """Tests for Real numbers."""

    def test_create_real(self):
        """Test creating a Real number."""
        r = Real(3.14)
        assert r.value == 3.14

    def test_real_addition(self):
        """Test Real addition."""
        r1 = Real(2.0)
        r2 = Real(3.0)
        result = r1 + r2
        assert isinstance(result, Real)
        assert result.value == 5.0

    def test_real_addition_with_python(self):
        """Test Real addition with Python types."""
        r = Real(2.0)
        result = r + 3
        assert isinstance(result, Real)
        assert result.value == 5.0

        result2 = 3 + r
        assert isinstance(result2, Real)
        assert result2.value == 5.0

    def test_real_subtraction(self):
        """Test Real subtraction."""
        r1 = Real(5.0)
        r2 = Real(3.0)
        result = r1 - r2
        assert isinstance(result, Real)
        assert result.value == 2.0

    def test_real_multiplication(self):
        """Test Real multiplication."""
        r1 = Real(2.0)
        r2 = Real(3.0)
        result = r1 * r2
        assert isinstance(result, Real)
        assert result.value == 6.0

    def test_real_division(self):
        """Test Real division."""
        r1 = Real(6.0)
        r2 = Real(3.0)
        result = r1 / r2
        assert isinstance(result, Real)
        assert result.value == 2.0

    def test_real_division_by_zero(self):
        """Test division by zero returns Infinity."""
        r = Real(5.0)
        result = r / 0
        assert isinstance(result, Infinity)
        assert result.sign == 1

    def test_real_power(self):
        """Test Real exponentiation."""
        r = Real(2.0)
        result = r**3
        assert isinstance(result, Real)
        assert result.value == 8.0

    def test_real_negative_power_to_complex(self):
        """Test that negative numbers to fractional powers become Complex."""
        r = Real(-1.0)
        result = r**0.5
        assert isinstance(result, Complex)

    def test_real_negation(self):
        """Test unary negation."""
        r = Real(5.0)
        result = -r
        assert isinstance(result, Real)
        assert result.value == -5.0

    def test_real_abs(self):
        """Test absolute value."""
        r = Real(-5.0)
        result = abs(r)
        assert isinstance(result, Real)
        assert result.value == 5.0

    def test_real_comparison(self):
        """Test Real comparison operators."""
        r1 = Real(3.0)
        r2 = Real(5.0)

        assert r1 < r2
        assert r1 <= r2
        assert r2 > r1
        assert r2 >= r1
        assert not (r1 == r2)

    def test_real_fuzzy_comparison(self):
        """Test fuzzy comparison with tolerance."""
        r1 = Real(1.0)
        r2 = Real(1.001)

        # Should be equal with default tolerance (0.001 relative)
        assert r1.compare(r2, tolerance=0.01)

        # Should not be equal with stricter tolerance
        assert not r1.compare(r2, tolerance=0.0001)

    def test_real_absolute_tolerance(self):
        """Test absolute tolerance mode."""
        r1 = Real(1.0)
        r2 = Real(1.0005)

        assert r1.compare(r2, tolerance=0.001, mode=ToleranceMode.ABSOLUTE)
        assert not r1.compare(r2, tolerance=0.0001, mode=ToleranceMode.ABSOLUTE)

    def test_real_to_string(self):
        """Test string conversion."""
        assert Real(5.0).to_string() == "5"
        assert Real(3.14).to_string() == "3.14"

    def test_real_to_python(self):
        """Test Python conversion."""
        r = Real(3.14)
        assert r.to_python() == 3.14
        assert isinstance(r.to_python(), float)


class TestComplex:
    """Tests for Complex numbers."""

    def test_create_complex(self):
        """Test creating a Complex number."""
        c = Complex(3.0, 4.0)
        assert c.real == 3.0
        assert c.imag == 4.0

    def test_complex_addition(self):
        """Test Complex addition."""
        c1 = Complex(1.0, 2.0)
        c2 = Complex(3.0, 4.0)
        result = c1 + c2
        assert isinstance(result, Complex)
        assert result.real == 4.0
        assert result.imag == 6.0

    def test_complex_subtraction(self):
        """Test Complex subtraction."""
        c1 = Complex(5.0, 6.0)
        c2 = Complex(2.0, 3.0)
        result = c1 - c2
        assert isinstance(result, Complex)
        assert result.real == 3.0
        assert result.imag == 3.0

    def test_complex_multiplication(self):
        """Test Complex multiplication."""
        c1 = Complex(1.0, 2.0)
        c2 = Complex(3.0, 4.0)
        result = c1 * c2
        # (1 + 2i)(3 + 4i) = 3 + 4i + 6i + 8i^2 = 3 + 10i - 8 = -5 + 10i
        assert isinstance(result, Complex)
        assert result.real == -5.0
        assert result.imag == 10.0

    def test_complex_division(self):
        """Test Complex division."""
        c1 = Complex(1.0, 2.0)
        c2 = Complex(3.0, 4.0)
        result = c1 / c2
        assert isinstance(result, Complex)
        # Approximate values
        assert abs(result.real - 0.44) < 0.01
        assert abs(result.imag - 0.08) < 0.01

    def test_complex_abs(self):
        """Test Complex magnitude."""
        c = Complex(3.0, 4.0)
        result = abs(c)
        assert isinstance(result, Real)
        assert result.value == 5.0  # sqrt(3^2 + 4^2) = 5

    def test_complex_to_string(self):
        """Test string conversion."""
        assert Complex(3.0, 4.0).to_string() == "3 + 4i"
        assert Complex(3.0, -4.0).to_string() == "3 - 4i"
        assert Complex(0.0, 1.0).to_string() == "i"
        assert Complex(0.0, -1.0).to_string() == "-i"
        assert Complex(5.0, 0.0).to_string() == "5"

    def test_complex_to_python(self):
        """Test Python conversion."""
        c = Complex(3.0, 4.0)
        result = c.to_python()
        assert result == complex(3.0, 4.0)

    def test_real_promotes_to_complex(self):
        """Test that Real promotes to Complex in mixed operations."""
        r = Real(2.0)
        c = Complex(1.0, 1.0)
        result = r + c
        assert isinstance(result, Complex)
        assert result.real == 3.0
        assert result.imag == 1.0


class TestInfinity:
    """Tests for Infinity."""

    def test_create_infinity(self):
        """Test creating Infinity."""
        inf = Infinity(1)
        assert inf.sign == 1

        neg_inf = Infinity(-1)
        assert neg_inf.sign == -1

    def test_infinity_addition(self):
        """Test Infinity addition."""
        inf = Infinity(1)
        result = inf + 5
        assert isinstance(result, Infinity)
        assert result.sign == 1

    def test_infinity_minus_infinity(self):
        """Test inf - inf = undefined."""
        inf1 = Infinity(1)
        inf2 = Infinity(1)
        result = inf1 - inf2
        assert isinstance(result, Infinity)
        assert result.sign == 0  # Undefined

    def test_infinity_multiplication(self):
        """Test Infinity multiplication."""
        inf = Infinity(1)
        result = inf * 5
        assert isinstance(result, Infinity)
        assert result.sign == 1

        result2 = inf * (-5)
        assert result2.sign == -1

    def test_infinity_times_zero(self):
        """Test inf * 0 = undefined."""
        inf = Infinity(1)
        result = inf * 0
        assert isinstance(result, Infinity)
        assert result.sign == 0

    def test_infinity_division(self):
        """Test n / inf = 0."""
        inf = Infinity(1)
        result = 5 / inf
        assert isinstance(result, Real)
        assert result.value == 0.0

    def test_infinity_to_string(self):
        """Test string conversion."""
        assert Infinity(1).to_string() == "inf"
        assert Infinity(-1).to_string() == "-inf"
        assert Infinity(0).to_string() == "NaN"

    def test_infinity_to_python(self):
        """Test Python conversion."""
        assert Infinity(1).to_python() == float("inf")
        assert Infinity(-1).to_python() == float("-inf")
        assert math.isnan(Infinity(0).to_python())


class TestTypePromotion:
    """Tests for type promotion system."""

    def test_real_to_complex_promotion(self):
        """Test Real promotes to Complex."""
        r = Real(2.0)
        c = Complex(1.0, 1.0)

        promoted_r, _ = r.promote_types(c)
        assert isinstance(promoted_r, Complex)
        assert promoted_r.real == 2.0
        assert promoted_r.imag == 0.0

    def test_type_precedence_ordering(self):
        """Test type precedence values."""
        from pg_math import TypePrecedence

        assert TypePrecedence.REAL < TypePrecedence.COMPLEX
        assert TypePrecedence.COMPLEX < TypePrecedence.FORMULA
