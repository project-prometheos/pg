#!/usr/bin/env python3
"""Test PGML parsing issue with FractionAnswer.pg"""

import sys
from pathlib import Path

# Add packages to path
pg_root = Path(__file__).parent
sys.path.insert(0, str(pg_root / "packages"))

from pg.translator import PGTranslator

# Test FractionAnswer.pg
problem_path = pg_root / "tutorial" / "sample-problems" / "Algebra" / "FractionAnswer.pg"

print("=" * 80)
print("Testing FractionAnswer.pg")
print("=" * 80)

translator = PGTranslator()
result = translator.translate(str(problem_path), seed=1234)

print("\n=== ERRORS ===")
if result.errors:
    for error in result.errors:
        print(f"ERROR: {error}")
else:
    print("No errors")

print("\n=== STATEMENT ===")
print(result.statement[:500] if result.statement else "No statement")

print("\n=== ANSWER BLANKS ===")
for name, spec in result.answer_blanks.items():
    print(f"{name}: {spec}")

print("\n=== SOLUTION ===")
print(result.solution[:300] if result.solution else "No solution")

