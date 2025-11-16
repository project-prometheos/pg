#!/usr/bin/env python3
"""Test pg_solve.py with unreduced fraction."""
import sys
import subprocess

# Run pg_solve with simulated input - UNREDUCED fraction
python_exe = r"C:\Users\mdahl\.conda\envs\pytorch-5090\python.exe"
pg_solve_path = r"d:\pg\pg_solve.py"
problem_path = r"d:\pg\tutorial\sample-problems\Algebra\FractionAnswer.pg"

process = subprocess.Popen(
    [python_exe, pg_solve_path, problem_path],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Provide the answer "6/4" (unreduced - should be marked INCORRECT)
stdout, stderr = process.communicate(input="6/4\n", timeout=10)

print(stdout)
if stderr:
    print("STDERR:", stderr, file=sys.stderr)

# Check if it correctly rejects unreduced fraction
if "INCORRECT" in stdout or "incorrect" in stdout:
    print("\n✓ Correctly rejected unreduced fraction")
elif "CORRECT" in stdout:
    print("\n✗ ERROR: Accepted unreduced fraction (should be incorrect)")
else:
    print("\n? Result unclear")
