"""Test variable capture with debug."""

from packages.pg_translator.pg_translator.in_process_sandbox import InProcessSandbox
from packages.pg_translator.pg_translator.preprocessor import PGPreprocessor

pg_code = """
$a = 8;
$num = Formula("8y-9");
"""

# Preprocess first
preprocessor = PGPreprocessor()
prep_result = preprocessor.preprocess(pg_code)
python_code = prep_result.code

print("Python code:")
print(python_code)
print("\n" + "="*60)

sandbox = InProcessSandbox()

# Execute the preprocessed code
result = sandbox.execute(python_code, seed=0)

print("\nNamespace has 'num':", 'num' in sandbox.namespace)
if 'num' in sandbox.namespace:
    num_val = sandbox.namespace['num']
    print(f"  Type: {type(num_val)}")
    print(f"  Has cmp: {hasattr(num_val, 'cmp')}")

print("\nResult variables:", list(result.variables.keys()))
print("Result success:", result.success)
print("Result errors:", result.errors)
