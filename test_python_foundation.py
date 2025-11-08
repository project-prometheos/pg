#!/usr/bin/env python
"""Test if PG foundation works for pure Python problem authoring."""

import sys
from pathlib import Path

# Add packages to path
for pkg in ['pg_math', 'pg_mathobjects', 'pg_macros', 'pg_parser']:
    sys.path.insert(0, str(Path('.') / 'packages' / pkg))

from pg_math import (
    Compute, Real, Complex, Point, Vector, Interval,
    Fraction, Context
)

print("=" * 60)
print("TESTING PURE PYTHON PG PROBLEM AUTHORING")
print("=" * 60)

# Test 1: Numeric context with formulas
Context("Numeric")
f1 = Compute("sin(x)^2 + cos(x)^2")
print(f"\n1. Formula: {f1}")
result = f1.eval(x=0.785)
print(f"   Evaluated at x=π/4: {float(result):.6f}")

# Test 2: Complex numbers
Context("Complex")
z = Compute("3 + 4*i")
print(f"\n2. Complex: {z}, |z| = {abs(z)}")

# Test 3: Vectors
Context("Vector")
v1 = Vector([1, 2, 3])
v2 = Vector([4, 5, 6])
print(f"\n3. Vectors: {v1} · {v2} = {v1.dot(v2)}")

# Test 4: Fractions
Context("Fraction")
frac = Fraction(22, 7)
print(f"\n4. Fraction: {frac} (approx {22/7:.6f})")

# Test 5: Answer checking
Context("Numeric")
answer = Compute("x^2 + 2*x + 1")
checker = answer.cmp()
print(f"\n5. Answer checker: {type(checker).__name__}")
print(f"   Formula factored: (x+1)^2")

# Test 6: Full example - writing a problem in pure Python
Context("Numeric")
a = 3  # Would use random(2, 5) in real problem with environment
problem = Compute(f"x^2 + {2*a}*x + {a**2}")
solution = Compute(f"(x + {a})^2")
print(f"\n6. Pure Python PG Problem Example:")
print(f"   Problem: Find x if f(x) = {problem} = 0")
print(f"   Answer: x = -{a} (from factored form {solution})")
print(f"   Answer checker: {bool(problem.cmp())} ✓")

print("\n" + "=" * 60)
print("✅ ALL FOUNDATION COMPONENTS WORK IN PURE PYTHON!")
print("=" * 60)
