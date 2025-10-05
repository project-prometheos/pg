"""Test AnswerUpToMultiple checking directly."""

from packages.pg_translator.pg_translator.in_process_sandbox import InProcessSandbox
from packages.pg_translator.pg_translator.preprocessor import PGPreprocessor
from packages.pg_translator.pg_translator import PGTranslator
from pathlib import Path

pg_src = Path(
    'tutorial/sample-problems/Algebra/AnswerUpToMultiple.pg').read_text()
t = PGTranslator()

# Check what's in env.answers

preprocessor = PGPreprocessor()
prep = preprocessor.preprocess(pg_src)

sandbox = InProcessSandbox()
env = sandbox.execute(prep.code, seed=3157)

print("env.answers:", env.answers)
print("\nVariables with 'ans':")
for k, v in env.variables.items():
    if 'ans' in k.lower():
        print(f"  {k}: {type(v).__name__}")

# First, render to see what we have
result = t.translate_source(pg_src, seed=3157)
print("\nAnswer blanks:", result.answer_blanks)

# Now check an answer
result_with_check = t.translate_source(
    pg_src, seed=3157, inputs={'AnSwEr0001': 'x^2-x-2'})
print("\nAnswer results:", result_with_check.answer_results)
print("Score:", result_with_check.score)
print("Errors:", result_with_check.errors)
