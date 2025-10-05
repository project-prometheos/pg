#!/usr/bin/env python3
"""Test to see why pi/6 shows as numeric."""

from pg_translator import PGTranslator

# Test ps1-prob03.pg which has two answers
translator = PGTranslator()
result = translator.translate('webwork_ps1_pg/ps1-prob03.pg', seed=1234)

print("=" * 70)
print("Problem: ps1-prob03.pg")
print("=" * 70)

for i, (blank_name, blank_info) in enumerate(result.answer_blanks.items(), 1):
    print(f"\nAnswer {i} ({blank_name}):")

    evaluator = blank_info.get("evaluator")
    if evaluator and isinstance(evaluator, dict):
        ans_eval = evaluator.get("ans_eval")
        if ans_eval:
            print(f"  Type: {type(ans_eval).__name__}")
            print(f"  TeX(): {ans_eval.TeX()}")
            print(f"  string(): {ans_eval.string()}")

            # Check if it has value attribute
            if hasattr(ans_eval, 'value'):
                print(f"  value: {ans_eval.value}")

print("\n" + "=" * 70)
print("\nNow testing ps1-prob02.pg for comparison:")
print("=" * 70)

result2 = translator.translate('webwork_ps1_pg/ps1-prob02.pg', seed=1234)

for i, (blank_name, blank_info) in enumerate(result2.answer_blanks.items(), 1):
    print(f"\nAnswer {i} ({blank_name}):")

    evaluator = blank_info.get("evaluator")
    if evaluator and isinstance(evaluator, dict):
        ans_eval = evaluator.get("ans_eval")
        if ans_eval:
            print(f"  Type: {type(ans_eval).__name__}")
            print(f"  TeX(): {ans_eval.TeX()}")
            print(f"  string(): {ans_eval.string()}")

            # Check if it has value attribute
            if hasattr(ans_eval, 'value'):
                print(f"  value: {ans_eval.value}")
