"""
Numeric MathValue types: Real, Complex, Infinity.

These are the fundamental numeric types in the MathObjects system.

Reference: lib/Value/Real.pm, lib/Value/Complex.pm, lib/Value/Infinity.pm
"""

from __future__ import annotations

import math
from typing import Any

from .value import MathValue, ToleranceMode, TypePrecedence


class Real(MathValue):
    """
    Real number value.

    The most common mathematical type, represents floating-point numbers
    with fuzzy comparison support.

    Reference: lib/Value/Real.pm
    """

    type_precedence = TypePrecedence.REAL

    def __init__(self, value: float | int):
        """
        Initialize a Real number.

        Args:
            value: Numeric value (will be converted to float)
        """
        self.value = float(value)

    def promote(self, other: MathValue) -> MathValue:
        """Promote Real to another type."""
        if isinstance(other, Complex):
            return Complex(self.value, 0.0)
        elif isinstance(other, Infinity):
            # Real doesn't promote to Infinity
            return self
        else:
            # For Point, Vector, etc., promotion happens at that level
            return self

    def compare(
        self, other: MathValue, tolerance: float = 0.001, mode: str = ToleranceMode.RELATIVE
    ) -> bool:
        """Fuzzy comparison of real numbers."""
        # Promote types if needed
        if not isinstance(other, Real):
            self_promoted, other_promoted = self.promote_types(other)
            if self_promoted is not self:
                return self_promoted.compare(other_promoted, tolerance, mode)
            # Can't promote, not comparable
            return False

        return fuzzy_compare(self.value, other.value, tolerance, mode)

    def to_string(self) -> str:
        """Convert to string."""
        # Remove .0 for integers
        if self.value == int(self.value) and abs(self.value) < 1e10:
            return str(int(self.value))
        return str(self.value)

    def to_tex(self) -> str:
        """Convert to LaTeX."""
        return self.to_string()

    def to_python(self) -> float:
        """Convert to Python float."""
        return self.value

    # Arithmetic operators

    def __add__(self, other: Any) -> MathValue:
        """Addition."""
        if isinstance(other, (int, float)):
            return Real(self.value + other)
        elif isinstance(other, Real):
            return Real(self.value + other.value)
        elif isinstance(other, MathValue):
            # Promote and retry
            self_promoted, other_promoted = self.promote_types(other)
            if self_promoted is not self:
                return self_promoted + other_promoted
            raise TypeError(f"Cannot add Real and {type(other)}")
        else:
            return NotImplemented

    def __radd__(self, other: Any) -> MathValue:
        """Right addition."""
        return self.__add__(other)

    def __sub__(self, other: Any) -> MathValue:
        """Subtraction."""
        if isinstance(other, (int, float)):
            return Real(self.value - other)
        elif isinstance(other, Real):
            return Real(self.value - other.value)
        elif isinstance(other, MathValue):
            self_promoted, other_promoted = self.promote_types(other)
            if self_promoted is not self:
                return self_promoted - other_promoted
            raise TypeError(f"Cannot subtract {type(other)} from Real")
        else:
            return NotImplemented

    def __rsub__(self, other: Any) -> MathValue:
        """Right subtraction."""
        if isinstance(other, (int, float)):
            return Real(other - self.value)
        else:
            return NotImplemented

    def __mul__(self, other: Any) -> MathValue:
        """Multiplication."""
        if isinstance(other, (int, float)):
            return Real(self.value * other)
        elif isinstance(other, Real):
            return Real(self.value * other.value)
        elif isinstance(other, MathValue):
            self_promoted, other_promoted = self.promote_types(other)
            if self_promoted is not self:
                return self_promoted * other_promoted
            raise TypeError(f"Cannot multiply Real and {type(other)}")
        else:
            return NotImplemented

    def __rmul__(self, other: Any) -> MathValue:
        """Right multiplication."""
        return self.__mul__(other)

    def __truediv__(self, other: Any) -> MathValue:
        """Division."""
        if isinstance(other, (int, float)):
            if other == 0:
                # Division by zero -> infinity
                return Infinity(1 if self.value > 0 else -1 if self.value < 0 else 0)
            return Real(self.value / other)
        elif isinstance(other, Real):
            if other.value == 0:
                return Infinity(1 if self.value > 0 else -1 if self.value < 0 else 0)
            return Real(self.value / other.value)
        elif isinstance(other, MathValue):
            self_promoted, other_promoted = self.promote_types(other)
            if self_promoted is not self:
                return self_promoted / other_promoted
            raise TypeError(f"Cannot divide Real by {type(other)}")
        else:
            return NotImplemented

    def __rtruediv__(self, other: Any) -> MathValue:
        """Right division."""
        if isinstance(other, (int, float)):
            if self.value == 0:
                return Infinity(1 if other > 0 else -1 if other < 0 else 0)
            return Real(other / self.value)
        else:
            return NotImplemented

    def __pow__(self, other: Any) -> MathValue:
        """Exponentiation."""
        if isinstance(other, (int, float)):
            result = self.value**other
            # Check if result is complex (e.g., (-1)^0.5)
            if isinstance(result, complex):
                return Complex(result.real, result.imag)
            return Real(result)
        elif isinstance(other, Real):
            result = self.value ** other.value
            if isinstance(result, complex):
                return Complex(result.real, result.imag)
            return Real(result)
        elif isinstance(other, MathValue):
            self_promoted, other_promoted = self.promote_types(other)
            if self_promoted is not self:
                return self_promoted**other_promoted
            raise TypeError(f"Cannot raise Real to {type(other)}")
        else:
            return NotImplemented

    def __rpow__(self, other: Any) -> MathValue:
        """Right exponentiation."""
        if isinstance(other, (int, float)):
            result = other**self.value
            if isinstance(result, complex):
                return Complex(result.real, result.imag)
            return Real(result)
        else:
            return NotImplemented

    def __neg__(self) -> Real:
        """Unary negation."""
        return Real(-self.value)

    def __pos__(self) -> Real:
        """Unary positive."""
        return Real(self.value)

    def __abs__(self) -> Real:
        """Absolute value."""
        return Real(abs(self.value))

    # Comparison operators (with tolerance)

    def __lt__(self, other: Any) -> bool:
        """Less than."""
        if isinstance(other, (int, float)):
            return self.value < other
        elif isinstance(other, Real):
            return self.value < other.value
        else:
            return NotImplemented

    def __le__(self, other: Any) -> bool:
        """Less than or equal."""
        return self.__eq__(other) or self.__lt__(other)

    def __gt__(self, other: Any) -> bool:
        """Greater than."""
        if isinstance(other, (int, float)):
            return self.value > other
        elif isinstance(other, Real):
            return self.value > other.value
        else:
            return NotImplemented

    def __ge__(self, other: Any) -> bool:
        """Greater than or equal."""
        return self.__eq__(other) or self.__gt__(other)


class Complex(MathValue):
    """
    Complex number value.

    Represents numbers with real and imaginary parts.

    Reference: lib/Value/Complex.pm
    """

    type_precedence = TypePrecedence.COMPLEX

    def __init__(self, real: float | int, imag: float | int = 0.0):
        """
        Initialize a Complex number.

        Args:
            real: Real part
            imag: Imaginary part (default 0)
        """
        self.real = float(real)
        self.imag = float(imag)

    def promote(self, other: MathValue) -> MathValue:
        """Complex is high in hierarchy, doesn't promote to much."""
        # Complex doesn't promote to Point, Vector, etc.
        return self

    def compare(
        self, other: MathValue, tolerance: float = 0.001, mode: str = ToleranceMode.RELATIVE
    ) -> bool:
        """Fuzzy comparison of complex numbers."""
        if isinstance(other, Real):
            # Promote Real to Complex
            other = Complex(other.value, 0.0)

        if not isinstance(other, Complex):
            return False

        # Compare both real and imaginary parts
        return fuzzy_compare(
            self.real, other.real, tolerance, mode
        ) and fuzzy_compare(self.imag, other.imag, tolerance, mode)

    def to_string(self) -> str:
        """Convert to string."""
        if self.imag == 0:
            return Real(self.real).to_string()
        elif self.real == 0:
            if self.imag == 1:
                return "i"
            elif self.imag == -1:
                return "-i"
            else:
                return f"{Real(self.imag).to_string()}i"
        else:
            imag_str = Real(abs(self.imag)).to_string()
            if abs(self.imag) == 1:
                imag_str = ""
            sign = "+" if self.imag > 0 else "-"
            return f"{Real(self.real).to_string()} {sign} {imag_str}i"

    def to_tex(self) -> str:
        """Convert to LaTeX."""
        # Similar to string, but with proper formatting
        return self.to_string()

    def to_python(self) -> complex:
        """Convert to Python complex."""
        return complex(self.real, self.imag)

    # Arithmetic operators

    def __add__(self, other: Any) -> MathValue:
        """Addition."""
        if isinstance(other, (int, float)):
            return Complex(self.real + other, self.imag)
        elif isinstance(other, Real):
            return Complex(self.real + other.value, self.imag)
        elif isinstance(other, Complex):
            return Complex(self.real + other.real, self.imag + other.imag)
        else:
            return NotImplemented

    def __radd__(self, other: Any) -> MathValue:
        """Right addition."""
        return self.__add__(other)

    def __sub__(self, other: Any) -> MathValue:
        """Subtraction."""
        if isinstance(other, (int, float)):
            return Complex(self.real - other, self.imag)
        elif isinstance(other, Real):
            return Complex(self.real - other.value, self.imag)
        elif isinstance(other, Complex):
            return Complex(self.real - other.real, self.imag - other.imag)
        else:
            return NotImplemented

    def __rsub__(self, other: Any) -> MathValue:
        """Right subtraction."""
        if isinstance(other, (int, float)):
            return Complex(other - self.real, -self.imag)
        elif isinstance(other, Real):
            return Complex(other.value - self.real, -self.imag)
        else:
            return NotImplemented

    def __mul__(self, other: Any) -> MathValue:
        """Multiplication."""
        if isinstance(other, (int, float)):
            return Complex(self.real * other, self.imag * other)
        elif isinstance(other, Real):
            return Complex(self.real * other.value, self.imag * other.value)
        elif isinstance(other, Complex):
            # (a + bi)(c + di) = (ac - bd) + (ad + bc)i
            real_part = self.real * other.real - self.imag * other.imag
            imag_part = self.real * other.imag + self.imag * other.real
            return Complex(real_part, imag_part)
        else:
            return NotImplemented

    def __rmul__(self, other: Any) -> MathValue:
        """Right multiplication."""
        return self.__mul__(other)

    def __truediv__(self, other: Any) -> MathValue:
        """Division."""
        if isinstance(other, (int, float)):
            if other == 0:
                # Division by zero
                raise ZeroDivisionError("Complex division by zero")
            return Complex(self.real / other, self.imag / other)
        elif isinstance(other, Real):
            if other.value == 0:
                raise ZeroDivisionError("Complex division by zero")
            return Complex(self.real / other.value, self.imag / other.value)
        elif isinstance(other, Complex):
            # (a + bi) / (c + di) = [(a + bi)(c - di)] / (c^2 + d^2)
            denom = other.real**2 + other.imag**2
            if denom == 0:
                raise ZeroDivisionError("Complex division by zero")
            real_part = (self.real * other.real + self.imag * other.imag) / denom
            imag_part = (self.imag * other.real - self.real * other.imag) / denom
            return Complex(real_part, imag_part)
        else:
            return NotImplemented

    def __rtruediv__(self, other: Any) -> MathValue:
        """Right division."""
        if isinstance(other, (int, float)):
            return Complex(other, 0.0) / self
        elif isinstance(other, Real):
            return Complex(other.value, 0.0) / self
        else:
            return NotImplemented

    def __pow__(self, other: Any) -> MathValue:
        """Exponentiation (using Python's complex power)."""
        if isinstance(other, (int, float)):
            result = complex(self.real, self.imag) ** other
            return Complex(result.real, result.imag)
        elif isinstance(other, Real):
            result = complex(self.real, self.imag) ** other.value
            return Complex(result.real, result.imag)
        elif isinstance(other, Complex):
            result = complex(self.real, self.imag) ** complex(other.real, other.imag)
            return Complex(result.real, result.imag)
        else:
            return NotImplemented

    def __rpow__(self, other: Any) -> MathValue:
        """Right exponentiation."""
        if isinstance(other, (int, float)):
            result = other ** complex(self.real, self.imag)
            return Complex(result.real, result.imag)
        elif isinstance(other, Real):
            result = other.value ** complex(self.real, self.imag)
            return Complex(result.real, result.imag)
        else:
            return NotImplemented

    def __neg__(self) -> Complex:
        """Unary negation."""
        return Complex(-self.real, -self.imag)

    def __pos__(self) -> Complex:
        """Unary positive."""
        return Complex(self.real, self.imag)

    def __abs__(self) -> Real:
        """Absolute value (magnitude)."""
        return Real(math.sqrt(self.real**2 + self.imag**2))


class Infinity(MathValue):
    """
    Infinity value.

    Represents positive infinity, negative infinity, or undefined (0*inf).

    Reference: lib/Value/Infinity.pm
    """

    type_precedence = TypePrecedence.INFINITY

    def __init__(self, sign: int = 1):
        """
        Initialize Infinity.

        Args:
            sign: 1 for +inf, -1 for -inf, 0 for undefined
        """
        if sign > 0:
            self.sign = 1
        elif sign < 0:
            self.sign = -1
        else:
            self.sign = 0

    def promote(self, other: MathValue) -> MathValue:
        """Infinity doesn't promote."""
        return self

    def compare(
        self, other: MathValue, tolerance: float = 0.001, mode: str = ToleranceMode.RELATIVE
    ) -> bool:
        """Infinity comparison."""
        if isinstance(other, Infinity):
            return self.sign == other.sign
        return False

    def to_string(self) -> str:
        """Convert to string."""
        if self.sign == 1:
            return "inf"
        elif self.sign == -1:
            return "-inf"
        else:
            return "NaN"

    def to_tex(self) -> str:
        """Convert to LaTeX."""
        if self.sign == 1:
            return r"\infty"
        elif self.sign == -1:
            return r"-\infty"
        else:
            return r"\text{NaN}"

    def to_python(self) -> float:
        """Convert to Python float."""
        if self.sign == 1:
            return float("inf")
        elif self.sign == -1:
            return float("-inf")
        else:
            return float("nan")

    # Arithmetic operators

    def __add__(self, other: Any) -> MathValue:
        """Addition with infinity."""
        if isinstance(other, (int, float, Real)):
            return self
        elif isinstance(other, Infinity):
            if self.sign == other.sign:
                return self
            else:
                # inf + (-inf) = undefined
                return Infinity(0)
        else:
            return NotImplemented

    def __radd__(self, other: Any) -> MathValue:
        """Right addition."""
        return self.__add__(other)

    def __sub__(self, other: Any) -> MathValue:
        """Subtraction."""
        if isinstance(other, (int, float, Real)):
            return self
        elif isinstance(other, Infinity):
            if self.sign == -other.sign:
                return self
            else:
                # inf - inf = undefined
                return Infinity(0)
        else:
            return NotImplemented

    def __rsub__(self, other: Any) -> MathValue:
        """Right subtraction."""
        return -self

    def __mul__(self, other: Any) -> MathValue:
        """Multiplication."""
        if isinstance(other, (int, float)):
            if other == 0:
                return Infinity(0)  # 0 * inf = undefined
            return Infinity(self.sign * (1 if other > 0 else -1))
        elif isinstance(other, Real):
            if other.value == 0:
                return Infinity(0)
            return Infinity(self.sign * (1 if other.value > 0 else -1))
        elif isinstance(other, Infinity):
            return Infinity(self.sign * other.sign)
        else:
            return NotImplemented

    def __rmul__(self, other: Any) -> MathValue:
        """Right multiplication."""
        return self.__mul__(other)

    def __truediv__(self, other: Any) -> MathValue:
        """Division."""
        if isinstance(other, (int, float, Real)):
            return self
        elif isinstance(other, Infinity):
            return Infinity(0)  # inf / inf = undefined
        else:
            return NotImplemented

    def __rtruediv__(self, other: Any) -> MathValue:
        """Right division."""
        # n / inf = 0
        return Real(0.0)

    def __pow__(self, other: Any) -> MathValue:
        """Exponentiation."""
        if isinstance(other, (int, float, Real)):
            # inf^positive = inf, inf^negative = 0, inf^0 = undefined
            if isinstance(other, Real):
                exp = other.value
            else:
                exp = other

            if exp > 0:
                return self
            elif exp < 0:
                return Real(0.0)
            else:
                return Infinity(0)  # undefined
        else:
            return NotImplemented

    def __rpow__(self, other: Any) -> MathValue:
        """Right exponentiation."""
        # base^inf
        if isinstance(other, (int, float, Real)):
            base = other.value if isinstance(other, Real) else other
            if abs(base) > 1:
                return self
            elif abs(base) < 1:
                return Real(0.0)
            else:
                return Infinity(0)  # undefined
        else:
            return NotImplemented

    def __neg__(self) -> Infinity:
        """Unary negation."""
        return Infinity(-self.sign)

    def __pos__(self) -> Infinity:
        """Unary positive."""
        return self

    def __abs__(self) -> Infinity:
        """Absolute value."""
        if self.sign == 0:
            return self
        return Infinity(1)


# Helper function for fuzzy comparison


def fuzzy_compare(a: float, b: float, tolerance: float, mode: str) -> bool:
    """
    Compare two floats with tolerance.

    Args:
        a: First value
        b: Second value
        tolerance: Tolerance value
        mode: Comparison mode (relative, absolute, sigfigs)

    Returns:
        True if values are equal within tolerance
    """
    # Exact equality
    if a == b:
        return True

    if mode == ToleranceMode.ABSOLUTE:
        return abs(a - b) < tolerance

    elif mode == ToleranceMode.RELATIVE:
        # Avoid division by zero
        if b == 0:
            return abs(a) < tolerance
        return abs((a - b) / b) < tolerance

    elif mode == ToleranceMode.SIGFIGS:
        # Significant figures mode
        if a == b:
            return True
        diff = abs(a - b)
        if diff == 0:
            return True
        avg = (abs(a) + abs(b)) / 2
        if avg == 0:
            return diff < 10 ** (-tolerance)
        return math.floor(math.log10(diff / avg)) < -tolerance

    else:
        raise ValueError(f"Unknown tolerance mode: {mode}")
