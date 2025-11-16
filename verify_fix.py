#!/usr/bin/env python3
"""Verify that the answer checking fixes work."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_translator"))

from pg.translator import PGTranslator

print("=" * 70)
print("VERIFYING ANSWER CHECKING FIX")
print("=" * 70)

problem_file = "d:/pg/tutorial/sample-problems/Algebra/FractionAnswer.pg"
translator = PGTranslator()

# First translation - render problem
print("\n1. RENDERING PROBLEM (seed=75965)...")
result1 = translator.translate(problem_file, seed=75965)

print(f"   Errors: {result1.errors if result1.errors else 'None'}")
print(f"   Answer blanks found: {len(result1.answer_blanks)}")

if result1.answer_blanks:
    for name, spec in result1.answer_blanks.items():
        print(f"     - {name}")
        if isinstance(spec, dict):
            if 'evaluator' in spec:
                print(f"       ✓ Has evaluator: {type(spec['evaluator']).__name__}")
            else:
                print(f"       ✗ NO EVALUATOR KEY!")
            if 'options' in spec:
                print(f"       ✓ Has options: {list(spec['options'].keys())}")
else:
    print("   ✗ NO ANSWER BLANKS FOUND!")

# Second translation - check answer (correct)
print("\n2. CHECKING ANSWER: 3/2 (correct, reduced)...")
result2 = translator.translate(problem_file, seed=75965, inputs={"AnSwEr0001": "3/2"})

if result2.answer_results:
    for name, ans_result in result2.answer_results.items():
        print(f"   Answer: {name}")
        print(f"     ✓ Score: {ans_result.score}")
        print(f"     ✓ Correct: {ans_result.correct}")
        if ans_result.answer_message:
            print(f"     Message: {ans_result.answer_message}")
    if result2.answer_results["AnSwEr0001"].correct:
        print("   ✓✓✓ CORRECT ANSWER ACCEPTED!")
    else:
        print("   ✗✗✗ CORRECT ANSWER REJECTED!")
else:
    print("   ✗✗✗ NO ANSWER RESULTS! Answer checking FAILED!")
    if result2.errors:
        print(f"   Errors: {result2.errors}")

# Third translation - check answer (incorrect - not reduced)
print("\n3. CHECKING ANSWER: 6/4 (incorrect, not reduced)...")
result3 = translator.translate(problem_file, seed=75965, inputs={"AnSwEr0001": "6/4"})

if result3.answer_results:
    for name, ans_result in result3.answer_results.items():
        print(f"   Answer: {name}")
        print(f"     Score: {ans_result.score}")
        print(f"     Correct: {ans_result.correct}")
        if ans_result.answer_message:
            print(f"     Feedback: {ans_result.answer_message}")
    if not result3.answer_results["AnSwEr0001"].correct:
        print("   ✓✓✓ INCORRECT ANSWER REJECTED!")
    else:
        print("   ✗✗✗ INCORRECT ANSWER ACCEPTED!")
else:
    print("   ✗✗✗ NO ANSWER RESULTS! Answer checking FAILED!")
    if result3.errors:
        print(f"   Errors: {result3.errors}")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
