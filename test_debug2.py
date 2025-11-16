#!/usr/bin/env python3
"""Debug test to trace the answer blank flow."""
import sys
sys.path.insert(0, 'packages/pg')

from pg.translator import PGTranslator

# Create translator
translator = PGTranslator()

print("=" * 70)
print("STEP 1: Initial translation (no inputs)")
print("=" * 70)

result1 = translator.translate(
    'tutorial/sample-problems/Algebra/FractionAnswer.pg',
    seed=42
)

print(f"Answer blanks: {result1.answer_blanks}")
print(f"Answer results: {result1.answer_results}")
print(f"Errors: {result1.errors[:3] if result1.errors else 'None'}")

if result1.answer_blanks:
    print("\nAnswer blank names:")
    for name in result1.answer_blanks.keys():
        print(f"  - '{name}'")

print("\n" + "=" * 70)
print("STEP 2: Translation with inputs")
print("=" * 70)

# Try with correct answer blank name
if result1.answer_blanks:
    blank_name = list(result1.answer_blanks.keys())[0]
    print(f"\nUsing answer blank name: '{blank_name}'")

    result2 = translator.translate(
        'tutorial/sample-problems/Algebra/FractionAnswer.pg',
        seed=42,
        inputs={blank_name: '3/2'}
    )

    print(f"Answer results: {result2.answer_results}")
    if result2.answer_results:
        for name, ans_result in result2.answer_results.items():
            print(f"  {name}:")
            print(f"    score={ans_result.score}")
            print(f"    correct={ans_result.correct}")
            print(f"    message='{ans_result.answer_message}'")
    else:
        print("  (No answer results)")

    print(f"\nErrors: {result2.errors[:3] if result2.errors else 'None'}")
