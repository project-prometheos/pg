#!/usr/bin/env python3
"""Test pg_solve.py with user input."""
import sys
import subprocess
from pathlib import Path

# Run pg_solve with simulated input
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

# Provide the answer "3/2"
stdout, stderr = process.communicate(input="3/2\n", timeout=10)

print(stdout)
if stderr:
    print("STDERR:", stderr, file=sys.stderr)

# Check if answer checking worked
if "CORRECT" in stdout or "correct" in stdout or "score" in stdout.lower():
    print("\n✓ Answer checking WORKED!")
elif "Unable to check answers" in stdout:
    print("\n✗ Answer checking FAILED - still showing unable to check")
else:
    print("\n? Answer checking result unclear")
