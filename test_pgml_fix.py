#!/usr/bin/env python3
"""Quick test of the PGML fix."""
import sys
sys.path.insert(0, 'packages/pg')

from pg.translator import PGTranslator

# Create translator
translator = PGTranslator()

# Translate the test problem
result = translator.translate(
    'tutorial/sample-problems/Algebra/FractionAnswer.pg',
    seed=42
)

print("=== TRANSLATION RESULT ===")
print(f"Statement HTML length: {len(result.statement_html)}")
print(f"Answer blanks found: {len(result.answer_blanks)}")
print(f"Errors: {result.errors}")

# Check what's in answer blanks
if result.answer_blanks:
    for name, blank_info in result.answer_blanks.items():
        print(f"\nAnswer blank '{name}':")
        print(f"  Type: {type(blank_info)}")
        if isinstance(blank_info, dict):
            print(f"  Keys: {list(blank_info.keys())}")
else:
    print("\n(No answer blanks detected)")

# Show a snippet of the statement
print(f"\nStatement snippet:")
print(result.statement_html[:300] if result.statement_html else "(empty)")
