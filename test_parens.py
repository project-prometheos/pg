#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test the parentheses simplification logic"""

import re


def needs_parens(term):
    """Check if a term needs parentheses"""
    # Keep parens if term contains operators (but not just negative sign at start)
    if any(op in term for op in ['+', '*', '÷', '·', '×']):
        return True
    # Keep parens if term contains multiple adjacent minuses or minus not at start
    if '-' in term.lstrip('-'):
        return True
    # Keep parens if term contains spaces (likely multiple terms or function call)
    if ' ' in term.strip():
        return True
    # Keep parens if term contains function calls (has parentheses)
    if '(' in term:
        return True
    return False


def simplify_fraction_parens(match):
    num = match.group(1)
    den = match.group(2)

    # Simplify numerator and denominator
    num_simple = num if needs_parens(num) else num
    den_simple = den if needs_parens(den) else den

    # Add back parens only if needed
    num_display = f'({num_simple})' if needs_parens(num) else num_simple
    den_display = f'({den_simple})' if needs_parens(den) else den_simple

    return f'{num_display}/{den_display}'


# Test cases
test_cases = [
    ('(23π)/(6)', '23π/6'),  # Simple terms
    ('(a+b)/(c)', '(a+b)/c'),  # Operator in numerator
    ('(23π)/(a+b)', '23π/(a+b)'),  # Operator in denominator
    ('(sin(x))/(2)', '(sin(x))/2'),  # Function call
    ('(a)/(b)', 'a/b'),  # Single variables
    ('(-5)/(3)', '(-5)/3'),  # Negative number
    ('(a-b)/(c)', '(a-b)/c'),  # Subtraction
]

print("="*70)
print("Testing Parentheses Simplification")
print("="*70)

for input_expr, expected in test_cases:
    result = re.sub(r'\(([^)]+)\)/\(([^)]+)\)',
                    simplify_fraction_parens, input_expr)
    status = "✓" if result == expected else "✗"
    print(f"{status} {input_expr:20} → {result:20} (expected: {expected})")
