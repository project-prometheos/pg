#!/usr/bin/env python3
"""Test two problems in sequence to see if caching causes issues."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_translator"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_pgml"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_macros"))

from pg_translator import PGTranslator

problems = [
    'tutorial/sample-problems/DiffCalc/AnswerWithUnits.pg',
    'tutorial/sample-problems/IntegralCalc/IndefiniteIntegrals.pg',
]

for file_path in problems:
    print(f"\n{'='*70}")
    print(f"Testing: {file_path}")
    print('='*70)
    
    translator = PGTranslator()  # New translator for each problem
    result = translator.translate(file_path, seed=1234)
    
    print(f"Statement: {len(result.statement_html) if result.statement_html else 0} chars")
    print(f"Answers: {len(result.answer_blanks) if result.answer_blanks else 0}")
    print(f"Solution: {len(result.solution_html) if result.solution_html else 0} chars")
    print(f"Errors: {result.errors}")
