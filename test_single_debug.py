#!/usr/bin/env python3
"""Debug single problem to see rendered output."""

from pg_translator.in_process_sandbox import InProcessSandbox
from pg_translator.preprocessor import PGPreprocessor
import sys
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_translator"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_macros"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_answer"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_math"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_pgml"))


# Test a problem that shows "no content"
problem_file = "tutorial/sample-problems/IntegralCalc/IndefiniteIntegrals.pg"

print("="*70)
print(f"TESTING: {problem_file}")
print("="*70)

with open(problem_file, "r", encoding="utf-8") as f:
    pg_code = f.read()

print("\n--- ORIGINAL PG CODE (first 500 chars) ---")
print(pg_code[:500])

preprocessor = PGPreprocessor()
python_code = preprocessor.preprocess(pg_code).code

print("\n--- PREPROCESSED PYTHON CODE ---")
print(python_code)

sandbox = InProcessSandbox()
exec_result = sandbox.execute(python_code, seed=1234)

print("\n--- EXECUTION RESULT ---")
print(f"Success: {exec_result.success}")
print(f"Output length: {len(exec_result.output_text)} chars")
print(f"\n--- RENDERED OUTPUT ---")
print(exec_result.output_text)

if exec_result.errors:
    print(f"\n--- ERRORS ---")
    print(exec_result.errors)

# Show some variables
print("\n--- CONTEXT VARIABLES ---")
interesting_vars = [k for k in sandbox.namespace.keys()
                    if not k.startswith('_') and k not in ['DOCUMENT', 'ENDDOCUMENT', 'TEXT', 'PGML']]
for var in interesting_vars[:10]:
    print(f"  {var}: {sandbox.namespace[var]}")
