#!/usr/bin/env python3
"""Test py-asciimath for LaTeX conversion"""

from py_asciimath.translator.translator import Tex2ASCIIMath

# Create converter
conv = Tex2ASCIIMath(log=False, inplace=True)

# Test cases
test_cases = [
    (r"\tan\left(\frac{23\pi}{6}\right)", "Trig with fraction"),
    (r"\frac{23\pi}{6}", "Simple fraction"),
    (r"\tan(x)=1/\sqrt{3}", "Equation with sqrt"),
    (r"\cos(x)=-1/\sqrt{3}", "Another equation"),
    (r"[0,2\pi[", "Interval notation"),
    (r"-\frac{\pi}{2}", "Negative fraction"),
    (r"\frac{\pi}{2}", "Simple pi fraction"),
    (r"\sqrt{2}-1", "Sqrt expression"),
    (r"x^2 + 1", "Power"),
]

print("="*70)
print("Testing py-asciimath LaTeX to ASCII Conversion")
print("="*70)

for latex, description in test_cases:
    print(f"\n{description}:")
    print(f"  LaTeX:  {latex}")
    try:
        result = conv.translate(latex)
        print(f"  ASCII:  {result}")
    except Exception as e:
        print(f"  ERROR:  {e}")

print("\n" + "="*70)
