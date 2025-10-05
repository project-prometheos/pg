#!/usr/bin/env python3
"""Debug LinearApprox.pg"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_translator"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_pgml"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_macros"))

from pg_translator.preprocessor import PGPreprocessor
from pg_translator.in_process_sandbox import InProcessSandbox

with open('tutorial/sample-problems/DiffCalc/LinearApprox.pg') as f:
    content = f.read()

prep = PGPreprocessor()
result = prep.preprocess(content)

print("=== PREPROCESSED CODE (lines 30-50) ===")
lines = result.code.split('\n')
for i in range(29, min(50, len(lines))):
    print(f"{i+1:3d}: {lines[i]}")

print("\n=== EXECUTING ===")
sandbox = InProcessSandbox()
exec_result = sandbox.execute(result.code, 1234)

print(f"\nSuccess: {exec_result.success}")
print(f"Output: {len(exec_result.output_text)} chars")
print(f"Answers: {len(exec_result.answers)}")
if exec_result.errors:
    print(f"Errors: {exec_result.errors[:500]}")

if exec_result.output_text:
    print(f"\nOutput (first 200 chars):")
    print(exec_result.output_text[:200])
