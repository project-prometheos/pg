#!/usr/bin/env python3
"""Debug script to test FractionAnswer problem."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_translator"))

from pg.translator import PGTranslator

problem_file = "d:/pg/tutorial/sample-problems/Algebra/FractionAnswer.pg"
translator = PGTranslator()

# First pass: render problem without inputs
print("=" * 70)
print("FIRST PASS: Render problem without inputs")
print("=" * 70)
result1 = translator.translate(problem_file, seed=75965)

print(f"Answer blanks found: {len(result1.answer_blanks)}")
for name, blank_info in result1.answer_blanks.items():
    print(f"  {name}: {blank_info}")

print(f"\nStatement (first 200 chars):\n{result1.statement_html[:200]}")

# Second pass: check answers
print("\n" + "=" * 70)
print("SECOND PASS: Check answers with inputs")
print("=" * 70)

user_answers = {"AnSwEr0001": "3/2"}
print(f"User answers: {user_answers}")

result2 = translator.translate(problem_file, seed=75965, inputs=user_answers)

print(f"Answer results: {result2.answer_results}")
if result2.answer_results:
    for name, ans_result in result2.answer_results.items():
        print(f"  {name}:")
        print(f"    score: {ans_result.score}")
        print(f"    correct: {ans_result.correct}")
        print(f"    message: {ans_result.answer_message}")
else:
    print("  No answer results!")

if result2.errors:
    print(f"\nErrors: {result2.errors}")
