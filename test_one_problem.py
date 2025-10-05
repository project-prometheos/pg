#!/usr/bin/env python3
"""Test a specific problem with verbose output."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_translator"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_pgml"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_macros"))

from pg_translator import PGTranslator

file_path = 'tutorial/sample-problems/IntegralCalc/IndefiniteIntegrals.pg'
seed = 1234

print(f"Testing: {file_path}")
print("=" * 70)

translator = PGTranslator()
result = translator.translate(file_path, seed=seed)

print(f"\nErrors: {result.errors}")
print(f"Statement HTML: {len(result.statement_html) if result.statement_html else 0} chars")
print(f"Answer blanks: {len(result.answer_blanks) if result.answer_blanks else 0}")
print(f"Solution HTML: {len(result.solution_html) if result.solution_html else 0} chars")

if result.statement_html:
    print(f"\nStatement (first 200 chars):")
    print(result.statement_html[:200])
