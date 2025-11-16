#!/usr/bin/env python3
"""Test that PGML spec dicts include evaluator key."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_translator"))

from pg.translator import PGTranslator

# Test the FractionAnswer problem
problem_file = "d:/pg/tutorial/sample-problems/Algebra/FractionAnswer.pg"
translator = PGTranslator()

print("=" * 70)
print("Testing PGML answer blank spec dict structure")
print("=" * 70)

# Render problem without inputs
result = translator.translate(problem_file, seed=75965)

print(f"\nAnswer blanks found: {len(result.answer_blanks)}")
print()

success = True
for name, blank_info in result.answer_blanks.items():
    print(f"Answer blank: {name}")
    print(f"  Type: {type(blank_info)}")
    print(f"  Content: {blank_info}")
    print()

    # Check if it has the evaluator key
    if isinstance(blank_info, dict):
        if "evaluator" in blank_info:
            print(f"  ✓ HAS 'evaluator' key: {type(blank_info['evaluator'])}")
        else:
            print(f"  ✗ MISSING 'evaluator' key!")
            success = False

        if "options" in blank_info:
            print(f"  ✓ HAS 'options' key: {blank_info['options']}")
        else:
            print(f"  ⚠ Missing 'options' key")
    else:
        print(f"  ✗ Not a dict!")
        success = False

print()
print("=" * 70)
if success:
    print("✓ TEST PASSED: All answer blanks have evaluator key")
else:
    print("✗ TEST FAILED: Some answer blanks missing evaluator key")
print("=" * 70)
