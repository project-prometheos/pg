"""Test the checker function directly."""

from pg_mathobjects import Formula

# Create the formulas as they appear in the problem
a, b, c = 8, 9, 1

# This is what's happening - no interpolation
num_formula = Formula("a*y - b")  # Should be Formula("8*y - 9")
den_formula = Formula("y - c")     # Should be Formula("y - 1")

print("Correct formulas (with variables):")
print(f"  num: {num_formula}")
print(f"  den: {den_formula}")

# Student answers
student_num = Formula("8*y-9")
student_den = Formula("y-1")

print("\nStudent formulas:")
print(f"  num: {student_num}")
print(f"  den: {student_den}")

# Try comparing
print("\nComparison:")
print(f"  num == student_num: {num_formula == student_num}")
print(f"  den == student_den: {den_formula == student_den}")

# The formulas have different variables, so they won't match
# Let me try with proper values
print("\n" + "="*60)
print("With proper interpolation:")
num_proper = Formula(f"{a}*y - {b}")
den_proper = Formula(f"y - {c}")

print(f"  num_proper: {num_proper}")
print(f"  den_proper: {den_proper}")
print(f"  num_proper == student_num: {num_proper == student_num}")
print(f"  den_proper == student_den: {den_proper == student_den}")

# Try using cmp().check()
print("\n" + "="*60)
print("Using cmp().check():")
num_checker = num_proper.cmp()
result = num_checker.check("8y-9")  # Student input as string
print(f"  num check result: {result}")

den_checker = den_proper.cmp()
result2 = den_checker.check("y-1")
print(f"  den check result: {result2}")
