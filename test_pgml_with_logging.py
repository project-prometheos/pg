#!/usr/bin/env python3
"""Test with logging enabled to trace PGML execution."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_translator"))

from pg.translator import PGTranslator

problem_file = "tutorial/sample-problems/Algebra/FractionAnswer.pg"
translator = PGTranslator()

print("=" * 70)
print("TESTING PGML WITH LOGGING ENABLED")
print("=" * 70)
print("\nTranslating problem with logging enabled...")
print("(Check stderr for [SANDBOX-PGML] messages)\n")

result = translator.translate(problem_file, seed=75965)

print(f"\nAfter translate():")
print(f"  Answer blanks: {len(result.answer_blanks)}")
for name, entry in result.answer_blanks.items():
    print(f"    {name}: type={type(entry)}")
    if isinstance(entry, dict):
        print(f"      keys={list(entry.keys())}")
        if 'options' in entry:
            print(f"      ✓ has options={entry['options']}")
        else:
            print(f"      ✗ NO OPTIONS KEY!")
    else:
        print(f"      value={entry}")

print("\n" + "=" * 70)
