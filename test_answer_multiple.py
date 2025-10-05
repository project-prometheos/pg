"""Debug AnswerUpToMultiple variable capture."""

from packages.pg_translator.pg_translator.in_process_sandbox import InProcessSandbox
from packages.pg_translator.pg_translator.preprocessor import PGPreprocessor
from pathlib import Path

pg_src = Path('tutorial/sample-problems/Algebra/AnswerUpToMultiple.pg').read_text()

# Preprocess
preprocessor = PGPreprocessor()
prep_result = preprocessor.preprocess(pg_src)

print("Preprocessed code (relevant part):")
lines = prep_result.code.split('\n')
for i, line in enumerate(lines[20:40], start=21):
    print(f"{i:3}: {line}")

# Execute
sandbox = InProcessSandbox()
exec_result = sandbox.execute(prep_result.code, seed=3157)

print("\n" + "="*60)
print("Variables captured:")
for k, v in exec_result.variables.items():
    if k in ['ans', 'Compute', 'Formula']:
        print(f"  {k}: {type(v).__name__} = {str(v)[:100]}")

print("\n" + "="*60)
print("Answers:")
for k, v in exec_result.answers.items():
    print(f"  {k}: {type(v).__name__} = {str(v)[:100]}")
