"""
Compute() function for parsing and evaluating expressions.
"""

import re
from typing import Union
from .value import Value
from .real import Real


def Compute(expression: Union[str, int, float], context=None) -> Value:
    """
    Parse and evaluate a mathematical expression.

    If the expression is constant, returns a Real number.
    If the expression contains variables, returns a Formula.

    Args:
        expression: Expression to parse
        context: Context to use (None = current)

    Returns:
        Real or Formula

    Examples:
        >>> Compute("2+2")
        Real(4)

        >>> Compute("x^2")
        Formula("x^2")

        >>> Compute("sin(pi/2)")
        Real(1.0)
    """
    if context is None:
        from .context import get_current_context
        context = get_current_context()

    # If it's already a number, just return Real
    if isinstance(expression, (int, float)):
        return Real(expression, context)

    # Convert to string
    expr_str = str(expression).strip()

    # Try to parse as a simple number
    try:
        value = float(expr_str)
        return Real(value, context)
    except ValueError:
        pass

    # Check if it's a constant expression (no variables)
    if _is_constant_expression(expr_str, context):
        # Check reduceConstants flag - if it's off, keep as Formula
        reduce_constants = context.flags.get('reduceConstants')
        if reduce_constants is None:
            reduce_constants = 1  # Default is on

        if not reduce_constants:
            # Don't reduce - return as Formula to keep symbolic form
            from .formula import Formula
            return Formula(expr_str, context)

        # Evaluate as constant
        try:
            value = _evaluate_constant(expr_str, context)
            return Real(value, context)
        except Exception:
            pass

    # Otherwise, return as Formula
    from .formula import Formula
    return Formula(expr_str, context)


def _is_constant_expression(expr: str, context) -> bool:
    """Check if expression contains only constants (no variables)."""
    # Get list of variables from context
    variables = context.variables.list()

    # Remove constants, numbers, operators, functions, and parentheses
    stripped = expr

    # Remove function calls
    for func in context.functions.list():
        stripped = re.sub(rf'\b{func}\s*\(', '', stripped)

    # Remove constants
    for const in context.constants.list():
        stripped = stripped.replace(const, '')

    # Remove numbers (including decimals and scientific notation)
    stripped = re.sub(r'\b\d+\.?\d*([eE][+-]?\d+)?\b', '', stripped)

    # Remove operators and parentheses
    for char in '+-*/^()[], \t\n':
        stripped = stripped.replace(char, '')

    # If anything remains, it might be a variable
    if stripped:
        # Check if any remaining parts are variables
        parts = re.findall(r'\b\w+\b', stripped)
        for part in parts:
            if part in variables:
                return False

    return True


def _evaluate_constant(expr: str, context) -> float:
    """
    Evaluate a constant expression.

    This is a simple evaluator for constant expressions.
    Uses Python's eval() with a restricted namespace.
    """
    import math

    # Build safe namespace
    namespace = {
        # Constants
        'pi': math.pi,
        'e': math.e,
        # Functions
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'asin': math.asin,
        'acos': math.acos,
        'atan': math.atan,
        'sinh': math.sinh,
        'cosh': math.cosh,
        'tanh': math.tanh,
        'asinh': math.asinh,
        'acosh': math.acosh,
        'atanh': math.atanh,
        'exp': math.exp,
        'ln': math.log,
        'log': math.log,
        'log10': math.log10,
        'sqrt': math.sqrt,
        'abs': abs,
        'int': int,
        # Add context constants
        **{name: value for name, value in context.constants._constants.items()},
    }

    # Convert ^ to **
    expr = expr.replace('^', '**')

    # Evaluate safely
    try:
        result = eval(expr, {"__builtins__": {}}, namespace)
        return float(result)
    except Exception as e:
        raise ValueError(f"Cannot evaluate expression: {expr}") from e
