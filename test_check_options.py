#!/usr/bin/env python3
"""Check if cmp_options are being extracted correctly."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_translator"))

from pg.translator import PGTranslator

problem_file = "tutorial/sample-problems/Algebra/FractionAnswer.pg"
translator = PGTranslator()

print("=" * 70)
print("CHECKING CMP OPTIONS")
print("=" * 70)

# First translation - render problem without inputs
result = translator.translate(problem_file, seed=75965)

print(f"\nAfter first translation:")
print(f"  Answer blanks: {len(result.answer_blanks)}")
for name, entry in result.answer_blanks.items():
    print(f"\n  {name}:")
    print(f"    Type: {type(entry)}")
    if isinstance(entry, dict):
        print(f"    Keys: {list(entry.keys())}")
        if 'options' in entry:
            print(f"    Options: {entry['options']}")
            if 'studentsMustReduceFractions' in entry['options']:
                print(f"      studentsMustReduceFractions = {entry['options']['studentsMustReduceFractions']}")
        if 'evaluator' in entry:
            print(f"    Evaluator: {entry['evaluator']}")

print("\n" + "=" * 70)
