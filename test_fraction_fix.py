#!/usr/bin/env python3
"""Test the fraction reduction fix."""
import sys
sys.path.insert(0, 'packages/pg')

from pg.math.fraction import Fraction
from pg.math.context import get_current_context

# Test the FractionAnswerChecker with studentsMustReduceFractions
print("Testing FractionAnswerChecker with studentsMustReduceFractions...")

# Set up context
Context('Fraction-NoDecimals')
context = get_current_context()

# Create a correct fraction answer
correct = Compute('3/2')
print(f"Correct answer: {correct}")
print(f"Correct type: {type(correct)}")

# Create a checker with studentsMustReduceFractions enabled
checker = correct.cmp(studentsMustReduceFractions=True, showFractionReductionWarnings=True)
print(f"Checker type: {type(checker)}")
print(f"Checker options: {checker.options}")

# Test with reduced fraction (should pass)
result1 = checker.check("3/2")
print(f"\nTest 1: Student enters '3/2' (reduced):")
print(f"  Result: {result1}")
print(f"  Expected: {{'correct': True, 'score': 1.0, 'message': ''}}")

# Test with unreduced fraction (should fail)
result2 = checker.check("12/8")
print(f"\nTest 2: Student enters '12/8' (unreduced):")
print(f"  Result: {result2}")
print(f"  Expected: {{'correct': False, 'score': 0.0, 'message': '...not reduced...'}}")

# Test with another unreduced fraction (should fail)
result3 = checker.check("6/4")
print(f"\nTest 3: Student enters '6/4' (unreduced):")
print(f"  Result: {result3}")
print(f"  Expected: {{'correct': False, 'score': 0.0, 'message': '...not reduced...'}}")

print("\nAll tests complete!")
