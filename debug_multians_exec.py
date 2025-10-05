"""Debug MultiAnswer execution."""

from packages.pg_translator.pg_translator.in_process_sandbox import InProcessSandbox
from packages.pg_translator.pg_translator.preprocessor import PGPreprocessor

pg_code = """
$a = 8;
$num = Formula("8y-9");
$den = Formula("y-1");
$multians = MultiAnswer($num, $den);
"""

# First preprocess
preprocessor = PGPreprocessor()
result_pre = preprocessor.preprocess(pg_code)
python_code = result_pre.code
print("Preprocessed code:")
print(python_code)
print("\n" + "="*60 + "\n")

sandbox = InProcessSandbox()
result = sandbox.execute(pg_code, seed=0)

print("Variables:")
for k, v in result.variables.items():
    print(f"  {k}: {type(v).__name__} = {v}")
