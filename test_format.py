#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test format_math function."""

import sys
import re


def clean_latex(latex_str):
    """Clean up LaTeX for terminal display with mathematical notation."""
    # Remove \! (thin space) and \displaystyle
    latex_str = latex_str.replace(r'\!', '')
    latex_str = latex_str.replace(r'\displaystyle', '')

    # Convert \left( and \right) to just ( and )
    latex_str = latex_str.replace(r'\left(', '(')
    latex_str = latex_str.replace(r'\right)', ')')
    latex_str = latex_str.replace(r'\left[', '[')
    latex_str = latex_str.replace(r'\right]', ']')
    latex_str = latex_str.replace(r'\left\{', '{')
    latex_str = latex_str.replace(r'\right\}', '}')

    # Convert fractions: frac{num}{den} → (num)/(den)
    # Use regex to find nested fractions
    while 'frac{' in latex_str or r'\frac{' in latex_str:
        # Match \frac{...}{...} where ... can contain nested braces
        match = re.search(
            r'\\?frac\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', latex_str)
        if match:
            num = match.group(1).strip()
            den = match.group(2).strip()
            # Format as (num)/(den)
            replacement = f'({num})/({den})'
            latex_str = latex_str[:match.start()] + \
                replacement + latex_str[match.end():]
        else:
            # Fallback: simple replacement
            latex_str = latex_str.replace(r'\frac', 'frac')
            break

    # Convert Greek letters
    latex_str = latex_str.replace(r'\pi', 'π')
    latex_str = latex_str.replace(r'\theta', 'θ')

    # Simplify parentheses around single terms in fractions: (23π)/(6) → 23π/6
    # Helper to check if a term needs parentheses
    def needs_parens(term):
        term = term.strip()
        # Keep parens if empty or just parens
        if not term or term == '()':
            return True
        # Keep parens if term contains operators (but allow division for nested fractions)
        if any(op in term for op in ['+', '-', '*', '÷', '·', '×']):
            # Exception: if it's just a leading minus sign, that's okay
            if term.startswith('-') and not any(op in term[1:] for op in ['+', '-', '*', '÷', '·', '×']):
                return False
            return True
        # Keep parens if term contains spaces (likely multiple terms)
        if ' ' in term:
            return True
        # Keep parens for function calls (has parentheses)
        if '(' in term:
            return True
        return False

    # Simplify fractions: (num)/(den) → simplified
    # Match pattern with non-greedy matching for nested parens
    def simplify_match(match):
        full = match.group(0)
        num = match.group(1).strip()
        den = match.group(2).strip()

        # Simplify
        num_display = num if needs_parens(num) else num
        den_display = den if needs_parens(den) else den

        # Rebuild
        num_final = f'({num_display})' if needs_parens(
            num) else num_display
        den_final = f'({den_display})' if needs_parens(
            den) else den_display

        return f'{num_final}/{den_final}'

    # Apply multiple times to handle nested cases
    # Use a pattern that matches balanced parentheses better
    prev = None
    while prev != latex_str:
        prev = latex_str
        # Match simple (content)/(content) where content has no unmatched parens
        latex_str = re.sub(
            r'\(([^()]+)\)/\(([^()]+)\)', simplify_match, latex_str)

    # Clean up extra spaces
    latex_str = re.sub(r'\s+', ' ', latex_str).strip()
    return latex_str


def format_math(text):
    """Convert LaTeX math delimiters for terminal display."""
    # Inline math: \(...\) - use proper escaping
    text = re.sub(r'\\\((.+?)\\\)',
                  lambda m: f'[ {clean_latex(m.group(1))} ]', text)
    return text


# Test cases
test_inputs = [
    r'\(\frac{7 \pi}{6}\)',
    r'\(\frac{23\pi}{6}\)',
    r'\(-\frac{\pi}{2}\)',
]

print("Testing format_math with LaTeX inputs:\n")
for test in test_inputs:
    result = format_math(test)
    print(f"Input:  {test}")
    print(f"Output: {result}")
    print()
