"""Limited Polynomial Context - Restricts formulas to polynomial form.

This module provides a context that only allows polynomial expressions,
rejecting functions, fractional powers, and other non-polynomial operations.

Usage:
    from pg_mathobjects import Context

    ctx = Context('LimitedPolynomial')
    f = Formula('x^2 + 2*x + 1', ctx)  # OK
    g = Formula('sin(x)', ctx)  # Error: functions not allowed
"""

import sympy as sp
from typing import Tuple

from .context import Context
from .formula import Formula


def create_limited_polynomial_context(strict: bool = False) -> Context:
    """Create a LimitedPolynomial context.

    Args:
        strict: If True, disallow operations in coefficients

    Returns:
        Context configured for polynomial expressions
    """
    ctx = Context('Numeric')
    ctx.name = 'LimitedPolynomial' + ('-Strict' if strict else '')
    ctx.flags.set('limitedPolynomial', True)
    ctx.flags.set('strictCoefficients', strict)
    ctx.flags.set('singlePowers', False)

    return ctx


class PolynomialValidator:
    """Validates that expressions are in polynomial form."""

    def __init__(self, strict: bool = False, single_powers: bool = False):
        """Initialize validator.

        Args:
            strict: Disallow operations in coefficients
            single_powers: Allow only one term per degree
        """
        self.strict = strict
        self.single_powers = single_powers

    def validate(self, formula: Formula) -> Tuple[bool, str | None]:
        """Validate that formula is polynomial form.

        Args:
            formula: Formula to validate

        Returns:
            (is_valid, error_message) tuple
        """
        expr = formula._tree
        variables = self._get_variables(formula)

        # Check for disallowed functions FIRST (more specific errors)
        result = self._check_functions(expr, variables)
        if not result[0]:
            return result

        # Check power restrictions (before general polynomial check)
        result = self._check_powers(expr, variables)
        if not result[0]:
            return result

        # Check if polynomial in all variables (general check)
        result = self._is_polynomial_tree(expr, variables)
        if not result[0]:
            return result

        # Strict mode: check coefficient operations
        if self.strict:
            result = self._check_strict_coefficients(expr, variables)
            if not result[0]:
                return result

        # Single powers: check for duplicate degrees
        if self.single_powers:
            result = self._check_single_powers(expr, variables)
            if not result[0]:
                return result

        return True, None

    def _get_variables(self, formula: Formula) -> set:
        """Get variable symbols from formula context."""
        var_names = formula.context.variables.list()
        return {sp.Symbol(v) for v in var_names}

    def _is_polynomial_tree(self, expr: sp.Expr, variables: set) -> Tuple[bool, str | None]:
        """Check if expression is polynomial in given variables."""
        for var in variables:
            # Sympy's is_polynomial check
            if not expr.is_polynomial(var):
                return False, f"Expression is not a polynomial in {var}"
        return True, None

    def _check_functions(self, expr: sp.Expr, variables: set) -> Tuple[bool, str | None]:
        """Check that no non-polynomial functions are used on variables."""
        # Get all function applications
        functions = expr.atoms(sp.Function)

        for func in functions:
            # Check if function arguments contain variables
            func_args = func.args
            for arg in func_args:
                arg_vars = arg.free_symbols & variables
                if arg_vars:
                    # Function applied to variable - not allowed
                    func_name = func.func.__name__
                    # Map sympy names back to common names
                    name_map = {'log': 'ln'}
                    display_name = name_map.get(func_name, func_name)
                    # Use lowercase for common functions
                    if display_name in ['sin', 'cos', 'tan', 'ln', 'log', 'exp', 'sqrt', 'abs']:
                        return False, f"function '{display_name}' not allowed in a polynomial"
                    else:
                        return False, f"Cannot use function '{display_name}' in a polynomial"

        return True, None

    def _check_powers(self, expr: sp.Expr, variables: set) -> Tuple[bool, str | None]:
        """Check that all variable powers are non-negative integers."""
        powers = expr.atoms(sp.Pow)

        for pow_expr in powers:
            base, exponent = pow_expr.as_base_exp()

            # Only check powers of variables
            if base not in variables:
                continue

            # Exponent must be a positive integer
            if not exponent.is_Integer:
                return False, f"Exponent must be integer in a polynomial (got {exponent})"

            if exponent < 0:
                return False, f"Exponents must be non-negative in a polynomial (got {exponent})"

        return True, None

    def _check_strict_coefficients(self, expr: sp.Expr, variables: set) -> Tuple[bool, str | None]:
        """Check that coefficients don't contain operations (strict mode)."""
        # In strict mode, coefficients should be simple numbers
        # This is complex to check perfectly, so we'll do a simplified check

        # Get all terms
        if expr.is_Add:
            terms = expr.args
        else:
            terms = [expr]

        for term in terms:
            # Extract coefficient and monomial
            coeff, monomial = self._split_coefficient(term, variables)

            # Check if coefficient has operations
            if self._has_operations(coeff):
                return False, "Cannot use operations in coefficients (strict mode)"

        return True, None

    def _split_coefficient(self, term: sp.Expr, variables: set) -> Tuple[sp.Expr, sp.Expr]:
        """Split term into coefficient and monomial parts."""
        # Separate numeric coefficient from variable part
        coeff_parts = []
        var_parts = []

        if term.is_Mul:
            for factor in term.args:
                if factor.free_symbols & variables:
                    var_parts.append(factor)
                else:
                    coeff_parts.append(factor)
        else:
            if term.free_symbols & variables:
                var_parts.append(term)
                coeff_parts.append(sp.Integer(1))
            else:
                coeff_parts.append(term)

        coeff = sp.Mul(*coeff_parts) if coeff_parts else sp.Integer(1)
        monomial = sp.Mul(*var_parts) if var_parts else sp.Integer(1)

        return coeff, monomial

    def _has_operations(self, expr: sp.Expr) -> bool:
        """Check if expression contains arithmetic operations."""
        # Simple check: if expression is Add or Mul with multiple args, it has operations
        if isinstance(expr, (sp.Add, sp.Mul)) and len(expr.args) > 1:
            # But allow rational numbers (like 1/2)
            if expr.is_Rational:
                return False
            return True

        # Check for nested operations
        if isinstance(expr, sp.Pow):
            # Powers are operations
            return True

        return False

    def _check_single_powers(self, expr: sp.Expr, variables: set) -> Tuple[bool, str | None]:
        """Check that each degree appears at most once (singlePowers flag)."""
        # Expand and collect terms
        expanded = sp.expand(expr)

        for var in variables:
            # Get polynomial in this variable
            other_vars = [v for v in variables if v != var]
            if other_vars:
                # Multi-variable case
                domain_spec = 'ZZ[' + ','.join(str(v)
                                               for v in other_vars) + ']'
                poly = sp.Poly(expanded, var, domain=domain_spec)
            else:
                # Single variable case
                poly = sp.Poly(expanded, var, domain='ZZ')

            # Check degrees
            degrees = poly.as_dict()

            # In multivariate case, this is complex
            # For now, simple check: no duplicate total degrees in single variable case
            if len(variables) == 1:
                # degrees is {(n,): coeff}
                if len(degrees) != len(set(d[0] for d in degrees.keys())):
                    return False, "Polynomials must have at most one term of each degree (singlePowers flag)"

        return True, None


def validate_polynomial_formula(formula: Formula) -> Tuple[bool, str | None]:
    """Validate formula is polynomial (used by Formula when parsing).

    Args:
        formula: Formula to validate

    Returns:
        (is_valid, error_message) tuple
    """
    # Check if context requires polynomial validation
    if not formula.context.flags.get('limitedPolynomial'):
        return True, None

    # Get validation settings from context
    strict = formula.context.flags.get('strictCoefficients') or False
    single_powers = formula.context.flags.get('singlePowers') or False

    # Validate
    validator = PolynomialValidator(strict, single_powers)
    return validator.validate(formula)
