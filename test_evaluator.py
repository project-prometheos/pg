#!/usr/bin/env python3
"""Test script to check evaluator structure."""

from pg_translator import PGTranslator

# Create translator and translate problem
translator = PGTranslator()
result = translator.translate('webwork_ps1_pg/ps1-prob01.pg', seed=1234)

# Get first answer blank
blank_name = list(result.answer_blanks.keys())[0]
blank_info = result.answer_blanks[blank_name]

print(f"Blank name: {blank_name}")
print(f"Blank info type: {type(blank_info)}")
print(
    f"Blank info keys: {blank_info.keys() if isinstance(blank_info, dict) else 'Not a dict'}")

evaluator = blank_info.get("evaluator") if isinstance(
    blank_info, dict) else blank_info

print(f"\nEvaluator type: {type(evaluator)}")

if isinstance(evaluator, dict):
    print(f"Evaluator keys: {evaluator.keys()}")
    print(f"Evaluator contents:")
    for key, value in evaluator.items():
        print(f"  {key}: {type(value)} = {repr(value)[:100]}")

    # Check for ans_eval
    if 'ans_eval' in evaluator:
        ans_eval = evaluator['ans_eval']
        print(f"\nans_eval type: {type(ans_eval)}")
        print(
            f"ans_eval dir: {[x for x in dir(ans_eval) if not x.startswith('_')]}")
        print(
            f"ans_eval has correct_answer: {hasattr(ans_eval, 'correct_answer')}")

        # Try different methods to get the answer
        print(f"\nans_eval value: {ans_eval}")
        print(f"ans_eval repr: {repr(ans_eval)}")

        if hasattr(ans_eval, 'TeX'):
            print(f"ans_eval.TeX(): {ans_eval.TeX()}")
        if hasattr(ans_eval, 'string'):
            print(f"ans_eval.string: {ans_eval.string}")
        if hasattr(ans_eval, 'value'):
            print(f"ans_eval.value: {ans_eval.value}")
        if hasattr(ans_eval, 'to_string'):
            print(f"ans_eval.to_string(): {ans_eval.to_string()}")
        if hasattr(ans_eval, 'correct_answer'):
            correct = ans_eval.correct_answer
            print(f"\nCorrect answer type: {type(correct)}")
            print(f"Correct answer value: {correct}")
            if hasattr(correct, 'to_string'):
                print(f"Correct answer to_string(): {correct.to_string()}")
else:
    print(
        f"Evaluator dir: {[x for x in dir(evaluator) if not x.startswith('_')]}")
    print(f"Has correct_answer: {hasattr(evaluator, 'correct_answer')}")

    if hasattr(evaluator, 'correct_answer'):
        correct = evaluator.correct_answer
        print(f"\nCorrect answer type: {type(correct)}")
        print(f"Correct answer value: {correct}")
        print(f"Correct answer repr: {repr(correct)}")

        if hasattr(correct, 'to_string'):
            print(f"Correct answer to_string(): {correct.to_string()}")
