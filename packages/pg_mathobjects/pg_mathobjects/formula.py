"""
Formula class for symbolic expressions.

Represents mathematical expressions with variables, supporting evaluation,
substitution, reduction, and differentiation.
"""

from typing import Dict, Any, Optional, Union
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from .value import Value


class CMPWrapper:
    """
    Wrapper for .cmp that works as both property access and method call.

    Handles Perl idiom where ->cmp can be used without parentheses and
    chained with ->withPostFilter.
    """
    def __init__(self, formula, **default_options):
        self.formula = formula
        self.default_options = default_options

    def __call__(self, **options):
        """Call as cmp() to get answer checker."""
        from .answer_checker import FormulaAnswerChecker
        merged_options = {**self.default_options, **options}
        return FormulaAnswerChecker(self.formula, **merged_options)

    def withPostFilter(self, filter_function):
        """Chain with withPostFilter like Perl ->cmp->withPostFilter."""
        from .answer_checker import FormulaAnswerChecker
        checker = FormulaAnswerChecker(self.formula, **self.default_options)
        return checker.withPostFilter(filter_function)


class Formula(Value):
    """
    Symbolic formula MathObject.

    Represents a mathematical expression that contains variables and can be
    evaluated, substituted, reduced, and differentiated.
    """

    def __init__(self, expression: Union[str, sp.Expr], context=None):
        """
        Create a Formula.

        Args:
            expression: String expression or sympy expression
            context: Context (None = current)
        """
        super().__init__(context)

        # Store original string
        if isinstance(expression, str):
            self.expression = expression
            # Parse to sympy expression
            self._parse_expression()
        else:
            # Already a sympy expression
            self._tree = expression
            self.expression = str(expression)

    def _parse_expression(self):
        """Parse string expression to sympy tree."""
        try:
            # Get context functions and constants
            local_dict = {}

            # Add constants from context
            for name in self.context.constants.list():
                value = self.context.constants.get(name)
                if name == 'pi':
                    local_dict[name] = sp.pi
                elif name == 'e':
                    local_dict[name] = sp.E
                elif name == 'i':
                    local_dict[name] = sp.I
                else:
                    local_dict[name] = value

            # Add variables from context
            for name in self.context.variables.list():
                local_dict[name] = sp.Symbol(name)

            # Add standard math functions
            for func in ['sin', 'cos', 'tan', 'sec', 'csc', 'cot',
                         'arcsin', 'arccos', 'arctan',
                         'sinh', 'cosh', 'tanh',
                         'ln', 'log', 'exp', 'sqrt', 'abs']:
                if func == 'ln':
                    local_dict[func] = sp.ln
                elif func in self.context.functions.list():
                    # Map to sympy equivalents
                    local_dict[func] = getattr(
                        sp, func, None) or sp.Function(func)

            # Convert ^ to ** for exponentiation
            expr_str = self.expression.replace('^', '**')

            # Handle equations (formulas with =)
            # If the formula contains =, treat it as an equation
            if '=' in expr_str and '==' not in expr_str and '!=' not in expr_str and '<=' not in expr_str and '>=' not in expr_str:
                # Split on = and parse as equation
                parts = expr_str.split('=', 1)
                if len(parts) == 2:
                    transformations = standard_transformations + \
                        (implicit_multiplication_application,)
                    lhs = parse_expr(parts[0].strip(), local_dict=local_dict, transformations=transformations)
                    rhs = parse_expr(parts[1].strip(), local_dict=local_dict, transformations=transformations)
                    self._tree = sp.Eq(lhs, rhs)
                else:
                    # Fallback to regular parsing
                    transformations = standard_transformations + \
                        (implicit_multiplication_application,)
                    self._tree = parse_expr(
                        expr_str,
                        local_dict=local_dict,
                        transformations=transformations
                    )
            else:
                # Parse with implicit multiplication
                transformations = standard_transformations + \
                    (implicit_multiplication_application,)
                self._tree = parse_expr(
                    expr_str,
                    local_dict=local_dict,
                    transformations=transformations
                )

            # Validate polynomial form if required by context
            self._validate_polynomial()

        except Exception as e:
            raise ValueError(f"Error parsing formula '{self.expression}': {e}")

    def _validate_polynomial(self):
        """Validate polynomial form if context requires it."""
        if self.context.flags.get('limitedPolynomial'):
            from .limited_polynomial import validate_polynomial_formula
            is_valid, error = validate_polynomial_formula(self)
            if not is_valid:
                raise ValueError(f"Not a polynomial: {error}")

        # Also check for factored polynomial form if required
        if self.context.flags.get('polynomialFactors'):
            from .polynomial_factors import validate_factored_polynomial
            validate_factored_polynomial(self)

    def eval(self, **values) -> 'Value':
        """
        Evaluate the formula with given variable values.

        Args:
            **values: Variable assignments (e.g., x=5, y=3)

        Returns:
            Real if result is numeric, Formula if still symbolic
        """
        from .real import Real

        try:
            # Substitute values into sympy expression
            subs_dict = {}
            for var, val in values.items():
                if isinstance(val, Value):
                    val = val.value
                subs_dict[sp.Symbol(var)] = val

            result = self._tree.subs(subs_dict)

            # If result is numeric, return Real
            if result.is_number:
                return Real(float(result), self.context)

            # Otherwise return Formula
            return Formula(result, self.context)

        except Exception as e:
            raise ValueError(f"Error evaluating formula: {e}")

    def substitute(self, **substitutions) -> 'Formula':
        """
        Substitute expressions for variables.

        Args:
            **substitutions: Variable substitutions (e.g., x='2*y', y='t+1')

        Returns:
            New Formula with substitutions applied
        """
        try:
            subs_dict = {}
            for var, expr in substitutions.items():
                # Parse substitution expression
                if isinstance(expr, str):
                    sub_formula = Formula(expr, self.context)
                    subs_dict[sp.Symbol(var)] = sub_formula._tree
                elif isinstance(expr, Formula):
                    subs_dict[sp.Symbol(var)] = expr._tree
                elif isinstance(expr, (int, float)):
                    subs_dict[sp.Symbol(var)] = expr
                else:
                    from .real import Real
                    if isinstance(expr, Real):
                        subs_dict[sp.Symbol(var)] = expr.value
                    else:
                        subs_dict[sp.Symbol(var)] = expr

            result = self._tree.subs(subs_dict)
            return Formula(result, self.context)

        except Exception as e:
            raise ValueError(f"Error substituting in formula: {e}")

    def reduce(self) -> 'Formula':
        """
        Simplify/reduce the formula.

        Returns:
            Simplified Formula
        """
        try:
            simplified = sp.simplify(self._tree)
            return Formula(simplified, self.context)
        except Exception as e:
            raise ValueError(f"Error reducing formula: {e}")

    def D(self, var: str = 'x') -> 'Formula':
        """
        Differentiate the formula with respect to a variable.

        Args:
            var: Variable to differentiate with respect to

        Returns:
            Derivative as Formula
        """
        try:
            derivative = sp.diff(self._tree, sp.Symbol(var))
            return Formula(derivative, self.context)
        except Exception as e:
            raise ValueError(f"Error differentiating formula: {e}")

    def __str__(self) -> str:
        """String representation."""
        # Use sympy's string representation
        return str(self._tree)

    def __repr__(self) -> str:
        """Python representation."""
        return f"Formula('{self.expression}')"

    def TeX(self) -> str:
        """LaTeX representation."""
        return sp.latex(self._tree)

    # Arithmetic operations
    def __add__(self, other):
        """Add two formulas or a formula and a number."""
        if isinstance(other, Formula):
            return Formula(self._tree + other._tree, self.context)
        elif isinstance(other, (int, float)):
            return Formula(self._tree + other, self.context)
        else:
            from .real import Real
            if isinstance(other, Real):
                return Formula(self._tree + other.value, self.context)
        return NotImplemented

    def __radd__(self, other):
        """Right addition."""
        return self.__add__(other)

    def __sub__(self, other):
        """Subtract two formulas or a formula and a number."""
        if isinstance(other, Formula):
            return Formula(self._tree - other._tree, self.context)
        elif isinstance(other, (int, float)):
            return Formula(self._tree - other, self.context)
        else:
            from .real import Real
            if isinstance(other, Real):
                return Formula(self._tree - other.value, self.context)
        return NotImplemented

    def __rsub__(self, other):
        """Right subtraction."""
        if isinstance(other, (int, float)):
            return Formula(other - self._tree, self.context)
        else:
            from .real import Real
            if isinstance(other, Real):
                return Formula(other.value - self._tree, self.context)
        return NotImplemented

    def __mul__(self, other):
        """Multiply two formulas or a formula and a number."""
        if isinstance(other, Formula):
            return Formula(self._tree * other._tree, self.context)
        elif isinstance(other, (int, float)):
            return Formula(self._tree * other, self.context)
        else:
            from .real import Real
            if isinstance(other, Real):
                return Formula(self._tree * other.value, self.context)
        return NotImplemented

    def __rmul__(self, other):
        """Right multiplication."""
        return self.__mul__(other)

    def __truediv__(self, other):
        """Divide two formulas or a formula and a number."""
        if isinstance(other, Formula):
            return Formula(self._tree / other._tree, self.context)
        elif isinstance(other, (int, float)):
            return Formula(self._tree / other, self.context)
        else:
            from .real import Real
            if isinstance(other, Real):
                return Formula(self._tree / other.value, self.context)
        return NotImplemented

    def __rtruediv__(self, other):
        """Right division."""
        if isinstance(other, (int, float)):
            return Formula(other / self._tree, self.context)
        else:
            from .real import Real
            if isinstance(other, Real):
                return Formula(other.value / self._tree, self.context)
        return NotImplemented

    def __pow__(self, other):
        """Raise formula to a power."""
        if isinstance(other, Formula):
            return Formula(self._tree ** other._tree, self.context)
        elif isinstance(other, (int, float)):
            return Formula(self._tree ** other, self.context)
        else:
            from .real import Real
            if isinstance(other, Real):
                return Formula(self._tree ** other.value, self.context)
        return NotImplemented

    def __rpow__(self, other):
        """Right power."""
        if isinstance(other, (int, float)):
            return Formula(other ** self._tree, self.context)
        else:
            from .real import Real
            if isinstance(other, Real):
                return Formula(other.value ** self._tree, self.context)
        return NotImplemented

    def __neg__(self):
        """Negate the formula."""
        return Formula(-self._tree, self.context)

    @property
    def cmp(self):
        """
        Create an answer evaluator for this formula.

        Returns a CMPWrapper that can be:
        - Called as cmp() to get answer checker
        - Chained as cmp.withPostFilter(...) for Perl compatibility

        Returns:
            CMPWrapper that works as both callable and has withPostFilter
        """
        return CMPWrapper(self)
