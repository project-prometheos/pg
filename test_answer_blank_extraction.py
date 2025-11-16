#!/usr/bin/env python3
"""Test if answer blanks are being extracted and registered from PGML."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_translator"))

from pg.translator import PGTranslator

# Test the FractionAnswer problem
problem_file = "d:/pg/tutorial/sample-problems/Algebra/FractionAnswer.pg"
translator = PGTranslator()

print("=" * 70)
print("Testing answer blank extraction from PGML")
print("=" * 70)

# First pass: render problem without inputs
result = translator.translate(problem_file, seed=75965)

print(f"\nAfter first translation (without inputs):")
print(f"  Answer blanks: {len(result.answer_blanks)}")
for name, blank_info in result.answer_blanks.items():
    print(f"    {name}: {type(blank_info)}")

print(f"\n  Problem has {len(result.answer_blanks)} answer blank(s)")

# Second pass: check answers
print(f"\nBefore second translation (with inputs):")
user_answers = {"AnSwEr0001": "3/2"}
print(f"  User answers: {user_answers}")

result2 = translator.translate(problem_file, seed=75965, inputs=user_answers)

print(f"\nAfter second translation (with inputs):")
print(f"  Answer results: {result2.answer_results}")

if result2.answer_results:
    print(f"  ✓ Answer checking worked!")
    for name, ans_result in result2.answer_results.items():
        print(f"    {name}: score={ans_result.score}, correct={ans_result.correct}")
else:
    print(f"  ✗ No answer results!")
    if result2.errors:
        print(f"  Errors: {result2.errors}")
