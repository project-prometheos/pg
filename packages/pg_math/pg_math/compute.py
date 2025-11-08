"""
Compute() function for parsing and evaluating expressions.

Port to pg_math from pg_mathobjects for Perl 1:1 parity.
"""

import re
import math
from typing import Union


def Compute(expression: Union[str, int, float], context=None):
    """
    Parse and evaluate a mathematical expression.

    If the expression is constant, returns a Real number.
    If the expression contains variables, returns a Formula.
    In Interval context, parses interval notation like [a, b], (a, b), etc.

    Args:
        expression: Expression to parse
        context: Context to use (None = current)

    Returns:
        Real, Formula, Interval, or other MathObject type

    Examples:
        >>> Compute("2+2")
        Real(4)

        >>> Compute("x^2")
        Formula("x^2")

        >>> Compute("sin(pi/2)")
        Real(1.0)

        >>> Context('Interval'); Compute("[1, 5]")
        Interval('[', 1, 5, ']')
    """
    if context is None:
        from .context import get_current_context
        context = get_current_context()

    # If it's already a number, just return Real
    if isinstance(expression, (int, float)):
        from .numeric import Real
        return Real(expression)

    # Convert to string
    expr_str = str(expression).strip()

    # Try to parse as a simple number
    try:
        value = float(expr_str)
        from .numeric import Real
        return Real(value)
    except ValueError:
        pass

    # Check for interval notation in Interval context
    # Pattern: [a, b], (a, b), [a, b), (a, b]
    if context.name == 'Interval' and _is_interval_notation(expr_str):
        return _parse_interval(expr_str, context)

    # Check if it's a constant expression (no variables)
    if _is_constant_expression(expr_str, context):
        # Evaluate as constant
        try:
            value = _evaluate_constant(expr_str, context)
            from .numeric import Real
            return Real(value)
        except Exception:
            pass

    # Otherwise, return as Formula
    from .formula import Formula

    # Get variables from context
    variables = context.variables.list()

    return Formula(expr_str, variables, context)


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
        **{name: context.constants.get(name) for name in context.constants.list()},
    }

    # Convert ^ to **
    expr = expr.replace('^', '**')

    # Evaluate safely
    try:
        result = eval(expr, {"__builtins__": {}}, namespace)
        return float(result)
    except Exception as e:
        raise ValueError(f"Cannot evaluate expression: {expr}") from e


def _is_interval_notation(expr: str) -> bool:
    """
    Check if expression looks like interval notation.

    Patterns: [a, b], (a, b), [a, b), (a, b]
    """
    expr = expr.strip()
    if len(expr) < 5:
        return False

    # Must start with [ or ( and end with ] or )
    if expr[0] not in ['[', '('] or expr[-1] not in [']', ')']:
        return False

    # Must contain a comma
    if ',' not in expr:
        return False

    # Extract content inside brackets
    content = expr[1:-1].strip()

    # Should have exactly one comma at the top level (not inside nested parentheses)
    depth = 0
    comma_count = 0
    for ch in content:
        if ch in '([':
            depth += 1
        elif ch in ')]':
            depth -= 1
        elif ch == ',' and depth == 0:
            comma_count += 1

    return comma_count == 1


def _parse_interval(expr: str, context) -> 'Interval':
    """
    Parse interval notation into an Interval object.

    Syntax: [a, b], (a, b), [a, b), (a, b]
    Endpoints can be numbers or inf/infinity/-inf/-infinity

    Reference: lib/Parser/List/Interval.pm, lib/Value/Interval.pm
    """
    from .sets import Interval

    expr = expr.strip()

    # Extract open/close brackets
    open_bracket = expr[0]
    close_bracket = expr[-1]

    # Extract content
    content = expr[1:-1].strip()

    # Split on comma (at top level only)
    depth = 0
    comma_pos = -1
    for i, ch in enumerate(content):
        if ch in '([':
            depth += 1
        elif ch in ')]':
            depth -= 1
        elif ch == ',' and depth == 0:
            comma_pos = i
            break

    if comma_pos < 0:
        raise ValueError(f"Intervals must have two endpoints: {expr}")

    left_str = content[:comma_pos].strip()
    right_str = content[comma_pos + 1:].strip()

    # Parse endpoints
    left_value = _parse_interval_endpoint(left_str, context)
    right_value = _parse_interval_endpoint(right_str, context)

    # Validate according to Perl rules (lib/Parser/List/Interval.pm::_check)

    # Check for positive infinity on left
    if left_value == float('inf'):
        raise ValueError("The left endpoint of an interval can't be positive infinity")

    # Check for negative infinity on right
    if right_value == float('-inf'):
        raise ValueError("The right endpoint of an interval can't be negative infinity")

    # Check that infinite endpoints are open
    if left_value == float('-inf') and open_bracket != '(':
        raise ValueError("Infinite endpoints must be open")

    if right_value == float('inf') and close_bracket != ')':
        raise ValueError("Infinite endpoints must be open")

    # Check ordering (left < right) for finite endpoints
    if left_value != float('-inf') and right_value != float('inf'):
        if left_value >= right_value:
            raise ValueError("Left endpoint must be less than right endpoint")

    # Create Interval object
    return Interval(open_bracket, left_value, right_value, close_bracket)


def _parse_interval_endpoint(s: str, context) -> float:
    """
    Parse an interval endpoint (number or infinity).

    Reference: lib/Value/Interval.pm::new
    """
    s = s.strip()

    # Check for infinity
    if s in ['inf', 'infinity']:
        return float('inf')
    if s in ['-inf', '-infinity']:
        return float('-inf')

    # Try to parse as number
    try:
        return float(s)
    except ValueError:
        pass

    # Try to evaluate as expression (e.g., "2*pi", "sqrt(2)")
    try:
        value = _evaluate_constant(s, context)
        return value
    except Exception:
        raise ValueError(f"Interval endpoints must be numbers or infinity: {s}")
