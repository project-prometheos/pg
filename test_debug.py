#!/usr/bin/env python3
"""Debug test to see what's happening with answer blanks."""
import sys
sys.path.insert(0, 'packages/pg')

from pg.translator import PGTranslator

# Create translator
translator = PGTranslator()

# Translate the test problem
print("=== INITIAL TRANSLATION ===")
result = translator.translate(
    'tutorial/sample-problems/Algebra/FractionAnswer.pg',
    seed=42
)

print(f"Statement HTML length: {len(result.statement_html)}")
print(f"Answer blanks found: {len(result.answer_blanks)}")
print(f"Answer results: {result.answer_results}")
print(f"Errors: {result.errors}")

print("\n=== STATEMENT HTML (first 500 chars) ===")
print(result.statement_html[:500])

print("\n=== ANSWER BLANKS ===")
if result.answer_blanks:
    for name, blank_info in result.answer_blanks.items():
        print(f"Answer '{name}':")
        print(f"  Type: {type(blank_info)}")
        if isinstance(blank_info, dict):
            print(f"  Keys: {list(blank_info.keys())}")
            if 'evaluator' in blank_info:
                print(f"  Evaluator type: {type(blank_info['evaluator'])}")
                print(f"  Evaluator: {blank_info['evaluator']}")
        else:
            print(f"  Value: {blank_info}")
else:
    print("(No answer blanks)")

print("\n=== TESTING WITH USER ANSWERS ===")
result2 = translator.translate(
    'tutorial/sample-problems/Algebra/FractionAnswer.pg',
    seed=42,
    inputs={'AnSwEr0001': '3/2'}
)

print(f"Answer results: {result2.answer_results}")
if result2.answer_results:
    for name, ans_result in result2.answer_results.items():
        print(f"  {name}: score={ans_result.score}, correct={ans_result.correct}, message='{ans_result.answer_message}'")
else:
    print("(No answer results)")

print(f"Errors: {result2.errors}")
