"""Test Formula capture."""

from packages.pg_translator.pg_translator.in_process_sandbox import InProcessSandbox

pg_code = """
$a = 8;
$num = Formula("8y-9");
"""

sandbox = InProcessSandbox()
result = sandbox.execute(pg_code, seed=0)

print("Variables:")
for k, v in result.variables.items():
    print(f"  {k}: {type(v).__name__}")

if 'num' in result.variables:
    print("\nFound 'num'!")
    print("  Type:", type(result.variables['num']))
    print("  Has cmp:", hasattr(result.variables['num'], 'cmp'))
else:
    print("\n'num' NOT found in variables")
    print("\nAll captured variables:", list(result.variables.keys()))
