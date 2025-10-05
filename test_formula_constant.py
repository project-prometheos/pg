"""Debug FormulaUpToConstant issue."""

from pg_mathobjects import FormulaUpToConstant, Formula
from pg_mathobjects.context import Context

# Set up context with x as a variable
ctx = Context()
ctx.variables.add('x')

print("Context variables:", list(ctx.variables._vars.keys()))

# Try creating FormulaUpToConstant
try:
    func = FormulaUpToConstant('e^x')
    print(f"Success! Formula: {func}")
    print(f"Constant: {func.constant}")
except Exception as e:
    print(f"Error: {e}")

# Try with explicit constant
try:
    func2 = FormulaUpToConstant('e^x + C')
    print(f"\nWith C: {func2}")
    print(f"Constant: {func2.constant}")
except Exception as e:
    print(f"Error with C: {e}")
