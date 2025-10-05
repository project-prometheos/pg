"""Test what Compute().cmp() returns."""

from pg_mathobjects import Compute

# Create a Compute object
formula = Compute('(x + 1)(x - 2)')
print(f"Formula type: {type(formula).__name__}")
print(f"Formula: {formula}")

# Call cmp()
checker = formula.cmp()
print(f"\nChecker type: {type(checker).__name__}")
print(f"Checker: {checker}")
print(f"Has check: {hasattr(checker, 'check')}")
print(f"Has cmp: {hasattr(checker, 'cmp')}")

# Test with custom checker
checker_custom = formula.cmp(checker=lambda correct, student, self: True)
print(f"\nCustom checker type: {type(checker_custom).__name__}")
print(f"Custom checker: {checker_custom}")
