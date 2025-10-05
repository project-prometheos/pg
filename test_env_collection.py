#!/usr/bin/env python3
"""Debug environment collection in detail."""

import sys
sys.path.insert(0, 'packages/pg_translator')
sys.path.insert(0, 'packages/pg_pgml')
sys.path.insert(0, 'packages/pg_macros')

from pg_translator.preprocessor import PGPreprocessor
from pg_translator.in_process_sandbox import InProcessSandbox

problem_path = 'tutorial/sample-problems/IntegralCalc/IndefiniteIntegrals.pg'

with open(problem_path) as f:
    content = f.read()

prep = PGPreprocessor()
result = prep.preprocess(content)

print("=== INITIALIZING SANDBOX ===")
sandbox = InProcessSandbox()
print(f"Has _pg_core: {hasattr(sandbox, '_pg_core')}")
print(f"Has _stub_env: {hasattr(sandbox, '_stub_env')}")

if hasattr(sandbox, '_pg_core'):
    print(f"_pg_core module: {sandbox._pg_core}")
    print(f"_pg_core._pg_environment before: {sandbox._pg_core._pg_environment}")

print("\n=== EXECUTING CODE ===")
exec_result = sandbox.execute(result.code, 12345)

print("\n=== AFTER EXECUTION ===")
if hasattr(sandbox, '_pg_core'):
    print(f"_pg_core._pg_environment after: {sandbox._pg_core._pg_environment}")
    if sandbox._pg_core._pg_environment:
        env = sandbox._pg_core._pg_environment
        print(f"Environment output_array: {env.output_array}")
        print(f"Environment answers_hash: {list(env.answers_hash.keys())}")

if hasattr(sandbox, '_stub_env'):
    env = sandbox._stub_env
    print(f"Stub env output_array: {env.output_array}")
    print(f"Stub env answers_hash: {list(env.answers_hash.keys())}")

print(f"\n=== EXECUTION RESULT ===")
print(f"Success: {exec_result.success}")
print(f"Output text length: {len(exec_result.output_text)}")
print(f"Output text (first 200 chars): {exec_result.output_text[:200]}")
print(f"Answers: {list(exec_result.answers.keys())}")
print(f"Errors: {exec_result.errors}")
