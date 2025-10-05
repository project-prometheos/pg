#!/usr/bin/env python3
"""Debug environment collection."""

from pg_translator.in_process_sandbox import InProcessSandbox
from pg_translator.preprocessor import PGPreprocessor
import sys
sys.path.insert(0, 'packages/pg_translator')
sys.path.insert(0, 'packages/pg_pgml')


problem_path = 'tutorial/sample-problems/Algebra/AlgebraicFractionAnswer.pg'

with open(problem_path) as f:
    content = f.read()

prep = PGPreprocessor()
result = prep.preprocess(content)

print("=== PREPROCESSED CODE (first 500 chars) ===")
print(result.code[:500])
print("\n=== EXECUTING ===")

sandbox = InProcessSandbox()

# Check what environment we're using
print(f"Has _pg_core: {hasattr(sandbox, '_pg_core')}")
print(f"Has _stub_env: {hasattr(sandbox, '_stub_env')}")

exec_result = sandbox.execute(result.code, 12345)

print(f"\n=== AFTER EXECUTION ===")
print(f"Has _stub_env: {hasattr(sandbox, '_stub_env')}")
if hasattr(sandbox, '_stub_env'):
    env = sandbox._stub_env
    print(f"Stub env output_array length: {len(env.output_array)}")
    print(f"Stub env output_array content: {env.output_array}")
    print(f"Stub env answers_hash: {env.answers_hash}")

print(f"\n=== RESULT ===")
print(f"Success: {exec_result.success}")
print(f"Output text: {len(exec_result.output_text)} chars")
print(f"Answers: {len(exec_result.answers)}")
print(f"Errors: {exec_result.errors}")
