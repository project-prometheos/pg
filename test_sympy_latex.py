#!/usr/bin/env python3
"""Test SymPy for LaTeX conversion"""

from sympy.parsing.latex import parse_latex
from sympy import pretty, latex as sympy_latex
import sympy as sp

# Test cases
test_cases = [
    (r"\frac{23\pi}{6}", "Simple fraction"),
    (r"\tan\left(\frac{23\pi}{6}\right)", "Trig with fraction"),
    (r"\tan(x)", "Trig function"),
    (r"1/\sqrt{3}", "Division with sqrt"),
    (r"-\frac{\pi}{2}", "Negative fraction"),
    (r"\frac{\pi}{2}", "Simple pi fraction"),
    (r"\sqrt{2}-1", "Sqrt expression"),
    (r"x^2 + 1", "Power"),
]

print("="*70)
print("Testing SymPy LaTeX Parsing")
print("="*70)

for latex_str, description in test_cases:
    print(f"\n{description}:")
    print(f"  LaTeX:     {latex_str}")
    try:
        expr = parse_latex(latex_str)
        print(f"  SymPy:     {expr}")
        print(f"  str():     {str(expr)}")
        print(f"  ASCII:     {sp.pretty(expr, use_unicode=False)}")
        # Try custom formatting
        simple = str(expr).replace('**', '^').replace('*', '·')
        print(f"  Custom:    {simple}")
    except Exception as e:
        print(f"  ERROR:     {type(e).__name__}: {e}")

print("\n" + "="*70)
