"""
Formula type for the WeBWorK PG MathObjects system.

Formula wraps an AST (Abstract Syntax Tree) for deferred evaluation, providing:
- Variable substitution
- Differentiation (using SymPy)
- Simplification/reduction
- Multiple evaluation modes
- Multiple output formats

Reference: lib/Value/Formula.pm (1,156 lines) in legacy Perl codebase
"""

from __future__ import annotations

import random
import types
from typing import Any, Callable

try:
    import sympy as sp
    from sympy.parsing.sympy_parser import parse_expr

    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False

from .value import MathValue, ToleranceMode, TypePrecedence


class Formula(MathValue):
    """
    Formula represents a mathematical expression with deferred evaluation.

    Unlike numeric types (Real, Complex) which have immediate values, Formula
    stores an expression that can be:
    - Evaluated with variable bindings
    - Differentiated with respect to variables
    - Simplified/reduced
    - Substituted with other values

    Examples:
        >>> f = Formula("x^2 + 2*x + 1")
        >>> f.eval(x=3)  # Returns Real(16)
        >>> f.diff("x")  # Returns Formula("2*x + 2")
        >>> f.substitute("x", Real(5))  # Returns Formula("36")
    """

    type_precedence = TypePrecedence.FORMULA

    def __init__(
        self,
        expression: str | Any,
        variables: list[str] | None = None,
        context: Any | None = None,
    ):
        """
        Create a Formula from an expression.

        Args:
            expression: Mathematical expression (string or AST node or SymPy expr)
            variables: List of variable names in the expression
            context: Mathematical context (for parsing and evaluation)
        """
        self.expression = expression
        self.variables = variables or []
        self.context = context

        # If expression is a string and SymPy is available, parse it
        if isinstance(expression, str) and SYMPY_AVAILABLE:
            try:
                self._sympy_expr = parse_expr(
                    expression,
                    transformations="all",
                    local_dict={var: sp.Symbol(var) for var in self.variables},
                )
            except Exception:
                # Fallback: store as string
                self._sympy_expr = None
        else:
            self._sympy_expr = expression if SYMPY_AVAILABLE and isinstance(expression, sp.Expr) else None

    def eval(self, **bindings: float | MathValue) -> MathValue:
        """
        Evaluate the formula with variable bindings.

        Args:
            **bindings: Variable name → value mappings

        Returns:
            Result as MathValue (Real, Complex, etc.)

        Example:
            >>> f = Formula("x^2 + 1")
            >>> f.eval(x=3)
            Real(10)
        """
        if self._sympy_expr is not None:
            # Use SymPy evaluation
            sympy_bindings = {}
            for var, value in bindings.items():
                if isinstance(value, MathValue):
                    sympy_bindings[sp.Symbol(var)] = value.to_python()
                else:
                    sympy_bindings[sp.Symbol(var)] = value

            result = self._sympy_expr.subs(sympy_bindings)

            # Convert back to MathValue
            if result.is_number:
                from .numeric import Real

                return Real(float(result))
            else:
                # Still symbolic - return as Formula
                return Formula(result, self.variables, self.context)
        else:
            # Fallback: string-based evaluation
            # This requires the pg_parser package
            try:
                from pg_parser.parser import Parser
                from pg_parser.visitors import EvalVisitor

                parser = Parser(self.context)
                ast = parser.parse(self.expression)

                # Convert MathValue bindings to float
                eval_bindings = {}
                for var, value in bindings.items():
                    if isinstance(value, MathValue):
                        eval_bindings[var] = value.to_python()
                    else:
                        eval_bindings[var] = value

                visitor = EvalVisitor(eval_bindings, self.context)
                result = ast.accept(visitor)

                # Convert to MathValue
                return MathValue.from_python(result)
            except ImportError:
                raise RuntimeError("Cannot evaluate Formula: neither SymPy nor pg_parser available")

    def reduce(self) -> Formula:
        """
        Simplify/reduce the formula.

        Returns:
            Simplified Formula

        Example:
            >>> f = Formula("x + x")
            >>> f.reduce()
            Formula("2*x")
        """
        if self._sympy_expr is not None:
            simplified = sp.simplify(self._sympy_expr)
            return Formula(simplified, self.variables, self.context)
        else:
            # No simplification without SymPy
            return self

    def substitute(self, var: str, value: MathValue | float) -> Formula:
        """
        Substitute a variable with a value.

        Args:
            var: Variable name
            value: Value to substitute

        Returns:
            New Formula with substitution

        Example:
            >>> f = Formula("x^2 + y")
            >>> f.substitute("x", 2)
            Formula("4 + y")
        """
        if self._sympy_expr is not None:
            python_value = value.to_python() if isinstance(value, MathValue) else value
            substituted = self._sympy_expr.subs(sp.Symbol(var), python_value)

            # Update variable list
            new_vars = [v for v in self.variables if v != var]

            return Formula(substituted, new_vars, self.context)
        else:
            # Fallback: can't substitute without SymPy
            raise NotImplementedError("Substitution requires SymPy")

    def diff(self, var: str) -> Formula:
        """
        Differentiate with respect to a variable.

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Derivative as Formula

        Example:
            >>> f = Formula("x^2")
            >>> f.diff("x")
            Formula("2*x")
        """
        if not SYMPY_AVAILABLE:
            raise RuntimeError("Differentiation requires SymPy")

        if self._sympy_expr is not None:
            derivative = sp.diff(self._sympy_expr, sp.Symbol(var))
            return Formula(derivative, self.variables, self.context)
        else:
            raise RuntimeError("Cannot differentiate: expression not parsed")

    def integrate(self, var: str) -> Formula:
        """
        Integrate with respect to a variable.

        Args:
            var: Variable to integrate with respect to

        Returns:
            Integral as Formula

        Example:
            >>> f = Formula("2*x")
            >>> f.integrate("x")
            Formula("x^2")
        """
        if not SYMPY_AVAILABLE:
            raise RuntimeError("Integration requires SymPy")

        if self._sympy_expr is not None:
            integral = sp.integrate(self._sympy_expr, sp.Symbol(var))
            return Formula(integral, self.variables, self.context)
        else:
            raise RuntimeError("Cannot integrate: expression not parsed")

    # MathValue interface implementation

    def promote(self, other: MathValue) -> MathValue:
        """
        Formula is the highest precedence type, so no promotion needed.
        """
        return self

    def compare(
        self, other: MathValue, tolerance: float = 0.001, mode: str = ToleranceMode.RELATIVE
    ) -> bool:
        """
        Compare two formulas for equality.

        Two formulas are equal if:
        1. They are symbolically equivalent (using SymPy), OR
        2. They evaluate to the same value at multiple test points

        Args:
            other: Other value to compare
            tolerance: Tolerance for numeric comparison
            mode: Tolerance mode

        Returns:
            True if formulas are equivalent
        """
        if not isinstance(other, Formula):
            # Try to promote other to Formula
            if isinstance(other, MathValue):
                other = Formula(str(other.to_python()), [], self.context)
            else:
                return False

        # Try symbolic comparison first
        if SYMPY_AVAILABLE and self._sympy_expr is not None and other._sympy_expr is not None:
            difference = sp.simplify(self._sympy_expr - other._sympy_expr)
            if difference == 0:
                return True

        # Fall back to test point evaluation
        if self.variables:
            # Test at multiple points
            import random

            random.seed(12345)  # Deterministic testing
            test_points = 5

            for _ in range(test_points):
                # Generate random test values
                bindings = {var: random.uniform(-10, 10) for var in self.variables}

                try:
                    val1 = self.eval(**bindings)
                    val2 = other.eval(**bindings)

                    if not val1.compare(val2, tolerance, mode):
                        return False
                except (ValueError, ZeroDivisionError):
                    # Skip test points that cause errors
                    continue

            return True
        else:
            # No variables - compare constant values
            try:
                val1 = self.eval()
                val2 = other.eval()
                return val1.compare(val2, tolerance, mode)
            except Exception:
                return False

    def to_string(self) -> str:
        """Convert to human-readable string."""
        if self._sympy_expr is not None:
            return str(self._sympy_expr)
        else:
            return str(self.expression)

    def to_tex(self) -> str:
        """Convert to LaTeX representation."""
        if SYMPY_AVAILABLE and self._sympy_expr is not None:
            return sp.latex(self._sympy_expr)
        else:
            # Fallback: use pg_parser TeXVisitor
            try:
                from pg_parser.parser import Parser
                from pg_parser.visitors import TeXVisitor

                parser = Parser(self.context)
                ast = parser.parse(self.expression)
                visitor = TeXVisitor(self.context)
                return ast.accept(visitor)
            except ImportError:
                return str(self.expression)

    def to_python(self) -> Any:
        """
        Convert to Python representation.

        If formula has no variables, returns the evaluated value.
        Otherwise, returns the expression string.
        """
        if not self.variables:
            try:
                return self.eval().to_python()
            except Exception:
                pass

        return self.to_string()

    # Operator overloading

    def __add__(self, other: Any) -> Formula:
        """Addition: self + other"""
        if not isinstance(other, MathValue):
            from .numeric import Real

            other = Real(float(other))

        if SYMPY_AVAILABLE and self._sympy_expr is not None:
            if isinstance(other, Formula) and other._sympy_expr is not None:
                result = self._sympy_expr + other._sympy_expr
            else:
                result = self._sympy_expr + other.to_python()

            # Combine variable lists
            combined_vars = list(set(self.variables) | set(getattr(other, "variables", [])))
            return Formula(result, combined_vars, self.context)
        else:
            # Fallback: string concatenation
            return Formula(f"({self.to_string()}) + ({other.to_string()})", self.variables, self.context)

    def __radd__(self, other: Any) -> Formula:
        """Right addition: other + self"""
        return self.__add__(other)

    def __sub__(self, other: Any) -> Formula:
        """Subtraction: self - other"""
        if not isinstance(other, MathValue):
            from .numeric import Real

            other = Real(float(other))

        if SYMPY_AVAILABLE and self._sympy_expr is not None:
            if isinstance(other, Formula) and other._sympy_expr is not None:
                result = self._sympy_expr - other._sympy_expr
            else:
                result = self._sympy_expr - other.to_python()

            combined_vars = list(set(self.variables) | set(getattr(other, "variables", [])))
            return Formula(result, combined_vars, self.context)
        else:
            return Formula(f"({self.to_string()}) - ({other.to_string()})", self.variables, self.context)

    def __rsub__(self, other: Any) -> Formula:
        """Right subtraction: other - self"""
        if not isinstance(other, MathValue):
            from .numeric import Real

            other = Real(float(other))

        return Formula.from_math_value(other).__sub__(self)

    def __mul__(self, other: Any) -> Formula:
        """Multiplication: self * other"""
        if not isinstance(other, MathValue):
            from .numeric import Real

            other = Real(float(other))

        if SYMPY_AVAILABLE and self._sympy_expr is not None:
            if isinstance(other, Formula) and other._sympy_expr is not None:
                result = self._sympy_expr * other._sympy_expr
            else:
                result = self._sympy_expr * other.to_python()

            combined_vars = list(set(self.variables) | set(getattr(other, "variables", [])))
            return Formula(result, combined_vars, self.context)
        else:
            return Formula(f"({self.to_string()}) * ({other.to_string()})", self.variables, self.context)

    def __rmul__(self, other: Any) -> Formula:
        """Right multiplication: other * self"""
        return self.__mul__(other)

    def __truediv__(self, other: Any) -> Formula:
        """Division: self / other"""
        if not isinstance(other, MathValue):
            from .numeric import Real

            other = Real(float(other))

        if SYMPY_AVAILABLE and self._sympy_expr is not None:
            if isinstance(other, Formula) and other._sympy_expr is not None:
                result = self._sympy_expr / other._sympy_expr
            else:
                result = self._sympy_expr / other.to_python()

            combined_vars = list(set(self.variables) | set(getattr(other, "variables", [])))
            return Formula(result, combined_vars, self.context)
        else:
            return Formula(f"({self.to_string()}) / ({other.to_string()})", self.variables, self.context)

    def __rtruediv__(self, other: Any) -> Formula:
        """Right division: other / self"""
        if not isinstance(other, MathValue):
            from .numeric import Real

            other = Real(float(other))

        return Formula.from_math_value(other).__truediv__(self)

    def __pow__(self, other: Any) -> Formula:
        """Exponentiation: self ** other"""
        if not isinstance(other, MathValue):
            from .numeric import Real

            other = Real(float(other))

        if SYMPY_AVAILABLE and self._sympy_expr is not None:
            if isinstance(other, Formula) and other._sympy_expr is not None:
                result = self._sympy_expr ** other._sympy_expr
            else:
                result = self._sympy_expr ** other.to_python()

            combined_vars = list(set(self.variables) | set(getattr(other, "variables", [])))
            return Formula(result, combined_vars, self.context)
        else:
            return Formula(f"({self.to_string()}) ** ({other.to_string()})", self.variables, self.context)

    def __rpow__(self, other: Any) -> Formula:
        """Right exponentiation: other ** self"""
        if not isinstance(other, MathValue):
            from .numeric import Real

            other = Real(float(other))

        return Formula.from_math_value(other).__pow__(self)

    def __neg__(self) -> Formula:
        """Unary negation: -self"""
        if SYMPY_AVAILABLE and self._sympy_expr is not None:
            return Formula(-self._sympy_expr, self.variables, self.context)
        else:
            return Formula(f"-({self.to_string()})", self.variables, self.context)

    def __pos__(self) -> Formula:
        """Unary positive: +self"""
        return self

    def __abs__(self) -> Formula:
        """Absolute value: abs(self)"""
        if SYMPY_AVAILABLE and self._sympy_expr is not None:
            return Formula(sp.Abs(self._sympy_expr), self.variables, self.context)
        else:
            return Formula(f"abs({self.to_string()})", self.variables, self.context)

    @classmethod
    def from_math_value(cls, value: MathValue) -> Formula:
        """Convert a MathValue to a Formula."""
        if isinstance(value, Formula):
            return value

        if SYMPY_AVAILABLE:
            python_val = value.to_python()
            if isinstance(python_val, (int, float)):
                return cls(sp.sympify(python_val), [], None)
            else:
                return cls(str(python_val), [], None)
        else:
            return cls(str(value.to_python()), [], None)
